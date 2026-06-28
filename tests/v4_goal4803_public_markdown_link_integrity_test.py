from __future__ import annotations

from pathlib import Path
import re
import unittest
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MARKDOWN_ROOTS = [
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "tutorials",
    ROOT / "examples",
]

STALE_PUBLIC_SURFACE_PATTERNS = [
    "05_prepare_run_continue.md",
    "06_measure_a_program.md",
    "07_benchmark_apps.md",
    "08_choose_a_partner.md",
    "09_benchmark_harness_protocol.md",
    "parity/control",
    "review debt",
    "file://",
    "C:\\Users",
    "tools/_archive",
    "history/legacy",
]


def public_markdown_files() -> list[Path]:
    files: list[Path] = []
    for root in PUBLIC_MARKDOWN_ROOTS:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(sorted(root.rglob("*.md")))
    return sorted(files)


def split_markdown_link_target(raw: str) -> tuple[str, str | None]:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split(' "')[0].strip()
    if "#" in target:
        path, anchor = target.split("#", 1)
    else:
        path, anchor = target, None
    return unquote(path), anchor


def github_anchor_slug(heading: str) -> str:
    slug = re.sub(r"<[^>]+>", "", heading).strip().lower()
    slug = re.sub(r"[^a-z0-9 _-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug


class V4Goal4803PublicMarkdownLinkIntegrityTest(unittest.TestCase):
    def test_public_markdown_relative_links_resolve(self) -> None:
        missing: list[str] = []
        link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
        image_pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
        for path in public_markdown_files():
            text = path.read_text(encoding="utf-8")
            for match in list(link_pattern.finditer(text)) + list(image_pattern.finditer(text)):
                raw = match.group(1).strip()
                if raw.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target_path, _anchor = split_markdown_link_target(raw)
                if not target_path:
                    continue
                resolved = (path.parent / target_path).resolve()
                if not resolved.exists():
                    line = text[: match.start()].count("\n") + 1
                    missing.append(f"{path.relative_to(ROOT)}:{line} -> {raw}")
        self.assertEqual([], missing)

    def test_public_markdown_anchor_links_resolve(self) -> None:
        broken: list[str] = []
        link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
        for path in public_markdown_files():
            text = path.read_text(encoding="utf-8")
            for match in link_pattern.finditer(text):
                raw = match.group(1).strip()
                if raw.startswith(("http://", "https://", "mailto:")) or "#" not in raw:
                    continue
                target_path, anchor = split_markdown_link_target(raw)
                if not anchor:
                    continue
                target_file = path if not target_path else (path.parent / target_path).resolve()
                if not target_file.is_file():
                    continue
                target_text = target_file.read_text(encoding="utf-8")
                anchors = {
                    github_anchor_slug(m.group(1))
                    for m in re.finditer(r"^#{1,6}\s+(.+)$", target_text, re.MULTILINE)
                }
                if anchor.lower() not in anchors:
                    line = text[: match.start()].count("\n") + 1
                    broken.append(f"{path.relative_to(ROOT)}:{line} -> {raw}")
        self.assertEqual([], broken)

    def test_public_markdown_has_no_stale_internal_navigation_terms(self) -> None:
        hits: list[str] = []
        for path in public_markdown_files():
            text = path.read_text(encoding="utf-8")
            for pattern in STALE_PUBLIC_SURFACE_PATTERNS:
                if pattern in text:
                    hits.append(f"{path.relative_to(ROOT)} contains {pattern!r}")
        self.assertEqual([], hits)


if __name__ == "__main__":
    unittest.main()
