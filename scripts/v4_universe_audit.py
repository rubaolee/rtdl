from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_DOCS = (
    "README.md",
    "docs/README.md",
    "docs/current_v4_status.md",
    "docs/v4_release_notes.md",
    "docs/v4_engineering_summary.md",
    "docs/app_level_benchmark_summary.md",
    "docs/public_documentation_map.md",
    "docs/learn/README.md",
    "docs/learn/operator_catalog.md",
    "docs/learn/partner_choice.md",
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
    "tutorials/current/07_partner_choice.md",
    "examples/README.md",
    "examples/benchmark_apps/README.md",
    "examples/paper_reproduction/README.md",
    "examples/simple/README.md",
)

PUBLIC_CODE_PREFIXES = (
    "examples/simple/",
)

PUBLIC_CODE_FILES = (
    "examples/benchmark_apps/_support/v4_public_entry.py",
    "examples/benchmark_apps/rt_dbscan/v4_app.py",
    "examples/benchmark_apps/rtnn/v4_app.py",
    "examples/benchmark_apps/triangle_counting/v4_app.py",
    "examples/benchmark_apps/robot_collision/v4_app.py",
    "examples/benchmark_apps/raydb_style/v4_app.py",
    "examples/benchmark_apps/librts_spatial_index/v4_app.py",
    "examples/benchmark_apps/contact_manifold/v4_app.py",
    "examples/benchmark_apps/spatial_rayjoin/v4_app.py",
    "examples/benchmark_apps/barnes_hut/v4_app.py",
    "examples/benchmark_apps/hausdorff_xhd/v4_app.py",
)

CURRENT_CODE_PREFIXES = (
    ".github/workflows/",
    "src/rtdsl/",
    "src/native/",
    "scripts/",
    "tests/",
    "tools/",
    "examples/simple/",
    "examples/benchmark_apps/",
)

ROOT_RELEASE_FILES = {
    ".gitattributes",
    ".gitignore",
    "Makefile",
    "VERSION",
    "pyproject.toml",
    "requirements.txt",
    "run_review_tests.py",
}

ARCHIVE_PREFIXES = (
    "history/",
)

PROVENANCE_PREFIXES = (
    "future/",
)

PUBLIC_FORBIDDEN_PATTERNS = (
    re.compile(r"\bGoal\d+\b", re.IGNORECASE),
    re.compile(r"\bgoal\d+\b", re.IGNORECASE),
    re.compile(r"\bv4_goal\b", re.IGNORECASE),
    re.compile(r"review debt", re.IGNORECASE),
    re.compile(r"\baudit\b", re.IGNORECASE),
    re.compile(r"\breviewer\b", re.IGNORECASE),
    re.compile(r"release-review", re.IGNORECASE),
    re.compile(r"\bClaude\b|\bGemini\b|\bAntigravity\b"),
    re.compile(r"release candidate", re.IGNORECASE),
    re.compile(r"parity/control", re.IGNORECASE),
    re.compile(r"docs/reviews", re.IGNORECASE),
    re.compile(r"future/v4/reviews", re.IGNORECASE),
    re.compile(r"external review", re.IGNORECASE),
    re.compile(r"bounded framing", re.IGNORECASE),
    re.compile(r"(?<![\w/])history[\\/]", re.IGNORECASE),
    re.compile(r"(?<![\w/])future[\\/]", re.IGNORECASE),
)

MARKDOWN_LINK_PATTERN = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")

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
    if path in PUBLIC_CODE_FILES:
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_CODE_PREFIXES)


def _is_code(path: str) -> bool:
    return Path(path).suffix.lower() in CODE_EXTENSIONS


def _is_doc(path: str) -> bool:
    return Path(path).suffix.lower() in DOC_EXTENSIONS


def _tracked_bucket(path: str) -> str:
    if path in PUBLIC_DOCS or path in PUBLIC_CODE_FILES or any(path.startswith(prefix) for prefix in PUBLIC_CODE_PREFIXES):
        return "public_current"
    if any(path.startswith(prefix) for prefix in ARCHIVE_PREFIXES):
        return "history_archive"
    if any(path.startswith(prefix) for prefix in PROVENANCE_PREFIXES):
        return "maintainer_provenance"
    if path in ROOT_RELEASE_FILES:
        return "current_code_or_gate"
    if any(path.startswith(prefix) for prefix in CURRENT_CODE_PREFIXES):
        return "current_code_or_gate"
    return "other_tracked"


def _untracked_bucket(path: str) -> str:
    if path.startswith("history/local_workspace_debris_2026-06-27/"):
        return "local_history_archive_payload"
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


def _scan_public_links(paths: list[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    root_resolved = ROOT.resolve()
    for path in paths:
        if path not in PUBLIC_DOCS:
            continue
        full = ROOT / path
        if not full.exists() or not full.is_file():
            continue
        text = _read(path)
        for label, raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            target = raw_target.strip()
            lower = target.lower()
            if (
                "://" in lower
                or lower.startswith("#")
                or lower.startswith("mailto:")
                or lower.startswith("tel:")
            ):
                continue
            clean_target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not clean_target:
                continue
            clean_lower = clean_target.replace("\\", "/").lower()
            if clean_lower.startswith(("history/", "../history/", "future/", "../future/")):
                findings.append(
                    {
                        "path": path,
                        "label": label,
                        "target": target,
                        "problem": "public_doc_links_to_non_current_material",
                    }
                )
                continue
            if clean_target.startswith(("/", "\\")):
                findings.append(
                    {
                        "path": path,
                        "label": label,
                        "target": target,
                        "problem": "absolute_local_link_not_portable",
                    }
                )
                continue
            resolved = (full.parent / clean_target).resolve()
            try:
                resolved.relative_to(root_resolved)
            except ValueError:
                findings.append(
                    {
                        "path": path,
                        "label": label,
                        "target": target,
                        "problem": "local_link_escapes_repository",
                    }
                )
                continue
            if not resolved.exists():
                findings.append(
                    {
                        "path": path,
                        "label": label,
                        "target": target,
                        "problem": "local_link_target_missing",
                    }
                )
    return findings


def run_audit(*, strict_release: bool = False) -> dict[str, Any]:
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
    public_link_findings = _scan_public_links(tracked_public)
    tracked_docs_reviews = [path for path in tracked if path.startswith("docs/reviews/")]

    required_public_files = [path for path in PUBLIC_DOCS if not (ROOT / path).exists()]
    required_history_dirs = [
        path
        for path in ("history/", "history/v4_0_release_audit_2026-06-27/")
        if not (ROOT / path).exists()
    ]

    unknown_untracked = [path for path in untracked if _untracked_bucket(path) == "unknown_untracked"]

    status = "pass"
    if public_findings or public_link_findings or tracked_docs_reviews or required_public_files or required_history_dirs:
        status = "fail_public_surface"
    elif strict_release and untracked:
        status = "fail_local_debris"
    elif unknown_untracked:
        status = "pass_with_unknown_untracked"
    elif untracked:
        status = "pass_with_known_local_debris"

    return {
        "status": status,
        "strict_release": strict_release,
        "tracked_file_count": len(tracked),
        "untracked_file_count": len(untracked),
        "tracked_bucket_counts": dict(sorted(tracked_buckets.items())),
        "tracked_doc_bucket_counts": dict(sorted(doc_buckets.items())),
        "tracked_code_bucket_counts": dict(sorted(code_buckets.items())),
        "untracked_bucket_counts": dict(sorted(untracked_buckets.items())),
        "untracked_samples": dict(sorted(untracked_samples.items())),
        "public_file_count": len(tracked_public),
        "public_findings": public_findings,
        "public_link_findings": public_link_findings,
        "tracked_docs_reviews": tracked_docs_reviews,
        "missing_required_public_files": required_public_files,
        "missing_required_history_dirs": required_history_dirs,
        "unknown_untracked": unknown_untracked[:100],
        "unknown_untracked_count": len(unknown_untracked),
        "interpretation": (
            "Public V4 current surface must be clean. history/ is archival. "
            "future/ is maintainer provenance. Known untracked raw evidence, "
            "working records, and local debris are not public V4 files. Use "
            "--strict-release before a final tag/package gate to require a "
            "debris-free local tree."
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
    lines.extend(["", "## Public Link Findings", ""])
    if result["public_link_findings"]:
        for finding in result["public_link_findings"]:
            lines.append(
                f"- `{finding['path']}` link `{finding['target']}`: `{finding['problem']}`"
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
    parser.add_argument(
        "--strict-release",
        action="store_true",
        help="fail when any untracked local debris remains",
    )
    args = parser.parse_args()

    result = run_audit(strict_release=args.strict_release)
    payload = json.dumps(result, indent=2, sort_keys=True) if args.format == "json" else _to_markdown(result)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if result["status"].startswith("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
