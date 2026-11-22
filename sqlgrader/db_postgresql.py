import os
import psycopg2
from psycopg2 import sql
from .database import fetch
from .sqlguard import validate_sql, select_requirements

IDENT = sql.Identifier


def validate_config(config):
    if config.database != "sql_grader_demo" or config.user != "sql_runner":
        raise ValueError("PostgreSQL esetén az elkülönített sql_grader_demo / sql_runner környezet szükséges.")


def connect(config):
    validate_config(config)
    return psycopg2.connect(host=config.host, port=config.port, dbname=config.database,
                           user=config.user, password=os.getenv("SQLGRADER_DB_PASSWORD", os.getenv("SQLGRADER_PASSWORD", "local_runner_demo_only")),
                           connect_timeout=config.connect_seconds, application_name="sqlgrader",
                           options=f"-c statement_timeout={config.statement_ms} -c lock_timeout={config.lock_ms}")


def check(config):
    with connect(config) as conn, conn.cursor() as cur:
        cur.execute("SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname=current_user")
        if any(cur.fetchone()):
            raise ValueError("A futtató szerepkör túl nagy jogosultságú.")
        cur.execute("SET LOCAL ROLE sql_student")
        cur.execute("SELECT current_database(), current_user, version()")
        return cur.fetchone()


def validate(statement, task):
    validate_sql(statement, task.kind, task.target.lower() if task.target else None)
    return statement


def snapshot(cur, schema, limit):
    cur.execute("""SELECT c.oid, c.relname, c.relkind
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname=%s AND c.relkind IN ('r','p','v') ORDER BY c.relname""", (schema,))
    result = {}
    for oid, name, kind in fetch(cur, limit):
        cur.execute("""SELECT a.attname, format_type(a.atttypid,a.atttypmod), a.attnotnull,
                        pg_get_expr(d.adbin,d.adrelid), a.attidentity, a.attgenerated
                       FROM pg_attribute a LEFT JOIN pg_attrdef d
                         ON d.adrelid=a.attrelid AND d.adnum=a.attnum
                      WHERE a.attrelid=%s AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum""", (oid,))
        columns = [
            (column, typ, notnull, expr.replace(schema + ".", "") if expr else expr, identity, generated)
            for column, typ, notnull, expr, identity, generated in fetch(cur, limit)
        ]
        cur.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid=%s", (oid,))
        constraints = sorted(value.replace(schema + ".", "") for (value,) in fetch(cur, limit))
        cur.execute(sql.SQL("SELECT * FROM {}").format(IDENT(name)))
        result[name] = ((kind, columns, constraints), fetch(cur, limit))
    return result


def run(config, task, scripts, answer, token):
    from pglast import parser
    conn = None
    stage = "setup"
    schema = "sg_" + token
    try:
        conn = connect(config)
        with conn.cursor() as cur:
            cur.execute(sql.SQL("CREATE SCHEMA {}").format(IDENT(schema)))
            cur.execute(sql.SQL("SET LOCAL search_path TO {}, pg_catalog").format(IDENT(schema)))
            # Trusted teacher scripts are parsed one statement at a time; transactions
            # and other session-changing statements are forbidden.
            for source in scripts:
                for statement in parser.split(source):
                    validate_setup(statement)
                    cur.execute(statement)
            cur.execute(sql.SQL("GRANT USAGE, CREATE ON SCHEMA {} TO sql_student").format(IDENT(schema)))
            cur.execute("""SELECT c.relname, c.relkind FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                WHERE n.nspname=%s AND c.relkind IN ('r','p','v')""", (schema,))
            for name, kind in fetch(cur, config.max_rows):
                action = sql.SQL("ALTER VIEW {} OWNER TO sql_student") if kind == "v" else sql.SQL("ALTER TABLE {} OWNER TO sql_student")
                cur.execute(action.format(IDENT(name)))
            cur.execute("SET LOCAL ROLE sql_student")
            before = snapshot(cur, schema, config.max_rows) if task.kind != "select" else None
            stage = "answer"
            cur.execute(answer)
            if task.kind == "select":
                return "OK", ([col.name for col in cur.description], fetch(cur, config.max_rows)), None
            return "OK", (before, snapshot(cur, schema, config.max_rows)), None
    except OverflowError:
        return ("RESULT_LIMIT" if stage == "answer" else "SYSTEM_ERROR"), None, None
    except psycopg2.Error as exc:
        code = exc.pgcode or "CONNECTION"
        if stage == "answer" and code == "57014":
            return "SQL_TIMEOUT", None, code
        if stage == "answer" and code == "42601":
            return "SYNTAX_ERROR", None, code
        if stage == "answer" and code[:2] in {"22", "23", "42"}:
            return "SQL_ERROR", None, code
        return "SYSTEM_ERROR", None, code
    finally:
        if conn is not None:
            conn.close()  # No commit; schema and all data are rolled back.


def validate_setup(statement):
    from pglast import parser
    import json
    root = json.loads(parser.parse_sql_json(statement))["stmts"][0]["stmt"]
    if not set(root) <= {"CreateStmt", "ViewStmt", "InsertStmt", "UpdateStmt", "DeleteStmt",
                         "AlterTableStmt", "IndexStmt", "DropStmt", "TruncateStmt", "CreateSeqStmt"}:
        raise ValueError("Az előkészítő SQL-ben nem támogatott utasítás van.")


def cleanup(config, tokens):
    pass  # A lezárt PostgreSQL-kapcsolat visszagörgeti a sémát is.
