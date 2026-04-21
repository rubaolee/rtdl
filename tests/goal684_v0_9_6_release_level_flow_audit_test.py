from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "docs" / "reports" / "goal684_v0_9_6_release_level_flow_audit_2026-04-21.md"
CONSENSUS = REPO_ROOT / "docs" / "reports" / "goal684_consensus_2026-04-21.md"


class Goal684V096ReleaseLevelFlowAuditTest(unittest.TestCase):
    def test_public_docs_mark_v096_as_release_not_candidate(self) -> None:
        public_paths = (
            "README.md",
            "docs/README.md",
            "docs/current_main_support_matrix.md",
            "docs/release_reports/v0_9_6/README.md",
            "docs/release_reports/v0_9_6/release_statement.md",
            "docs/release_reports/v0_9_6/support_matrix.md",
            "docs/release_reports/v0_9_6/audit_report.md",
            "docs/release_reports/v0_9_6/tag_preparation.md",
        )
        combined = "\n".join((REPO_ROOT / path).read_text(encoding="utf-8") for path in public_paths)

        self.assertIn("current released version: `v0.9.6`", combined)
        self.assertIn("Status: released as `v0.9.6`.", combined)
        self.assertNotIn("Release-Candidate", combined)
        self.assertNotIn("release candidate / hold", combined.lower())
        self.assertNotIn("not tagged", combined.lower())
        self.assertNotIn("current public release remains `v0.9.5`", combined)

    def test_release_flow_audit_records_multi_ai_coverage(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")

        self.assertIn("No release-relevant goal in the `v0.9.6` chain is single-developer-only", text)
        self.assertIn("Codex + Claude + Gemini Flash", text)
        self.assertIn("accepted by 2 AI; no single-developer-only action", text)
        self.assertIn("Goal684", text)
        self.assertIn("accepted by 3 AI", text)

        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("The 3-AI consensus is ACCEPT", consensus)
        self.assertIn("Claude | ACCEPT", consensus)
        self.assertIn("Gemini Flash | ACCEPT", consensus)

    def test_release_non_claims_are_preserved(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")

        for phrase in (
            "broad DB, graph, full-row, or one-shot speedup",
            "AMD GPU validation for HIPRT",
            "RT-core acceleration from GTX 1070 evidence",
            "Apple MPS ray-tracing traversal for DB or graph workloads",
            "native backend acceleration for `reduce_rows`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
