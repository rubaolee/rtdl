#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-04"
GOAL = "Goal1249 v1.0 release audit"

PACKAGE_FILES = (
    "README.md",
    "release_statement.md",
    "support_matrix.md",
    "audit_report.md",
    "tag_preparation.md",
)

REQUIRED_REPORTS = (
    "docs/reports/goal1246_two_ai_front_page_diet_consensus_2026-05-04.md",
    "docs/reports/goal1247_two_ai_quick_tutorial_final_polish_consensus_2026-05-04.md",
    "docs/reports/goal1248_gemini_v1_0_release_candidate_package_review_2026-05-04.md",
    "docs/reports/goal1248_gemini_v1_0_release_candidate_package_rereview_2026-05-04.md",
    "docs/reports/goal1248_two_ai_v1_0_release_candidate_package_consensus_2026-05-04.md",
)

REVIEWED_PHASES = (
    "service_coverage_gaps / prepared_gap_summary",
    "event_hotspot_screening / prepared_count_summary",
    "outlier_detection / prepared_fixed_radius_density_summary",
    "dbscan_clustering / prepared_fixed_radius_core_flags",
    "robot_collision_screening / prepared_pose_flags",
    "facility_knn_assignment / coverage_threshold_prepared_recentered",
    "road_hazard_screening / prepared_native_compact_summary_40k",
    "segment_polygon_hitcount / segment_polygon_hitcount_native_experimental",
    "segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate",
    "ann_candidate_search / candidate_threshold_prepared",
    "barnes_hut_force_app / node_coverage_prepared_rich",
    "hausdorff_distance / directed_threshold_prepared",
)

FORBIDDEN_PHRASES = (
    "broad whole-app speedup claim is allowed",
    "all-app NVIDIA RT-core speedup claim is allowed",
    "broad or whole-app public speedup claim authorized: `True`",
)


def _read(rel_path: str) -> str:
    path = ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _package_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in PACKAGE_FILES:
        rel_path = f"docs/release_reports/v1_0/{name}"
        text = _read(rel_path)
        missing_required = [
            phrase
            for phrase in (
                "Status: released as `v1.0`",
                "v1.0",
            )
            if phrase not in text
        ]
        forbidden_hits = [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
        rows.append(
            {
                "path": rel_path,
                "exists": bool(text),
                "missing_required_phrases": missing_required,
                "forbidden_phrases": forbidden_hits,
                "status": "ok" if text and not missing_required and not forbidden_hits else "failure",
            }
        )
    return rows


def _support_matrix_state() -> dict[str, Any]:
    support = _read("docs/release_reports/v1_0/support_matrix.md")
    status = _read("docs/v1_0_rtx_app_status.md")
    support_phases = re.findall(r"^\| `([^`]+)` \| reviewed \| yes \|", support, flags=re.MULTILINE)
    status_phases = re.findall(r"^\| `([^`]+)` \| `[^`]+` \| `[^`]+` \|", status, flags=re.MULTILINE)
    return {
        "support_reviewed_phases": support_phases,
        "status_reviewed_phases": status_phases,
        "expected_reviewed_phases": list(REVIEWED_PHASES),
        "support_matches_expected": support_phases == list(REVIEWED_PHASES),
        "status_matches_expected": status_phases == list(REVIEWED_PHASES),
        "support_reviewed_count": len(support_phases),
        "status_reviewed_count": len(status_phases),
        "blocked_rows_present": all(
            phrase in support
            for phrase in (
                "`graph_analytics` | blocked",
                "`polygon_pair_overlap_area_rows` | blocked",
            )
        ),
        "not_reviewed_rows_present": all(
            phrase in support
            for phrase in (
                "`database_analytics` | not reviewed",
                "`polygon_set_jaccard` | not reviewed",
            )
        ),
        "non_nvidia_rows_present": all(
            phrase in support
            for phrase in (
                "`apple_rt_demo` | non-NVIDIA target",
                "`hiprt_ray_triangle_hitcount` | non-NVIDIA target",
            )
        ),
    }


def build_audit() -> dict[str, Any]:
    package_rows = _package_rows()
    support_state = _support_matrix_state()
    missing_reports = [path for path in REQUIRED_REPORTS if not (ROOT / path).exists()]
    readme = _read("docs/README.md")
    version = _read("VERSION").strip()
    package_ok = all(row["status"] == "ok" for row in package_rows)
    support_ok = (
        support_state["support_matches_expected"]
        and support_state["status_matches_expected"]
        and support_state["support_reviewed_count"] == 12
        and support_state["status_reviewed_count"] == 12
        and support_state["blocked_rows_present"]
        and support_state["not_reviewed_rows_present"]
        and support_state["non_nvidia_rows_present"]
    )
    release_marker_ok = version == "v1.0" and "The current released version is `v1.0`." in readme
    docs_index_ok = all(
        phrase in readme
        for phrase in (
            "[v1.0 Release Package](release_reports/v1_0/README.md)",
            "[v1.0 Support Matrix](release_reports/v1_0/support_matrix.md)",
            "[v0.9.8 Release Package](release_reports/v0_9_8/README.md)",
        )
    )
    reports_ok = not missing_reports
    valid = package_ok and support_ok and release_marker_ok and docs_index_ok and reports_ok
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": valid,
        "recommendation": (
            "v1_0_release_action_complete"
            if valid
            else "blocked_pending_v1_0_release_action_fixes"
        ),
        "pod_needed_now": False,
        "pod_decision": (
            "No pod is required for the v1.0 release-candidate package audit. "
            "Use a pod only if the release scope changes to promote blocked or "
            "not-reviewed rows into new public RTX speedup wording."
        ),
        "release_marker": version,
        "release_marker_ok": release_marker_ok,
        "docs_index_ok": docs_index_ok,
        "reports_ok": reports_ok,
        "missing_reports": missing_reports,
        "package_ok": package_ok,
        "package_rows": package_rows,
        "support_ok": support_ok,
        "support_state": support_state,
        "boundary": (
            "This audit covers the released v1.0 package and live version "
            "marker. It does not authorize new public speedup wording beyond "
            "the reviewed bounded sub-path rows."
        ),
        "next_steps": [
            "Run the release-surface documentation test gate.",
            "Run focused release-action tests.",
            "Commit the release action.",
            "Tag the release-action commit.",
        ],
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1249 v1.0 Release Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- recommendation: `{payload['recommendation']}`",
        f"- pod needed now: `{payload['pod_needed_now']}`",
        f"- release marker: `{payload['release_marker']}`",
        f"- package ok: `{payload['package_ok']}`",
        f"- support matrix ok: `{payload['support_ok']}`",
        f"- docs index ok: `{payload['docs_index_ok']}`",
        f"- reports ok: `{payload['reports_ok']}`",
        "",
        "## Reviewed RTX Phase Count",
        "",
        f"- support matrix reviewed rows: `{payload['support_state']['support_reviewed_count']}`",
        f"- status page reviewed rows: `{payload['support_state']['status_reviewed_count']}`",
        "- expected reviewed rows: `12`",
        "",
        "## Package Files",
        "",
        "| Path | Status | Missing required phrases | Forbidden phrases |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in payload["package_rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | "
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
    parser = argparse.ArgumentParser(description="Audit v1.0 release package readiness.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1249_v1_0_release_candidate_audit_2026-05-04.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1249_v1_0_release_candidate_audit_2026-05-04.md",
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
