from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


def compact(relative_path: str) -> str:
    return " ".join((ROOT / relative_path).read_text(encoding="utf-8").split())


class Goal1460V152PostLinkGateAlignmentTest(unittest.TestCase):
    def test_release_gate_records_public_doc_link_consensus_without_release(self) -> None:
        gate = rt.validate_v1_5_2_prepared_host_output_release_surface_gate()

        self.assertEqual(
            gate["status"],
            "candidate_docs_publicly_discoverable_pending_explicit_release_action",
        )
        self.assertEqual(
            gate["public_doc_link_consensus"],
            "docs/reports/three_ai_goal1458_v1_5_2_public_docs_link_consensus_2026-05-07.md",
        )
        self.assertTrue(gate["public_docs_link_accepted"])
        self.assertTrue(gate["publicly_discoverable"])
        self.assertTrue(gate["explicit_release_approval_required"])
        self.assertFalse(gate["prepared_buffer_reuse_claim_authorized_by_this_gate"])
        self.assertFalse(gate["stable_promotion_authorized_by_this_gate"])
        self.assertFalse(gate["public_speedup_wording_authorized_by_this_gate"])
        self.assertFalse(gate["zero_copy_wording_authorized_by_this_gate"])
        self.assertFalse(gate["whole_app_speedup_claim_authorized_by_this_gate"])
        self.assertFalse(gate["release_tag_action_authorized_by_this_gate"])

    def test_candidate_package_docs_match_post_link_state(self) -> None:
        combined = " ".join(
            compact(path)
            for path in (
                "docs/release_reports/v1_5_2/README.md",
                "docs/release_reports/v1_5_2/prepared_host_output_buffers.md",
                "docs/release_reports/v1_5_2/release_surface_gate.md",
            )
        )

        self.assertIn("Goal1458 public-doc-link review", combined)
        self.assertIn("public docs link accepted", combined)
        self.assertIn("publicly discoverable", combined)
        self.assertIn("documented experimental evidence candidate", combined)
        self.assertIn("no public speedup wording", combined)
        self.assertIn("no zero-copy wording", combined)
        self.assertIn("no whole-app claims", combined)
        self.assertIn("no release tag action", combined)

    def test_candidate_package_docs_do_not_overclaim_after_link(self) -> None:
        combined = " ".join(
            compact(path)
            for path in (
                "docs/release_reports/v1_5_2/README.md",
                "docs/release_reports/v1_5_2/prepared_host_output_buffers.md",
                "docs/release_reports/v1_5_2/release_surface_gate.md",
            )
        )

        for forbidden in (
            "v1.5.2 is released",
            "prepared buffer reuse is proven",
            "true zero-copy is authorized",
            "public speedup is authorized",
            "stable primitive promotion is authorized",
            "whole-app speedup is authorized",
            "release tag action is authorized",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
