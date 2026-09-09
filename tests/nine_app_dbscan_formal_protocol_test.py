from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/nine_app_dbscan_formal_compare.py"


def _load():
    name = "nine_app_dbscan_formal_compare_test_module"
    specification = importlib.util.spec_from_file_location(name, SCRIPT)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load DBSCAN formal protocol")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class NineAppDbscanFormalProtocolTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = _load()

    def test_schedule_has_eight_balanced_fresh_process_pairs(self):
        self.assertEqual(len(self.protocol.ORDERS), 8)
        self.assertEqual(
            sum(order == ("A", "C") for order in self.protocol.ORDERS), 4)
        self.assertEqual(
            sum(order == ("C", "A") for order in self.protocol.ORDERS), 4)

    def test_source_closure_names_only_existing_tracked_inputs(self):
        self.assertEqual(len(set(self.protocol.SOURCE_PATHS)), 9)
        for relative in self.protocol.SOURCE_PATHS:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_evidence_writer_is_create_only_and_hash_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "evidence.json"
            row = self.protocol.write_new(path, {"finite": 1.25})
            self.assertEqual(row, self.protocol.binding(path))
            with self.assertRaises(FileExistsError):
                self.protocol.write_new(path, {"replacement": True})
            with self.assertRaises(ValueError):
                self.protocol.write_new(Path(temporary) / "bad.json", {
                    "not_finite": float("inf"),
                })

    def test_block_bootstrap_is_deterministic_and_bounded(self):
        values = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]
        first = self.protocol.bootstrap_median_interval(values)
        second = self.protocol.bootstrap_median_interval(values)
        self.assertEqual(first, second)
        self.assertLessEqual(min(values), first[0])
        self.assertLessEqual(first[0], first[1])
        self.assertLessEqual(first[1], max(values))

    def test_cli_separates_predecessors_freeze_measure_and_recount(self):
        help_text = self.protocol.parser().format_help()
        for command in (
            "config", "worker", "check", "calibrate", "lifecycle",
            "freeze", "measure", "recount",
        ):
            self.assertIn(command, help_text)
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('getattr(args, "preregistration", None)', source)
        self.assertIn("targets_are_not_sample_filters", source)
        self.assertIn("independent recount rejects retained full output", source)
        self.assertIn("prepared timed calls must use the same two-traversal", source)


if __name__ == "__main__":
    unittest.main()
