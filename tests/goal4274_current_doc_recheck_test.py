"""Goal4274: current public docs remain link-clean and version-clean."""

from __future__ import annotations

from pathlib import Path
import re
import unittest
import urllib.parse


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4274_current_doc_recheck_2026-06-10.md"

EXCLUDED_PREFIXES = (
    "docs/history/",
    "docs/reports/",
    "docs/reviews/",
    "docs/handoff/",
    "docs/audit/",
    "docs/release_reports/",
    "docs/directives/",
    "docs/engineering/",
    "docs/research/archive/",
    "examples/generated/",
    "examples/internal/",
    "examples/legacy_or_backend_proofs/",
    "examples/reference/",
)

BLOCKED_CURRENT_TOKENS = (
    "examples/v2_0",
    "examples\\v2_0",
    "examples.v2_0",
    "PyTorch",
    "Triton-first",
    "true-zero",
    "true zero",
    "current released",
    "pre-release",
    "pre release",
)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _current_public_docs() -> list[Path]:
    files = [ROOT / "README.md"]
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend((ROOT / "examples").rglob("*.md"))
    docs: list[Path] = []
    for path in files:
        rel = _rel(path)
        if not any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            docs.append(path)
    return sorted(docs)


class Goal4274CurrentDocRecheckTest(unittest.TestCase):
    def test_report_records_current_scope_and_validation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        current_count = len(_current_public_docs())

        self.assertIn("Goal4274 Current Documentation Recheck", text)
        self.assertIn(f"Current public Markdown files scanned | {current_count}", text)
        self.assertIn("Broken local Markdown links | 0", text)
        self.assertIn("Stale current-surface wording hits | 0", text)
        self.assertIn("Generated primitive catalog drift | 0", text)
        self.assertIn("All three validation bundles passed", text)

    def test_current_public_docs_have_no_blocked_current_tokens(self) -> None:
        hits: list[str] = []
        for path in _current_public_docs():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in BLOCKED_CURRENT_TOKENS:
                for match in re.finditer(re.escape(token), text, flags=re.IGNORECASE):
                    line_number = text[: match.start()].count("\n") + 1
                    hits.append(f"{_rel(path)}:{line_number}:{token}")

        self.assertEqual([], hits)

    def test_current_public_docs_have_no_broken_local_markdown_links(self) -> None:
        link_re = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
        broken: list[str] = []

        for path in _current_public_docs():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in link_re.finditer(text):
                raw = match.group(1).strip()
                if not raw or raw.startswith(
                    ("#", "http://", "https://", "mailto:", "computer://", "file://")
                ):
                    continue
                target = raw.split("#", 1)[0].strip()
                if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                target_path = (path.parent / urllib.parse.unquote(target)).resolve()
                if not target_path.exists():
                    line_number = text[: match.start()].count("\n") + 1
                    broken.append(f"{_rel(path)}:{line_number}:{raw}")

        self.assertEqual([], broken)


if __name__ == "__main__":
    unittest.main()
