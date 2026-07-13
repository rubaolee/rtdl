from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
SCRIPT = APP_DIR / "run_same_input_point_contains_gate.py"


def _load_runner():
    sys.path.insert(0, str(APP_DIR))
    spec = importlib.util.spec_from_file_location("librts_goal5454_gate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Goal5454 gate")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5454LibRTSSameInputPointContainsGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = _load_runner()
        cls.fixture_dir = APP_DIR / "data" / "fixtures"

    def test_author_output_parser_fails_closed(self):
        parsed = self.runner.parse_author_summary(
            "Loaded boxes 4\nLoaded point queries 5\n"
            "RT, load 3.358 ms, query 0.087 ms, results: 5\n"
        )
        self.assertEqual(parsed["result_count"], 5)
        with self.assertRaisesRegex(ValueError, "lacks the expected result summary"):
            self.runner.parse_author_summary("results unavailable")

    def test_same_input_summary_requires_author_count_and_rtdl_exact_rows(self):
        rtdl_payload = {
            "matched": True,
            "rtdl": {
                "backend": "optix",
                "public_api": "expanded_aabb_point_membership_rows_2d",
                "contract": "generic_expanded_aabb_point_membership_rows_2d_v1",
                "valid_count": 5,
                "candidate_id_rows": [[0, 0], [1, 0], [1, 1], [2, 1], [3, 2]],
                "rt_core_accelerated": True,
                "native_engine_customization": False,
            },
            "expected": {
                "valid_count": 5,
                "candidate_id_rows": [[0, 0], [1, 0], [1, 1], [2, 1], [3, 2]],
            },
        }
        with mock.patch.object(self.runner, "run_local_point_contains", return_value=rtdl_payload):
            summary = self.runner.build_gate_summary(
                boxes_path=self.fixture_dir / "tiny_boxes.wkt",
                points_path=self.fixture_dir / "tiny_points.wkt",
                expected_path=self.fixture_dir / "tiny_point_contains_expected.json",
                author_stdout="RT, load 3.358 ms, query 0.087 ms, results: 5\n",
                author_command=["rtspatial_exec"],
            )
        self.assertTrue(summary["matched"])
        self.assertTrue(summary["input_identity"]["same_files_passed_to_author_and_rtdl"])
        self.assertFalse(summary["author"]["pair_rows_exposed"])
        self.assertTrue(summary["author"]["commit_matches_pin"])
        self.assertFalse(summary["claim_boundary"]["author_pair_relation_agreement_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_claimed"])
        self.assertFalse(summary["claim_boundary"]["embree_evidence_used"])

    def test_count_mismatch_fails_gate(self):
        rtdl_payload = {
            "matched": True,
            "rtdl": {
                "backend": "optix",
                "public_api": "expanded_aabb_point_membership_rows_2d",
                "contract": "generic_expanded_aabb_point_membership_rows_2d_v1",
                "valid_count": 5,
                "candidate_id_rows": [],
                "rt_core_accelerated": True,
                "native_engine_customization": False,
            },
            "expected": {"valid_count": 5, "candidate_id_rows": []},
        }
        with mock.patch.object(self.runner, "run_local_point_contains", return_value=rtdl_payload):
            summary = self.runner.build_gate_summary(
                boxes_path=self.fixture_dir / "tiny_boxes.wkt",
                points_path=self.fixture_dir / "tiny_points.wkt",
                expected_path=self.fixture_dir / "tiny_point_contains_expected.json",
                author_stdout="RT, load 1 ms, query 1 ms, results: 4\n",
                author_command=["rtspatial_exec"],
            )
        self.assertFalse(summary["matched"])

    def test_manifest_keeps_larger_claims_closed(self):
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["rtdl_program"]["backend_scope"]["embree_in_scope"])
        forbidden = " ".join(manifest["boundaries"]["forbidden_claims"])
        self.assertIn("Embree", forbidden)


if __name__ == "__main__":
    unittest.main()
