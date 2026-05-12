import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1768_v1_8_release_authorization_readiness_after_docs_audit_2026-05-12.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal1766_claude_review_goal1763_1765_release_docs_audit_2026-05-12.md"
GEMINI = ROOT / "docs" / "reviews" / "goal1767_gemini_review_goal1763_1765_release_docs_audit_2026-05-12.md"


class Goal1768V18ReleaseAuthorizationReadinessAfterDocsAuditTest(unittest.TestCase):
    def test_three_user_requirements_are_marked_satisfied(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1_8_release_authorization_packet_ready_pending_user_go", text)
        self.assertIn("Requirement 1: Public Docs Updated", text)
        self.assertIn("Status: `pass`", text)
        self.assertIn("Requirement 2: Post-v1.5 Rule Audit", text)
        self.assertIn("Status: `pass-with-quarantine`", text)
        self.assertIn("Requirement 3: GitHub Learner Double Check", text)

    def test_docs_surfaces_and_design_message_are_recorded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for rel in (
            "README.md",
            "docs/README.md",
            "docs/quick_tutorial.md",
            "examples/README.md",
            "docs/app_example_quickstart.md",
            "docs/public_documentation_map.md",
            "docs/current_architecture.md",
        ):
            self.assertIn(rel, text)
        self.assertIn("Python writes the application", text)
        self.assertIn("RTDL expresses the RT-shaped kernel", text)
        self.assertIn("Native backends execute generic engine contracts", text)

    def test_post_v1_5_audit_counts_and_quarantine_are_recorded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("80 passing", text)
        self.assertIn("98 missing or invalid", text)
        self.assertIn("351 ambiguous", text)
        self.assertIn("quarantined from release claims", text)
        self.assertIn("distinct-AI review", text)

    def test_external_reviews_exist_and_are_accepted(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertTrue(CLAUDE.exists())
        self.assertTrue(GEMINI.exists())
        self.assertIn("goal1766_claude_review_goal1763_1765_release_docs_audit_2026-05-12.md", text)
        self.assertIn("Verdict: `accept`", text)
        self.assertIn("goal1767_gemini_review_goal1763_1765_release_docs_audit_2026-05-12.md", text)
        self.assertIn("Verdict: `accept-with-boundary`", text)

    def test_release_actions_and_overclaims_remain_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "`VERSION` bump",
            "tag",
            "push",
            "package upload",
            "public release",
            "package-install claim",
            "public speedup wording",
            "Python+partner+RTDL claim",
            "PyTorch/CuPy integration claim",
            "true zero-copy claim",
        ):
            self.assertIn(phrase, text)

    def test_no_pod_needed_for_this_phase_and_protected_files_are_named(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("No pod is needed for this docs/audit/learner phase", text)
        self.assertIn("docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz", text)
        self.assertIn("id_ed25519_rtdl_codex", text)
        self.assertIn("rtdl_v0_4.tar.gz", text)
        self.assertIn("scratch/", text)


if __name__ == "__main__":
    unittest.main()
