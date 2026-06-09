from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4070_rt_dbscan_partition_pair_enumeration_app_timing.py"
REPORT = ROOT / "docs" / "reports" / "goal4070_rt_dbscan_partition_pair_enumeration_app_timing_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4070_rt_dbscan_partition_pair_enumeration_app_timing_pod.json"


class Goal4070RtDbscanPartitionPairEnumerationAppTimingSourceTest(unittest.TestCase):
    def test_script_and_report_define_bounded_app_level_timing_packet(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4070",
            "partition_pair_enumeration=mode_default",
            "partition_pair_enumeration=device_count_then_emit",
            "time_ratio_count_then_emit_over_default_median",
            "pair_capacity_reduction",
            "same_signature",
            "does not promote",
            "release wording",
            "do not use RT cores",
        ):
            self.assertIn(fragment, text)


class Goal4070RtDbscanPartitionPairEnumerationAppTimingPodArtifactTest(unittest.TestCase):
    def test_pod_artifact_records_app_level_timing_without_claim_leakage(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal4070 pod artifact has not been produced yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4070")
        self.assertEqual(payload["schema"], "rtdl.goal4070.rt_dbscan_partition_pair_enumeration_app_timing.v1")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["native_abi_added"])
        self.assertEqual(len(payload["rows"]), 12)
        for row in payload["rows"]:
            self.assertTrue(row["same_signature"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"])
            self.assertFalse(row["true_zero_copy_claim_authorized"])
            self.assertFalse(row["partition_convergence_hybrid_promoted"])
            self.assertEqual(row["count_then_emit_digest"]["effective_pair_enumeration"], "device_count_then_emit")
            self.assertFalse(row["count_then_emit_digest"]["full_dbscan_semantics"])
            self.assertTrue(row["count_then_emit_digest"]["graph_component_contract_only"])


if __name__ == "__main__":
    unittest.main()
