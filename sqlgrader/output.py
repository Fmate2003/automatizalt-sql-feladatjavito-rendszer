import csv
import json
import re
import statistics
from pathlib import Path

PENDING = "Függőben"


def stem(name, neptun):
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")[:100] or "Hallgato"
    return f"{safe}_{neptun}"


def point_label(points):
    return str(points) if points is not None else PENDING


def write_text(path, text):
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def write_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def individual_header(report):
    return [
        "SQL feladatsor – egyéni értékelés",
        f"Név: {report['name']}",
        f"Neptun: {report['neptun']}",
        f"Összpont: {point_label(report['points'])}/{report['maximum']}", "",
    ]


def individual_task(task):
    return [
        f"{task['id']} – {point_label(task['points'])}/{task['maximum']} {task['source'] or '–'}",
        f"Feladat: {task['description']}",
        task["reason"],
        *(f"  {case['case']}: {case['reason']}" for case in task["cases"]),
        *(f"  {item['label']}: {item['points']}/{item['maximum']} pont, "
          f"levonás {item['deducted']} pont"
          + (" (" + ", ".join(f"{c['case']}: {c['earned']}" for c in item["cases"]) + ")" if item["cases"] else "")
          for item in task.get("criteria", [])), "",
    ]


def individual_footer():
    return ["S: szabályalapú SQL-értékelés. Az AI külön tanári javaslat; nem módosít pontot."]


def individual(directory, report):
    root = directory / stem(report["name"], report["neptun"])
    txt, machine = Path(str(root) + ".txt"), Path(str(root) + ".json")
    lines = individual_header(report)
    for task in report["tasks"]:
        lines.extend(individual_task(task))
    lines.extend(individual_footer())
    write_text(txt, "\n".join(lines) + "\n")
    write_json(machine, report)
    return txt


def excel_text(value):
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def summary_header(writer, ids):
    writer.writerow(["Név", "Neptun", "Összpont", *ids])


def summary_row(writer, report):
    fields = [point_label(report["points"]), *(point_label(row["points"]) for row in report["tasks"])]
    writer.writerow([excel_text(report["name"]), report["neptun"], *fields])


def summary_footer(writer, reports, tasks):
    def avg(values):
        known = [x for x in values if x is not None]
        return f"{statistics.mean(known):.2f}".replace(".", ",") if known else ""
    writer.writerow([])
    writer.writerow(["Átlagok", "", avg(r["points"] for r in reports),
                     *(avg(r["tasks"][index]["points"] for r in reports) for index in range(len(tasks)))])


def write_summary(path, reports, tasks, *, delimiter):
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=delimiter)
        summary_header(writer, [task.id for task in tasks])
        for row in reports:
            summary_row(writer, row)
        summary_footer(writer, reports, tasks)


def summary(directory, reports, tasks, *, spec_output=False):
    path = directory / "osszesito.xls"
    write_summary(path, reports, tasks, delimiter="\t" if spec_output else ";")
    if not spec_output:
        from .excel_summary import export_summary
        export_summary(path)
    return path


def write_feedback(directory, report, notes):
    from .ai import factual_note
    path = directory / (stem(report["name"], report["neptun"]) + ".txt")
    old = path.read_text(encoding="utf-8")
    header = "\nAI-értékelés – magyarázat a megállapított pontokhoz\n"
    main = old.partition(header)[0].rstrip()
    lines = ["A magyarázat a javító által igazolt eredményekből készült.", ""]
    for row in report["tasks"]:
        record = notes.get(row["id"])
        suggestion = (record or {}).get("javaslat") or {}
        text = factual_note(row, suggestion.get("kiemeles"))
        lines.append(f"{row['id']}. feladat [szabály]: {text}")
    write_text(path, main + "\n\n" + header + "\n".join(lines) + "\n")


def write_teacher_feedback(path, report, notes):
    lines = ["Tanári ellenőrzésre – az AI nem módosította a pontokat.", ""]
    for row in report["tasks"]:
        suggestion = notes.get(row["id"], {}).get("javaslat")
        if suggestion is None:
            lines.append(f"{row['id']}. feladat: nincs AI-javaslat.")
            continue
        mark = " (ELTÉR)" if suggestion["elter_a_szabalytol"] else ""
        lines.append(f"{row['id']}. feladat: szabály {row['points']}/{row['maximum']}; "
                     f"AI-javaslat {suggestion['javasolt_pont']}/{row['maximum']}{mark}")
        lines.append(f"  Ellenőrizendő: {suggestion['indoklas']}")
    write_text(path, "\n".join(lines) + "\n")
