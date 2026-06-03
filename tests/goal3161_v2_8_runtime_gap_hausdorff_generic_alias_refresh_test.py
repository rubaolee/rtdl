import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal3161_v2_8_runtime_gap_hausdorff_generic_alias_refresh_2026-06-03.md"
)


class Goal3161V28RuntimeGapHausdorffGenericAliasRefreshTest(unittest.TestCase):
    def test_hausdorff_gap_row_records_generic_alias_and_remaining_rt_stream_gap(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        hausdorff = rows["hausdorff_xhd"]

        self.assertIn("generic directed max-of-nearest-distance", hausdorff["current_best_path"])
        self.assertIn("active-frontier RTDL/OptiX", hausdorff["current_best_path"])
        self.assertIn("Numba is the recommended exact partner continuation", hausdorff["partner_position"])
        self.assertIn("CuPy remains the CUDA-core fairness baseline", hausdorff["partner_position"])
        self.assertIn("front-door naming is now generic", hausdorff["current_bottleneck"])
        self.assertIn("RT-core nearest-witness stream", hausdorff["current_bottleneck"])
        self.assertEqual(hausdorff["generic_runtime_target"], "typed nearest-witness streams plus grouped max-distance continuation")
        self.assertIn("Goal3143", hausdorff["evidence_refs"])
        self.assertIn("Goal3160", hausdorff["evidence_refs"])

    def test_gap_map_still_blocks_release_and_speedup_claims(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()
        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])
        self.assertFalse(validation["rt_core_speedup_claim_authorized"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])

    def test_report_records_status_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3160",
            "directed_max_of_nearest_distance_2d_partner_columns",
            "Solved",
            "Still open",
            "typed RT nearest-witness producer streams",
            "`v2_8_release_authorized: False`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
