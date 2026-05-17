import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2289_packed_left_direct_index_segment_pair_2026-05-17.md"


def _artifact(run: int, label: str) -> dict:
    path = ROOT / "docs" / "reports" / f"goal2289_direct_index_packed_ab_run{run}_{label}_2026-05-17.json"
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2289PackedLeftDirectIndexSegmentPairTest(unittest.TestCase):
    def test_native_candidate_row_carries_dense_indices(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("unsigned int left_index, right_index;", core)
        self.assertIn("unsigned int  left_offset;", core)
        self.assertIn("r.left_index = params.left_offset + pidx;", core)
        self.assertIn("r.right_index = bidx;", core)
        self.assertIn("uint32_t left_id, right_id, left_index, right_index", core)

        self.assertIn("uint32_t          left_offset;", workloads)
        self.assertIn("lp.left_offset = static_cast<uint32_t>(left_offset);", workloads)
        self.assertIn("gpu_row.left_index < left_count && gpu_row.right_index < right_count", workloads)
        self.assertIn("segment-pair intersection direct candidate index exceeds uint32_t", workloads)

    def test_artifacts_show_packed_left_candidate_improves_both_repetitions(self) -> None:
        for run in (1, 2):
            baseline = _artifact(run, "baseline")
            candidate = _artifact(run, "candidate")

            self.assertEqual(baseline["raw_row_count"], candidate["raw_row_count"])
            self.assertEqual(baseline["scalar_count"], candidate["scalar_count"])
            self.assertEqual(candidate["raw_row_count"], 8921)
            self.assertEqual(candidate["scalar_count"], 8921)
            self.assertEqual(baseline["goal2289_ab_label"], "baseline_origin_main")
            self.assertEqual(candidate["goal2289_ab_label"], "candidate_direct_index_packed_patch")

            raw_speedup = baseline["raw_median_sec"] / candidate["raw_median_sec"]
            count_speedup = baseline["count_median_sec"] / candidate["count_median_sec"]
            self.assertGreater(raw_speedup, 1.03)
            self.assertGreater(count_speedup, 1.02)

    def test_report_preserves_negative_goal2280_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2280 rejected direct-index", text)
        self.assertIn("packed-left path only", text)
        self.assertIn("does not add RayJoin-specific native logic", text)
        self.assertIn("claim that Goal2280's tuple-input rejection is overturned", text)
        self.assertIn("Codex verdict: `accept-with-boundary`", text)


if __name__ == "__main__":
    unittest.main()
