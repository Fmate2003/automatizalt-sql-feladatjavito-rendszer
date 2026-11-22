"""Database adapter contract: check(config), run(config, task, scripts, sql, token), cleanup(...)."""
from importlib import import_module
import re


class SQLSyntaxError(ValueError):
    """Confirmed database dialect syntax error."""


def adapter_name(engine):
    if not isinstance(engine, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", engine):
        raise ValueError("Érvénytelen adatbázis-adapternév.")
    return f"{__package__}.db_{engine}"


def adapter(config):
    name = adapter_name(config.engine)
    try:
        return import_module(name)
    except ModuleNotFoundError as error:
        if error.name == name:
            raise ValueError(f"Nincs {config.engine!r} nevű adatbázis-adapter.") from None
        raise ValueError(f"Az adatbázis-adapter szükséges csomagja hiányzik: {error.name}.") from None


def validate_configuration(config):
    validate_config = getattr(adapter(config), "validate_config", None)
    if validate_config is not None:
        validate_config(config)


def needs_timeout_cleanup(config):
    return bool(getattr(adapter(config), "NEEDS_TIMEOUT_CLEANUP", False))


def cleanup_labels(config, tokens):
    labeler = getattr(adapter(config), "cleanup_labels", None)
    return labeler(tokens) if labeler is not None else []


def check(config):
    return adapter(config).check(config)


def run(config, task, scripts, answer, token):
    return adapter(config).run(config, task, scripts, answer, token)


def cleanup(config, tokens):
    return adapter(config).cleanup(config, tokens)


def validate(config, statement, task):
    return adapter(config).validate(statement, task)


def fetch(cur, limit):
    rows = cur.fetchmany(limit + 1)
    if len(rows) > limit:
        raise OverflowError()
    return rows


def select_requirements(config, task, statement):
    if not (getattr(task, "require_order_by", False) or getattr(task, "required_functions", ())):
        return []
    check_requirement = getattr(adapter(config), "select_requirements", None)
    if check_requirement is None:
        raise ValueError("Ez az adapter nem ellenőrzi a SELECT szerkezeti előírását.")
    return check_requirement(statement, task)
