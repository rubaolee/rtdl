from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_PREFIXES = (
    "docs/reports/",
    "docs/reviews/",
    "docs/handoff/",
    "docs/release_reports/",
    "docs/history/",
    "docs/audit/",
    "docs/directives/",
    "docs/engineering/",
    "docs/research/archive/",
)
EXCLUDED_FILES = {
    "docs/research/future_version_to_do_list.md",
}

STALE_PATTERNS = (
    "PyTorch",
    "torch-cuda",
    "Triton",
    "v2.6",
    "v2.7",
    "v2.8",
    "v2.9",
    "examples/" + "v2_0",
    "examples\\" + "v2_0",
    "examples." + "v2_0",
    "stale backend",
    "old Python",
)

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _current_doc_files() -> list[Path]:
    files: list[Path] = [REPO_ROOT / "README.md"]
    for root in (
        REPO_ROOT / "tutorials",
        REPO_ROOT / "docs",
        REPO_ROOT / "examples" / "current",
    ):
        for path in root.rglob("*.md"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in EXCLUDED_FILES or any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
                continue
            files.append(path)
    return sorted(set(files), key=lambda path: path.relative_to(REPO_ROOT).as_posix())


def _github_slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def _heading_slugs(path: Path) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = _github_slug(match.group(2))
        if not base:
            continue
        count = counts.get(base, 0)
        counts[base] = count + 1
        slugs.add(base if count == 0 else f"{base}-{count}")
    return slugs


def _normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    return unquote(target)


class Goal4271V210UserDocCleanupTest(unittest.TestCase):
    def test_current_user_docs_do_not_reintroduce_stale_version_or_partner_guidance(self) -> None:
        offenders: list[str] = []
        for path in _current_doc_files():
            rel = path.relative_to(REPO_ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            for pattern in STALE_PATTERNS:
                if pattern in text:
                    offenders.append(f"{rel}: contains {pattern!r}")
        self.assertEqual([], offenders)

    def test_current_user_doc_links_resolve(self) -> None:
        issues: list[str] = []
        slug_cache: dict[Path, set[str]] = {}
        for path in _current_doc_files():
            rel = path.relative_to(REPO_ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            for raw_target in MARKDOWN_LINK_RE.findall(text):
                target = _normalize_link_target(raw_target)
                if not target or target.startswith(("#", "http://", "https://", "mailto:", "file:")):
                    continue
                if target.startswith("computer://"):
                    continue
                path_part, _, anchor = target.partition("#")
                linked = (path.parent / path_part).resolve() if path_part else path
                try:
                    linked.relative_to(REPO_ROOT.resolve())
                except ValueError:
                    issues.append(f"{rel}: link escapes repo: {raw_target}")
                    continue
                if not linked.exists():
                    issues.append(f"{rel}: missing link target: {raw_target}")
                    continue
                if anchor and linked.is_file() and linked.suffix.lower() == ".md":
                    slugs = slug_cache.setdefault(linked, _heading_slugs(linked))
                    if anchor.lower() not in slugs:
                        issues.append(f"{rel}: missing anchor {anchor!r} in {linked.relative_to(REPO_ROOT).as_posix()}")
        self.assertEqual([], issues)

    def test_key_entrypoints_state_current_v2_10_surface(self) -> None:
        key_files = (
            "README.md",
            "tutorials/README.md",
            "tutorials/current/README.md",
            "docs/README.md",
            "docs/current_architecture.md",
            "docs/partner_acceleration_boundaries.md",
            "docs/learn/partner_choice_for_custom_logic.md",
            "examples/current/README.md",
        )
        missing: list[str] = []
        for rel in key_files:
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            if "v2.10" not in text:
                missing.append(rel)
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
