from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5411_bounded_statused_deferral_sample_row_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5411_bounded_statused_deferral_sample_row_gate_pod.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5411_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load Goal5411 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5411BoundedStatusedDeferralSampleRowGateTest(unittest.TestCase):
    def test_sample_pair_membership_detects_missing_and_present_rows(self) -> None:
        module = _load_module()
        rows = module.sample_pair_membership(
            source_ids=np.asarray([10, 10, 11], dtype=np.int64),
            cell_ids=np.asarray([5, 7, 9], dtype=np.int64),
            sample_source_ids=[10, 11, 12],
            sample_cell_ids=[7, 8, 9],
        )
        self.assertTrue(rows[0]["author_cell_present_in_statused_deferral_stream"])
        self.assertFalse(rows[1]["author_cell_present_in_statused_deferral_stream"])
        self.assertFalse(rows[2]["author_cell_present_in_statused_deferral_stream"])

    def test_columns_for_source_subset_preserves_original_ids(self) -> None:
        module = _load_module()
        points = np.arange(30, dtype=np.float64).reshape(10, 3)
        columns = module._columns_for_source_subset(points, [2, 7])
        self.assertEqual([2, 7], columns["ids"].tolist())
        self.assertEqual((2, 3), columns["coordinate_matrix"].shape)
        self.assertEqual(points[2].tolist(), columns["coordinate_matrix"][0].tolist())
        self.assertEqual(points[7].tolist(), columns["coordinate_matrix"][1].tolist())

    def test_runner_source_keeps_claim_boundary_closed(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"explicit_lb_support_claimed": False', source)
        self.assertIn('"figure7_reproduction_claimed": False', source)
        self.assertIn('"full_xhd_paper_reproduction_claimed": False', source)
        self.assertIn("author_cell_present_in_statused_deferral_stream", source)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal5411 POD artifact not present")
    def test_pod_artifact_is_bounded_sample_gate_not_lb_support(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "rtdl.paper_reproduction.xhd.goal5411.bounded_statused_deferral_sample_row_gate.v1",
            payload["schema"],
        )
        self.assertTrue(payload["matched"])
        self.assertFalse(payload["decision"]["explicit_lb_support_authorized"])
        self.assertFalse(payload["claim_boundary"]["explicit_lb_support_claimed"])
        self.assertIn("bounded_xhd_author_sample_row_gate_passed", payload["decision"])
        self.assertIn("author_sample_membership", payload)


if __name__ == "__main__":
    unittest.main()
