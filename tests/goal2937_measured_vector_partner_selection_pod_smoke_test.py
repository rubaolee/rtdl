from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2937_measured_vector_partner_selection_pod_smoke_2026-06-01.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2937_measured_partner_selection_pod"
    / "goal2937_measured_partner_selection.json"
)


class Goal2937MeasuredVectorPartnerSelectionPodSmokeTest(unittest.TestCase):
    def test_pod_artifact_selects_fastest_same_contract_partner(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        metadata = payload["metadata"]
        candidates = {row["partner"]: row for row in metadata["candidate_results"]}

        self.assertEqual("pass", payload["status"])
        self.assertEqual("9f477c02e97a676b4d7a79056039df2877e6e5c8", payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual("cupy", metadata["selected_partner"])
        self.assertEqual("pass", candidates["torch"]["status"])
        self.assertEqual("pass", candidates["triton"]["status"])
        self.assertEqual("pass", candidates["cupy"]["status"])
        self.assertLess(candidates["cupy"]["median_sec"], candidates["torch"]["median_sec"])
        self.assertLess(candidates["torch"]["median_sec"], candidates["triton"]["median_sec"])
        self.assertFalse(metadata["silent_auto_selection_authorized"])

    def test_claim_boundary_and_readiness_index(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_claim_authorized"])
        self.assertFalse(boundary["v2_5_release_authorized"])
        self.assertFalse(boundary["native_engine_customization"])
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2937_measured_vector_partner_selection_pod_smoke_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2937_measured_vector_partner_selection_pod_smoke_green", packet["allowed_next_actions"])
        self.assertEqual("accept", rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)["status"])

    def test_report_documents_no_automatic_partner_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2937",
            "selected partner: `cupy`",
            "caller-requested same-contract measurement",
            "not a v2.5 release authorization",
            "automatic partner selection claim",
            "does not make CuPy, Torch, or Triton globally preferred",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
