import csv
import json
from pathlib import Path
import tempfile
import unittest

from sqlgrader import ai, comparison, inputs, oracle_syntax, output
from sqlgrader.config import Config
from sqlgrader.sqlguard import validate_sql

PROJECT = Path(__file__).resolve().parents[1]


class Core(unittest.TestCase):
    def test_teacher_format_and_samples(self):
        folder = PROJECT / "minta/postgresql"
        tasks, pregen, cases, excluded = inputs.key(folder, Config.max_input_bytes)
        self.assertEqual(sum(task.points for task in tasks), 50)
        self.assertEqual(set(cases), {"base", "edge"})
        self.assertIn("CREATE TABLE customers", pregen)
        self.assertEqual(excluded, {"edge.sql", "create_db.sql", "solution.sql"})
        name, code, answers = inputs.submission(folder / "mixed.sql", {t.id for t in tasks}, 20000)
        self.assertEqual(code, "MINTA1")
        self.assertEqual(answers["10"], "")

    def test_letter_headers_preserve_comments(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "candidate.sql"
            p.write_text("--név: Minta\n--neptun: ABC123\n--1a\nSELECT id\n-- rendes megjegyzés\nFROM products;\n--2\n", encoding="utf-8")
            _, _, answers = inputs.submission(p, {"1a", "2"}, 2000)
            self.assertIn("-- rendes megjegyzés", answers["1a"])
            self.assertEqual(answers["2"], "")

    def test_column_count_order_and_case(self):
        task = inputs.key(PROJECT / "minta/postgresql", 20000)[0][1]
        result = comparison.compare_select((["id"], [(1,), (2,)]), (["id"], [(2,), (1,)]), task)
        self.assertFalse(result[0])
        self.assertIn("sorrend", result[1])
        self.assertTrue(comparison.rows_equal([("ABC",)], [("abc",)], ignore_case=True))
        self.assertFalse(comparison.rows_equal([(1,), (1,)], [(1,), (2,)]))

    def test_ddl_is_restricted_to_declared_target(self):
        self.assertTrue(validate_sql("CREATE TABLE demo (id int PRIMARY KEY)", "create_table", "demo"))
        self.assertTrue(validate_sql("CREATE VIEW demo AS SELECT id FROM products", "create_view", "demo"))
        self.assertTrue(validate_sql("DROP TABLE demo", "drop_table", "demo"))
        with self.assertRaises(ValueError):
            validate_sql("DROP TABLE products", "drop_table", "demo")
        with self.assertRaises(ValueError):
            validate_sql("DROP VIEW demo", "drop_table", "demo")

    def test_oracle_sample_framing_without_driver(self):
        folder = PROJECT / "minta/oracle"
        tasks, pregen, cases, _ = inputs.key(folder, Config.max_input_bytes)
        self.assertEqual(len(oracle_syntax.split(pregen)), 21)
        for task in tasks:
            self.assertTrue(oracle_syntax.validate(task.solution, task))
        self.assertEqual(len(oracle_syntax.split("SELECT q'[a;b]' FROM dual; -- x;y\nSELECT 1 FROM dual;")), 2)
        with self.assertRaises(ValueError):
            oracle_syntax.validate("SELECT id FROM products; SELECT 1 FROM dual;", tasks[0])

    def test_summary_blanks_pending_average_and_shapes(self):
        class T:
            id = "1a"
        with tempfile.TemporaryDirectory() as temp:
            reports = [{"name": "=teszt", "neptun": "ABC123", "points": None, "tasks": [{"points": None}]},
                       {"name": "Minta", "neptun": "ABC124", "points": 4, "tasks": [{"points": 4}]}]
            path = output.summary(Path(temp), reports, [T()])
            with path.open(encoding="utf-8-sig", newline="") as source:
                rows = list(csv.reader(source, delimiter=";"))
            self.assertEqual({file.name for file in Path(temp).iterdir()},
                             {"osszesito.xls", "osszesito.xlsx"})
            self.assertEqual(rows[0], ["Név", "Neptun", "Összpont", "1a"])
            self.assertEqual(rows[1][0], "'=teszt")
            self.assertEqual(rows[-1], ["Átlagok", "", "4,00", "4,00"])

    def test_ai_does_not_receive_identity_or_sql(self):
        visible = ai.payload([{"id": "1a", "description": "feladat", "points": 0, "maximum": 4,
                               "status": "MISSING", "reason": "Hiányzik", "cases": [],
                               "neptun": "NEPTUN", "name": "NÉV", "sql": "HALLGATO_SQL"}])
        encoded = json.dumps(visible, ensure_ascii=False)
        for secret in ("NEPTUN", "NÉV", "HALLGATO_SQL"):
            self.assertNotIn(secret, encoded)


if __name__ == "__main__":
    unittest.main()
