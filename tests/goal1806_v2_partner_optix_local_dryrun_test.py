from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal1806_v2_partner_optix_local_dryrun"


class Goal1806V2PartnerOptixLocalDryRunTest(unittest.TestCase):
    def test_local_dryrun_artifacts_preserve_claim_boundary(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(
            sorted(summary),
            ["example_cupy-cuda_optix", "example_numpy_optix", "example_torch-cuda_optix"],
        )
        for result in summary.values():
            self.assertEqual(result["hit_count"], 1)
            self.assertEqual(result["transfer_mode"], "host_stage")
            self.assertFalse(result["true_zero_copy_authorized"])
            self.assertFalse(result["rt_core_speedup_claim_authorized"])

    def test_local_dryrun_report_marks_non_release_evidence(self) -> None:
        report = (ROOT / "docs" / "reports" / "goal1806_v2_partner_optix_local_dryrun_2026-05-12.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("local-dev-pass", report)
        self.assertIn("NVIDIA GeForce GTX 1070", report)
        self.assertIn("not RTX-class pod evidence", report)
        self.assertIn("does not authorize RT-core speedup", report)
        self.assertIn("v2.0 remains blocked", report)

    def test_focused_unittest_log_passed(self) -> None:
        log = (ARTIFACT_DIR / "focused_unittest.log").read_text(encoding="utf-8")
        self.assertIn("Ran 31 tests", log)
        self.assertIn("OK", log)


if __name__ == "__main__":
    unittest.main()
