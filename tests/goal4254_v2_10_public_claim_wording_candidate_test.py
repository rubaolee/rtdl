import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4254_v2_10_public_claim_wording_candidate_2026-06-09.md"


class Goal4254V210PublicClaimWordingCandidateTest(unittest.TestCase):
    def test_candidate_allowed_claims_are_scoped(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Candidate Allowed Claims", text)
        self.assertIn("generic, app-agnostic native engine", text)
        self.assertIn("Users choose the backend and partner explicitly", text)
        self.assertIn("ten promoted benchmark front doors pass on an RTX 4000 Ada pod", text)
        self.assertIn("second-level timing for all ten promoted", text)
        self.assertIn("selected RT-heavy contracts", text)
        self.assertIn("measured OptiX", text)
        self.assertIn("RayJoin-style evidence is contract-split", text)
        self.assertNotIn("strong OptiX", text)
        self.assertNotIn("where a benchmark needs custom continuation logic", text)

    def test_candidate_forbidden_claims_are_explicit(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "package-install product",
            "every user program faster",
            "broad RT-core speedup guarantee",
            "whole-application acceleration",
            "RTDL beats RayJoin",
            "authors-code results",
            "general true-zero-copy product guarantee",
            "automatically chooses",
            "AMD/HIPRT performance evidence",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_front_page_paragraph_keeps_boundary_language(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Candidate Front-Page Paragraph", text)
        self.assertIn("used from the source tree", text)
        self.assertIn("see the README for platform-specific", text)
        self.assertIn("setup", text)
        self.assertNotIn("used from the source tree with `PYTHONPATH=src:.`", text)
        self.assertIn("specific workload contracts and reviewed timing artifacts", text)
        self.assertIn("Do not read v2.10 as", text)
        self.assertIn("universal speedup promise", text)
        self.assertIn("paper-reproduction claim", text)
        self.assertIn("AMD/HIPRT performance claim", text)


if __name__ == "__main__":
    unittest.main()
