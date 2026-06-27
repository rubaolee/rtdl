from __future__ import annotations

from dataclasses import dataclass
import subprocess
from pathlib import Path
from typing import Any


V4_GOAL4774_STATUS = "release_packaging_audit_created__clean_commit_required_before_tag"


EXCLUDE_PREFIXES = (
    "external/",
    "dist/",
)

EXCLUDE_EXACT = (
    "write_review.py",
)

EXCLUDE_SUFFIXES = (
    ".pid",
    ".tgz",
    ".whl",
    ".pyc",
)

EXCLUDE_CONTAINS = (
    "__pycache__",
    ".stderr.txt",
    ".stdout.txt",
)

RELEASE_PREFIXES = (
    "README.md",
    "docs/",
    "examples/",
    "future/v4/",
    "scripts/",
    "src/",
    "tests/",
    "tutorials/",
    "tools/",
)

REQUIRED_CURRENT_FILES = (
    "README.md",
    "docs/current_v4_status.md",
    "docs/app_level_benchmark_summary.md",
    "future/v4/README.md",
    "future/v4/V4_CURRENT_AGENT_REFRESH_RUNBOOK_2026-06-25.md",
    "future/v4/reviews/v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md",
    "future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md",
    "future/v4/v4_goal4773_antigravity_review_intake_and_release_owner_status_2026-06-27.md",
    "src/rtdsl/v4_goal4773_release_authorization_status.py",
    "tests/v4_goal4773_release_authorization_status_test.py",
)


@dataclass(frozen=True)
class PackagingAuditRow:
    status_code: str
    path: str
    bucket: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "status_code": self.status_code,
            "path": self.path,
            "bucket": self.bucket,
            "reason": self.reason,
        }


def _git_status(repo: Path) -> list[tuple[str, str]]:
    output = subprocess.check_output(
        ["git", "status", "--porcelain=v1"],
        cwd=repo,
        text=True,
        encoding="utf-8",
    )
    rows: list[tuple[str, str]] = []
    for line in output.splitlines():
        if not line:
            continue
        rows.append((line[:2], line[3:].replace("\\", "/")))
    return rows


def _bucket(path: str) -> tuple[str, str]:
    if path in EXCLUDE_EXACT:
        return "exclude_from_release_commit", "ad_hoc_review_helper_not_release_surface"
    if path.startswith(EXCLUDE_PREFIXES):
        return "exclude_from_release_commit", "external_or_built_artifact_directory"
    if path.endswith(EXCLUDE_SUFFIXES):
        return "exclude_from_release_commit", "temporary_binary_or_process_artifact"
    if any(marker in path for marker in EXCLUDE_CONTAINS):
        return "exclude_from_release_commit", "tool_output_or_cache_artifact"
    if path.startswith("future/v4/evidence/") and path.endswith((".cdb", ".edgebin")):
        return "manual_review_required", "large_raw_benchmark_payload"
    if path.startswith(RELEASE_PREFIXES):
        return "release_commit_candidate", "source_doc_test_or_compact_evidence"
    return "manual_review_required", "unclassified_top_level_path"


def v4_goal4774_release_packaging_audit(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    rows = []
    for status_code, path in _git_status(repo):
        bucket, reason = _bucket(path)
        rows.append(PackagingAuditRow(status_code, path, bucket, reason))

    counts: dict[str, int] = {}
    for row in rows:
        counts[row.bucket] = counts.get(row.bucket, 0) + 1

    missing_required = tuple(path for path in REQUIRED_CURRENT_FILES if not (repo / path).exists())
    required_not_dirty = tuple(
        path
        for path in REQUIRED_CURRENT_FILES
        if path not in {row.path for row in rows} and (repo / path).exists()
    )
    release_candidates = tuple(row.path for row in rows if row.bucket == "release_commit_candidate")
    excluded = tuple(row.path for row in rows if row.bucket == "exclude_from_release_commit")
    manual = tuple(row.path for row in rows if row.bucket == "manual_review_required")

    return {
        "status": V4_GOAL4774_STATUS,
        "total_dirty_entries": len(rows),
        "bucket_counts": counts,
        "rows": tuple(row.as_dict() for row in rows),
        "release_commit_candidate_count": len(release_candidates),
        "exclude_from_release_commit_count": len(excluded),
        "manual_review_required_count": len(manual),
        "release_commit_candidates": release_candidates,
        "excluded_from_release_commit": excluded,
        "manual_review_required": manual,
        "missing_required_current_files": missing_required,
        "required_current_files_not_dirty": required_not_dirty,
        "direct_git_tag_allowed_now": False,
        "clean_commit_required_before_tag": True,
        "pod_required_for_packaging": False,
        "claude_required_for_packaging_audit": False,
    }


def validate_v4_goal4774_release_packaging_audit(root: Path | None = None) -> dict[str, Any]:
    audit = v4_goal4774_release_packaging_audit(root)
    if audit["status"] != V4_GOAL4774_STATUS:
        raise ValueError("Goal4774 packaging audit status drift")
    if audit["missing_required_current_files"]:
        raise ValueError(f"Goal4774 missing required files: {audit['missing_required_current_files']}")
    if audit["direct_git_tag_allowed_now"]:
        raise ValueError("Goal4774 must not allow direct git tagging from dirty tree")
    if not audit["clean_commit_required_before_tag"]:
        raise ValueError("Goal4774 must require clean release commit before tag")
    if audit["pod_required_for_packaging"]:
        raise ValueError("Goal4774 packaging audit must not require POD")
    for required in REQUIRED_CURRENT_FILES:
        if required not in audit["release_commit_candidates"] and required not in audit["required_current_files_not_dirty"]:
            raise ValueError(f"Goal4774 required file is not classified for release: {required}")
    for forbidden_prefix in EXCLUDE_PREFIXES:
        if any(path.startswith(forbidden_prefix) for path in audit["release_commit_candidates"]):
            raise ValueError(f"Goal4774 release candidates include excluded prefix: {forbidden_prefix}")
    for forbidden_marker in EXCLUDE_CONTAINS:
        if any(forbidden_marker in path for path in audit["release_commit_candidates"]):
            raise ValueError(f"Goal4774 release candidates include excluded marker: {forbidden_marker}")
    return audit


__all__ = [
    "V4_GOAL4774_STATUS",
    "PackagingAuditRow",
    "v4_goal4774_release_packaging_audit",
    "validate_v4_goal4774_release_packaging_audit",
]
