import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2733_public_claim_boundary_guard_after_primitive_first_2026-05-30.md"

PUBLIC_DOC_ROOTS = (
    ROOT / "docs",
    ROOT / "docs" / "tutorials",
    ROOT / "docs" / "learn",
    ROOT / "docs" / "rtdl",
    ROOT / "docs" / "features",
)

EXCLUDED_PARTS = {
    "reports",
    "reviews",
    "handoff",
    "history",
    "audit",
    "release_reports",
    "research",
}

FORBIDDEN_DIAGNOSTIC_RATIO_FRAGMENTS = (
    "64.018x",
    "342.722x",
    "65.416x",
    "210.336x",
    "Goal2726 diagnostic",
)


def _public_markdown_files() -> list[Path]:
    files: set[Path] = set()
    for root in PUBLIC_DOC_ROOTS:
        if not root.exists():
            continue
        if root == ROOT / "docs":
            candidates = root.glob("*.md")
        else:
            candidates = root.rglob("*.md")
        for path in candidates:
            relative_parts = set(path.relative_to(ROOT / "docs").parts)
            if relative_parts.isdisjoint(EXCLUDED_PARTS):
                files.add(path)
    return sorted(files)


class Goal2733PublicClaimBoundaryGuardAfterPrimitiveFirstTest(unittest.TestCase):
    def test_goal2726_diagnostic_ratios_do_not_leak_into_public_docs(self) -> None:
        offenders: list[str] = []
        for path in _public_markdown_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for fragment in FORBIDDEN_DIAGNOSTIC_RATIO_FRAGMENTS:
                if fragment in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {fragment}")

        self.assertEqual(offenders, [])

    def test_guard_report_documents_scope_and_exclusions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Public Claim Boundary Guard", text)
        self.assertIn("learner-facing docs", text)
        self.assertIn("docs/reports/", text)
        self.assertIn("does not authorize any public performance claim", text)


if __name__ == "__main__":
    unittest.main()
