from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
SCRIPT = APP_DIR / "run_same_input_range_contains_gate.py"


def _load_runner():
    sys.path.insert(0, str(APP_DIR))
    spec = importlib.util.spec_from_file_location("librts_goal5455_gate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Goal5455 gate")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5455LibRTSSameInputRangeContainsGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = _load_runner()
        cls.app = sys.modules["librts_reproduction"]
        cls.fixture_dir = APP_DIR / "data" / "fixtures"

    def test_cpu_reference_is_direction_discriminating(self):
        payload = self.app.run_range_contains(backend="cpu")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["rtdl"]["result_count"], 5)
        self.assertEqual(payload["fixture"]["reverse_direction_count"], 2)
        self.assertTrue(payload["fixture"]["direction_discriminating"])
        self.assertEqual(
            payload["exact_fixture_oracle"]["candidate_id_rows"],
            [[0, 0], [0, 1], [1, 0], [3, 2], [4, 3]],
        )

    def test_gate_requires_direction_and_count_match(self):
        rtdl_payload = {
            "matched": True,
            "fixture": {"direction_discriminating": True},
            "rtdl": {
                "backend": "optix",
                "public_api": "query_aabb_index_2d",
                "contract": "generic_prepared_aabb_index_2d",
                "result_count": 5,
                "pair_rows_exposed": False,
                "rt_core_accelerated": True,
                "native_engine_customization": False,
            },
            "exact_fixture_oracle": {
                "candidate_id_rows": [[0, 0], [0, 1], [1, 0], [3, 2], [4, 3]],
                "valid_count": 5,
            },
            "expected": {"valid_count": 5, "reverse_direction_count": 2},
        }
        with mock.patch.object(self.runner, "run_range_contains", return_value=rtdl_payload):
            summary = self.runner.build_gate_summary(
                boxes_path=self.fixture_dir / "tiny_boxes.wkt",
                queries_path=self.fixture_dir / "tiny_range_queries.wkt",
                expected_path=self.fixture_dir / "tiny_range_contains_expected.json",
                author_stdout="RT, load 2 ms, query 0.1 ms, results: 5\n",
                author_command=["rtspatial_exec"],
            )
        self.assertTrue(summary["matched"])
        self.assertEqual(summary["semantics"]["reverse_direction_count"], 2)
        self.assertFalse(summary["author"]["pair_rows_exposed"])
        self.assertFalse(summary["claim_boundary"]["author_pair_relation_agreement_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_claimed"])
        self.assertFalse(summary["claim_boundary"]["embree_evidence_used"])

    def test_reverse_direction_fixture_cannot_pass(self):
        rtdl_payload = {
            "matched": True,
            "fixture": {"direction_discriminating": False},
            "rtdl": {
                "backend": "optix",
                "public_api": "query_aabb_index_2d",
                "contract": "generic_prepared_aabb_index_2d",
                "result_count": 5,
                "pair_rows_exposed": False,
                "rt_core_accelerated": True,
                "native_engine_customization": False,
            },
            "exact_fixture_oracle": {"candidate_id_rows": [], "valid_count": 5},
            "expected": {"valid_count": 5, "reverse_direction_count": 5},
        }
        with mock.patch.object(self.runner, "run_range_contains", return_value=rtdl_payload):
            summary = self.runner.build_gate_summary(
                boxes_path=self.fixture_dir / "tiny_boxes.wkt",
                queries_path=self.fixture_dir / "tiny_range_queries.wkt",
                expected_path=self.fixture_dir / "tiny_range_contains_expected.json",
                author_stdout="RT, load 2 ms, query 0.1 ms, results: 5\n",
                author_command=["rtspatial_exec"],
            )
        self.assertFalse(summary["matched"])


if __name__ == "__main__":
    unittest.main()
