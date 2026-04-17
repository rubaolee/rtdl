#!/usr/bin/env python3
"""Audit the post-v0.7.0 public docs/tutorial/example surface for 3C quality."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-16"

PUBLIC_FILES = [
    "README.md",
    "docs/README.md",
    "docs/quick_tutorial.md",
    "docs/release_facing_examples.md",
    "docs/tutorials/README.md",
    "docs/tutorials/hello_world.md",
    "docs/tutorials/sorting_demo.md",
    "docs/tutorials/segment_polygon_workloads.md",
    "docs/tutorials/nearest_neighbor_workloads.md",
    "docs/tutorials/graph_workloads.md",
    "docs/tutorials/db_workloads.md",
    "docs/tutorials/rendering_and_visual_demos.md",
    "docs/features/README.md",
    "docs/features/db_workloads/README.md",
    "docs/rtdl_feature_guide.md",
    "docs/current_milestone_qa.md",
    "docs/release_reports/v0_7/README.md",
    "docs/release_reports/v0_7/release_statement.md",
    "docs/release_reports/v0_7/support_matrix.md",
    "docs/release_reports/v0_7/audit_report.md",
    "docs/release_reports/v0_7/tag_preparation.md",
    "examples/README.md",
]

REQUIRED_TOKENS = {
    "README.md": [
        "current released version: `v0.7.0`",
        "bounded `v0.7.0` DB release surface",
        "RTDL is not a DBMS",
        "rtdl_v0_7_db_app_demo.py",
        "rtdl_v0_7_db_kernel_app_demo.py",
    ],
    "docs/README.md": [
        "current released version is `v0.7.0`",
        "current `main` carries the released bounded `v0.7.0` DB line",
        "v0.7 Release Statement",
    ],
    "docs/quick_tutorial.md": [
        "Optional bounded `v0.7.0` DB release examples",
        "not a database system",
        "rtdl_v0_7_db_app_demo.py",
    ],
    "docs/release_facing_examples.md": [
        "released bounded `v0.7.0` DB line",
        "current tagged mainline release",
        "Goal 452",
    ],
    "docs/tutorials/README.md": [
        "Released `v0.7.0` bounded DB kernels",
        "Database Workloads",
    ],
    "docs/tutorials/db_workloads.md": [
        "`v0.7.0` release line",
        "not a DBMS",
        "Goal 492 records",
        "current tagged mainline release",
    ],
    "docs/features/README.md": [
        "released bounded `v0.7.0` line",
    ],
    "docs/features/db_workloads/README.md": [
        "Status: released bounded `v0.7.0` line on `main`.",
        "not a DBMS",
        "Goal 452",
    ],
    "docs/rtdl_feature_guide.md": [
        "released bounded `v0.7.0` package",
        "conjunctive_scan",
        "arbitrary SQL execution or DBMS behavior",
    ],
    "examples/README.md": [
        "rtdl_v0_7_db_app_demo.py",
        "rtdl_v0_7_db_kernel_app_demo.py",
        "PostgreSQL remains a Linux correctness/performance anchor",
    ],
    "docs/release_reports/v0_7/README.md": [
        "RTDL v0.7 Release Package",
        "released tag: `v0.7.0`",
        "current mainline: `main`",
    ],
    "docs/release_reports/v0_7/release_statement.md": [
        "released bounded DB line",
        "now carried\non `main`",
        "`v0.7.0`: released bounded DB line",
    ],
    "docs/release_reports/v0_7/support_matrix.md": [
        "released bounded DB line",
        "Linux Repeated-Query Performance Gate",
        "PostgreSQL is not a public example backend flag.",
    ],
    "docs/release_reports/v0_7/audit_report.md": [
        "released bounded DB package",
        "release package is coherent, but still bounded",
    ],
    "docs/release_reports/v0_7/tag_preparation.md": [
        "Status: release authorized",
        "fast-forwarded to `main`",
        "Released as `v0.7.0`",
    ],
}

STALE_PATTERNS = [
    "current released version: `v0.6.1`",
    "current released version is `v0.6.1`",
    "current `main` carries the released `v0.6.1` line",
    "active `v0.7` bounded DB development line",
    "`v0.7` development line",
    "`v0.7` Development Line",
    "not the last tagged mainline release",
    "not the repository's last tagged mainline release",
    "this is still the active `v0.7` branch line",
    "Do not tag `v0.7` yet",
    "# RTDL v0.7 Branch Package",
    "Branch Statement",
    "Do not merge to",
    "active bounded DB branch line",
    "`v0.7`: active bounded DB branch line",
    "current branch line has already replaced",
]


def _git_diff_check() -> dict[str, Any]:
    proc = subprocess.run(["git", "diff", "--check"], cwd=ROOT, text=True, capture_output=True)
    return {
        "valid": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _category(path: str) -> str:
    if path == "README.md":
        return "front_page"
    if path.startswith("docs/tutorials/") or path == "docs/quick_tutorial.md":
        return "tutorial"
    if path.startswith("examples/"):
        return "example_index"
    if path.startswith("docs/features/"):
        return "feature_doc"
    if path.startswith("docs/release_reports/v0_7/"):
        return "release_report"
    return "doc_index"


def _markdown_links(text: str) -> list[str]:
    links = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).split("#", 1)[0]
        if target and not re.match(r"^[a-z]+://", target) and not target.startswith("mailto:"):
            links.append(target)
    return links


def _link_errors(rel: str, text: str) -> list[str]:
    base = (ROOT / rel).parent
    errors = []
    for target in _markdown_links(text):
        if target.startswith("/"):
            candidate = ROOT / target.lstrip("/")
        else:
            candidate = (base / target).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            continue
        if not candidate.exists():
            errors.append(target)
    return sorted(set(errors))


def _command_path_errors(text: str) -> list[str]:
    errors = []
    for match in re.finditer(r"(?:python|python3)\s+([A-Za-z0-9_./\\-]+\.py)", text):
        target = match.group(1).replace("\\", "/")
        if not (ROOT / target).exists():
            errors.append(target)
    return sorted(set(errors))


def _run_command(command: str) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=ROOT, shell=True, text=True, capture_output=True)
    return {
        "command": command,
        "valid": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-400:],
        "stderr_tail": proc.stderr[-400:],
    }


def _example_checks() -> list[dict[str, Any]]:
    commands = [
        "PYTHONPATH=src:. python3 examples/rtdl_hello_world.py",
        "PYTHONPATH=src:. python3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 4",
        "PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 4",
        "PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py",
        "PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py",
        "PYTHONPATH=src:. python3 examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_knn_rows.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_graph_bfs.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_graph_triangle_count.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_db_grouped_count.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_db_grouped_sum.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_app_demo.py --backend auto",
        "PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_kernel_app_demo.py --backend auto",
        "PYTHONPATH=src:. python3 examples/rtdl_sales_risk_screening.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 examples/rtdl_road_hazard_screening.py --backend cpu_python_reference",
        "PYTHONPATH=src:. python3 scripts/rtdl_sorting_demo.py --backend cpu_python_reference 3 1 4 1 5 0 2 5",
    ]
    return [_run_command(command) for command in commands]


def build_audit(run_examples: bool) -> dict[str, Any]:
    rows = []
    for rel in PUBLIC_FILES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        missing = [token for token in REQUIRED_TOKENS.get(rel, []) if token not in text]
        stale = [pattern for pattern in STALE_PATTERNS if pattern in text]
        link_errors = _link_errors(rel, text) if path.exists() and rel.endswith(".md") else []
        command_path_errors = _command_path_errors(text) if path.exists() else []
        correct = path.exists() and not missing and not stale and not command_path_errors
        consistent = not stale and not link_errors
        comprehensive = path.exists() and len(text.strip()) > 0
        rows.append(
            {
                "path": rel,
                "category": _category(rel),
                "exists": path.exists(),
                "correct": correct,
                "consistent": consistent,
                "comprehensive": comprehensive,
                "missing_required_tokens": missing,
                "stale_patterns": stale,
                "missing_links": link_errors,
                "missing_command_paths": command_path_errors,
                "valid": correct and consistent and comprehensive,
            }
        )
    example_checks = _example_checks() if run_examples else []
    diff_check = _git_diff_check()
    valid = all(row["valid"] for row in rows) and all(row["valid"] for row in example_checks) and diff_check["valid"]
    return {
        "goal": 493,
        "date": DATE,
        "repo_root": str(ROOT),
        "public_files": rows,
        "invalid_public_files": [row for row in rows if not row["valid"]],
        "example_execution_checks": example_checks,
        "invalid_example_execution_checks": [row for row in example_checks if not row["valid"]],
        "git_diff_check": diff_check,
        "valid": valid,
    }


def write_outputs(audit: dict[str, Any]) -> None:
    reports = ROOT / "docs" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    json_path = reports / f"goal493_public_surface_3c_audit_{DATE}.json"
    csv_path = reports / f"goal493_public_surface_3c_ledger_{DATE}.csv"
    md_path = reports / f"goal493_public_surface_3c_audit_{DATE}.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            lineterminator="\n",
            fieldnames=[
                "path",
                "category",
                "exists",
                "correct",
                "consistent",
                "comprehensive",
                "valid",
                "missing_required_tokens",
                "stale_patterns",
                "missing_links",
                "missing_command_paths",
            ],
        )
        writer.writeheader()
        for row in audit["public_files"]:
            out = row.copy()
            for key in ("missing_required_tokens", "stale_patterns", "missing_links", "missing_command_paths"):
                out[key] = "; ".join(out[key])
            writer.writerow(out)
    lines = [
        "# Goal 493: Public Surface 3C Audit",
        "",
        f"Date: {DATE}",
        "Author: Codex",
        "Status: generated post-v0.7.0 public-surface 3C audit",
        "",
        "## Scope",
        "",
        "This audit checks the front page, docs index, tutorials, feature index, v0.7 release reports, and public examples index for:",
        "",
        "- Correctness: required current-state claims are present and command paths exist.",
        "- Consistency: stale pre-release wording and broken local links are absent.",
        "- Comprehensiveness: each public file exists and has non-empty content.",
        "",
        "## Results",
        "",
        f"- Public files checked: `{len(audit['public_files'])}`",
        f"- Invalid public files: `{len(audit['invalid_public_files'])}`",
        f"- Example execution checks: `{len(audit['example_execution_checks'])}`",
        f"- Invalid example execution checks: `{len(audit['invalid_example_execution_checks'])}`",
        f"- `git diff --check` valid: `{audit['git_diff_check']['valid']}`",
        f"- Overall valid: `{audit['valid']}`",
        "",
        "## Artifacts",
        "",
        f"- JSON: `{json_path}`",
        f"- CSV ledger: `{csv_path}`",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    audit = build_audit(run_examples=True)
    write_outputs(audit)
    print(
        json.dumps(
            {
                "valid": audit["valid"],
                "invalid_public_files": len(audit["invalid_public_files"]),
                "invalid_example_execution_checks": len(audit["invalid_example_execution_checks"]),
                "diff_valid": audit["git_diff_check"]["valid"],
            },
            sort_keys=True,
        )
    )
    return 0 if audit["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
