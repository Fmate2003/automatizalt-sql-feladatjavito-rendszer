"""Write a real Excel workbook from the grader's text summary."""

import argparse
import csv
from pathlib import Path
import re
from tempfile import NamedTemporaryFile

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter


def export_summary(source):
    source = Path(source)
    destination = source.with_suffix(".xlsx")
    with source.open(encoding="utf-8-sig", newline="") as handle:
        first_line = handle.readline()
        handle.seek(0)
        delimiter = ";" if first_line.startswith("Név;Neptun;Összpont") else "\t"
        rows = list(csv.reader(handle, delimiter=delimiter, strict=True))
    if not rows or rows[0][:3] != ["Név", "Neptun", "Összpont"]:
        raise ValueError("A forrás nem a javító tabulátorral vagy pontosvesszővel tagolt összesítője.")
    if any(row and len(row) != len(rows[0]) for row in rows):
        raise ValueError("Az összesítő egyik sorában eltér az oszlopok száma.")

    book = Workbook()
    sheet = book.active
    sheet.title = "Összesítő"
    sheet.freeze_panes = "C2"
    sheet.column_dimensions["A"].width = 31
    sheet.column_dimensions["B"].width = 14
    sheet.column_dimensions["C"].width = 14
    for col in range(4, len(rows[0]) + 1):
        sheet.column_dimensions[get_column_letter(col)].width = 10

    for i, row in enumerate(rows, 1):
        average = row[:2] == ["Átlagok", ""]
        for j, value in enumerate(row, 1):
            if value == "":
                continue
            cell = sheet.cell(i, j)
            if i != 1 and j >= 3 and re.fullmatch(r"-?\d+(?:[,.]\d+)?", value):
                cell.value = float(value.replace(",", ".")) if re.search(r"[,.]", value) else int(value)
                if average:
                    cell.number_format = "0.00"
            else:
                cell.value = value
                cell.data_type = "s"
            if i == 1 or average:
                cell.font = Font(bold=True)

    with NamedTemporaryFile(dir=destination.parent, prefix=".osszesito-", suffix=".xlsx", delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        book.save(temp_path)
        temp_path.replace(destination)
    finally:
        book.close()
        temp_path.unlink(missing_ok=True)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="A meglévő osszesito.xls fájl")
    args = parser.parse_args()
    try:
        print(f"Elkészült: {export_summary(args.source)}")
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(2, f"Hiba: {error}\n")
