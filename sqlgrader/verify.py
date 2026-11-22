"""Read-only comparison of two grading runs."""
import argparse
import json
import re
from pathlib import Path


def read_run(directory):
    reports = {}
    for path in directory.glob("*.json"):
        row = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(row, dict) or not {"neptun", "points", "maximum", "tasks"} <= row.keys():
            continue
        code = row["neptun"]
        if code in reports:
            raise ValueError(f"Ismétlődő azonosító: {code}")
        task_map = {}
        for item in row["tasks"]:
            key = item["id"]
            if key in task_map:
                raise ValueError(f"Ismétlődő feladat: {code}/{key}")
            task_map[key] = (item["points"], item["maximum"], item["status"])
        reports[code] = (row["points"], row["maximum"], task_map)
    if not reports:
        raise ValueError(f"Nincsenek pontlapok: {directory}")
    return reports


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--kodterkep", type=Path, help="A próba beadasok.json kódmegfeleltetése")
    args = parser.parse_args(argv)
    try:
        a, b = read_run(args.old), read_run(args.new)
        if args.kodterkep:
            entries = json.loads(args.kodterkep.read_text(encoding="utf-8"))
            if not isinstance(entries, list) or any(
                not isinstance(item, dict)
                or not isinstance(item.get("regi_neptun"), str)
                or not isinstance(item.get("neptun"), str)
                for item in entries
            ):
                raise ValueError("Hibás kódtérkép.")
            mapping = {item["regi_neptun"]: item["neptun"] for item in entries}
            if (len(mapping) != len(entries) or len(set(mapping.values())) != len(mapping)
                    or set(mapping) != set(a)
                    or any(not re.fullmatch(r"[A-Z0-9]{5}", old)
                           or not re.fullmatch(r"[A-Z0-9]{6}", new)
                           or not new.startswith(old) for old, new in mapping.items())):
                raise ValueError("A kódtérkép nem egyezik a régi próbafutással.")
            a = {mapping[code]: report for code, report in a.items()}
    except (ValueError, OSError) as error:
        print(f"Hiba: {error}")
        return 2
    differences, tasks = [], 0
    for code in sorted(a.keys() | b.keys()):
        if code not in a or code not in b:
            differences.append(f"{code}: hiányzó pontlap az egyik futásból.")
            continue
        if a[code][:2] != b[code][:2]:
            differences.append(f"{code}: eltérő összpont: {a[code][:2]} → {b[code][:2]}")
        a_tasks, b_tasks = a[code][2], b[code][2]
        for task in sorted(a_tasks.keys() | b_tasks.keys()):
            tasks += 1
            if a_tasks.get(task) != b_tasks.get(task):
                differences.append(f"{code}/{task}: {a_tasks.get(task)} → {b_tasks.get(task)}")
    if differences:
        print("\n".join(differences))
        return 1
    print(f"Egyezik {len(a)} hallgató összpontja és {tasks} feladat pontja, maximuma és állapota.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
