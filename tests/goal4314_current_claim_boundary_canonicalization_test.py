from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "docs" / "learn" / "current_claim_boundaries.md"
SCAN_ARTIFACT = ROOT / "docs" / "reports" / "goal4248_current_public_docs_claim_boundary_scan.json"
REPORT = ROOT / "docs" / "reports" / "goal4314_current_claim_boundary_canonicalization_2026-06-11.md"


class Goal4314CurrentClaimBoundaryCanonicalizationTest(unittest.TestCase):
    def test_canonical_claim_boundary_page_exists_and_sets_rules(self) -> None:
        text = CANONICAL.read_text(encoding="utf-8")

        for phrase in (
            "Current Claim Boundaries",
            "v2.10 source-tree",
            "Active v2.11 work",
            "does not authorize",
            "Selecting `--backend optix`",
            "Use fused RTDL primitives first",
            "Choose a partner explicitly",
        ):
            self.assertIn(phrase, text)

    def test_public_front_doors_link_to_canonical_boundary(self) -> None:
        expected_links = {
            "README.md": "docs/learn/current_claim_boundaries.md",
            "docs/README.md": "learn/current_claim_boundaries.md",
            "docs/learn/README.md": "current_claim_boundaries.md",
            "docs/capability_boundaries.md": "learn/current_claim_boundaries.md",
            "docs/partner_acceleration_boundaries.md": "learn/current_claim_boundaries.md",
            "tutorials/current/README.md": "../../docs/learn/current_claim_boundaries.md",
            "examples/README.md": "../docs/learn/current_claim_boundaries.md",
        }

        for rel_path, link in expected_links.items():
            with self.subTest(rel_path=rel_path):
                text = (ROOT / rel_path).read_text(encoding="utf-8")
                self.assertIn(link, text)

    def test_public_claim_scan_includes_canonical_page_without_blockers(self) -> None:
        payload = json.loads(SCAN_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["hard_blocker_count"], 0)
        self.assertIn("docs/learn/current_claim_boundaries.md", payload["public_files_scanned"])
        for value in payload["claim_boundary"].values():
            self.assertFalse(value)

    def test_report_records_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4314",
            "canonical learner-facing claim-boundary page",
            "does not authorize",
            "34 public markdown files",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
