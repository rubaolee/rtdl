from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4034_partition_device_pair_preview_timing_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4034_partition_device_pair_preview_timing_2026-06-08.md"
SCRIPT = ROOT / "scripts" / "goal4034_partition_device_pair_preview_timing.py"


class Goal4034PartitionDevicePairPreviewTimingTest(unittest.TestCase):
    def test_pod_artifact_records_same_contract_device_pair_timing(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4034")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["native_abi_added"])
        self.assertEqual(len(payload["rows"]), 4)
        for row in payload["rows"]:
            self.assertEqual(row["same_contract_status"], "accept")
            self.assertGreater(row["pair_count"], 0)
            self.assertEqual(row["device_mode_metadata"]["pair_enumeration"], "device_bounded_offsets")
            self.assertTrue(row["device_mode_metadata"]["complete_candidate_coverage"])
            self.assertGreater(row["device_median_vs_host_median_speedup"], 100.0)
            self.assertLess(
                row["device_bounded_offsets"]["median_sec"],
                row["host_pair_enumeration"]["median_sec"],
            )

    def test_report_and_script_keep_preview_boundary_visible(self) -> None:
        text = REPORT.read_text(encoding="utf-8") + "\n" + SCRIPT.read_text(encoding="utf-8")
        for fragment in (
            "device_bounded_offsets",
            "not time the full grouped-stream application route",
            "does not promote",
            "public_speedup_claim_authorized",
            "partition_convergence_hybrid_promoted",
            "host_preview_warmup_not_counted",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()

