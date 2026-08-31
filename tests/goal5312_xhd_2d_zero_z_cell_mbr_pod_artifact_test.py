from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5312_2d_zero_z_cell_mbr_pod_smoke.json"
)


class Goal5312Xhd2dZeroZCellMbrPodArtifactTest(unittest.TestCase):
    def test_pod_smoke_uses_explicit_zero_z_lift_and_optix_cell_mbr_route(self) -> None:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        summary = payload["RTDL"]["route"]["cell_mbr_summary"]

        self.assertEqual(payload["HDResult"], 9.0)
        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-fast-scalar")
        self.assertEqual(payload["RTDL"]["route"]["route"], "rtdl_cell_mbr_frontier_optix_3d")
        self.assertEqual(summary["input_n_dims"], 2)
        self.assertEqual(summary["execution_n_dims"], 3)
        self.assertTrue(summary["lift_2d_to_3d_zero_z"])
        self.assertIn("lift_2d_to_3d_zero_z_for_cell_mbr", summary["reference_preprocessing"])
        self.assertEqual(summary["point_count_a"], 2)
        self.assertEqual(summary["point_count_b"], 2)
        self.assertFalse(payload["RTDL"]["claim_boundary"]["full_xhd_paper_reproduction_claim_authorized"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["performance_claim_authorized"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["author_rt_core_algorithm_equivalence_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
