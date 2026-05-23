#!/usr/bin/env python3
"""Fail if active Embree/OptiX native sources regain benchmark app terms."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = (
    REPO_ROOT / "src/native/embree",
    REPO_ROOT / "src/native/optix",
)

APP_TERM_PATTERNS = {
    "dbscan": re.compile(r"db[_-]?scan", re.IGNORECASE),
    "raydb": re.compile(r"raydb", re.IGNORECASE),
    "robot": re.compile(r"\brobot\b", re.IGNORECASE),
    "collision": re.compile(r"\bcollision\b", re.IGNORECASE),
    "barnes": re.compile(r"\bbarnes\b", re.IGNORECASE),
    "inverse_square": re.compile(r"inverse[_-]?square", re.IGNORECASE),
    "force": re.compile(r"\bforce\b", re.IGNORECASE),
}

FORCE_FALSE_POSITIVE_PATTERNS = (
    re.compile(r"__forceinline__", re.IGNORECASE),
    re.compile(r"brute-force", re.IGNORECASE),
)


def _is_allowed_false_positive(term: str, line: str) -> bool:
    if term != "force":
        return False
    return any(pattern.search(line) for pattern in FORCE_FALSE_POSITIVE_PATTERNS)


def scan_paths(paths: tuple[Path, ...]) -> list[str]:
    violations: list[str] = []
    files: list[Path] = []
    for root in paths:
        if root.is_file():
            files.append(root)
            continue
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix in {".h", ".hpp", ".c", ".cc", ".cpp", ".cu", ".mm"}
        )

    for path in sorted(files):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for term, pattern in APP_TERM_PATTERNS.items():
                if pattern.search(line) and not _is_allowed_false_positive(term, line):
                    rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
                    violations.append(f"{rel}:{line_number}: app term `{term}`: {line.strip()}")
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional source roots or files to scan. Defaults to active Embree/OptiX native roots.",
    )
    args = parser.parse_args(argv)
    paths = tuple(args.paths) if args.paths else DEFAULT_ROOTS
    violations = scan_paths(paths)
    if violations:
        print("Native engine app-term purity gate failed:", file=sys.stderr)
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1
    print("Native engine app-term purity gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
