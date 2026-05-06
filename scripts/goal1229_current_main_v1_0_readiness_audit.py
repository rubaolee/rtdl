#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


GOAL = "Goal1229 current-main v1.0 readiness audit"
DATE = "2026-05-03"

PUBLIC_DOCS = (
    "README.md",
    "docs/README.md",
    "docs/application_catalog.md",
    "docs/rtdl_feature_guide.md",
    "docs/release_facing_examples.md",
    "docs/app_engine_support_matrix.md",
    "docs/v1_0_rtx_app_status.md",
)

REQUIRED_REPORTS = (
    "docs/reports/goal1224_two_ai_consensus_2026-05-01.md",
    "docs/reports/goal1227_two_ai_consensus_2026-05-01.md",
    "docs/reports/goal1228_two_ai_consensus_2026-05-03.md",
    "docs/reports/goal1228_gemini_v1_0_positioning_docs_review_2026-05-03.md",
    "docs/reports/goal1228_v1_0_positioning_and_engine_customization_plan_2026-05-03.md",
    "docs/reports/goal1263_three_ai_consensus_polygon_pair_v1_1_2026-05-04.md",
)

STALE_CURRENT_MAIN_PHRASES = (
    "11 reviewed RTX app rows",
    "11 reviewed sub-path rows",
    "Current reviewed public wording rows after Goal1208",
    "road-hazard detection as the only newly promoted",
    "bounded public RTX sub-path wording after Goal1146 and Goal1208",
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _public_wording_state() -> dict[str, Any]:
    rows = rt.rtx_public_wording_matrix()
    by_status: dict[str, list[str]] = {
        "public_wording_reviewed": [],
        "public_wording_blocked": [],
        "public_wording_not_reviewed": [],
        "not_nvidia_public_wording_target": [],
    }
    for app, row in rows.items():
        by_status[row.status].append(app)
    return {
        "reviewed": sorted(by_status["public_wording_reviewed"]),
        "blocked": sorted(by_status["public_wording_blocked"]),
        "not_reviewed": sorted(by_status["public_wording_not_reviewed"]),
        "not_nvidia_target": sorted(by_status["not_nvidia_public_wording_target"]),
    }


def _surface_doc_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in PUBLIC_DOCS:
        text = _read(path)
        stale_hits = [phrase for phrase in STALE_CURRENT_MAIN_PHRASES if phrase in text]
        rows.append(
            {
                "path": path,
                "exists": (ROOT / path).exists(),
                "mentions_13_reviewed": "13 reviewed" in text,
                "mentions_goal1224": "Goal1224" in text,
                "mentions_goal1263": "Goal1263" in text,
                "stale_current_main_phrases": stale_hits,
            }
        )
    return rows


def build_audit() -> dict[str, Any]:
    public_state = _public_wording_state()
    surface_rows = _surface_doc_rows()
    missing_reports = [path for path in REQUIRED_REPORTS if not (ROOT / path).exists()]
    readme = _read("README.md")
    status_page = _read("docs/v1_0_rtx_app_status.md")
    current_main_positioning_ok = all(
        phrase in readme
        for phrase in (
            "## Roadmap Boundary",
            "v1.0 proof machinery, not the final architecture",
            "v1.5 is the released standalone Embree+OptiX",
            "v2.0 targets broader\nend-to-end performance",
        )
    )
    public_docs_ok = all(not row["stale_current_main_phrases"] for row in surface_rows)
    status_page_ok = all(
        phrase in status_page
        for phrase in (
            "reviewed public RTX sub-path wording rows: `13`",
            "Goal1263 promotes bounded polygon-pair wording",
            "Graph remains blocked",
        )
    )
    expected_reviewed_count = 13
    expected_blocked = ["graph_analytics"]
    expected_not_reviewed = ["database_analytics", "polygon_set_jaccard"]
    expected_non_targets = ["apple_rt_demo", "hiprt_ray_triangle_hitcount"]
    public_state_ok = (
        len(public_state["reviewed"]) == expected_reviewed_count
        and public_state["blocked"] == expected_blocked
        and public_state["not_reviewed"] == expected_not_reviewed
        and public_state["not_nvidia_target"] == expected_non_targets
    )
    valid = (
        public_state_ok
        and public_docs_ok
        and status_page_ok
        and current_main_positioning_ok
        and not missing_reports
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": valid,
        "boundary": (
            "This is a current-main v1.0 readiness audit. It does not move the "
            "v0.9.8 release tag and does not authorize a new public release."
        ),
        "public_wording_state": public_state,
        "expected": {
            "reviewed_public_wording_count": expected_reviewed_count,
            "blocked_public_speedup_wording": expected_blocked,
            "not_reviewed_public_speedup_wording": expected_not_reviewed,
            "not_nvidia_public_wording_targets": expected_non_targets,
        },
        "checks": {
            "public_state_ok": public_state_ok,
            "public_docs_ok": public_docs_ok,
            "status_page_ok": status_page_ok,
            "current_main_positioning_ok": current_main_positioning_ok,
            "required_reports_ok": not missing_reports,
        },
        "surface_rows": surface_rows,
        "missing_reports": missing_reports,
        "next_v1_0_work": [
            "Keep v0.9.8 release package historical and separate from current-main v1.0 docs.",
            "Keep current v1.5 front-page and app documentation aligned with selected RT sub-paths and native continuations.",
            "Do not move or retag v1.0 or v1.5 without explicit release authorization.",
        ],
    }


def to_markdown(payload: dict[str, Any]) -> str:
    state = payload["public_wording_state"]
    expected = payload["expected"]
    lines = [
        "# Goal1229 Current-Main v1.0 Readiness Audit",
        "",
        f"Date: {payload['date']}",
        "",
        f"Status: {'valid' if payload['valid'] else 'blocked'}",
        "",
        payload["boundary"],
        "",
        "## Public Wording State",
        "",
        f"- reviewed public RTX sub-path wording rows: `{len(state['reviewed'])}`",
        f"- expected reviewed rows: `{expected['reviewed_public_wording_count']}`",
        f"- blocked public speedup wording: `{', '.join(state['blocked'])}`",
        f"- not-reviewed public speedup wording: `{', '.join(state['not_reviewed'])}`",
        f"- non-NVIDIA public wording targets: `{', '.join(state['not_nvidia_target'])}`",
        "",
        "## Checks",
        "",
    ]
    for name, value in payload["checks"].items():
        lines.append(f"- {name}: `{value}`")
    lines.extend(["", "## Surface Docs", ""])
    for row in payload["surface_rows"]:
        stale = ", ".join(row["stale_current_main_phrases"]) or "none"
        lines.append(
            f"- `{row['path']}`: mentions_13_reviewed=`{row['mentions_13_reviewed']}`, "
            f"mentions_goal1224=`{row['mentions_goal1224']}`, "
            f"mentions_goal1263=`{row['mentions_goal1263']}`, stale_current_main_phrases=`{stale}`"
        )
    lines.extend(["", "## Next v1.0 Work", ""])
    for item in payload["next_v1_0_work"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()
    payload = build_audit()
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
