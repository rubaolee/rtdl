from __future__ import annotations

from dataclasses import dataclass
import subprocess
from pathlib import Path
from typing import Any


V4_GOAL4775_STATUS = "release_staging_manifest_created__pathspec_ready__tag_still_requires_clean_commit"


EXCLUDE_PREFIXES = (
    "dist/",
    "external/",
)

EXCLUDE_EXACT = (
    "write_review.py",
)

EXCLUDE_SUFFIXES = (
    ".pid",
    ".patch",
    ".tgz",
    ".whl",
    ".pyc",
)

EXCLUDE_CONTAINS = (
    "__pycache__",
    ".stderr.txt",
    ".stdout.txt",
)

V3_HISTORY_PREFIXES = (
    "docs/rebuild/v3/",
    "docs/handoff/HANDOFF_PHOENIX_V3",
    "docs/handoff/STOP_THE_CHURN_PHOENIX_V3",
    "scripts/v3_",
    "tests/v3_",
)

V3_HISTORY_MARKERS = (
    "phoenix_v3",
    "PHOENIX_V3",
)

OLD_TOPLEVEL_RELOCATION_PREFIXES = (
    "dist/",
    "future/",
    "history/",
)

STAGE_PREFIXES = (
    ".gitattributes",
    ".gitignore",
    "README.md",
    "docs/README.md",
    "docs/current_v4_status.md",
    "docs/v4_release_notes.md",
    "docs/v4_engineering_summary.md",
    "docs/app_level_benchmark_summary.md",
    "docs/learn/",
    "docs/public_documentation_map.md",
    "docs/reviews/claude_v4",
    "examples/README.md",
    "examples/benchmark_apps/",
    "examples/current/",
    "examples/paper_reproduction/",
    "examples/simple/",
    "tools/_archive/future/README.md",
    "tools/_archive/future/v4/",
    "tools/_archive/history/v4_0_benchmark_harness_archive_2026-06-27/",
    "tools/_archive/history/v4_0_release_audit_2026-06-27/",
    "tools/_archive/history/local_workspace_debris_2026-06-27/README.md",
    "scripts/v4_",
    "scripts/rt_barneshut_author_contract_probe.py",
    "scripts/run_claude_v4_0_release_candidate_review_2026_06_24.ps1",
    "src/native/optix/",
    "src/rtdsl/_example_support/",
    "src/rtdsl/partner_adapters.py",
    "src/rtdsl/rt_barneshut_author_contract.py",
    "src/rtdsl/v4",
    "tests/v4_",
    "tools/",
    "tutorials/current/",
)

FUTURE_V4_EVIDENCE_STAGE_SUFFIXES = (
    ".json",
    ".jsonl",
    ".md",
    ".cu",
    ".py",
)

FUTURE_V4_REVIEW_STAGE_EXACT = (
    "tools/_archive/future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md",
    "tools/_archive/future/v4/reviews/antigravity_v4_goal4757_final_v4_0_release_review_2026-06-26.md",
    "tools/_archive/future/v4/reviews/antigravity_v4_pre_release_items_1_to_5_completion_2026-06-27.md",
    "tools/_archive/future/v4/reviews/call_for_review_v4_pre_release_items_1_to_5_completion_2026-06-27.md",
    "tools/_archive/future/v4/reviews/forward_message_v4_pre_release_items_1_to_5_completion_2026-06-27.txt",
    "tools/_archive/future/v4/reviews/claude_v4_0_0_release_review_2026-06-25.md",
    "tools/_archive/future/v4/reviews/v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md",
    "tools/_archive/future/v4/reviews/v4_goal4757_final_release_external_review_debt_2026-06-26.md",
    "tools/_archive/future/v4/reviews/v4_benchmark_harness_public_entry_cleanup_2026-06-27.md",
)

REQUIRED_STAGE_PATHS = (
    "README.md",
    "docs/README.md",
    "docs/current_v4_status.md",
    "docs/v4_release_notes.md",
    "docs/v4_engineering_summary.md",
    "docs/app_level_benchmark_summary.md",
    "docs/learn/operator_catalog.md",
    "docs/learn/partner_choice.md",
    "docs/public_documentation_map.md",
    "examples/README.md",
    "examples/benchmark_apps/README.md",
    "examples/simple/sorting_rows.py",
    "examples/benchmark_apps/_support/_repo_bootstrap.py",
    "examples/benchmark_apps/_support/v4_public_entry.py",
    "examples/benchmark_apps/_support/rtdl_ann_candidate_app.py",
    "examples/benchmark_apps/_support/rtdl_barnes_hut_force_app.py",
    "examples/benchmark_apps/_support/rtdl_graph_triangle_count.py",
    "examples/benchmark_apps/_support/rtdl_language_reference.py",
    "examples/benchmark_apps/rt_dbscan/v4_app.py",
    "src/rtdsl/_example_support/benchmark_harness_compat.py",
    "tools/_archive/future/README.md",
    "tools/_archive/future/v4/README.md",
    "tools/_archive/history/v4_0_benchmark_harness_archive_2026-06-27/examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
    "tools/_archive/history/v4_0_release_audit_2026-06-27/README.md",
    "tutorials/current/03_sorting_rows.md",
    "tutorials/current/07_benchmark_apps.md",
    "tutorials/current/08_choose_a_partner.md",
    "tools/_archive/future/v4/V4_CURRENT_AGENT_REFRESH_RUNBOOK_2026-06-25.md",
    "tools/_archive/future/v4/reviews/v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md",
    "tools/_archive/future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md",
    "tools/_archive/future/v4/v4_goal4773_antigravity_review_intake_and_release_owner_status_2026-06-27.md",
    "tools/_archive/future/v4/v4_goal4779_pre_release_items_1_to_5_completion_2026-06-27.md",
    "tools/_archive/future/v4/reviews/antigravity_v4_pre_release_items_1_to_5_completion_2026-06-27.md",
    "tools/_archive/future/v4/reviews/call_for_review_v4_pre_release_items_1_to_5_completion_2026-06-27.md",
    "tools/_archive/future/v4/reviews/forward_message_v4_pre_release_items_1_to_5_completion_2026-06-27.txt",
    "tools/_archive/future/v4/evidence/v4_goal4774_release_packaging_audit_2026-06-27.json",
    "tools/_archive/future/v4/v4_goal4774_release_packaging_audit_2026-06-27.md",
    "tools/_archive/future/v4/evidence/v4_goal4775_release_staging_manifest_2026-06-27.json",
    "tools/_archive/future/v4/v4_goal4775_release_staging_manifest_2026-06-27.md",
    "tools/_archive/future/v4/v4_goal4775_release_stage_pathspec_2026-06-27.txt",
    "src/rtdsl/v4_goal4773_release_authorization_status.py",
    "src/rtdsl/v4_goal4774_release_packaging_audit.py",
    "src/rtdsl/v4_goal4775_release_staging_manifest.py",
    "scripts/v4_goal4775_release_staging_manifest.py",
    "scripts/v4_release_clean_checkout_gate.py",
    "tests/v4_goal4773_release_authorization_status_test.py",
    "tests/v4_goal4774_release_packaging_audit_test.py",
    "tests/v4_goal4775_release_staging_manifest_test.py",
    "tests/v4_release_clean_checkout_gate_test.py",
)


@dataclass(frozen=True)
class StagingRow:
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


def _git_status_uall(repo: Path) -> list[tuple[str, str]]:
    output = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-uall"],
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


def _is_future_v4_evidence_stage_file(path: str) -> bool:
    return path.startswith("tools/_archive/future/v4/evidence/") and path.endswith(FUTURE_V4_EVIDENCE_STAGE_SUFFIXES)


def _is_future_v4_review_stage_file(path: str) -> bool:
    return path in FUTURE_V4_REVIEW_STAGE_EXACT


def _classify(path: str) -> tuple[str, str]:
    if path.startswith(OLD_TOPLEVEL_RELOCATION_PREFIXES):
        return "exclude_from_v4_release_commit", "old_top_level_path_relocated_under_tools_archive"
    if path in EXCLUDE_EXACT:
        return "exclude_from_v4_release_commit", "ad_hoc_review_helper_not_release_surface"
    if path.startswith(EXCLUDE_PREFIXES):
        return "exclude_from_v4_release_commit", "external_or_built_artifact_directory"
    if path.endswith(EXCLUDE_SUFFIXES):
        return "exclude_from_v4_release_commit", "temporary_binary_or_process_artifact"
    if any(marker in path for marker in EXCLUDE_CONTAINS):
        return "exclude_from_v4_release_commit", "tool_output_or_cache_artifact"
    if path.startswith(V3_HISTORY_PREFIXES) or any(marker in path for marker in V3_HISTORY_MARKERS):
        return "hold_v3_history_not_v4_tag", "phoenix_v3_history_not_part_of_v4_public_tag"
    if path.startswith("tools/_archive/future/v4/evidence/") and not _is_future_v4_evidence_stage_file(path):
        return "exclude_from_v4_release_commit", "raw_or_noncompact_evidence_not_for_tag"
    if path.startswith("tools/_archive/future/v4/reviews/") and not _is_future_v4_review_stage_file(path):
        return "hold_review_debt_not_v4_tag", "older_review_debt_or_prompt_not_needed_for_public_tag"
    if path.startswith(STAGE_PREFIXES):
        return "stage_for_v4_release_commit", "current_v4_source_docs_tests_or_compact_evidence"
    return "manual_review_required", "not_matched_by_v4_release_staging_rules"


def v4_goal4775_release_staging_manifest(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    staged_rows: list[StagingRow] = []
    for status_code, path in _git_status_uall(repo):
        bucket, reason = _classify(path)
        full_path = repo / path
        if bucket == "stage_for_v4_release_commit" and full_path.is_file() and full_path.stat().st_size == 0:
            bucket = "exclude_from_v4_release_commit"
            reason = "empty_file_not_release_evidence"
        staged_rows.append(StagingRow(status_code, path, bucket, reason))
    rows = tuple(staged_rows)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.bucket] = counts.get(row.bucket, 0) + 1

    stage_paths = tuple(row.path for row in rows if row.bucket == "stage_for_v4_release_commit")
    excluded = tuple(row.path for row in rows if row.bucket == "exclude_from_v4_release_commit")
    held_v3 = tuple(row.path for row in rows if row.bucket == "hold_v3_history_not_v4_tag")
    manual = tuple(row.path for row in rows if row.bucket == "manual_review_required")
    dirty_paths = {row.path for row in rows}
    required_missing = tuple(path for path in REQUIRED_STAGE_PATHS if not (repo / path).exists())
    required_not_staged = tuple(
        path
        for path in REQUIRED_STAGE_PATHS
        if path in dirty_paths and path not in stage_paths
    )
    required_already_clean = tuple(
        path
        for path in REQUIRED_STAGE_PATHS
        if path not in dirty_paths and (repo / path).exists()
    )

    return {
        "status": V4_GOAL4775_STATUS,
        "total_dirty_file_entries": len(rows),
        "bucket_counts": counts,
        "rows": tuple(row.as_dict() for row in rows),
        "stage_for_v4_release_commit_count": len(stage_paths),
        "exclude_from_v4_release_commit_count": len(excluded),
        "hold_v3_history_not_v4_tag_count": len(held_v3),
        "manual_review_required_count": len(manual),
        "stage_for_v4_release_commit": stage_paths,
        "exclude_from_v4_release_commit": excluded,
        "hold_v3_history_not_v4_tag": held_v3,
        "manual_review_required": manual,
        "required_stage_paths": REQUIRED_STAGE_PATHS,
        "required_stage_paths_missing": required_missing,
        "required_stage_paths_not_staged": required_not_staged,
        "required_stage_paths_already_clean": required_already_clean,
        "direct_git_tag_allowed_now": False,
        "clean_release_commit_required_before_tag": True,
        "pathspec_ready": not manual and not required_missing and not required_not_staged,
        "pod_required_for_staging_manifest": False,
        "claude_required_for_staging_manifest": False,
    }


def validate_v4_goal4775_release_staging_manifest(root: Path | None = None) -> dict[str, Any]:
    manifest = v4_goal4775_release_staging_manifest(root)
    if manifest["status"] != V4_GOAL4775_STATUS:
        raise ValueError("Goal4775 release staging status drift")
    if manifest["manual_review_required"]:
        raise ValueError(f"Goal4775 has manual-review paths: {manifest['manual_review_required'][:10]}")
    if manifest["required_stage_paths_missing"]:
        raise ValueError(f"Goal4775 missing required stage paths: {manifest['required_stage_paths_missing']}")
    if manifest["required_stage_paths_not_staged"]:
        raise ValueError(f"Goal4775 required paths are not staged by manifest: {manifest['required_stage_paths_not_staged']}")
    if manifest["direct_git_tag_allowed_now"]:
        raise ValueError("Goal4775 must not permit direct tag before clean release commit")
    if not manifest["clean_release_commit_required_before_tag"]:
        raise ValueError("Goal4775 must require a clean release commit before tag")
    if not manifest["pathspec_ready"]:
        raise ValueError("Goal4775 pathspec is not ready")
    stage_paths = manifest["stage_for_v4_release_commit"]
    forbidden_markers = EXCLUDE_CONTAINS + EXCLUDE_SUFFIXES
    for path in stage_paths:
        if path.startswith(EXCLUDE_PREFIXES):
            raise ValueError(f"Goal4775 stage list includes excluded prefix: {path}")
        if path.startswith(V3_HISTORY_PREFIXES) or any(marker in path for marker in V3_HISTORY_MARKERS):
            raise ValueError(f"Goal4775 stage list includes V3 history path: {path}")
        if any(marker in path for marker in forbidden_markers):
            raise ValueError(f"Goal4775 stage list includes raw/generated artifact: {path}")
        if path.startswith("tools/_archive/future/v4/evidence/") and not _is_future_v4_evidence_stage_file(path):
            raise ValueError(f"Goal4775 stage list includes noncompact evidence: {path}")
        full_path = (root or Path(__file__).resolve().parents[2]) / path
        if full_path.is_file() and full_path.stat().st_size == 0:
            raise ValueError(f"Goal4775 stage list includes empty file: {path}")
    return manifest


__all__ = [
    "V4_GOAL4775_STATUS",
    "StagingRow",
    "v4_goal4775_release_staging_manifest",
    "validate_v4_goal4775_release_staging_manifest",
]
