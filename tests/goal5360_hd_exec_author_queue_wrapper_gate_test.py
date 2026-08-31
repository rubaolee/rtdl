import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5360_hd_exec_author_queue_wrapper_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5360_hd_exec_author_queue_wrapper_gate.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5360_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5360HdExecAuthorQueueWrapperGateTest(unittest.TestCase):
    def test_wrapper_gate_matches_author_queue_rows_and_exposes_iteration_semantics(self):
        payload = _load_module().build_artifact()
        self.assertEqual(
            "hd_exec_wrapper_author_like_queue_route_matches_bounded3d_author_trace",
            payload["status"],
        )
        self.assertTrue(payload["comparison"]["matched"])
        self.assertEqual(payload["comparison"]["author_rows"], payload["comparison"]["wrapper_rows"])
        self.assertEqual("cell-mbr-author-queue-diagnostic", payload["wrapper"]["route_label"])
        self.assertEqual(2.0, payload["wrapper"]["hd_result"])
        self.assertIn("author-like radius queue rows", payload["wrapper"]["running_iteration_semantics"])
        self.assertEqual(
            "author_like_queue_trace_available_from_cell_mbr_diagnostic_route",
            payload["wrapper"]["radius_trace_status"],
        )

    def test_explicit_author_tune_radius_still_fails_closed(self):
        payload = _load_module().build_artifact()
        fail_closed = payload["explicit_tune_radius_fail_closed"]
        self.assertEqual(2, fail_closed["exit_code"])
        self.assertEqual("unsupported_author_rt_options_fail_closed", fail_closed["status"])
        self.assertEqual(["tune_radius"], fail_closed["explicit_author_rt_options"])
        self.assertFalse(fail_closed["route_executed"])

    def test_saved_artifact_preserves_claim_boundary(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["comparison"]["matched"])
        self.assertIn("explicit_tune_radius_still_fail_closed", payload["exit_label"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
