"""Statement framing and a conservative Oracle teaching subset."""
import re

TOKEN = re.compile(
    r'''--[^\r\n]*|/\*[\s\S]*?\*/|[nN]?[qQ]'(?:\[[\s\S]*?\]|\{[\s\S]*?\}|\([\s\S]*?\)|<[\s\S]*?>|(?P<d>[^\s])[\s\S]*?(?P=d))'|'''
    r"""'(?:''|[^'])*'|"(?:""|[^"])*"|[a-zA-Z_][\w$#]*|[^\s]"""
)
ROOTS = {
    "select": r"^(SELECT|WITH)\b",
    "insert": r"^INSERT\s+INTO\s+",
    "update": r"^UPDATE\s+",
    "delete": r"^DELETE\s+FROM\s+",
    "create_table": r"^CREATE\s+TABLE\s+",
    "create_view": r"^CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+",
    "drop_table": r"^DROP\s+TABLE\s+",
    "drop_view": r"^DROP\s+VIEW\s+",
}


def tokens(source):
    return [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(source)
            if not m.group().startswith(("--", "/*"))]


def split(source):
    start = 0
    result = []
    for text, offset, end in tokens(source):
        if text == ";":
            part = source[start:offset].strip()
            if tokens(part):
                result.append(part)
            start = end
    last = source[start:].strip()
    if tokens(last):
        result.append(last)
    return result


def validate(statement, task):
    if not isinstance(statement, str) or len(statement) > 20000:
        raise ValueError("Hiányzó vagy túl hosszú SQL.")
    parts = split(statement)
    if len(parts) != 1:
        raise ValueError("Pontosan egy SQL-utasítás adható meg.")
    codes = [token for token, _, _ in tokens(parts[0])]
    if any(t in {"@", ":"} for t in codes):
        raise ValueError("Adatbázislink és kötött paraméter nem használható.")
    words = " ".join("STRING" if "'" in t[:3] else t.upper() for t in codes)
    match = re.match(ROOTS[task.kind], words, re.I)
    if not match or re.search(r"\b(?:FUNCTION|PROCEDURE|JAVA|EXTERNAL|DIRECTORY|DBMS_\w+|UTL_\w+|SYS|SYSTEM)\b", words):
        raise ValueError("Az utasítástípus vagy a használt elem nem támogatott.")
    if re.search(r"\bFOR\s+UPDATE\b|\bTABLESPACE\b|\bAS\s+SELECT\b", words) and task.kind != "create_view":
        raise ValueError("Ez az SQL-változat nem támogatott.")
    if task.kind != "select":
        rest = words[match.end():].split()
        if not rest or rest[0] != task.target.upper() or rest[1:2] == ["."]:
            raise ValueError("Nem a feladat helyi célobjektumát használja.")
    return parts[0]


