#!/usr/bin/env python3
"""Generate a visitor-facing complete history map for the repository."""

from __future__ import annotations

import csv
import json
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-16"


def _run(args: list[str]) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True)


def _git_files() -> list[str]:
    return [line for line in _run(["git", "ls-files", "--cached", "--others", "--exclude-standard"]).splitlines() if line]


def _git_tags() -> list[str]:
    return [line for line in _run(["git", "tag", "--list", "--sort=creatordate"]).splitlines() if line]


def _classify(path: str) -> str:
    if path == "README.md":
        return "front_page"
    if path.startswith("docs/release_reports/"):
        return "release_report"
    if path.startswith("docs/reports/"):
        return "report_or_review"
    if path.startswith("docs/handoff/"):
        return "ai_handoff"
    if path.startswith("docs/goal_"):
        return "live_goal_doc"
    if path.startswith("history/revisions/"):
        return "structured_history_archive"
    if path.startswith("history/ad_hoc_reviews/"):
        return "ad_hoc_review_or_consensus"
    if path in {"history/revision_dashboard.md", "history/revision_dashboard.html", "history/history.db"}:
        return "history_index"
    if path.startswith("history/"):
        return "history_support"
    if path.startswith("docs/tutorials/") or path == "docs/quick_tutorial.md":
        return "tutorial"
    if path.startswith("docs/features/"):
        return "feature_doc"
    if path.startswith("examples/"):
        return "example"
    if path.startswith("tests/"):
        return "test"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("src/") or path.startswith("include/") or path.startswith("native/"):
        return "source"
    return "other"


def _rounds() -> list[dict[str, Any]]:
    conn = sqlite3.connect(ROOT / "history" / "history.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        select
          r.slug,
          r.title,
          r.started_on,
          r.closed_on,
          r.source_commit,
          r.summary,
          s.version,
          s.status,
          s.gemini_review,
          s.codex_revision,
          s.final_result
        from revision_rounds r
        join revision_round_status s on s.round_id = r.id
        order by r.started_on desc, r.id desc
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def _history_db_counts() -> dict[str, int]:
    conn = sqlite3.connect(ROOT / "history" / "history.db")
    counts = {
        "revision_rounds": conn.execute("select count(*) from revision_rounds").fetchone()[0],
        "archived_files": conn.execute("select count(*) from archived_files").fetchone()[0],
        "external_reports": conn.execute(
            "select count(*) from archived_files where category = 'external_report'"
        ).fetchone()[0],
        "project_snapshots": conn.execute(
            "select count(*) from archived_files where category = 'project_snapshot'"
        ).fetchone()[0],
    }
    conn.close()
    return counts


def build_inventory() -> dict[str, Any]:
    files = _git_files()
    categories = Counter(_classify(path) for path in files)
    rounds = _rounds()
    release_tags = _git_tags()
    report_files = [path for path in files if path.startswith("docs/reports/")]
    ad_hoc = [path for path in files if path.startswith("history/ad_hoc_reviews/")]
    handoffs = [path for path in files if path.startswith("docs/handoff/")]
    metadata_files = [path for path in files if path.startswith("history/revisions/") and path.endswith("/metadata.txt")]
    top_rounds = rounds[:12]
    counts = {
        "tracked_files": len(files),
        "docs_reports": len(report_files),
        "ad_hoc_reviews": len(ad_hoc),
        "handoffs": len(handoffs),
        "revision_metadata_files": len(metadata_files),
        "release_tags": len(release_tags),
        **_history_db_counts(),
    }
    return {
        "goal": 495,
        "date": DATE,
        "repo_root": str(ROOT),
        "counts": counts,
        "categories": dict(sorted(categories.items())),
        "release_tags": release_tags,
        "top_revision_rounds": top_rounds,
        "history_boundaries": [
            "history/ is a public index over repo-preserved evidence, not a verbatim transcript of every chat message.",
            "All tracked docs/reports, handoffs, ad hoc review notes, structured revision rounds, and release packages are discoverable from this map.",
            "Older work is sometimes represented by catch-up revision rounds plus the underlying docs/reports artifacts rather than one directory per micro-goal.",
            "Git history remains the authoritative record for exact code diffs and commits.",
        ],
        "valid": bool(rounds and release_tags and report_files and ad_hoc and metadata_files),
    }


def _csv_rows(files: list[str]) -> list[dict[str, str]]:
    rows = []
    for path in files:
        rows.append({"path": path, "category": _classify(path)})
    return rows


def write_outputs(inventory: dict[str, Any]) -> None:
    reports = ROOT / "docs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    json_path = reports / f"goal495_complete_history_map_{DATE}.json"
    csv_path = reports / f"goal495_complete_history_file_inventory_{DATE}.csv"
    report_path = reports / f"goal495_complete_history_map_{DATE}.md"
    history_path = ROOT / "history" / "COMPLETE_HISTORY.md"
    files = _git_files()

    json_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "category"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(_csv_rows(files))

    top_rows = "\n".join(
        f"| `{row['version']}` | {row['started_on']} | `{row['status']}` | {row['title']} | `{row['final_result']}` | `{row['slug']}` |"
        for row in inventory["top_revision_rounds"]
    )
    tag_rows = "\n".join(f"- `{tag}`" for tag in inventory["release_tags"])
    category_rows = "\n".join(
        f"| `{category}` | {count} |" for category, count in sorted(inventory["categories"].items())
    )

    complete_history = f"""# RTDL Complete History Map

Date: {DATE}
Status: generated

This page answers the question a new visitor will ask: "Where is the full RTDL
history?"

Short answer: the repository now has a complete public map over the preserved
history artifacts, but `history/` is an index and archive, not a verbatim
conversation transcript. The exact code evolution remains in git commits and
tags; the reasoning, reviews, audits, and release evidence are preserved in the
files indexed here.

## What Is Recorded

- Structured revision rounds: `{inventory['counts']['revision_rounds']}`
- Archived files in `history/history.db`: `{inventory['counts']['archived_files']}`
- External report snapshots: `{inventory['counts']['external_reports']}`
- Project snapshots: `{inventory['counts']['project_snapshots']}`
- Tracked `docs/reports/` artifacts: `{inventory['counts']['docs_reports']}`
- Tracked `history/ad_hoc_reviews/` artifacts: `{inventory['counts']['ad_hoc_reviews']}`
- Tracked AI handoff files: `{inventory['counts']['handoffs']}`
- Tracked release tags: `{inventory['counts']['release_tags']}`

## How To Read The History

Use these layers together:

1. Start with `README.md` for the current released surface.
2. Read `docs/README.md` for the public documentation map.
3. Read `docs/release_reports/<version>/` for release statements, support
   matrices, audits, and tag preparation.
4. Read `history/revision_dashboard.md` for the chronological revision-round
   table.
5. Read `history/revisions/<round>/metadata.txt` and its snapshots for a
   specific archived round.
6. Read `history/ad_hoc_reviews/` for standalone Codex/Claude/Gemini consensus
   memos and review notes.
7. Read `docs/reports/` for the full report and review corpus.
8. Use git commits and tags for exact source-code diffs.

## Release Tags

{tag_rows}

## Current Top Revision Rounds

| Version | Date | Status | Round | Result | Archive |
| --- | --- | --- | --- | --- | --- |
{top_rows}

## Tracked File Categories

| Category | Count |
| --- | ---: |
{category_rows}

## Boundaries

- This page does not claim that every chat message or terminal line is
  preserved.
- It does claim that the repo-visible evidence is now discoverable through a
  stable map: release reports, goal reports, external reviews, handoffs,
  consensus notes, structured revision rounds, and git tags/commits.
- Some old periods are represented by catch-up revision rounds plus the
  underlying reports, rather than one revision directory per micro-goal.
- Historical records are not rewritten to look current. Newer repair rounds are
  appended when earlier indexes become stale.

## Machine Artifacts

- JSON inventory: `/Users/rl2025/rtdl_python_only/docs/reports/goal495_complete_history_map_{DATE}.json`
- CSV file inventory: `/Users/rl2025/rtdl_python_only/docs/reports/goal495_complete_history_file_inventory_{DATE}.csv`
- Report: `/Users/rl2025/rtdl_python_only/docs/reports/goal495_complete_history_map_{DATE}.md`
"""

    report = f"""# Goal 495: Complete History Map

Date: {DATE}
Status: generated
Valid: `{inventory['valid']}`

## Summary

Goal495 adds a visitor-facing answer to whether RTDL has a full recorded
history.

The answer is now explicit:

- `history/` is the public structured index and archive.
- `docs/reports/` contains the broad report/review corpus.
- `history/ad_hoc_reviews/` contains standalone consensus and review memos.
- `docs/handoff/` preserves AI review requests.
- git commits and tags are the exact code-change history.

## Counts

- tracked files: `{inventory['counts']['tracked_files']}`
- structured revision rounds: `{inventory['counts']['revision_rounds']}`
- archived files in `history/history.db`: `{inventory['counts']['archived_files']}`
- tracked `docs/reports/` artifacts: `{inventory['counts']['docs_reports']}`
- tracked `history/ad_hoc_reviews/` artifacts: `{inventory['counts']['ad_hoc_reviews']}`
- tracked handoff files: `{inventory['counts']['handoffs']}`
- release tags: `{inventory['counts']['release_tags']}`

## Outputs

- `/Users/rl2025/rtdl_python_only/history/COMPLETE_HISTORY.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal495_complete_history_map_{DATE}.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal495_complete_history_file_inventory_{DATE}.csv`
"""

    history_path.write_text(complete_history, encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")


def main() -> int:
    inventory = build_inventory()
    write_outputs(inventory)
    print(json.dumps({"valid": inventory["valid"], "counts": inventory["counts"]}, sort_keys=True))
    return 0 if inventory["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
