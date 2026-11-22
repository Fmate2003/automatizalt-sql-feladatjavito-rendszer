"""Local AI suggestions for a teacher; official grading is independent."""
import json
import logging
from pathlib import Path
import time
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

LOG = logging.getLogger(__name__)
RUBRIC = Path(__file__).resolve().parents[1] / "docs" / "AI_PONTOZASI_UTMUTATO.md"
SKIP = frozenset({"MISSING", "SYSTEM_ERROR", "MANUAL", "SYNTAX_ERROR", "INVALID_SQL"})


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def skipped(row):
    return row["status"] in SKIP or any(
        item["check"] == "syntax_credit" for item in row.get("criteria", [])
    )


def facts(row):
    items = {}
    for i, case in enumerate(row["cases"], 1):
        if case["status"] != "PASS":
            items[f"teszt_{i}"] = f"{case['case']}: {case['reason']}"
    for i, criterion in enumerate(row.get("criteria", []), 1):
        label = criterion["label"]
        if criterion["points"] == criterion["maximum"]:
            prefix = "Teljesült"
        elif criterion["points"]:
            prefix = "Részben teljesült"
        else:
            prefix = "Nem teljesült"
        items[f"feltetel_{i}"] = f"{prefix}: {label}. {criterion['points']}/{criterion['maximum']} pont."
    return items


def factual_note(row, highlight=None):
    if skipped(row):
        return row["reason"]
    if row["status"] == "PASS":
        return "Minden előírt ellenőrzés sikeres. A megoldás teljes pontot kapott."
    details = facts(row)
    if highlight in details:
        details = {highlight: details[highlight], **details}
    return " ".join(details.values()) or row["reason"]


def payload(tasks):
    """No student name, identifier, answer SQL or reference SQL is sent."""
    return {
        row["id"]: {
            "feladat": row["description"] if row["status"] == "PASS" else row.get("kind", ""),
            "status": row["status"], "megallapitott_pont": row["points"],
            "maximum": row["maximum"], "tenyek": facts(row),
        }
        for row in tasks
    }


def batches(data):
    chunk, size = {}, 0
    for key, item in data.items():
        length = len(json.dumps(item, ensure_ascii=False))
        if length > 4500:
            continue
        if chunk and (len(chunk) >= 3 or size + length > 3000):
            yield chunk
            chunk, size = {}, 0
        chunk[key] = item
        size += length
    if chunk:
        yield chunk


def object_schema(properties):
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}


def request_notes(config, rules, data, seconds):
    props = {
        key: object_schema({
            "kiemeles": {"type": "string", "enum": ["", *item["tenyek"]]},
            "javasolt_pont": {"type": "integer", "minimum": 0, "maximum": item["maximum"]},
            "indoklas": {"type": "string"},
        })
        for key, item in data.items()
    }
    request = Request(config.ai_url, data=json.dumps({
        "model": config.model, "stream": False, "think": False,
        "format": object_schema(props),
        "options": {"num_ctx": 4096, "num_predict": 700, "temperature": 0},
        "messages": [{"role": "system", "content": rules},
                     {"role": "user", "content": json.dumps(data, ensure_ascii=False)}],
    }, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    opener = build_opener(ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=seconds) as stream:
        raw = stream.read(80001)
    if len(raw) > 80000:
        raise ValueError("Az AI-válasz túl nagy.")
    response = json.loads(raw)
    if response.get("done_reason") == "length":
        raise ValueError("Az AI-válasz elérte a hosszhatárt.")
    result = json.loads(response["message"]["content"])
    if not isinstance(result, dict):
        raise ValueError("Az AI nem JSON-objektumot adott vissza.")
    return result


def validate_suggestion(candidate, item):
    """Return advisory content only after format and bounds checks."""
    if not isinstance(candidate, dict) or set(candidate) != {"kiemeles", "javasolt_pont", "indoklas"}:
        return None
    focus, score, reason = (candidate["kiemeles"], candidate["javasolt_pont"], candidate["indoklas"])
    if (not isinstance(focus, str) or focus not in ("", *item["tenyek"])
            or type(score) is not int or not 0 <= score <= item["maximum"]
            or not isinstance(reason, str) or not 0 < len(reason.strip()) <= 650
            or not reason.isprintable()):
        return None
    return {"kiemeles": focus or None, "javasolt_pont": score, "indoklas": reason.strip(),
            "elter_a_szabalytol": score != item["megallapitott_pont"]}


def deterministic(row):
    return {"text": factual_note(row), "source": "szabály", "javaslat": None}


def review(config, tasks):
    rules = RUBRIC.read_text(encoding="utf-8")
    notes = {row["id"]: deterministic(row) for row in tasks}
    eligible = {row["id"]: row for row in tasks if not skipped(row)}
    deadline = time.monotonic() + max(0, config.ai_seconds - 3)
    for batch in batches(payload(eligible.values())):
        remaining = deadline - time.monotonic()
        if remaining < 1:
            break
        try:
            decoded = request_notes(config, rules, batch, remaining)
        except OSError as error:
            LOG.error("Helyi AI nem érhető el (%s).", type(error).__name__)
            break
        except (ValueError, KeyError, TypeError) as error:
            LOG.error("Nem használható AI-válasz (%s).", type(error).__name__)
            continue
        for key, item in batch.items():
            suggestion = validate_suggestion(decoded.get(key), item)
            if suggestion is None:
                continue
            # The model can reference a grader fact. Its own text and proposed
            # score do not become part of the official grade or student prose.
            notes[key]["javaslat"] = suggestion
    return notes
