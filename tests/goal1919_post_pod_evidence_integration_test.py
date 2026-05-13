from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1919_post_pod_evidence_integration_2026-05-13.md"
READINESS = ROOT / "docs" / "reports" / "goal1911_v2_readiness_aggregator.json"
MANIFEST = ROOT / "docs" / "reports" / "goal1916_v2_post_pod_artifact_manifest.json"
ACCEPTANCE = ROOT / "docs" / "reports" / "goal1905_v2_partner_pod_batch_acceptance.json"


class Goal1919PostPodEvidenceIntegrationTest(unittest.TestCase):
    def test_report_records_evidence_and_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: evidence-collected-release-still-blocked", text)
        self.assertIn("NVIDIA RTX 2000 Ada Generation", text)
        self.assertIn("Goal1905 post-pod acceptance: `pass`", text)
        self.assertIn("Goal1916 post-pod artifact manifest: `pass`", text)
        self.assertIn("v2_0_release_authorized: false", text)
        self.assertIn("Claude is quota-blocked", text)
        self.assertIn("Treat it as advisory", text)

    def test_copied_post_pod_gates_pass_but_readiness_stays_blocked(self) -> None:
        acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        readiness = json.loads(READINESS.read_text(encoding="utf-8"))

        self.assertEqual(acceptance["status"], "pass")
        self.assertEqual(manifest["status"], "pass")
        self.assertEqual(readiness["status"], "blocked")
        self.assertTrue(readiness["claim_boundary"]["pod_evidence_collected"])
        self.assertFalse(readiness["claim_boundary"]["v2_0_release_authorized"])
        self.assertIn("fresh Claude or Pro-class review", " ".join(readiness["blockers"]))


if __name__ == "__main__":
    unittest.main()
