from collections import Counter
from decimal import Decimal


def cell(value, ignore_case):
    if value is None:
        return ("null", "")
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, (int, float, Decimal)):
        n = Decimal(str(value))
        return ("number", n if n.is_finite() else str(n))
    if isinstance(value, str):
        return ("str", value.casefold() if ignore_case else value)
    return (type(value).__name__, str(value))


def rows_equal(left, right, ordered=False, ignore_case=False):
    def shaped(rows):
        return [tuple(cell(value, ignore_case) for value in row) for row in rows]
    a, b = shaped(left), shaped(right)
    return a == b if ordered else Counter(a) == Counter(b)


def compare_select(expected, actual, task):
    columns, rows = expected
    received_columns, received_rows = actual
    if len(columns) != len(received_columns):
        return False, f"Eltérő oszlopszám: várt {len(columns)}, kapott {len(received_columns)}."
    if task.column_names and columns != received_columns:
        return False, "Az oszlopnevek vagy sorrendjük eltér."
    if len(rows) != len(received_rows):
        return False, f"Eltérő sorszám: várt {len(rows)}, kapott {len(received_rows)}."
    if rows_equal(rows, received_rows, task.ordered, task.case_insensitive):
        return True, "Az eredmény egyezik."
    if task.ordered and rows_equal(rows, received_rows, False, task.case_insensitive):
        return False, "A sorok egyeznek, de a kötelező sorrend eltér."
    if not task.case_insensitive and rows_equal(rows, received_rows, task.ordered, True):
        return False, "Csak a kis- és nagybetűk használata tér el."
    return False, "A sorok tartalma vagy ismétlődése eltér."


def compare_state(expected, actual, task):
    absent, extra = sorted(expected.keys() - actual.keys()), sorted(actual.keys() - expected.keys())
    faults = [*(f"Hiányzó objektum: {name}." for name in absent),
              *(f"Váratlan objektum: {name}." for name in extra)]
    for name in sorted(expected.keys() & actual.keys()):
        wanted_meta, wanted_rows = expected[name]
        actual_meta, actual_rows = actual[name]
        if wanted_meta != actual_meta:
            faults.append(f"{name}: az objektumtípus, oszlopok, adattípusok vagy megszorítások eltérnek.")
        if not rows_equal(wanted_rows, actual_rows, ignore_case=task.case_insensitive):
            reason = (f"várt {len(wanted_rows)}, kapott {len(actual_rows)} sor"
                      if len(wanted_rows) != len(actual_rows) else "a sorok tartalma vagy ismétlődése eltér")
            faults.append(f"{name}: {reason}.")
    return (False, " ".join(faults)) if faults else (True, "A táblák és nézetek végállapota egyezik.")


def compare_insert(expected, actual, task):
    return compare_state(expected[1], actual[1], task)


def compare_update(expected, actual, task):
    return compare_state(expected[1], actual[1], task)


def compare_delete(expected, actual, task):
    return compare_state(expected[1], actual[1], task)


def compare_create(expected, actual, task):
    return compare_state(expected[1], actual[1], task)


def compare_drop(expected, actual, task):
    return compare_state(expected[1], actual[1], task)
