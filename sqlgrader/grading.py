"""Evaluate each task against the teacher reference on identical or specified fixtures."""
import logging
from . import database, rubric
from .comparison import (compare_select, compare_insert, compare_update, compare_delete,
                         compare_create, compare_drop)

COMPARATORS = {
    "select": compare_select, "insert": compare_insert, "update": compare_update,
    "delete": compare_delete, "create_table": compare_create, "create_view": compare_create,
    "drop_table": compare_drop, "drop_view": compare_drop,
}
REASONS = {
    "SYNTAX_ERROR": "Az adatbázis szintaktikai hibát jelzett.",
    "SQL_ERROR": "A beadott SQL futtatási hibát adott.",
    "SQL_TIMEOUT": "A beadott SQL túllépte a futási időkorlátot.",
    "RESULT_LIMIT": "Az eredmény túllépte a megengedett méretet.",
    "SYSTEM_ERROR": "Technikai hiba miatt ellenőrzés szükséges.",
}
LOG = logging.getLogger(__name__)


def base_result(task):
    return {"id": task.id, "kind": task.kind, "description": task.description,
            "points": None, "maximum": task.points, "status": "SYSTEM_ERROR",
            "source": None, "reason": "Technikai hiba miatt kézi ellenőrzés szükséges.",
            "cases": [], "criteria": []}


def syntax_result(result, task, reason):
    amount = task.syntax_credit
    result.update(points=amount, status="PARTIAL" if amount else "SYNTAX_ERROR", source="S",
                  reason=(reason + f" A javítókulcs ilyen esetben {amount} pontot enged."
                          if amount else reason + " Nincs futtatható eredményből igazolt részpont."))
    result["criteria"] = [{"id": "syntax_credit", "check": "syntax_credit",
                           "label": "A javítókulcs szerinti pont szintaktikai hibás beadásnál",
                           "points": amount, "maximum": task.points,
                           "deducted": task.points - amount, "cases": []}]
    return result


def grade_task(config, task, answer, pregen, cases, tokens):
    result = base_result(task)
    if task.kind not in COMPARATORS:
        result.update(status="MANUAL", reason="Felhasználók és jogosultságok: elkülönített kézi ellenőrzés szükséges.")
        return result
    try:
        solution = database.validate(config, task.solution, task)
    except ValueError:
        result.update(reason="A megoldókulcs érvénytelen; kézi ellenőrzés szükséges.")
        return result
    if task.kind == "select":
        try:
            missing_ref = database.select_requirements(config, task, solution)
        except ValueError as error:
            result.update(reason=str(error))
            return result
        if missing_ref:
            result.update(reason="A tanári megoldás nem teljesíti a megadott SELECT szerkezeti feltételt.")
            return result

    references = []
    for (case, fixture), (teacher_token, _) in zip(cases.items(), tokens):
        status, value, code = database.run(config, task, (pregen, fixture, task.solutionpre), solution, teacher_token)
        if status != "OK":
            LOG.error("Referenciahiba: feladat=%s adatkészlet=%s állapot=%s kód=%s", task.id, case, status, code)
            result.update(reason="Nem futtatható a megoldókulcs vagy az előkészítés; kézi ellenőrzés szükséges.")
            return result
        references.append(value)
    # Validate configured projections against the reference even for an empty answer.
    try:
        for value in references:
            for _, check, _, columns, _ in task.partial:
                if columns:
                    rubric.ratio(check, columns, value, value, task)
    except ValueError:
        result.update(reason="A részpontrubrika oszlopindexe hibás; kézi ellenőrzés szükséges.")
        return result
    if not answer or not answer.strip():
        result.update(points=0, status="MISSING", source="S", reason="Nem érkezett megoldás.")
        return result
    try:
        answer = database.validate(config, answer, task)
    except database.SQLSyntaxError as exc:
        return syntax_result(result, task, str(exc))
    except ValueError as exc:
        result.update(points=0, status="INVALID_SQL", source="S", reason=str(exc))
        return result

    missing_features = (database.select_requirements(config, task, answer)
                        if task.kind == "select" else [])
    measured = []
    for ((case, fixture), (_, student_token)), wanted in zip(zip(cases.items(), tokens), references):
        status, actual, code = database.run(config, task, (pregen, fixture, task.studentpre), answer, student_token)
        scores = {}
        if status == "OK":
            ok, reason = COMPARATORS[task.kind](wanted, actual, task)
            scores = {id_: rubric.ratio(check, columns, wanted, actual, task)
                      for id_, check, _, columns, _ in task.partial}
            status = "PASS" if ok else "WRONG_RESULT"
            if missing_features:
                status = "WRONG_RESULT"
                reason += " " + " ".join(missing_features)
                for id_, check, _, _, _ in task.partial:
                    if check == "exact" or (check == "order" and task.require_order_by
                                            and any("ORDER BY" in msg for msg in missing_features)):
                        scores[id_] = False
        else:
            reason = REASONS[status]
            log = LOG.error if status in {"SYSTEM_ERROR", "SQL_TIMEOUT"} else LOG.info
            log("Futási eltérés: feladat=%s adatkészlet=%s állapot=%s kód=%s", task.id, case, status, code)
        measured.append((case, scores))
        result["cases"].append({"case": case, "status": status, "reason": reason})
    states = {case["status"] for case in result["cases"]}
    if "SYSTEM_ERROR" in states:
        return result
    if states == {"SYNTAX_ERROR"}:
        return syntax_result(result, task, REASONS["SYNTAX_ERROR"])
    if task.partial:
        result["criteria"] = rubric.score(task, measured)
        points = sum(criterion["points"] for criterion in result["criteria"])
    else:
        points = task.points if states == {"PASS"} else 0
    if points == task.points:
        status, reason = "PASS", "Minden előírt ellenőrzés sikeres."
    elif points:
        status, reason = "PARTIAL", "A megoldás részben teljesítette a feladat követelményeit."
    else:
        status, reason = "FAIL", "A megoldás egyetlen pontot érő feltételt sem teljesített."
    result.update(points=points, status=status, source="S", reason=reason)
    return result


def report(name, neptun, results):
    pending = any(row["points"] is None for row in results)
    total = None if pending else sum(row["points"] for row in results)
    return {"name": name, "neptun": neptun, "points": total, "tasks": results,
            "maximum": sum(row["maximum"] for row in results)}
