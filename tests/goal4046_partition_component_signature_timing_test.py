from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4046_partition_component_signature_timing_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4046_partition_component_signature_timing_2026-06-08.md"
SCRIPT = ROOT / "scripts" / "goal4046_partition_component_signature_timing.py"


class Goal4046PartitionComponentSignatureTimingTest(unittest.TestCase):
    def test_artifact_records_signature_timing_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4046")
        self.assertEqual(payload["schema"], "rtdl.goal4046.partition_component_signature_timing.v1")
        self.assertEqual(payload["source_commit"], "0c2da426")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["native_abi_added"])
        self.assertEqual(len(payload["rows"]), 8)

    def test_signature_path_matches_and_beats_full_label_materialization(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        wins = 0
        for row in payload["rows"]:
            self.assertTrue(row["component_signature_match"])
            self.assertEqual(row["summary_metadata"]["pair_enumeration"], "device_bounded_offsets")
            self.assertEqual(row["signature_metadata"]["label_materialization"], "component_size_signature_only")
            self.assertEqual(row["signature_metadata"]["ambiguous_union_execution"], "cupy_partition_points")
            self.assertGreater(row["signature_metadata"]["component_count"], 0)
            self.assertGreater(row["label_over_signature_min"], 1.0)
            self.assertLess(
                row["signature_repeated_run"]["min_sec"],
                row["label_repeated_run"]["min_sec"],
            )
            wins += 1
        self.assertEqual(wins, 8)

    def test_report_and_script_keep_non_promotion_language(self) -> None:
        text = REPORT.read_text(encoding="utf-8") + "\n" + SCRIPT.read_text(encoding="utf-8")
        for fragment in (
            "signature-only wins on all eight rows",
            "smallest generic output contract",
            "does not promote",
            "partition_convergence_hybrid_promoted",
            "component-size signature",
            "automatic partner selection",
            "native ABI",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
