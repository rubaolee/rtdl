#!/usr/bin/env python3
"""Generate the per-file audit ledger for Goal 409.

This is intentionally a first-pass classifier, not a claim that every file has
been line-by-line re-proven. The purpose is to give every tracked file a stable
record with a concrete default judgment, then let checker/verifier/proof review
the risky slices instead of starting from a blank CSV.
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path("/Users/rl2025/worktrees/rtdl_v0_4_main_publish")
OUTPUT = REPO_ROOT / "docs" / "reports" / "goal409_repo_file_status_ledger_2026-04-15.csv"


def tracked_files() -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in proc.stdout.splitlines() if line]


def category_for(path: str) -> str:
    if path.startswith("src/native/"):
        return "native_source"
    if path.startswith("src/"):
        return "source"
    if path.startswith("tests/"):
        return "test"
    if path.startswith("examples/"):
        return "example"
    if path.startswith("docs/tutorials/"):
        return "tutorial"
    if path.startswith("docs/release_reports/"):
        return "release_doc"
    if path.startswith("docs/reports/"):
        return "report"
    if path.startswith("docs/handoff/"):
        return "handoff"
    if path.startswith("docs/"):
        return "doc"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("apps/"):
        return "app"
    if path.startswith("generated/"):
        return "generated"
    if path.startswith("build/"):
        return "tracked_build_artifact"
    if path.startswith("history/"):
        return "history"
    return "repo_root"


def role_for(path: str, category: str) -> str:
    if path == "requirements.txt":
        return "dependency_manifest"
    if path == "VERSION":
        return "version_marker"
    if category in {"source", "native_source"}:
        return "implementation"
    if category == "test":
        return "verification"
    if category == "example":
        return "user_example"
    if category == "tutorial":
        return "tutorial"
    if category == "release_doc":
        return "release_surface"
    if category == "report":
        return "audit_or_result_record"
    if category == "handoff":
        return "review_or_handoff_packet"
    if category == "doc":
        return "documentation"
    if category == "script":
        return "engineering_support"
    if category == "schema":
        return "data_definition"
    if category == "app":
        return "native_entrypoint"
    if category == "generated":
        return "generated_example_or_artifact"
    if category == "tracked_build_artifact":
        return "tracked_output"
    if category == "history":
        return "historical_record"
    if path in {"README.md", "VERSION", ".gitignore", "Makefile"}:
        return "repo_front_door_or_build_surface"
    return "unclear"


def initial_status(path: str, category: str) -> str:
    if path.startswith("docs/history/"):
        return "historical"
    if path.startswith("docs/archive/"):
        return "historical"
    if path.startswith("docs/wiki_drafts/"):
        return "historical"
    if path.startswith("docs/engineering/handoffs/"):
        return "historical"
    if path == "docs/current_milestone_qa.md":
        return "historical"
    if re.match(r"^docs/goal_\d+.*\.md$", path):
        return "historical"
    if path in {"README.md", "VERSION", ".gitignore", "Makefile", "requirements.txt"}:
        return "live"
    if re.match(r"^src/.*/goal\d+.*\.(py|md|json)$", path):
        return "transitional"
    if re.match(r"^scripts/goal\d+.*\.(py|sh|md|json)$", path):
        return "transitional"
    if re.match(r"^examples/internal/rtdl_goal\d+.*\.py$", path):
        return "transitional"
    if category == "release_doc":
        if "/v0_6/" in path:
            return "live"
        return "historical"
    if category in {"release_doc", "source", "native_source", "test", "script", "schema"}:
        return "live"
    if category in {"doc", "tutorial", "example", "app"}:
        return "live"
    if category in {"history", "report", "handoff"}:
        return "historical"
    if category in {"tracked_build_artifact", "generated"}:
        return "transitional"
    return "unclear"


def correctness_for(path: str, category: str, status: str) -> str:
    if path == "README.md":
        return "front-door doc recently updated; spot-check still recommended"
    if path == "VERSION":
        return "machine-readable version marker; verify against live release"
    if path == "requirements.txt":
        return "dependency manifest; verify package list and pin ranges against live runtime"
    if status == "historical":
        return "historical record; not a live correctness surface by itself"
    if status == "transitional" and re.match(r"^(src/.*/goal\d+|scripts/goal\d+)", path):
        return "goal-scoped engineering surface; verify whether it is still imported or dead scaffolding"
    if category in {"history", "report", "handoff"}:
        return "historical record; not a live correctness surface by itself"
    if category in {"tracked_build_artifact", "generated"}:
        return "artifact or generated surface; correctness depends on source regeneration path"
    if category in {"source", "native_source", "test", "script", "schema", "app"}:
        return "live engineering surface; targeted correctness review still required"
    if category in {"release_doc", "doc", "tutorial", "example", "repo_root"}:
        return "content-bearing surface; wording and examples require audit"
    if status == "unclear":
        return "classification unclear; correctness needs direct inspection"
    return "needs direct inspection"


def freshness_for(path: str, category: str, status: str) -> str:
    if path == "README.md":
        return "current release front door"
    if path == "VERSION":
        return "must exactly match the current released version"
    if path == "requirements.txt":
        return "active install surface; confirm package list is still current"
    if category == "release_doc" and "/v0_6/" in path:
        return "current release line material"
    if status == "historical":
        return "time-stamped or archived snapshot; freshness acceptable if treated as archival"
    if category in {"history", "report", "handoff"}:
        return "time-stamped snapshot; freshness acceptable if treated as archival"
    if category in {"tracked_build_artifact", "generated"}:
        return "freshness uncertain; verify regeneration source"
    if status == "live":
        return "active line; confirm not stale"
    if status == "unclear":
        return "freshness unclear"
    return "not current-facing"


def dead_content_for(path: str, category: str, status: str) -> str:
    if path == "VERSION":
        return "high risk if value disagrees with README or release docs"
    if status == "historical":
        return "acceptable if clearly archival; misleading only if surfaced as live"
    if path in {
        "build/system_audit/views/file_status.csv",
        "build/system_audit/views/summary.json",
    }:
        return "high confusion risk; prior-generation audit artifact can be mistaken for current ledger"
    if category in {"tracked_build_artifact", "generated"}:
        return "possible dead or duplicated artifact; review needed"
    if status == "transitional" and re.match(r"^(src/.*/goal\d+|scripts/goal\d+)", path):
        return "possible dead scaffolding; verify not imported by live surfaces"
    if re.match(r"^examples/internal/rtdl_goal\d+.*\.py$", path):
        return "internal historical example; misleading if presented as release-facing"
    if category == "example":
        return "possible drift risk; verify runnable status and messaging"
    if category in {"doc", "tutorial", "release_doc"}:
        return "possible stale wording risk; review explicit version claims"
    if status == "unclear":
        return "unknown"
    return "no immediate dead-content signal from path alone"


def action_for(path: str, category: str, status: str) -> str:
    if path == "README.md":
        return "retain and keep aligned with live release surface"
    if path == "VERSION":
        return "revise immediately if it disagrees with the current release tag and front door"
    if path == "requirements.txt":
        return "retain; verify install surface against current runtime requirements"
    if status == "historical":
        return "retain as record; do not present as live spec"
    if category in {"history", "report", "handoff"}:
        return "retain as record; do not present as live spec"
    if category in {"tracked_build_artifact", "generated"}:
        return "review for deletion, relocation, or regeneration policy"
    if status == "transitional" and re.match(r"^(src/.*/goal\d+|scripts/goal\d+)", path):
        return "verify imports and either keep as bounded support or retire as scaffolding"
    if re.match(r"^examples/internal/rtdl_goal\d+.*\.py$", path):
        return "keep only if needed for bounded reproduction; otherwise archive or relabel clearly"
    if category in {"source", "native_source", "test", "script", "schema", "app"}:
        return "retain; audit grouped by subsystem"
    if category in {"doc", "tutorial", "example", "release_doc"}:
        return "retain; audit wording, examples, and version claims"
    if status == "unclear":
        return "inspect and classify explicitly"
    return "inspect further"


def notes_for(path: str, category: str, status: str) -> str:
    notes = []
    if status == "historical":
        notes.append("classified archival from path")
    if category == "tracked_build_artifact":
        notes.append("tracked build output deserves cleanup scrutiny")
    if path in {
        "build/system_audit/views/file_status.csv",
        "build/system_audit/views/summary.json",
    }:
        notes.append("older system-audit snapshot; do not confuse with Goal 409 ledger")
    if category == "generated":
        notes.append("generated content should point back to source generator")
    if category == "release_doc" and "/v0_6/" in path:
        notes.append("belongs to current v0.6.1 release package")
    if path == "README.md":
        notes.append("top-level front door")
    if path == "VERSION":
        notes.append("front-door machine-readable release marker")
    if path == "requirements.txt":
        notes.append("root install surface")
    if status == "transitional" and re.match(r"^(src/.*/goal\d+|scripts/goal\d+)", path):
        notes.append("goal-scoped harness or support file")
    if re.match(r"^examples/internal/rtdl_goal\d+.*\.py$", path):
        notes.append("internal goal-scoped example")
    if status == "unclear":
        notes.append("path alone did not establish live vs historical use")
    return "; ".join(notes)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for relpath in tracked_files():
        category = category_for(relpath)
        status = initial_status(relpath, category)
        rows.append(
            {
                "file_path": relpath,
                "file_category": category,
                "current_role": role_for(relpath, category),
                "status": status,
                "correctness_status": correctness_for(relpath, category, status),
                "content_freshness": freshness_for(relpath, category, status),
                "dead_or_misleading_content": dead_content_for(relpath, category, status),
                "action_recommendation": action_for(relpath, category, status),
                "notes": notes_for(relpath, category, status),
            }
        )
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file_path",
                "file_category",
                "current_role",
                "status",
                "correctness_status",
                "content_freshness",
                "dead_or_misleading_content",
                "action_recommendation",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
