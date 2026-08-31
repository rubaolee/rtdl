from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "goal3013_hausdorff_numba_device_score_rows_pod_runner.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.json"


class Goal3013HausdorffNumbaDeviceScoreRowsPodRunnerTest(unittest.TestCase):
    def test_runner_records_clean_claim_bounded_evidence(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for phrase in (
            "partner_numba_witness_exact",
            "source_dirty",
            "nvidia-smi",
            "host_score_row_materialization_used",
            "score_rows_generated_on_partner_device",
            "all_claim_flags_false",
        ):
            self.assertIn(phrase, source)

    def test_report_states_required_artifact_fields(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3013",
            "partner_numba_witness_exact",
            "evidence.matches_oracle: true",
            "evidence.host_score_row_materialization_used: false",
            "evidence.score_rows_generated_on_partner_device: true",
            "evidence.rt_core_accelerated: false",
            "all_claim_flags_false: true",
            "not RT-core evidence",
        ):
            self.assertIn(phrase, text)

    def test_artifact_contract_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3013 pod artifact has not been collected yet")

        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal3013")
        self.assertEqual(data["backend"], "partner_numba_witness_exact")
        self.assertEqual(data["partner"], "numba")
        self.assertEqual(data["source_dirty"], [])
        self.assertTrue(data["warmup"]["matches_oracle"])
        self.assertFalse(data["warmup"]["host_score_row_materialization_used"])
        self.assertTrue(data["warmup"]["score_rows_generated_on_partner_device"])
        evidence = data["evidence"]
        self.assertTrue(evidence["matches_oracle"])
        self.assertFalse(evidence["host_score_row_materialization_used"])
        self.assertTrue(evidence["score_rows_generated_on_partner_device"])
        self.assertFalse(evidence["rt_core_accelerated"])
        self.assertTrue(data["all_claim_flags_false"])


if __name__ == "__main__":
    unittest.main()
