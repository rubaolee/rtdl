from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


def _compact(relative_path: str) -> str:
    return " ".join((ROOT / relative_path).read_text(encoding="utf-8").split())


class Goal1422V151CollectKPostLinkGateAlignmentTest(unittest.TestCase):
    def test_release_gate_records_public_doc_link_consensus_without_release(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_release_surface_gate()

        self.assertEqual(
            gate["status"],
            "candidate_docs_publicly_discoverable_pending_explicit_release_action",
        )
        self.assertEqual(
            gate["public_doc_link_consensus"],
            "docs/reports/three_ai_goal1421_v1_5_1_collect_k_public_doc_link_consensus_2026-05-06.md",
        )
        self.assertFalse(gate["stable_promotion_authorized_by_this_gate"])
        self.assertFalse(gate["public_speedup_wording_authorized_by_this_gate"])
        self.assertFalse(gate["zero_copy_wording_authorized_by_this_gate"])
        self.assertFalse(gate["whole_app_speedup_claim_authorized_by_this_gate"])
        self.assertFalse(gate["release_tag_action_authorized_by_this_gate"])
        self.assertTrue(gate["explicit_release_approval_required"])

    def test_candidate_package_docs_match_post_link_state(self) -> None:
        combined = " ".join(
            _compact(path)
            for path in (
                "docs/release_reports/v1_5_1/README.md",
                "docs/release_reports/v1_5_1/collect_k_bounded.md",
                "docs/release_reports/v1_5_1/release_surface_gate.md",
            )
        )

        self.assertIn("Goal1421", combined)
        self.assertIn("public-doc-link review", combined)
        self.assertIn("publicly discoverable", combined)
        self.assertIn("documented experimental public-candidate", combined)
        self.assertIn("no public speedup wording", combined)
        self.assertIn("no zero-copy wording", combined)
        self.assertIn("no whole-app claims", combined)
        self.assertIn("no release tag action", combined)

    def test_candidate_package_docs_do_not_overclaim_after_link(self) -> None:
        combined = " ".join(
            _compact(path)
            for path in (
                "docs/release_reports/v1_5_1/README.md",
                "docs/release_reports/v1_5_1/collect_k_bounded.md",
                "docs/release_reports/v1_5_1/release_surface_gate.md",
            )
        )

        for forbidden in (
            "COLLECT_K_BOUNDED is stable",
            "public speedup is authorized",
            "zero-copy is authorized",
            "whole-app speedup is authorized",
            "release tag action is authorized",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
