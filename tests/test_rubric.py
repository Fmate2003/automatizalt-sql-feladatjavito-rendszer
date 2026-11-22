from fractions import Fraction
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from sqlgrader import ai, rubric


class Rubric(unittest.TestCase):
    def test_duplicate_rows_and_worst_fixture(self):
        task = SimpleNamespace(kind="select", case_insensitive=False, ordered=False,
                               column_names=False, partial=(("a", "matching_rows", 4, (), "adatok"),
                                                            ("b", "exact", 1, (), "teljes")))
        wanted = (["id"], [(1,), (1,), (2,)])
        received = (["id"], [(1,), (2,), (2,)])
        result = rubric.ratio("matching_rows", (), wanted, received, task)
        self.assertEqual(result, Fraction(2, 3))
        rows = rubric.score(task, [("base", {"a": 1, "b": 1}),
                                   ("edge", {"a": result, "b": 0})])
        self.assertEqual([row["points"] for row in rows], [2, 0])

    def test_noop_credit_requires_no_reference_change(self):
        task = SimpleNamespace(kind="update", target="sample", case_insensitive=False)
        meta = ("r", [("id",)], [])
        initial = {"sample": (meta, [(1,)])}
        changed = {"sample": (meta, [(2,)])}
        self.assertTrue(rubric.ratio("other_objects", (), (initial, initial), (initial, initial), task))
        self.assertFalse(rubric.ratio("other_objects", (), (initial, changed), (initial, initial), task))
        self.assertFalse(rubric.ratio("change_count", (), (initial, changed), (initial, initial), task))

    def test_bad_rubric_is_rejected_before_grading(self):
        for invalid in ({"exact": 2}, {"order": 1, "exact": 3},
                        {"wrong": 3, "exact": 1}, {"column_count": 4}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                rubric.parse(invalid, "select", 4, False, False)

    def test_ai_batches_thirty_without_losing_ids(self):
        data = {str(i): {"pont": i} for i in range(30)}
        chunks = list(ai.batches(data))
        self.assertEqual(len(chunks), 10)
        self.assertEqual({key: item for chunk in chunks for key, item in chunk.items()}, data)

    def test_ai_preserves_the_reason_for_empty_or_unsafe_output(self):
        def task(key, state, reason):
            return {"id":key,"description":"feladat","points":0,"maximum":4,
                    "status":state,"reason":reason,"cases":[]}
        tasks = [task("1", "MISSING", "Nem érkezett megoldás."),
                 task("2", "FAIL", "Eltér az eredmény.")]
        with patch.object(ai, "request_notes", return_value={"2": "SELECT id FROM products;"}) as request:
            notes = ai.review(SimpleNamespace(ai_seconds=20), tasks)
        self.assertEqual(set(request.call_args.args[2]), {"2"})
        self.assertEqual(notes["1"]["text"], "Nem érkezett megoldás.")
        self.assertEqual(notes["2"], {"text": "Eltér az eredmény.", "source": "szabály", "javaslat": None})


if __name__ == "__main__":
    unittest.main()
