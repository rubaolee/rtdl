#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1173 staged source archive manifest"
DEFAULT_JSON = ROOT / "docs/reports/goal1173_staged_source_archive_manifest_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1173_staged_source_archive_manifest_2026-04-30.md"

INCLUDE_DIRS = ("src", "examples", "scripts", "tests", "docs/handoff")
INCLUDE_FILES = (
    "README.md",
    "Makefile",
    "pyproject.toml",
    "setup.cfg",
    "pytest.ini",
)
EXCLUDE_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "build",
    "dist",
    "out",
    ".venv",
    "venv",
}
EXCLUDE_SUFFIXES = (".pyc", ".pyo", ".so", ".dylib", ".o", ".a", ".log")


def _iter_files() -> Iterable[Path]:
    for directory in INCLUDE_DIRS:
        root = ROOT / directory
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if any(part in EXCLUDE_PARTS for part in rel.parts):
                continue
            if path.suffix in EXCLUDE_SUFFIXES:
                continue
            yield rel
    for name in INCLUDE_FILES:
        path = ROOT / name
        if path.exists() and path.is_file():
            yield path.relative_to(ROOT)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> dict[str, object]:
    files = []
    aggregate = hashlib.sha256()
    for rel in sorted(set(_iter_files()), key=str):
        digest = _sha256(ROOT / rel)
        files.append({"path": str(rel), "sha256": digest, "bytes": (ROOT / rel).stat().st_size})
        aggregate.update(str(rel).encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\0")
    return {
        "goal": GOAL,
        "date": DATE,
        "file_count": len(files),
        "aggregate_sha256": aggregate.hexdigest(),
        "include_dirs": list(INCLUDE_DIRS),
        "include_files": list(INCLUDE_FILES),
        "files": files,
        "valid": len(files) > 0,
        "boundary": (
            "This manifest defines an exact staged source set for a future archive path. "
            "It does not create a pod artifact, run benchmarks, or authorize public wording."
        ),
    }


def to_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal1173 Staged Source Archive Manifest",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        f"File count: `{payload['file_count']}`",
        f"Aggregate SHA256: `{payload['aggregate_sha256']}`",
        "",
        "## Included Roots",
        "",
    ]
    for root in payload["include_dirs"]:  # type: ignore[index]
        lines.append(f"- `{root}`")
    for file_name in payload["include_files"]:  # type: ignore[index]
        lines.append(f"- `{file_name}`")
    lines.extend(["", "## Boundary", "", str(payload["boundary"]), ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a manifest for a staged RTDL source archive.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = build_manifest()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "file_count": payload["file_count"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
