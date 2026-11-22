"""Resumable, cross-platform feedback generation from already saved grade reports."""
import argparse
from dataclasses import replace
from datetime import datetime
from functools import partial
import hashlib
import json
import logging
import multiprocessing
from pathlib import Path
import re
import sys

from . import ai, output
from .config import load
from .runtime import bounded, enable_debug

LOG = logging.getLogger(__name__)


def redact_tasks(report, identifiers=None):
    """Guard against accidentally embedding this student's identifiers in teacher text."""
    if identifiers is None:
        identifiers = (str(report.get("name", "")).strip(), str(report.get("neptun", "")).strip())
    # Work on a deep copy; official report values are never rewritten.
    tasks = json.loads(json.dumps(report["tasks"], ensure_ascii=False))

    def redact(value):
        if isinstance(value, str):
            for token in identifiers:
                if token:
                    value = value.replace(token, "[kitakarva]")
            return value
        if isinstance(value, list):
            return [redact(item) for item in value]
        if isinstance(value, dict):
            return {key: redact(item) for key, item in value.items()}
        return value
    return redact(tasks)


def fill(run, reports, config, *, worker=bounded, notify=print, retry=False):
    folder = run / "ai-folyamat"
    folder.mkdir(exist_ok=True)
    completed = accepted = 0
    identifiers = sorted({str(report[field]).strip() for report in reports
                          for field in ("name", "neptun") if report.get(field)},
                         key=len, reverse=True)
    for i, report in enumerate(reports, 1):
        code = report["neptun"]
        tasks = report["tasks"]
        safe_tasks = {row["id"]: row for row in redact_tasks(report, identifiers)}
        checkpoint = folder / (code + ".json")
        grade_id = hashlib.sha256(json.dumps(tasks, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        state = json.loads(checkpoint.read_text(encoding="utf-8")) if checkpoint.exists() else {}
        if state.get("grade_id") == grade_id and state.get("model") == config.model:
            notes = state.get("feladatok", {})
        else:
            notes = {}
        todo = [row for row in tasks if row["id"] not in notes or
                (retry and not ai.skipped(row) and not notes[row["id"]].get("javaslat"))]
        output.write_feedback(run, report, notes)
        for start in range(0, len(todo), 3):
            group = todo[start:start + 3]
            notify(f"AI {i}/{len(reports)} – feladatok: " + ", ".join(row["id"] for row in group), flush=True)
            model_notes = {}
            if any(not ai.skipped(row) for row in group):
                try:
                    model_notes = worker(ai.review, (config, [safe_tasks[row["id"]] for row in group]),
                                         config.ai_seconds + 4)
                except (TimeoutError, RuntimeError) as error:
                    LOG.error("Az AI-kérés kimaradt (%s); a biztos indok megmarad.", type(error).__name__)
            for row in group:
                key = row["id"]
                verified = ai.deterministic(row)
                supplied = model_notes.get(key, {}).get("javaslat")
                if supplied:
                    verified["javaslat"] = supplied
                    verified["text"] = ai.factual_note(row, supplied.get("kiemeles"))
                notes[key] = verified
            output.write_json(checkpoint, {"grade_id": grade_id, "model": config.model, "feladatok": notes})
            output.write_feedback(run, report, notes)
        output.write_teacher_feedback(folder / (code + ".txt"), report, notes)
        count = sum(note.get("javaslat") is not None for note in notes.values())
        accepted += count
        completed += len(tasks)
        notify(f"Elkészült: {code} – {output.point_label(report['points'])}/{report['maximum']}; "
               f"tanári AI-javaslat: {count}/{len(tasks)}.", flush=True)
    notify(f"Visszajelzés: {completed} feladat; ellenőrizendő AI-javaslat: {accepted}.", flush=True)
    return completed, accepted


def main(argv=None):
    parser = argparse.ArgumentParser(description="Helyi AI-javaslatok folytatása mentett pontlapokon")
    parser.add_argument("run", type=Path, help="A konkrét időbélyeges eredménymappa")
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--ujraproba", action="store_true", help="A kimaradt, AI-ra alkalmas válaszok újbóli kérése")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Részletes függvényhívás-napló")
    args = parser.parse_args(argv)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    try:
        logdir = Path(__file__).resolve().parents[1] / "logs"
        logdir.mkdir(exist_ok=True)
        logfile = logdir / (stamp + ".log")
        logging.basicConfig(
            level=logging.DEBUG if args.debug else logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=[logging.FileHandler(logfile, encoding="utf-8"), logging.StreamHandler()],
        )
        worker = partial(bounded, logfile=logfile, debug=args.debug)
        if args.debug:
            enable_debug()
    except OSError as error:
        print(f"Nem hozható létre az AI-naplófájl: {error}", file=sys.stderr)
        return 2

    print(f"Napló: {logfile}", flush=True)
    LOG.info("AI-folytatás indul | futás=%s config=%s újrapróba=%s debug=%s",
             args.run, args.config, args.ujraproba, args.debug)
    exit_code = 2
    try:
        reports = []
        if not (args.run / "osszesito.xls").is_file():
            raise ValueError("A konkrét futásmappát add meg, amely az osszesito.xls fájlt tartalmazza.")
        for path in sorted(args.run.glob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict) or not {"name", "neptun", "tasks", "maximum", "points"} <= value.keys():
                continue
            if not isinstance(value["neptun"], str) or not re.fullmatch(r"[A-Z0-9]{6}", value["neptun"]):
                raise ValueError(f"Érvénytelen azonosító a mentett pontlapon: {path.name}")
            if not (args.run / (output.stem(value["name"], value["neptun"]) + ".txt")).is_file():
                raise ValueError(f"Hiányzik az egyéni TXT: {path.name}")
            reports.append(value)
        if not reports:
            raise ValueError("Nincs feldolgozható egyéni pontlap.")
        fill(args.run, reports, load(args.config), worker=worker, retry=args.ujraproba)
        exit_code = 0
    except KeyboardInterrupt:
        LOG.warning("Megszakítva; a már mentett javaslatok megmaradtak.")
        exit_code = 130
    except (OSError, ValueError) as error:
        LOG.error("%s", error)
    finally:
        LOG.info("AI-folytatás vége | kilépési kód: %s", exit_code)
        if args.debug:
            sys.setprofile(None)
    return exit_code


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
