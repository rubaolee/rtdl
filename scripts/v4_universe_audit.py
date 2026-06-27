from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_DOCS = (
    "README.md",
    "docs/README.md",
    "docs/current_v4_status.md",
    "docs/app_level_benchmark_summary.md",
    "docs/public_documentation_map.md",
    "docs/learn/README.md",
    "docs/learn/operator_catalog.md",
    "docs/learn/performance_wording.md",
    "docs/learn/source_tree_doctor.md",
    "tutorials/README.md",
    "tutorials/current/README.md",
    "tutorials/current/01_first_run.md",
    "tutorials/current/02_hello_world.md",
    "tutorials/current/03_backend_choice.md",
    "tutorials/current/04_prepared_runtime.md",
    "tutorials/current/05_measurement_boundaries.md",
    "tutorials/current/06_benchmark_apps.md",
    "examples/README.md",
    "examples/v4/README.md",
)

PUBLIC_CODE_PREFIXES = (
    "examples/v4/",
)

CURRENT_CODE_PREFIXES = (
    "src/rtdsl/",
    "scripts/",
    "tests/",
    "examples/v4/",
    "examples/current/research_benchmarks/",
)

ARCHIVE_PREFIXES = (
    "history/",
)

AUDIT_PREFIXES = (
    "future/",
)

PUBLIC_FORBIDDEN_PATTERNS = (
    re.compile(r"\bGoal\d+\b", re.IGNORECASE),
    re.compile(r"\bgoal\d+\b", re.IGNORECASE),
    re.compile(r"\bv4_goal\b", re.IGNORECASE),
    re.compile(r"review debt", re.IGNORECASE),
    re.compile(r"\bClaude\b|\bGemini\b|\bAntigravity\b"),
    re.compile(r"release candidate", re.IGNORECASE),
    re.compile(r"parity/control", re.IGNORECASE),
    re.compile(r"docs/reviews", re.IGNORECASE),
    re.compile(r"future/v4/reviews", re.IGNORECASE),
    re.compile(r"external review", re.IGNORECASE),
    re.compile(r"bounded framing", re.IGNORECASE),
)

PUBLIC_CONFUSING_OLD_PATH_PATTERNS = (
    re.compile(r"choose V2", re.IGNORECASE),
    re.compile(r"choose V3", re.IGNORECASE),
    re.compile(r"current V3", re.IGNORECASE),
    re.compile(r"V3 tutorial", re.IGNORECASE),
    re.compile(r"V2 tutorial", re.IGNORECASE),
    re.compile(r"V4/V3/V2\s+superset", re.IGNORECASE),
)

CODE_EXTENSIONS = {
    ".py",
    ".pyi",
    ".c",
    ".cc",
    ".cpp",
    ".cu",
    ".h",
    ".hpp",
    ".cmake",
    ".ps1",
    ".sh",
}

DOC_EXTENSIONS = {".md", ".rst", ".txt"}


def _git_lines(*args: str) -> list[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [line for line in proc.stdout.splitlines() if line.strip()]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def _is_public_path(path: str) -> bool:
    if path in PUBLIC_DOCS:
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_CODE_PREFIXES)


def _is_code(path: str) -> bool:
    return Path(path).suffix.lower() in CODE_EXTENSIONS


def _is_doc(path: str) -> bool:
    return Path(path).suffix.lower() in DOC_EXTENSIONS


def _tracked_bucket(path: str) -> str:
    if path in PUBLIC_DOCS or any(path.startswith(prefix) for prefix in PUBLIC_CODE_PREFIXES):
        return "public_current"
    if any(path.startswith(prefix) for prefix in ARCHIVE_PREFIXES):
        return "history_archive"
    if any(path.startswith(prefix) for prefix in AUDIT_PREFIXES):
        return "audit_provenance"
    if any(path.startswith(prefix) for prefix in CURRENT_CODE_PREFIXES):
        return "current_code_or_gate"
    return "other_tracked"


def _untracked_bucket(path: str) -> str:
    if path.startswith("dist/") or path.startswith("build/"):
        return "local_build_output"
    if path.startswith("external/"):
        return "local_external_checkout"
    if path.startswith("future/v4/evidence/"):
        return "local_raw_v4_evidence"
    if path.startswith("future/v4/reviews/"):
        return "local_v4_review_working_record"
    if path.startswith("scripts/v3_") or path.startswith("scripts/phoenix_v3_"):
        return "local_v3_phoenix_script_debris"
    if path.startswith("tests/v3_") or path.startswith("tests/v3"):
        return "local_v3_phoenix_test_debris"
    if path.startswith("scripts/run_claude_phoenix_") or path.startswith("scripts/run_phoenix_v3_"):
        return "local_v3_phoenix_review_helper"
    if path.startswith("tools/rtbarneshut_"):
        return "local_paper_reproduction_patch"
    if path == "write_review.py":
        return "local_review_helper"
    return "unknown_untracked"


def _scan_public(paths: list[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in paths:
        if not _is_public_path(path):
            continue
        full = ROOT / path
        if not full.exists() or not full.is_file():
            continue
        text = _read(path)
        patterns = PUBLIC_FORBIDDEN_PATTERNS
        if path in PUBLIC_DOCS:
            patterns = PUBLIC_FORBIDDEN_PATTERNS + PUBLIC_CONFUSING_OLD_PATH_PATTERNS
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                findings.append(
                    {
                        "path": path,
                        "pattern": pattern.pattern,
                        "match": match.group(0),
                    }
                )
    return findings


def run_audit() -> dict[str, Any]:
    tracked = _git_lines("ls-files")
    untracked = _git_lines("ls-files", "--others", "--exclude-standard")

    tracked_buckets = Counter(_tracked_bucket(path) for path in tracked)
    untracked_buckets = Counter(_untracked_bucket(path) for path in untracked)
    doc_buckets = Counter(_tracked_bucket(path) for path in tracked if _is_doc(path))
    code_buckets = Counter(_tracked_bucket(path) for path in tracked if _is_code(path))
    untracked_samples: dict[str, list[str]] = {}
    for path in untracked:
        bucket = _untracked_bucket(path)
        untracked_samples.setdefault(bucket, [])
        if len(untracked_samples[bucket]) < 12:
            untracked_samples[bucket].append(path)

    tracked_public = [path for path in tracked if _is_public_path(path)]
    public_findings = _scan_public(tracked_public)
    tracked_docs_reviews = [path for path in tracked if path.startswith("docs/reviews/")]

    required_public_files = [path for path in PUBLIC_DOCS if not (ROOT / path).exists()]
    required_history_dirs = [
        path
        for path in ("history/", "history/v4_0_release_audit_2026-06-27/")
        if not (ROOT / path).exists()
    ]

    unknown_untracked = [path for path in untracked if _untracked_bucket(path) == "unknown_untracked"]

    status = "pass"
    if public_findings or tracked_docs_reviews or required_public_files or required_history_dirs:
        status = "fail_public_surface"
    elif unknown_untracked:
        status = "pass_with_unknown_untracked"
    elif untracked:
        status = "pass_with_known_local_debris"

    return {
        "status": status,
        "tracked_file_count": len(tracked),
        "untracked_file_count": len(untracked),
        "tracked_bucket_counts": dict(sorted(tracked_buckets.items())),
        "tracked_doc_bucket_counts": dict(sorted(doc_buckets.items())),
        "tracked_code_bucket_counts": dict(sorted(code_buckets.items())),
        "untracked_bucket_counts": dict(sorted(untracked_buckets.items())),
        "untracked_samples": dict(sorted(untracked_samples.items())),
        "public_file_count": len(tracked_public),
        "public_findings": public_findings,
        "tracked_docs_reviews": tracked_docs_reviews,
        "missing_required_public_files": required_public_files,
        "missing_required_history_dirs": required_history_dirs,
        "unknown_untracked": unknown_untracked[:100],
        "unknown_untracked_count": len(unknown_untracked),
        "interpretation": (
            "Public V4 current surface must be clean. history/ is archival. "
            "future/ is audit provenance. Known untracked raw evidence and old "
            "Phoenix/V3 debris are local workspace cleanup items, not public V4 files."
        ),
    }


def _to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# V4 Universe Audit Snapshot",
        "",
        "Date: 2026-06-27",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Counts",
        "",
        f"- tracked files: `{result['tracked_file_count']}`",
        f"- untracked files: `{result['untracked_file_count']}`",
        f"- public current files scanned: `{result['public_file_count']}`",
        "",
        "## Tracked Buckets",
        "",
    ]
    for key, value in result["tracked_bucket_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Tracked Documentation Buckets", ""])
    for key, value in result["tracked_doc_bucket_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Tracked Code Buckets", ""])
    for key, value in result["tracked_code_bucket_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Public Surface Findings", ""])
    if result["public_findings"]:
        for finding in result["public_findings"]:
            lines.append(
                f"- `{finding['path']}` matched `{finding['pattern']}` as `{finding['match']}`"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Untracked Buckets", ""])
    for key, value in result["untracked_bucket_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Untracked Samples", ""])
    for key, values in result["untracked_samples"].items():
        lines.append(f"### `{key}`")
        for value in values:
            lines.append(f"- `{value}`")
    lines.extend(["", "## Interpretation", "", result["interpretation"]])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("json", "md"), default="json")
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()

    result = run_audit()
    payload = json.dumps(result, indent=2, sort_keys=True) if args.format == "json" else _to_markdown(result)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if result["status"].startswith("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
