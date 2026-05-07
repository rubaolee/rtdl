import json
from pathlib import Path
import unittest

from scripts import goal1473_v1_5_3_evidence_summary as summary


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_JSON = ROOT / "docs" / "reports" / "goal1473_v1_5_3_evidence_summary_2026-05-07.json"


class Goal1473V153EvidenceSummaryTest(unittest.TestCase):
    def test_build_summary_accepts_committed_parity_and_sweep_payloads(self) -> None:
        payload = summary.build_summary(
            summary.load_json(summary.PARITY_JSON),
            summary.load_json(summary.SWEEP_JSON),
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_diagnostic_evidence_summary")
        self.assertTrue(payload["parity"]["accepted"])
        self.assertTrue(payload["diagnostic_sweep"]["accepted"])
        self.assertEqual(payload["parity"]["backend_summary"]["embree"], {"fail": 0, "pass": 4, "skipped": 0})
        self.assertEqual(payload["parity"]["backend_summary"]["optix"], {"fail": 0, "pass": 4, "skipped": 0})
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertIn("does not authorize true zero-copy", payload["claim_boundary"])

    def test_summary_ratios_cover_both_backends(self) -> None:
        payload = summary.build_summary(
            summary.load_json(summary.PARITY_JSON),
            summary.load_json(summary.SWEEP_JSON),
        )
        ratio_summary = payload["diagnostic_sweep"]["ratio_summary_by_backend"]

        self.assertEqual(set(ratio_summary), {"embree", "optix"})
        for backend, row in ratio_summary.items():
            with self.subTest(backend=backend):
                self.assertLess(row["min_typed_to_baseline_elapsed_ratio"], 1.0)
                self.assertLess(row["max_typed_to_baseline_elapsed_ratio"], 1.0)
                self.assertTrue(all(delta > 0 for delta in row["materialization_deltas"]))

    def test_generated_summary_artifact_is_self_consistent(self) -> None:
        payload = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(payload["surface"], "typed_host_input_plus_prepared_host_output")
        for relative_path in payload["evidence_paths"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())
        self.assertFalse(payload["release_action_authorized"])


if __name__ == "__main__":
    unittest.main()
