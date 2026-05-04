#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-04"
GOAL = "Goal1250 v1.0 release-surface documentation audit"

SURFACE_REQUIRED_PHRASES: dict[str, tuple[str, ...]] = {
    "README.md": (
        "The current released version is `v0.9.8`.",
        "## v1.0 Direction",
        "v1.0 proof machinery, not the final architecture",
        "v1.5 is planned to replace app-specific engine customization",
        "v2.0 targets broader end-to-end performance",
        "Reviewed rows are bounded public sub-path wording",
        "[Public Documentation Map](docs/public_documentation_map.md)",
        "[Quick Tutorial](docs/quick_tutorial.md)",
        "[App And Example Quickstart](docs/app_example_quickstart.md)",
        "[Performance Model](docs/performance_model.md)",
    ),
    "docs/README.md": (
        "The current released version is `v0.9.8`.",
        "Public Surfaces",
        "Front page",
        "Tutorials",
        "Apps and examples",
        "Architecture/model/IR/performance",
        "v1.0 is a foundation release line",
        "v1.5 should replace app-specific native continuations",
        "v2.0 is the broader end-to-end performance target",
        "[v1.0 Release Candidate Package](release_reports/v1_0/README.md)",
    ),
    "docs/public_documentation_map.md": (
        "Current Public Surfaces",
        "Front page and project promise",
        "Tutorials",
        "Apps",
        "Examples",
        "Architecture",
        "Programming model",
        "IR and lowering",
        "Performance",
        "v1.0 is a foundation release line",
        "v1.5 should replace app-specific native continuations",
        "v2.0 is the real broader performance target",
    ),
    "docs/quick_tutorial.md": (
        "NVIDIA RT-core claim note",
        "`--backend optix` selects an OptiX-capable path",
        "not by itself a",
        "NVIDIA RT-core acceleration claim",
        "`ray_triangle_any_hit`",
        "`visibility_rows`",
        "`reduce_rows`",
    ),
    "docs/tutorials/README.md": (
        "Ray/Triangle Any-Hit Example",
        "Visibility Rows Example",
        "Reduce Rows Example",
        "`ray_triangle_any_hit`",
        "`visibility_rows`",
        "`reduce_rows`",
    ),
    "docs/app_example_quickstart.md": (
        "First Three Commands",
        "Choose An App",
        "RTX Rule For App Runs",
        "Recommended v1.0 Demo Path",
        "v1.0 includes app-specific native continuations",
        "intentional proof machinery",
        "--backend optix is not a public NVIDIA RT-core speedup claim",
        "Only claim the exact prepared/native sub-path",
    ),
    "docs/application_catalog.md": (
        "--require-rt-core",
        "is not by itself a NVIDIA RT-core claim",
        "v1.0 RTX App Status",
        "whole-app speedup",
        "OptiX slower than Embree",
        "Service coverage gaps",
        "Facility KNN assignment",
        "Barnes-Hut force approximation",
    ),
    "docs/v1_0_app_acceleration_inventory.md": (
        "Status: current-main v1.0 documentation aid.",
        "not a release authorization",
        "whole-app speedup table",
        "The v1.0 architecture intentionally contains app-specific native continuations.",
        "v1.5 should replace these",
        "app-specific continuations with reviewed generic traversal-plus-reduction",
        "v1.5 Replacement Target",
        "ANY_HIT",
        "COUNT_HITS",
        "REDUCE_FLOAT",
        "REDUCE_INT",
    ),
    "docs/current_architecture.md": (
        "## v1.0 Lens",
        "Some app paths use app-specific native continuations",
        "not the final engine architecture",
        "v1.5 should replace app-specific continuation code",
        "v2.0 is the broader end-to-end performance target",
        "`ray_triangle_any_hit`",
        "`visibility_rows`",
        "`reduce_rows`",
    ),
    "docs/rtdl/itre_app_model.md": (
        "Python",
        "CPU/oracle",
        "Embree",
        "OptiX",
        "Vulkan",
    ),
    "docs/rtdl/ir_and_lowering.md": (
        "CompiledKernel",
        "RTExecutionPlan",
        "rtdl-plan-v1alpha1",
        "Current lowering is predicate-specific",
        "ANY_HIT",
        "COUNT_HITS",
        "REDUCE_FLOAT",
        "REDUCE_INT",
        "COLLECT_K_BOUNDED",
    ),
    "docs/performance_model.md": (
        "Python is the authoring/control plane",
        "Only level 4 is a public speedup claim",
        "Raw/prepared/native summary paths are the serious performance path",
        "v1.0 still uses app-specific native continuations",
        "v2.0 is the broader performance target",
        "RTDL accelerates <exact prepared/native sub-path>",
    ),
    "docs/v1_0_rtx_app_status.md": (
        "reviewed public RTX sub-path wording rows: `12`",
        "broad or whole-app public speedup claim authorized: `False`",
        "These are not whole-app, default-mode",
        "Goal1224 resolves the remaining graph, polygon-pair, and Hausdorff rows",
        "graph and polygon-pair stay blocked",
        "Forbidden Wording",
    ),
    "docs/release_reports/v1_0/README.md": (
        "Status: draft release candidate for `v1.0`; not released.",
        "The current released version remains `v0.9.8`",
        "`12` reviewed bounded NVIDIA RTX public wording rows",
        "Final v1.0 release still needs",
    ),
    "docs/release_reports/v1_0/release_statement.md": (
        "Status: draft release candidate for `v1.0`; not released.",
        "The current released version remains `v0.9.8`.",
        "foundation release for",
        "What This Release Candidate Must Not Claim",
    ),
    "docs/release_reports/v1_0/support_matrix.md": (
        "Status: draft release candidate for `v1.0`; not released.",
        "Reviewed bounded NVIDIA RTX public wording rows: `12`.",
        "Blocked, Not-Reviewed, Or Non-NVIDIA Rows",
        "v1.5 And v2.0 Handoff",
    ),
    "docs/release_reports/v1_0/audit_report.md": (
        "Status: draft release candidate for `v1.0`; not released.",
        "This audit checks whether current main is ready",
        "not yet a released v1.0",
        "No immediate pod is required",
    ),
    "docs/release_reports/v1_0/tag_preparation.md": (
        "Status: draft release candidate for `v1.0`; not released.",
        "Do not run these until final authorization is saved",
        "This file is tag preparation only.",
        "not a release authorization",
    ),
}

FORBIDDEN_RELEASE_SURFACE_PHRASES = (
    "Status: released as `v1.0`",
    "The current released version is `v1.0`",
    "current released version: `v1.0`",
    "broad or whole-app public speedup claim authorized: `True`",
    "all apps now have public RTX speedup wording",
    "app-specific native continuations are already removed in v1.0",
)


def _read(relative: str) -> str:
    path = ROOT / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _surface_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel_path, required in SURFACE_REQUIRED_PHRASES.items():
        text = _read(rel_path)
        missing = [phrase for phrase in required if phrase not in text]
        forbidden = [phrase for phrase in FORBIDDEN_RELEASE_SURFACE_PHRASES if phrase in text]
        rows.append(
            {
                "path": rel_path,
                "exists": bool(text),
                "missing_required_phrases": missing,
                "forbidden_phrases": forbidden,
                "line_count": len(text.splitlines()) if text else 0,
                "status": "ok" if text and not missing and not forbidden else "failure",
            }
        )
    return rows


def build_audit() -> dict[str, Any]:
    rows = _surface_rows()
    failures = [row for row in rows if row["status"] != "ok"]
    version = _read("VERSION").strip()
    version_ok = version == "v0.9.8"
    valid = not failures and version_ok
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": valid,
        "recommendation": (
            "v1_0_release_surface_ready_for_full_local_discovery"
            if valid
            else "blocked_pending_release_surface_doc_fixes"
        ),
        "version": version,
        "version_ok": version_ok,
        "surface_count": len(rows),
        "failure_count": len(failures),
        "rows": rows,
        "pod_needed_now": False,
        "pod_decision": (
            "No pod is required for this release-surface documentation gate. "
            "Use a pod only if new public speedup wording is added or existing "
            "blocked/not-reviewed RTX rows are promoted."
        ),
        "boundary": (
            "This is a documentation release-surface audit. It does not release "
            "v1.0, update VERSION, authorize a tag, or authorize new performance "
            "claims."
        ),
        "next_steps": [
            "Run full local discovery or an approved release-equivalent gate.",
            "Seek final external review and final authorization.",
            "Update VERSION and tag only after final authorization.",
        ],
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1250 v1.0 Release-Surface Documentation Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- recommendation: `{payload['recommendation']}`",
        f"- version: `{payload['version']}`",
        f"- version ok: `{payload['version_ok']}`",
        f"- surface count: `{payload['surface_count']}`",
        f"- failure count: `{payload['failure_count']}`",
        f"- pod needed now: `{payload['pod_needed_now']}`",
        "",
        "## Surface Rows",
        "",
        "| Path | Status | Lines | Missing required phrases | Forbidden phrases |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | `{row['line_count']}` | "
            f"`{len(row['missing_required_phrases'])}` | `{len(row['forbidden_phrases'])}` |"
        )
    lines.extend(
        [
            "",
            "## Pod Decision",
            "",
            payload["pod_decision"],
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
            "## Next Steps",
            "",
        ]
    )
    for step in payload["next_steps"]:
        lines.append(f"- {step}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit v1.0 release-surface documentation.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1250_v1_0_release_surface_doc_audit_2026-05-04.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1250_v1_0_release_surface_doc_audit_2026-05-04.md",
    )
    args = parser.parse_args()
    payload = build_audit()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    (ROOT / args.output_md).write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
