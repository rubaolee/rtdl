from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4036_partition_component_preview_vs_grouped_stream_timing_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4036_partition_component_preview_vs_grouped_stream_timing_2026-06-08.md"
SCRIPT = ROOT / "scripts" / "goal4036_partition_component_preview_vs_grouped_stream_timing.py"


class Goal4036PartitionComponentPreviewVsGroupedStreamTimingTest(unittest.TestCase):
    def test_artifact_records_route_selection_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4036")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["native_abi_added"])
        self.assertEqual(len(payload["rows"]), 8)
        one_shot_wins = 0
        for row in payload["rows"]:
            self.assertTrue(row["component_signature_match"])
            self.assertEqual(row["preview_metadata"]["partition_union_execution"], "cupy_safe_full")
            self.assertEqual(row["preview_metadata"]["partition_summary_pair_enumeration"], "device_bounded_offsets")
            self.assertFalse(row["preview_metadata"]["summary_same_contract_validation_enabled"])
            self.assertTrue(row["grouped_metadata"]["rt_core_accelerated"])
            if row["grouped_prepare_run_over_preview_one_shot"] > 1.0:
                one_shot_wins += 1
            self.assertLess(
                row["partition_summary_reuse_repeated_run"]["min_sec"],
                row["preview_repeated_run"]["min_sec"],
            )
            self.assertLess(
                row["grouped_prepared_repeated_over_preview_repeated"],
                1.0,
            )
            self.assertLess(
                row["grouped_prepared_repeated_over_reuse_repeated"],
                1.0,
            )
        self.assertGreaterEqual(one_shot_wins, 6)

    def test_report_and_script_state_no_promotion(self) -> None:
        text = REPORT.read_text(encoding="utf-8") + "\n" + SCRIPT.read_text(encoding="utf-8")
        for fragment in (
            "not as a universal replacement",
            "remain a candidate route",
            "partition_summary=",
            "does not promote",
            "partition_convergence_hybrid_promoted",
            "cupy_safe_full",
            "device_bounded_offsets",
            "hidden dispatch",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
