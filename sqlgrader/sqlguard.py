"""Conservative PostgreSQL AST gate for this teaching subset, not a full sandbox."""
import json
from pglast import parser
from .database import SQLSyntaxError

FUNCTIONS = {"count", "sum", "avg", "min", "max", "round", "abs", "lower",
             "upper", "length", "char_length", "date_part", "date_trunc",
             "row_number", "rank", "dense_rank", "concat", "concat_ws", "substring",
             "btrim", "ltrim", "rtrim", "replace", "left", "right", "position", "strpos",
             "split_part", "translate", "regexp_replace", "regexp_match", "regexp_substr",
             "floor", "ceil", "ceiling", "mod", "power", "sqrt", "trunc", "sign",
             "to_char", "to_date", "make_date", "extract", "age", "row_number",
             "lag", "lead", "first_value", "last_value", "ntile", "percent_rank",
             "string_agg", "array_agg", "bool_and", "bool_or", "every"}
ROOTS = {"select": "SelectStmt", "insert": "InsertStmt",
         "update": "UpdateStmt", "delete": "DeleteStmt", "create_table": "CreateStmt",
         "create_view": "ViewStmt", "drop_table": "DropStmt", "drop_view": "DropStmt"}


def validate_sql(sql, kind, target=None):
    if not isinstance(sql, str) or not sql.strip() or len(sql) > 20000:
        raise ValueError("Hiányzó vagy túl hosszú SQL.")
    try:
        tree = json.loads(parser.parse_sql_json(sql))
    except parser.ParseError as error:
        raise SQLSyntaxError("Az SQL szintaxisa hibás.") from error
    statements = tree.get("stmts", [])
    if len(statements) != 1:
        raise ValueError("Pontosan egy SQL-utasítás adható meg.")
    root = statements[0]["stmt"]
    expected = ROOTS[kind]
    if set(root) != {expected}:
        raise ValueError(f"A feladat típusa: {kind}.")
    node = root[expected]
    if kind in {"insert", "update", "delete"}:
        if node["relation"]["relname"] != target:
            raise ValueError("Nem a feladat céltábláját módosítja.")
        if node.get("returningList") or node.get("onConflictClause"):
            raise ValueError("RETURNING és ON CONFLICT még nem támogatott.")

    if kind in {"create_table", "create_view"}:
        rel = node["relation"] if kind == "create_table" else node["view"]
        if rel.get("relname") != target or rel.get("relpersistence", "p") != "p":
            raise ValueError("Csak az előírt nevű, helyi objektum hozható létre.")
        if any(node.get(key) for key in ("inhRelations", "partspec", "tablespacename", "ofTypename", "replace")):
            raise ValueError("Ez a CREATE-változat nem támogatott.")
    if kind in {"drop_table", "drop_view"}:
        objects = node["objects"]
        wanted = "OBJECT_TABLE" if kind == "drop_table" else "OBJECT_VIEW"
        plain = [[part["String"]["sval"] for part in item["List"]["items"]] for item in objects]
        if plain != [[target]] or node["removeType"] != wanted:
            raise ValueError("Csak az előírt helyi tábla vagy nézet törölhető.")

    def walk(value, top=False):
        if isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                if key[0].isupper() and key.endswith("Stmt") and key != "SelectStmt" and not (top and key == expected):
                    raise ValueError("Beágyazott módosítás nem engedélyezett.")
                if key in ("intoClause", "lockingClause") and item:
                    raise ValueError("SELECT INTO és sorzárolás nem engedélyezett.")
                if key in ("schemaname", "catalogname") and item:
                    raise ValueError("Séma- vagy adatbázis-minősítés nem engedélyezett.")
                if key == "RangeVar" and item.get("relname", "").startswith(("pg_", "sql_")):
                    raise ValueError("Rendszertábla nem használható.")
                if key == "FuncCall":
                    names = [part["String"]["sval"] for part in item["funcname"]]
                    if names[-1] not in FUNCTIONS or (len(names) != 1 and (len(names) != 2 or names[0] != "pg_catalog")):
                        raise ValueError("A függvény nem része az engedélyezett tananyagnak.")
                walk(item)
    walk(root, True)
    return sql


def select_requirements(statement, task):
    """Inspect only explicitly requested SQL structure, using the parsed PostgreSQL AST."""
    if not (task.require_order_by or task.required_functions):
        return []
    tree = json.loads(parser.parse_sql_json(statement))["stmts"][0]["stmt"]["SelectStmt"]
    found = set()
    def visit(value):
        if isinstance(value, dict):
            if "FuncCall" in value:
                names = value["FuncCall"].get("funcname", [])
                if names:
                    found.add(names[-1]["String"]["sval"])
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    visit(tree)
    missing = []
    if task.require_order_by and not tree.get("sortClause"):
        missing.append("A feladat a külső lekérdezésben ORDER BY záradékot ír elő.")
    for name in task.required_functions:
        if name not in found:
            missing.append(f"A feladat a(z) {name.upper()} szövegfüggvény használatát írja elő.")
    return missing
