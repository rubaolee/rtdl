from __future__ import annotations

import json
import unittest
from pathlib import Path

from examples.v2_0.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_v2_function as hd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2801_hausdorff_xhd_v25_canonical_entrypoint.py"
REPORT = ROOT / "docs" / "reports" / "goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md"
FUTURE_TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2809_hausdorff_warm_tuned_entrypoint_pod"
    / "hausdorff_xhd_v25_warm_median_4096.json"
)
EXPECTED_COMMIT = "b328b9b3aafc14a862f1287a2948fa47474fe690"


class Goal2809HausdorffWarmTunedEntrypointTest(unittest.TestCase):
    def test_adaptive_default_uses_warm_v2_5_group_floor(self) -> None:
        self.assertEqual(hd.default_adaptive_target_points_per_group(4096), 512)
        self.assertEqual(hd.default_adaptive_target_points_per_group(8192), 512)
        self.assertEqual(hd.default_adaptive_target_points_per_group(131072), 1024)

    def test_script_records_warmup_repeat_and_tuned_adaptive_metadata(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("DEFAULT_RTDL_WARMUP = 1", text)
        self.assertIn("DEFAULT_REPEAT = 3", text)
        self.assertIn("DEFAULT_ADAPTIVE_GROWTH_FACTOR = 8.0", text)
        self.assertIn("DEFAULT_ADAPTIVE_TARGET_POINTS_PER_GROUP = 512", text)
        self.assertIn("elapsed_runs_sec", text)
        self.assertIn("median_elapsed_sec", text)
        self.assertIn("warmup_elapsed_sec", text)

    def test_pod_artifact_is_exact_bounded_and_faster_than_old_cold_artifact(self) -> None:
        artifact = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["source_commit"], EXPECTED_COMMIT)
        self.assertEqual(artifact["source_dirty"], [])
        self.assertIn("NVIDIA RTX A5000", artifact["gpu"])
        self.assertTrue(artifact["matches_exact_baseline"])
        self.assertEqual(float(artifact["distance_error"]), 0.0)
        self.assertTrue(artifact["rtdl"]["uses_rt_cores"])
        self.assertEqual(artifact["scenario"]["repeat"], 3)
        self.assertEqual(artifact["scenario"]["rtdl_warmup"], 1)
        self.assertEqual(artifact["rtdl"]["adaptive_growth_factor"], 8.0)
        self.assertEqual(artifact["rtdl"]["adaptive_target_points_per_group"], 512)
        self.assertLess(float(artifact["rtdl_over_cupy_grid_elapsed_ratio"]), 25.0)

    def test_claim_flags_remain_false(self) -> None:
        artifact = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        for key, value in artifact["claim_boundary"].items():
            if "claim_authorized" in key or "speedup_claim_authorized" in key or "reproduction_claim_authorized" in key:
                with self.subTest(key=key):
                    self.assertFalse(value)
        self.assertFalse(artifact["claim_boundary"]["native_engine_customization"])

    def test_report_and_future_todo_record_remaining_design_gap(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        future = FUTURE_TODO.read_text(encoding="utf-8")

        self.assertIn("17.558764x slower", report)
        self.assertIn("does not claim RTDL beats CuPy", report)
        self.assertIn("device-resident nearest-witness/max-distance continuation", report)
        self.assertIn("Exact Hausdorff Device-Resident Nearest-Witness Continuation", future)
        self.assertIn("Do not reintroduce Hausdorff-specific native ABI names", future)


if __name__ == "__main__":
    unittest.main()
