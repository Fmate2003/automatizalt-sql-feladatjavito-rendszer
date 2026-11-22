"""The teacher key and the student submission are separate UTF-8 SQL files."""
from dataclasses import dataclass
import json
from pathlib import Path
import re

from .rubric import parse as parse_rubric

ID = r"(?:[1-9]\d*)(?:[a-z])?"
KEY = re.compile(rf"^\s*--\s*({ID})\s+(solutionpre|studentpre|solution|comparetype)\b\s*(.*?)\s*$", re.I)
ANSWER = re.compile(rf"^\s*--\s*({ID})(?:[ \t]*((?:select|with|insert|update|delete|create|drop|grant)\b.*))?\s*$", re.I)
HEADER = re.compile(r"^\s*--\s*(név|nev|neptun)\s*:\s*(.*?)\s*$", re.I)
PREGEN = re.compile(r"^\s*--\s*pregen\s+(\S+)\s*$", re.I)
CASE = re.compile(r"^\s*--\s*case\s+([a-z0-9_]+)(?:\s+(\S+))?\s*$", re.I)
KINDS = {"select", "insert", "update", "delete", "create_table", "create_view", "drop_table", "drop_view", "create_user", "grant"}
OBJECT = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,29}\Z")


@dataclass(frozen=True)
class Task:
    id: str
    kind: str
    points: int
    solution: str
    description: str
    target: str | None
    ordered: bool
    column_names: bool
    case_insensitive: bool
    solutionpre: str
    studentpre: str
    partial: tuple
    syntax_credit: int
    require_order_by: bool = False
    required_functions: tuple = ()


def read(path, limit):
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"Túl nagy bemeneti fájl: {path.name}")
    return data.decode("utf-8-sig")


def local_sql(folder, name, limit):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.sql", name, re.I) or name.casefold() == "solution.sql":
        raise ValueError(f"Érvénytelen előkészítő fájlnév: {name}")
    path = (folder / name).resolve()
    if path.parent != folder.resolve() or not path.is_file():
        raise ValueError(f"Hiányzó vagy érvénytelen előkészítő fájl: {name}")
    return read(path, limit)


def key(folder, limit):
    source = read(folder / "solution.sql", limit)
    blocks, cases = {}, {}
    section = None
    pregen = "create_db.sql"
    explicit_pregen = False
    for line in source.splitlines():
        if match := PREGEN.fullmatch(line):
            if explicit_pregen or section is not None:
                raise ValueError("A --pregen fejléc egyszer, a feladatok előtt szerepelhet.")
            pregen, explicit_pregen = match[1], True
        elif match := CASE.fullmatch(line):
            name, script = match[1].casefold(), match[2]
            if name in cases or section is not None:
                raise ValueError("Ismétlődő vagy rossz helyen szereplő --case fejléc.")
            cases[name] = script
        elif match := KEY.fullmatch(line):
            task_id, directive = match[1].lower(), match[2].lower()
            parts = blocks.setdefault(task_id, {})
            if directive in parts:
                raise ValueError(f"Ismétlődő fejléc: {task_id} {directive}.")
            section = parts[directive] = [match[3]]
        elif section is not None:
            section.append(line)
        elif line.strip() and not line.lstrip().startswith("--"):
            raise ValueError("SQL-utasítás szerepel feladatfejléc előtt a javítókulcsban.")
    if not blocks:
        raise ValueError("A solution.sql nem tartalmaz feladatot.")

    tasks = []
    for id_, block in blocks.items():
        parts = {tag: "\n".join(lines).strip() for tag, lines in block.items()}
        try:
            settings = json.loads(parts.get("comparetype", ""))
        except ValueError as exc:
            raise ValueError(f"{id_}: a comparetype blokkban JSON objektum szükséges.") from exc
        known = {"kind", "points", "description", "target", "ordered", "column_names", "case_insensitive", "partial", "syntax_credit", "require_order_by", "required_functions"}
        if not isinstance(settings, dict) or set(settings) - known:
            raise ValueError(f"{id_}: hibás vagy ismeretlen comparetype mező.")
        kind, points, target = settings.get("kind"), settings.get("points"), settings.get("target")
        if not isinstance(kind, str) or kind not in KINDS or type(points) is not int or not 0 < points <= 10000:
            raise ValueError(f"{id_}: érvénytelen feladattípus vagy maximumpont.")
        if not parts.get("solution") or (kind != "select" and
                (not isinstance(target, str) or not OBJECT.fullmatch(target))):
            raise ValueError(f"{id_}: hiányzó megoldás vagy célnév.")
        flags = [settings.get(name, False) for name in ("ordered", "column_names", "case_insensitive")]
        if any(type(value) is not bool for value in flags):
            raise ValueError(f"{id_}: a kapcsolók true vagy false értékűek legyenek.")
        try:
            partial = parse_rubric(settings.get("partial", "auto"), kind, points, flags[0], flags[1])
        except ValueError as exc:
            raise ValueError(f"{id_}: {exc}") from exc
        syntax_credit = settings.get("syntax_credit", 0)
        if type(syntax_credit) is not int or not 0 <= syntax_credit < points:
            raise ValueError(f"{id_}: a syntax_credit egész szám és a maximumpontnál kisebb legyen.")
        require_order_by = settings.get("require_order_by", False)
        required_functions = settings.get("required_functions", [])
        if (type(require_order_by) is not bool or not isinstance(required_functions, list)
                or any(f not in ("lower", "upper") for f in required_functions)
                or len(set(required_functions)) != len(required_functions)
                or (kind != "select" and (require_order_by or required_functions))):
            raise ValueError(f"{id_}: hibás SELECT technikai követelmény.")
        description = settings.get("description", f"{id_} feladat")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"{id_}: érvénytelen feladatleírás.")
        tasks.append(Task(id_, kind, points, parts["solution"], description, target,
                          *flags, parts.get("solutionpre", ""), parts.get("studentpre", ""), partial, syntax_credit,
                          require_order_by, tuple(required_functions)))

    cases = cases or {"base": None}
    scripts = {name: local_sql(folder, filename, limit) if filename else "" for name, filename in cases.items()}
    excluded = {"solution.sql", pregen.casefold(), *(name.casefold() for name in cases.values() if name)}
    return tasks, local_sql(folder, pregen, limit), scripts, excluded


def submission(path, task_ids, limit):
    meta, answers = {}, {}
    section = None
    for line in read(path, limit).splitlines():
        if match := ANSWER.fullmatch(line):
            task = match[1].lower()
            if task not in task_ids or task in answers:
                raise ValueError(f"Ismeretlen vagy ismétlődő feladatazonosító: {task}.")
            section = answers[task] = [match[2]] if match[2] else []
        elif section is not None:
            section.append(line)
        elif match := HEADER.fullmatch(line):
            name = "neptun" if match[1].lower() == "neptun" else "name"
            if name in meta:
                raise ValueError("Ismétlődő hallgatói fejléc.")
            meta[name] = match[2]
        elif line.strip() and not line.lstrip().startswith("--"):
            raise ValueError("Fejléc nélküli SQL-utasítás.")
    name, neptun = meta.get("name", ""), meta.get("neptun", "").upper()
    if not name or len(name) > 100 or not re.fullmatch(r"[0-9A-Z]{6}", neptun):
        raise ValueError("A --név: és a 6 karakteres --neptun: fejléc kötelező.")
    return name, neptun, {id_: "\n".join(lines).strip() for id_, lines in answers.items()}
