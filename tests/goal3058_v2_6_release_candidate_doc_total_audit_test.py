from __future__ import annotations

from pathlib import Path
import re
import unittest
import urllib.parse


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md"


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

FORBIDDEN_CURRENT_PATTERNS = (
    re.compile(r"\bv0\."),
    re.compile(r"\bv1\."),
    re.compile(r"\bv2\.0\b"),
    re.compile(r"\bv2\.1\b"),
    re.compile(r"\bv2\.2\b"),
    re.compile(r"\bv2\.4\b"),
    re.compile(r"\bv2\.5\b"),
    re.compile(r"pre-release", re.IGNORECASE),
    re.compile(r"pre release", re.IGNORECASE),
    re.compile(r"Triton-first", re.IGNORECASE),
    re.compile(r"true-zero", re.IGNORECASE),
    re.compile(r"true zero", re.IGNORECASE),
    re.compile(r"current released", re.IGNORECASE),
    re.compile(r"partner_optix_zero_copy_anyhit", re.IGNORECASE),
)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _current_docs() -> list[Path]:
    files = [ROOT / "README.md"]
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend((ROOT / "examples").rglob("*.md"))
    out: list[Path] = []
    for path in files:
        rel = _rel(path)
        if not any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            out.append(path)
    return sorted(out)


def _current_plus_research_archive_docs() -> list[Path]:
    files = [ROOT / "README.md"]
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend((ROOT / "examples").rglob("*.md"))
    out: list[Path] = []
    excluded = tuple(prefix for prefix in EXCLUDED_PREFIXES if prefix != "docs/research/archive/")
    for path in files:
        rel = _rel(path)
        if not any(rel.startswith(prefix) for prefix in excluded):
            out.append(path)
    return sorted(out)


class Goal3058V26ReleaseCandidateDocTotalAuditTest(unittest.TestCase):
    def test_report_covers_every_current_file_and_archive_move(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal3058", text)
        self.assertIn("Current-Facing File Audit", text)
        self.assertIn("Historical / Archived File Audit", text)
        self.assertIn("Current-facing Markdown files audited | 86", text)
        self.assertIn("Research files moved to archive lane | 16", text)
        self.assertIn("Local current-plus-research-archive Markdown link check | 103 checked / 0 broken", text)
        self.assertIn("Tutorial/example execution | local portable smoke passed; pod/full native Embree+OptiX validation still pending", text)
        self.assertIn("ALL_PORTABLE_SMOKE_OK", text)
        self.assertIn("Release authorization | blocked until final 3-AI consensus", text)

        moved_examples = [
            "docs/research/archive/app_notes/README.md",
            "docs/research/archive/future_version_to_do_list.md",
            "docs/research/archive/proposals/v0_9_hiprt_backend_full_support_plan_2026-04-18.md",
            "docs/research/archive/rayjoin_legacy/rayjoin_target.md",
        ]
        for rel in moved_examples:
            self.assertIn(f"`{rel}`", text)
            self.assertTrue((ROOT / rel).exists())

    def test_current_docs_do_not_expose_stale_version_or_old_claim_language(self) -> None:
        offenders: list[str] = []
        for path in _current_docs():
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = _rel(path)
            for pattern in FORBIDDEN_CURRENT_PATTERNS:
                for match in pattern.finditer(text):
                    line_number = text[: match.start()].count("\n") + 1
                    offenders.append(f"{rel}:{line_number}:{match.group(0)}")

            for match in re.finditer(r"\bv2\.3\b", text):
                line = text[: match.start()].count("\n") + 1
                line_text = text.splitlines()[line - 1].lower()
                allowed = (
                    "previous" in line_text
                    or "archive" in line_text
                    or "evidence" in line_text
                    or "release_reports/v2_3" in line_text
                )
                if not allowed:
                    offenders.append(f"{rel}:{line}:v2.3 outside archive context")

        self.assertEqual([], offenders)

    def test_current_docs_have_no_broken_local_markdown_links(self) -> None:
        link_re = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
        broken: list[str] = []

        checked = _current_plus_research_archive_docs()
        for path in checked:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in link_re.finditer(text):
                raw = match.group(1).strip()
                if not raw or raw.startswith(("#", "http://", "https://", "mailto:", "computer://", "file://")):
                    continue
                target = raw.split("#", 1)[0].strip()
                if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                target_path = (path.parent / urllib.parse.unquote(target)).resolve()
                if not target_path.exists():
                    line_number = text[: match.start()].count("\n") + 1
                    broken.append(f"{_rel(path)}:{line_number}:{raw}")

        self.assertGreaterEqual(len(checked), 100)
        self.assertEqual([], broken)

    def test_live_research_door_points_to_archive_not_old_live_dirs(self) -> None:
        research = (ROOT / "docs" / "research" / "README.md").read_text(encoding="utf-8")
        rayjoin = (ROOT / "docs" / "research" / "rayjoin" / "README.md").read_text(encoding="utf-8")

        self.assertIn("Archived Research Notes", research)
        self.assertNotIn("app_notes/README.md", research)
        self.assertNotIn("proposals/", research)
        self.assertNotIn("future/README.md", research)

        self.assertIn("../archive/rayjoin_legacy/", rayjoin)
        self.assertNotIn("embree_baseline_plan.md](embree_baseline_plan.md)", rayjoin)
        self.assertNotIn("rayjoin_target.md](rayjoin_target.md)", rayjoin)


if __name__ == "__main__":
    unittest.main()
