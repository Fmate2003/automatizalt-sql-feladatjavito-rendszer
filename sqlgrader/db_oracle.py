"""Oracle adapter for a dedicated, isolated teaching PDB or instance."""
import os
import re
import secrets
import oracledb
from .database import fetch

from .oracle_syntax import split, tokens, validate


NEEDS_TIMEOUT_CLEANUP = True


def validate_config(config):
    if config.user.upper() != "SQLGRADER_ADMIN":
        raise ValueError("Oracle esetén dedikált SQLGRADER_ADMIN fiókot használj.")
    if config.oracle_client is not None and not isinstance(config.oracle_client, str):
        raise ValueError("Az oracle_client mező útvonal vagy null legyen.")
    if not isinstance(config.oracle_tablespace, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,29}", config.oracle_tablespace):
        raise ValueError("Hibás Oracle táblatérnév.")


def cleanup_labels(tokens):
    return [username(token) for token in tokens]


def connect(config, user=None, password=None):
    validate_config(config)
    if config.oracle_client and oracledb.is_thin_mode():
        oracledb.init_oracle_client(lib_dir=config.oracle_client)
    password = password if password is not None else os.getenv("SQLGRADER_DB_PASSWORD")
    if not password:
        raise ValueError("Oracle esetén állítsd be a SQLGRADER_DB_PASSWORD változót.")
    conn = oracledb.connect(user=user or config.user, password=password,
                            params=oracledb.ConnectParams(host=config.host, port=config.port,
                                                         service_name=config.database,
                                                         tcp_connect_timeout=config.connect_seconds,
                                                         retry_count=0))
    conn.call_timeout = config.statement_ms
    return conn


def check(config):
    with connect(config) as conn, conn.cursor() as cur:
        cur.execute("SELECT SYS_CONTEXT('USERENV','SESSION_USER'),SYS_CONTEXT('USERENV','CON_NAME') FROM dual")
        user, container = cur.fetchone()
        if user != "SQLGRADER_ADMIN" or container == "CDB\u0024ROOT":
            raise ValueError("Különálló Oracle oktatási PDB szükséges.")
        return container, user, conn.version


def username(token):
    if not re.fullmatch(r"[a-f0-9]{16}", token):
        raise ValueError("Érvénytelen futási azonosító.")
    return "SG_" + token.upper()


def quoted(name):
    return '"' + name.replace('"', '""') + '"'


def bounded_lob(value):
    if value.size() > 4096:
        raise OverflowError()
    return value.read()


def values(cur, limit):
    return [tuple(bounded_lob(value) if isinstance(value, oracledb.LOB) else value for value in row)
            for row in fetch(cur, limit)]


def snapshot(cur, limit):
    cur.execute("""SELECT object_name,object_type FROM user_objects
        WHERE object_type IN ('TABLE','VIEW') AND object_name NOT LIKE 'BIN$%' ORDER BY object_name""")
    result = {}
    for name, kind in fetch(cur, limit):
        cur.execute("""SELECT column_name,data_type,data_length,data_precision,data_scale,
                        char_length,char_used,nullable,data_default
                        FROM user_tab_columns WHERE table_name=:n ORDER BY column_id""", n=name)
        columns = [(*row[:-1], row[-1].strip() if row[-1] else None) for row in fetch(cur, limit)]
        cur.execute("""SELECT constraint_name,constraint_type,search_condition,r_constraint_name,delete_rule
                        FROM user_constraints WHERE table_name=:n AND constraint_type IN ('P','U','C','R')""", n=name)
        constraints = []
        for uc_name, uc_type, condition, ref, delete_rule in fetch(cur, limit):
            cur.execute("SELECT column_name FROM user_cons_columns WHERE constraint_name=:n ORDER BY position", n=uc_name)
            names = tuple(item[0] for item in fetch(cur, limit))
            reference = None
            if ref:
                cur.execute("""SELECT table_name,column_name FROM user_cons_columns
                               WHERE constraint_name=:n ORDER BY position""", n=ref)
                reference = tuple(fetch(cur, limit))
            constraints.append((uc_type, names, condition.strip() if condition else None, reference, delete_rule))
        cur.execute("SELECT * FROM " + quoted(name))
        result[name.casefold()] = ((kind, columns, sorted(constraints, key=repr)), values(cur, limit))
    return result


def cleanup(config, tokens_):
    with connect(config) as conn, conn.cursor() as cur:
        for token in tokens_:
            user = username(token)
            try:
                cur.execute(f"DROP USER {user} CASCADE")
            except oracledb.DatabaseError as exc:
                if getattr(exc.args[0], "code", None) != 1918:  # already absent
                    raise RuntimeError(f"Nem törölhető a javítói ideiglenes fiók: {user}") from exc


def run(config, task, scripts, answer, token):
    account = username(token)
    password = "Sg9_" + secrets.token_hex(12)
    stage, created = "setup", False
    try:
        with connect(config) as admin, admin.cursor() as cur:
            cur.execute(f'CREATE USER {account} IDENTIFIED BY "{password}" QUOTA 32M ON {config.oracle_tablespace}')
            created = True
            cur.execute(f"GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW TO {account}")
        with connect(config, account, password) as conn, conn.cursor() as cur:
            for source in scripts:
                for command in split(source):
                    if not re.match(r"^(CREATE\s+(TABLE|VIEW)|ALTER\s+TABLE|DROP\s+(TABLE|VIEW)|INSERT|UPDATE|DELETE)\b",
                                    " ".join(token for token, _, _ in tokens(command)), re.I):
                        raise ValueError("Nem támogatott Oracle előkészítő utasítás.")
                    cur.execute(command)
            before = snapshot(cur, config.max_rows) if task.kind != "select" else None
            stage = "answer"
            cur.execute(answer)
            if task.kind == "select":
                return "OK", ([col.name for col in cur.description], values(cur, config.max_rows)), None
            return "OK", (before, snapshot(cur, config.max_rows)), None
    except OverflowError:
        return ("RESULT_LIMIT" if stage == "answer" else "SYSTEM_ERROR"), None, None
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if stage == "answer" and (code == 1013 or getattr(exc.args[0], "full_code", "") in {"DPY-4024", "DPI-1067"}):
            return "SQL_TIMEOUT", None, code
        if stage == "answer" and code in {900, 905, 906, 907, 917, 921, 923, 933, 936}:
            return "SYNTAX_ERROR", None, code
        if stage == "answer" and (900 <= code <= 999 or 1400 <= code <= 1499 or 1700 <= code <= 1799 or code in {1, 942, 955, 2290, 2291, 2292}):
            return "SQL_ERROR", None, code
        return "SYSTEM_ERROR", None, code
    finally:
        if created:
            cleanup(config, [token])
