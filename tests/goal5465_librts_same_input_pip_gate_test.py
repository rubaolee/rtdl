from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
RUNNER_PATH = APP_DIR / "run_same_input_pip_gate.py"


def _load_runner():
    sys.path.insert(0, str(APP_DIR))
    spec = importlib.util.spec_from_file_location("librts_goal5465_gate", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5465LibRtsSameInputPipGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = _load_runner()
        cls.fixtures = APP_DIR / "data" / "fixtures"

    def test_author_output_parser_fails_closed(self) -> None:
        parsed = self.runner.parse_author_output(
            "Loading Time 2.479 ms\nQuery Time 0.068 ms\nResults 4\n"
        )
        self.assertEqual(parsed["result_count"], 4)
        self.assertEqual(parsed["loading_ms_diagnostic_only"], 2.479)
        self.assertEqual(parsed["query_ms_diagnostic_only"], 0.068)
        with self.assertRaisesRegex(ValueError, "lacks Results count"):
            self.runner.parse_author_output("Results unavailable")

    def test_summary_requires_author_count_and_polygon_refine(self) -> None:
        rtdl_payload = {
            "matched": True,
            "rt_core_accelerated": True,
            "result_count": 4,
            "expected_rows": [[0, 0], [0, 2], [2, 1], [4, 0]],
            "candidate_id_rows": [[0, 0], [0, 2], [2, 1], [4, 0]],
            "bbox_only_candidate_count": 5,
            "polygon_refine_discriminating": True,
            "native_engine_customization": False,
        }
        with mock.patch.object(self.runner, "run_pip", return_value=rtdl_payload):
            payload = self.runner.build_summary(
                polygons_path=self.fixtures / "tiny_pip_polygons.wkt",
                points_path=self.fixtures / "tiny_pip_points.wkt",
                expected_path=self.fixtures / "tiny_pip_expected.json",
                author_stdout="Results 4\n",
                author_command=["librts_author_pip"],
            )
        self.assertTrue(payload["matched"])
        self.assertTrue(payload["input_identity"]["same_files_passed_to_author_and_rtdl"])
        self.assertFalse(payload["author"]["pair_rows_exposed"])
        self.assertFalse(payload["claim_boundary"]["author_pair_relation_agreement_claimed"])
        self.assertFalse(payload["claim_boundary"]["figure12_performance_claimed"])
        self.assertFalse(payload["claim_boundary"]["ray_multicast_equivalence_claimed"])
        self.assertFalse(payload["claim_boundary"]["embree_evidence_used"])

    def test_bbox_only_or_author_count_mismatch_fails_gate(self) -> None:
        rtdl_payload = {
            "matched": True,
            "rt_core_accelerated": True,
            "result_count": 4,
            "expected_rows": [[0, 0], [0, 2], [2, 1], [4, 0]],
            "bbox_only_candidate_count": 4,
            "polygon_refine_discriminating": False,
        }
        with mock.patch.object(self.runner, "run_pip", return_value=rtdl_payload):
            payload = self.runner.build_summary(
                polygons_path=self.fixtures / "tiny_pip_polygons.wkt",
                points_path=self.fixtures / "tiny_pip_points.wkt",
                expected_path=self.fixtures / "tiny_pip_expected.json",
                author_stdout="Results 5\n",
                author_command=["librts_author_pip"],
            )
        self.assertFalse(payload["matched"])

    def test_provenance_pins_and_core_boundary_are_explicit(self) -> None:
        self.assertEqual(
            self.runner.BENCHMARK_COMMIT,
            "9140ad997519713bb5fdceba639a357afa4609ad",
        )
        source = RUNNER_PATH.read_text(encoding="utf-8")
        self.assertIn("same_files_passed_to_author_and_rtdl", source)
        self.assertIn('"librts_specific_rtdl_primitive_added": False', source)
        self.assertNotIn("embree", source.lower().split("claim_boundary", 1)[0])

    def test_committed_linux_optix_gate_matches(self) -> None:
        import json

        payload = json.loads(
            (APP_DIR / "results" / "librts_goal5465_same_input_pip.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["author"]["result_count"], 4)
        self.assertEqual(payload["rtdl"]["result_count"], 4)
        self.assertEqual(payload["rtdl"]["bbox_only_candidate_count"], 5)
        self.assertTrue(payload["rtdl"]["polygon_refine_discriminating"])
        self.assertTrue(payload["rtdl"]["rt_core_accelerated"])
        self.assertFalse(payload["environment"]["performance_evidence_authorized"])


if __name__ == "__main__":
    unittest.main()
