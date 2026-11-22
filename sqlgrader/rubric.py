"""Evidence-based partial scoring. The key chooses checks and weights, never SQL text style."""
from collections import Counter
from fractions import Fraction

from .comparison import cell, compare_select, compare_state, rows_equal

LABELS = {
    "exact": "Teljes egyezés",
    "column_count": "Elvárt oszlopszám",
    "column_names": "Elvárt oszlopnevek",
    "row_count": "Elvárt sorszám",
    "matching_rows": "Helyes sorok tartalma és előfordulása",
    "matching_rows_ci": "Helyes sorok kis- és nagybetűtől függetlenül",
    "order": "Kötelező sorrend",
    "target_row_count": "A célobjektum elvárt sorszáma",
    "target_rows": "A célobjektum elvárt adatai",
    "changed_rows": "Az elvárt adatváltozások",
    "change_count": "Az adatváltozások elvárt darabszáma",
    "other_objects": "A többi objektum elvárt állapota",
    "object": "Az előírt nevű és típusú objektum",
    "columns": "Oszlopnevek és sorrendjük",
    "types": "Adattípusok és oszloptulajdonságok",
    "constraints": "Megszorítások",
    "removed": "A célobjektum törlése",
}
SELECT = {"column_count", "column_names", "row_count", "matching_rows", "matching_rows_ci", "order"}
DML = {"target_row_count", "target_rows", "changed_rows", "change_count", "other_objects"}
DDL = {"object", "columns", "types", "constraints", "target_rows", "other_objects"}
DROP = {"removed", "other_objects"}
CHECKS = {"select": SELECT, "insert": DML, "update": DML, "delete": DML,
          "create_table": DDL, "create_view": DDL - {"constraints"},
          "drop_table": DROP, "drop_view": DROP}
PROJECTION = {"matching_rows", "matching_rows_ci", "target_rows", "changed_rows"}


def allowed(kind, ordered, names):
    checks = set(CHECKS.get(kind, ())) | {"exact"}
    if not ordered:
        checks.discard("order")
    if not names:
        checks.discard("column_names")
    return checks


def auto(kind, points, ordered, names):
    if kind not in CHECKS:
        return {}
    weights = {
        "select": {"matching_rows": 5, "column_count": 1, "row_count": 1,
                   **({"order": 2} if ordered else {}), **({"column_names": 1} if names else {})},
        "insert": {"changed_rows": 5, "change_count": 1, "other_objects": 1},
        "update": {"changed_rows": 5, "change_count": 1, "other_objects": 1},
        "delete": {"changed_rows": 5, "change_count": 1, "other_objects": 1},
        "create_table": {"object": 1, "columns": 2, "types": 2, "constraints": 2, "other_objects": 1},
        "create_view": {"object": 1, "columns": 1, "types": 1, "target_rows": 4, "other_objects": 1},
        "drop_table": {"removed": 4, "other_objects": 1},
        "drop_view": {"removed": 4, "other_objects": 1},
    }[kind]
    shares = {check: Fraction(weight * (points - 1), sum(weights.values())) for check, weight in weights.items()}
    amounts = {check: int(value) for check, value in shares.items()}
    left = points - 1 - sum(amounts.values())
    for check in sorted(weights, key=lambda name: (shares[name] - amounts[name], weights[name]), reverse=True)[:left]:
        amounts[check] += 1
    return {**{key: value for key, value in amounts.items() if value}, "exact": 1}


def parse(raw, kind, points, ordered, names):
    if raw == "auto" or raw == {}:
        raw = auto(kind, points, ordered, names)
    elif raw == "off":
        return ()
    if not isinstance(raw, dict):
        raise ValueError("A partial mező auto, off vagy név szerinti pontrubrika legyen.")
    if not raw and kind not in CHECKS:
        return ()
    criteria, signatures = [], set()
    for id_, spec in raw.items():
        if type(spec) is int:
            check, weight, columns, label = id_, spec, [], None
        elif isinstance(spec, dict) and set(spec) <= {"check", "points", "columns", "label"}:
            check, weight = spec.get("check"), spec.get("points")
            columns, label = spec.get("columns", []), spec.get("label")
        else:
            raise ValueError(f"Érvénytelen részpont-feltétel: {id_}.")
        if not isinstance(check, str) or check not in allowed(kind, ordered, names):
            raise ValueError(f"{id_}: ez az ellenőrzés nem alkalmazható erre a feladatra.")
        if type(weight) is not int or weight <= 0:
            raise ValueError(f"{id_}: pozitív egész súly szükséges.")
        if not isinstance(columns, list) or any(type(c) is not int or not 1 <= c <= 512 for c in columns) or len(set(columns)) != len(columns):
            raise ValueError(f"{id_}: az oszlopok egytől számozott, különböző egész számok.")
        if columns and check not in PROJECTION:
            raise ValueError(f"{id_}: ez az ellenőrzés nem fogad oszloplistát.")
        if label is not None and (not isinstance(label, str) or not label.strip() or len(label) > 240):
            raise ValueError(f"{id_}: érvénytelen címke.")
        signature = check, tuple(sorted(columns))
        if signature in signatures:
            raise ValueError(f"{id_}: ugyanaz a részpont-feltétel kétszer szerepel.")
        signatures.add(signature)
        criteria.append((id_, check, weight, tuple(columns), label or LABELS[check]))
    if sum(item[2] for item in criteria) != points or ("exact", ()) not in signatures:
        raise ValueError("A részpontok maximumának összege egyezzen a feladat maximumával, és legyen 'exact' feltétel.")
    return tuple(criteria)


def bag(rows, columns, ignore_case):
    return Counter(tuple(cell(row[c - 1], ignore_case) for c in columns)
                   if columns else tuple(cell(v, ignore_case) for v in row) for row in rows)


def overlap(wanted, actual):
    denominator = max(sum(wanted.values()), sum(actual.values()))
    return Fraction(sum((wanted & actual).values()), denominator) if denominator else Fraction(1)


def projection(total, actual, columns):
    if columns and (max(columns) > total or max(columns) > actual):
        if max(columns) > total:
            raise ValueError("A rubrika oszlopindexe nem létezik a tanári eredményben.")
        return False
    return True


def delta(before, after, name, columns, ignore_case):
    old = bag(before.get(name, (None, []))[1], columns, ignore_case)
    new = bag(after.get(name, (None, []))[1], columns, ignore_case)
    return Counter({(direction, row): count
                    for direction, changes in ((1, new - old), (-1, old - new))
                    for row, count in changes.items()})


def ratio(check, columns, expected, actual, task):
    if task.kind == "select":
        wc, wr = expected
        ac, ar = actual
        if check == "exact":
            return compare_select(expected, actual, task)[0]
        if check == "column_count":
            return len(wc) == len(ac)
        if check == "column_names":
            return wc == ac
        if check == "row_count":
            return len(wr) == len(ar)
        if check == "order":
            return rows_equal(wr, ar, True, task.case_insensitive)
        if not projection(len(wc), len(ac), columns):
            return False
        ignore_case = task.case_insensitive or check == "matching_rows_ci"
        return overlap(bag(wr, columns, ignore_case), bag(ar, columns, ignore_case))

    eb, ea = expected
    ab, aa = actual
    target = task.target.casefold()
    if check == "exact":
        return compare_state(ea, aa, task)[0]
    w, a = ea.get(target), aa.get(target)
    if check == "other_objects":
        # A no-op is valid if the reference also has no target change.
        def changed(before, after):
            previous, current = before.get(target), after.get(target)
            if previous is None or current is None:
                return previous != current
            return previous[0] != current[0] or not rows_equal(previous[1], current[1])
        if changed(eb, ea) and not changed(ab, aa):
            return False
        return compare_state({key: item for key, item in ea.items() if key != target},
                             {key: item for key, item in aa.items() if key != target}, task)[0]
    if check == "removed":
        return target in eb and target in ab and w is None and a is None
    if not w or not a:
        return False
    (wk, wc, wcons), wr = w
    (ak, ac, acons), ar = a
    if wk != ak:
        return False
    if check == "object":
        return True
    if check == "columns":
        return [field[0] for field in wc] == [field[0] for field in ac]
    if check == "types":
        return wc == ac
    if check == "constraints":
        return bool(wc) and [field[0] for field in wc] == [field[0] for field in ac] and wcons == acons
    if check == "target_row_count":
        return len(wr) == len(ar)
    if check == "change_count":
        def counts(changes):
            groups = Counter()
            for (direction, _), number in changes.items():
                groups[direction] += number
            return groups
        return counts(delta(eb, ea, target, (), task.case_insensitive)) == counts(
            delta(ab, aa, target, (), task.case_insensitive))
    if not projection(len(wc), len(ac), columns):
        return False
    if check == "target_rows":
        return overlap(bag(wr, columns, task.case_insensitive), bag(ar, columns, task.case_insensitive))
    return overlap(delta(eb, ea, target, columns, task.case_insensitive),
                   delta(ab, aa, target, columns, task.case_insensitive))


def score(task, case_checks):
    rows = []
    for id_, check, weight, _, label in task.partial:
        checks = [{"case": case, "earned": int(Fraction(result.get(id_, 0)) * weight)}
                  for case, result in case_checks]
        amount = min((case["earned"] for case in checks), default=0)
        rows.append({"id": id_, "check": check, "label": label, "points": amount,
                     "maximum": weight, "deducted": weight - amount, "cases": checks})
    return rows
