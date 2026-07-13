from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
SCRIPT = APP_DIR / "run_same_input_range_intersects_gate.py"


def _load_runner():
    sys.path.insert(0, str(APP_DIR))
    spec = importlib.util.spec_from_file_location("librts_goal5456_gate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Goal5456 gate")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5456LibRTSSameInputRangeIntersectsGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = _load_runner()
        cls.app = sys.modules["librts_reproduction"]
        cls.fixture_dir = APP_DIR / "data" / "fixtures"

    def test_cpu_count_and_rows_match_discriminating_fixture(self):
        payload = self.app.run_range_intersects(backend="cpu")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["rtdl"]["result_count"], 8)
        self.assertEqual(payload["fixture"]["range_contains_count"], 5)
        self.assertTrue(payload["fixture"]["predicate_discriminating"])
        self.assertEqual(len(payload["rtdl"]["candidate_id_rows"]), 8)
        self.assertTrue(payload["rtdl"]["complete_candidate_coverage"])

    def test_gate_requires_author_count_and_rtdl_native_rows(self):
        rows = [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1], [3, 2], [4, 3]]
        rtdl_payload = {
            "matched": True,
            "fixture": {"predicate_discriminating": True},
            "rtdl": {
                "backend": "optix",
                "result_count": 8,
                "candidate_id_rows": rows,
                "complete_candidate_coverage": True,
                "rt_core_accelerated": True,
            },
            "expected": {"valid_count": 8, "range_contains_count": 5},
        }
        with mock.patch.object(self.runner, "run_range_intersects", return_value=rtdl_payload):
            summary = self.runner.build_gate_summary(
                boxes_path=self.fixture_dir / "tiny_boxes.wkt",
                queries_path=self.fixture_dir / "tiny_range_queries.wkt",
                expected_path=self.fixture_dir / "tiny_range_intersects_expected.json",
                author_stdout="RT, load 2 ms, query 0.1 ms, results: 8\n",
                author_command=["rtspatial_exec"],
            )
        self.assertTrue(summary["matched"])
        self.assertTrue(summary["claim_boundary"]["rtdl_native_pair_rows_matched"])
        self.assertFalse(summary["claim_boundary"]["author_pair_relation_agreement_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_claimed"])
        self.assertFalse(summary["claim_boundary"]["embree_evidence_used"])

    def test_contains_count_cannot_substitute_for_intersection_count(self):
        rtdl_payload = {
            "matched": True,
            "fixture": {"predicate_discriminating": True},
            "rtdl": {
                "result_count": 8,
                "candidate_id_rows": [[0, 0]] * 8,
                "complete_candidate_coverage": True,
                "rt_core_accelerated": True,
            },
            "expected": {"valid_count": 8, "range_contains_count": 5},
        }
        with mock.patch.object(self.runner, "run_range_intersects", return_value=rtdl_payload):
            summary = self.runner.build_gate_summary(
                boxes_path=self.fixture_dir / "tiny_boxes.wkt",
                queries_path=self.fixture_dir / "tiny_range_queries.wkt",
                expected_path=self.fixture_dir / "tiny_range_intersects_expected.json",
                author_stdout="RT, load 2 ms, query 0.1 ms, results: 5\n",
                author_command=["rtspatial_exec"],
            )
        self.assertFalse(summary["matched"])


if __name__ == "__main__":
    unittest.main()
