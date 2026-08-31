from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4041_partition_device_ambiguous_union_timing_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4041_partition_device_ambiguous_union_timing_2026-06-08.md"
SCRIPT = ROOT / "scripts" / "goal4041_partition_device_ambiguous_union_timing.py"


class Goal4041PartitionDeviceAmbiguousUnionTimingTest(unittest.TestCase):
    def test_artifact_records_internal_timing_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4041")
        self.assertEqual(payload["schema"], "rtdl.goal4041.partition_device_ambiguous_union_timing.v1")
        self.assertEqual(payload["source_commit"], "42462c3e")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["native_abi_added"])
        self.assertEqual(len(payload["rows"]), 8)

    def test_device_path_matches_signatures_and_skips_empty_ambiguous_rows(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = payload["rows"]
        zero_ambiguous_rows = 0
        positive_ambiguous_rows = 0
        road_wins = 0
        small_ambiguous_losses = 0

        for row in rows:
            self.assertTrue(row["component_signature_match"])
            self.assertEqual(row["summary_metadata"]["pair_enumeration"], "device_bounded_offsets")
            self.assertEqual(row["summary_metadata"]["pair_capacity_source"], "device_upper_bound")
            self.assertEqual(row["host_metadata"]["ambiguous_union_execution"], "host")
            self.assertFalse(row["host_metadata"]["device_ambiguous_union_used"])
            self.assertEqual(row["device_metadata"]["ambiguous_union_execution"], "cupy_partition_points")
            ambiguous_pairs = row["summary_metadata"]["status_counts"]["ambiguous_partition_pairs"]
            if ambiguous_pairs == 0:
                zero_ambiguous_rows += 1
                self.assertFalse(row["device_metadata"]["device_ambiguous_union_used"])
                self.assertEqual(
                    row["device_metadata"]["ambiguous_union_skipped_reason"],
                    "no_ambiguous_partition_pairs",
                )
            else:
                positive_ambiguous_rows += 1
                self.assertTrue(row["device_metadata"]["device_ambiguous_union_used"])
                self.assertIsNone(row["device_metadata"]["ambiguous_union_skipped_reason"])
            if row["profile"].startswith("road3d_") and row["device_over_host_min"] > 1.0:
                road_wins += 1
            if row["profile"] == "clustered3d_4096" and row["device_over_host_min"] < 1.0:
                small_ambiguous_losses += 1

        self.assertEqual(zero_ambiguous_rows, 2)
        self.assertEqual(positive_ambiguous_rows, 6)
        self.assertGreaterEqual(road_wins, 3)
        self.assertEqual(small_ambiguous_losses, 1)

    def test_report_and_script_keep_non_promotion_language(self) -> None:
        text = REPORT.read_text(encoding="utf-8") + "\n" + SCRIPT.read_text(encoding="utf-8")
        for fragment in (
            "universal speed win",
            "optional resident continuation",
            "not a promoted default route",
            "no_ambiguous_partition_pairs",
            "does not promote",
            "partition_convergence_hybrid_promoted",
            "native_abi_added",
            "automatic partner selection",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
