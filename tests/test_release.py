from dataclasses import replace
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sqlgrader import ai, feedback, inputs, output
from sqlgrader.config import Config
from sqlgrader.runtime import bounded
from sqlgrader.sqlguard import select_requirements

PROJECT = Path(__file__).resolve().parents[1]


class Release(unittest.TestCase):
    def test_cli_help_with_legacy_and_utf8_output(self):
        help_text = {
            "sqlgrader": "XLS-összesítő",
            "sqlgrader.feedback": "időbélyeges",
            "sqlgrader.verify": "kódmegfeleltetése",
            "sqlgrader.excel_summary": "meglévő",
        }
        for encoding in ("cp1252", "utf-8"):
            for module, expected in help_text.items():
                with self.subTest(module=module, encoding=encoding):
                    result = subprocess.run(
                        [sys.executable, "-m", module, "--help"],
                        cwd=PROJECT,
                        env={**os.environ, "PYTHONIOENCODING": f"{encoding}:strict"},
                        capture_output=True,
                        timeout=20,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn(expected.encode(encoding, errors="backslashreplace"), result.stdout)

    def test_codes_and_inline_answer(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "beadas.sql"
            for code in ("AZ782B", "ABC123"):
                p.write_text(f"--név: Kitalált Név\n--neptun: {code}\n--1aSELECT 1;\n-- teszt\n--2\n",
                             encoding="utf-8")
                _, parsed, answers = inputs.submission(p, {"1a", "2"}, 1000)
                self.assertEqual(parsed, code)
                self.assertEqual(answers, {"1a": "SELECT 1;\n-- teszt", "2": ""})

    def test_rejects_five_char_neptun(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "beadas.sql"
            p.write_text("--név: Próba\n--neptun: ABC12\n--1\nSELECT 1;\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "6 karakteres"):
                inputs.submission(p, {"1"}, 1000)

    def test_explicit_select_syntax_is_opt_in(self):
        task = inputs.key(PROJECT / "minta/postgresql", 20000)[0][0]
        self.assertEqual(select_requirements("SELECT city FROM customers", task), [])
        required = replace(task, require_order_by=True, required_functions=("lower",))
        self.assertEqual(len(select_requirements("SELECT 'ORDER BY LOWER' FROM customers", required)), 2)
        self.assertEqual(select_requirements("SELECT lower(city) FROM customers ORDER BY 1", required), [])
        self.assertEqual(len(select_requirements(
            "SELECT lower(city) FROM (SELECT city FROM customers ORDER BY city) AS c", required)), 1)

    def test_spawn_without_shell(self):
        self.assertEqual(bounded(sum, ([2, 3],), 10), 5)

    def test_unsafe_ai_claim_never_reaches_student_and_resume_is_read_only(self):
        report = {
            "name": "Kitalált Név", "neptun": "AZ782B", "points": 5, "maximum": 5,
            "tasks": [{"id": "2a", "kind": "select", "description": "Kitalált Név AZ782B: Listázd a sorokat.",
                       "points": 5, "maximum": 5, "status": "PASS", "source": "S",
                       "reason": "Minden előírt ellenőrzés sikeres.", "cases": [], "criteria": []}],
        }
        count = 0

        def mock_worker(function, args, seconds):
            nonlocal count
            count += 1
            self.assertEqual(function, ai.review)
            encoded = str(ai.payload(args[1]))
            self.assertNotIn("AZ782B", encoded)
            self.assertNotIn("Kitalált Név", encoded)
            return {"2a": {"text": "Nem megbízható szöveg", "source": "szabály",
                           "javaslat": {"kiemeles": None, "javasolt_pont": 0,
                                        "indoklas": "A modell tévesen állította, hogy elbukott.",
                                        "elter_a_szabalytol": True}}}

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text_path = output.individual(root, report)
            original = text_path.with_suffix(".json").read_bytes()
            for _ in range(2):
                feedback.fill(root, [report], Config(), worker=mock_worker, notify=lambda *a, **k: None)
            self.assertEqual(count, 1)
            self.assertEqual(text_path.with_suffix(".json").read_bytes(), original)
            student = text_path.read_text(encoding="utf-8")
            self.assertEqual(student.count("AI-értékelés – magyarázat"), 1)
            self.assertNotIn("elbukott", student)
            self.assertIn("Összpont: 5/5", student)
            self.assertIn("ELTÉR", (root/"ai-folyamat/AZ782B.txt").read_text(encoding="utf-8"))

    def test_ai_validates_range_and_unknown_anchors(self):
        item = {"tenyek": {"teszt_1": "Megfigyelés"}, "maximum": 5, "megallapitott_pont": 3}
        self.assertIsNone(ai.validate_suggestion(
            {"kiemeles": "teszt_9", "javasolt_pont": 3, "indoklas": "Minta."}, item))
        self.assertIsNone(ai.validate_suggestion(
            {"kiemeles": "teszt_1", "javasolt_pont": 6, "indoklas": "Minta."}, item))
        self.assertFalse(ai.validate_suggestion(
            {"kiemeles": "teszt_1", "javasolt_pont": 3, "indoklas": "Minta."}, item)["elter_a_szabalytol"])


if __name__ == "__main__":
    unittest.main()
