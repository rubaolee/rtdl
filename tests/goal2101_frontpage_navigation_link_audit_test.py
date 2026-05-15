from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]


LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)")
OLD_MARKER_RE = re.compile(
    r"\bv[01]\.|"
    r"\bv1_[0-9]|"
    r"\bv0_[0-9]|"
    r"legacy|"
    r"historical|"
    r"Goal\d+",
    re.IGNORECASE,
)


def tracked_markdown() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "*.md"],
        cwd=ROOT,
        text=True,
    )
    return [ROOT / line for line in output.splitlines() if line.strip()]


def is_public_navigation_file(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in {"README.md", "examples/README.md"}:
        return True
    if not rel.startswith("docs/"):
        return False
    excluded_prefixes = (
        "docs/audit/",
        "docs/engineering/",
        "docs/handoff/",
        "docs/history/",
        "docs/release_reports/",
        "docs/reports/",
        "docs/research/",
        "docs/reviews/",
    )
    return not rel.startswith(excluded_prefixes)


def local_link_target(source: Path, raw: str) -> Path | None:
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        return None
    parsed = urlparse(raw)
    if parsed.scheme in {"http", "https", "mailto", "computer", "file", "app"}:
        return None
    if re.match(r"^[A-Za-z]:[\\/]", raw):
        return None
    target = raw.split("#", 1)[0].split("?", 1)[0].strip()
    if not target:
        return None
    try:
        target = unquote(target)
    except ValueError:
        pass
    base = ROOT if target.startswith("/") else source.parent
    return (base / target).resolve()


class FrontpageNavigationLinkAuditTest(unittest.TestCase):
    def test_public_navigation_local_links_resolve(self) -> None:
        broken: list[str] = []
        checked = 0
        for path in tracked_markdown():
            if not is_public_navigation_file(path):
                continue
            text = path.read_text(encoding="utf-8")
            for match in LINK_RE.finditer(text):
                target = local_link_target(path, match.group(1))
                if target is None:
                    continue
                checked += 1
                if not target.exists():
                    rel_source = path.relative_to(ROOT).as_posix()
                    rel_target = target.relative_to(ROOT).as_posix() if target.is_relative_to(ROOT) else str(target)
                    broken.append(f"{rel_source} -> {match.group(1)} ({rel_target})")
        self.assertGreater(checked, 300)
        self.assertEqual([], broken)

    def test_public_navigation_has_no_old_version_markers(self) -> None:
        offenders: list[str] = []
        for path in tracked_markdown():
            if not is_public_navigation_file(path):
                continue
            text = path.read_text(encoding="utf-8")
            if OLD_MARKER_RE.search(text):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual([], offenders)

    def test_old_topic_dirs_are_not_top_level_docs_doors(self) -> None:
        top_dirs = {p.name for p in (ROOT / "docs").iterdir() if p.is_dir()}
        self.assertNotIn("archive", top_dirs)
        self.assertNotIn("directives", top_dirs)
        self.assertNotIn("proposals", top_dirs)
        self.assertNotIn("technical_app_notes", top_dirs)


if __name__ == "__main__":
    unittest.main()

