#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1196 public wording decision packet after Goal1195"
DEFAULT_INTAKE = ROOT / "docs" / "reports" / "goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.json"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal1196_public_wording_decision_packet_2026-04-30.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal1196_public_wording_decision_packet_2026-04-30.md"

MIN_PUBLIC_RATIO = 1.2

APP_WORDING: dict[str, dict[str, str]] = {
    "database_analytics": {
        "path": "prepared_db_compact_summary",
        "blocked_wording": "No positive public RTX speedup wording is authorized for database_analytics from Goal1195 evidence.",
        "boundary": "Prepared compact-summary traversal/filter/grouping is evidence-ready, but the measured OptiX phase is slower than Embree; no SQL-engine, DBMS, full-row, dashboard, or whole-app speedup claim is allowed.",
    },
    "graph_analytics": {
        "path": "visibility_edges_prepared_anyhit",
        "blocked_wording": "No positive public RTX speedup wording is authorized for graph_analytics from Goal1195 evidence.",
        "boundary": "Bounded visibility/graph-ray RT traversal is evidence-ready, but the measured OptiX phase is slower than Embree; no BFS, triangle-count, graph-system, shortest-path, distributed-analytics, or whole-app speedup claim is allowed.",
    },
    "road_hazard_screening": {
        "path": "prepared_native_road_hazard_summary",
        "reviewed_wording": "RTDL's prepared native road-hazard summary RTX sub-path measured 0.103539 s and 4.01x versus the reviewed same-contract Embree sub-path.",
        "boundary": "Only the prepared native segment/polygon road-hazard summary traversal and threshold-count continuation are covered; default app behavior, full GIS/routing, row materialization, Python setup, and whole-app speedup remain outside this wording.",
    },
    "polygon_pair_overlap_area_rows": {
        "path": "native_assisted_lsi_pip_candidate_discovery",
        "blocked_wording": "No positive public RTX speedup wording is authorized for polygon_pair_overlap_area_rows from Goal1195 evidence.",
        "boundary": "Native-assisted LSI/PIP candidate discovery is evidence-ready, but the measured OptiX phase is slower than Embree; exact polygon-area refinement, row materialization, broad spatial-join performance, and whole-app speedup are outside any wording.",
    },
    "polygon_set_jaccard": {
        "path": "native_assisted_lsi_pip_candidate_discovery",
        "blocked_wording": "No positive public RTX speedup wording is authorized for polygon_set_jaccard from Goal1195 evidence.",
        "boundary": "Native-assisted LSI/PIP candidate discovery is evidence-ready after recovery, but the first pod run failed parity, chunk-sensitive or nondeterministic behavior was observed during the recovery trail, and the final measured OptiX phase is slower than Embree; exact set-area/Jaccard refinement, row materialization, and whole-app speedup are outside any wording. Any future positive-wording consideration requires stability testing across chunk configurations.",
    },
    "hausdorff_distance": {
        "path": "prepared_directed_threshold_decision",
        "reviewed_wording": "RTDL's prepared Hausdorff threshold-decision RTX sub-path measured 0.122389 s and 13.73x versus the reviewed same-contract Embree directed-summary sub-path.",
        "boundary": "Only the prepared fixed-radius Hausdorff <= threshold decision sub-path is covered; exact Hausdorff distance, KNN-row output, nearest-neighbor ranking, violating-ID witnesses in scalar mode, Python setup, and whole-app speedup remain outside this wording.",
    },
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_sec(value: float) -> str:
    return f"{value:.6f}"


def _fmt_ratio(value: float) -> str:
    return f"{value:.2f}x"


def build_packet(intake_path: Path = DEFAULT_INTAKE) -> dict[str, Any]:
    intake = _load(intake_path)
    if not intake.get("valid"):
        raise ValueError(f"{intake_path} is not a valid intake")
    rows: list[dict[str, Any]] = []
    for pair in intake["pairs"]:
        app = pair["app"]
        spec = APP_WORDING[app]
        ratio = float(pair["raw_phase_ratio_embree_over_optix"])
        optix_phase = float(pair["optix_phase_sec"])
        embree_phase = float(pair["embree_phase_sec"])
        positive_candidate = ratio >= MIN_PUBLIC_RATIO
        decision = "propose_public_wording_reviewed" if positive_candidate else "keep_public_wording_blocked_no_positive_speedup"
        status_to_apply = "public_wording_reviewed" if positive_candidate else "public_wording_blocked"
        candidate_wording = spec.get("reviewed_wording") if positive_candidate else spec.get("blocked_wording")
        rows.append(
            {
                "app": app,
                "path_name": spec["path"],
                "decision": decision,
                "status_to_apply": status_to_apply,
                "embree_phase_sec": embree_phase,
                "optix_phase_sec": optix_phase,
                "raw_ratio_embree_over_optix": ratio,
                "candidate_public_wording": candidate_wording,
                "boundary": spec["boundary"],
                "public_speedup_claim_authorized_here": False,
            }
        )
    reviewed = [row["app"] for row in rows if row["status_to_apply"] == "public_wording_reviewed"]
    blocked = [row["app"] for row in rows if row["status_to_apply"] == "public_wording_blocked"]
    return {
        "goal": GOAL,
        "date": DATE,
        "source_intake": str(intake_path.relative_to(ROOT)),
        "source_consensus": "docs/reports/goal1195_two_ai_consensus_2026-04-30.md",
        "min_public_ratio": MIN_PUBLIC_RATIO,
        "public_speedup_claim_authorized_count": 0,
        "proposed_public_wording_reviewed_apps": reviewed,
        "proposed_public_wording_blocked_apps": blocked,
        "rows": rows,
        "boundary": (
            "Goal1196 is a public-wording decision packet after Goal1195 evidence-readiness. "
            "It proposes narrow public wording only for rows with same-contract OptiX advantage, "
            "keeps slower OptiX rows blocked from positive speedup wording, and does not edit "
            "public docs or authorize release by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1196 Public Wording Decision Packet",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- source intake: `{payload['source_intake']}`",
        f"- source consensus: `{payload['source_consensus']}`",
        f"- minimum positive public ratio used by packet: `{payload['min_public_ratio']}`",
        f"- proposed reviewed apps: `{', '.join(payload['proposed_public_wording_reviewed_apps'])}`",
        f"- proposed blocked apps: `{', '.join(payload['proposed_public_wording_blocked_apps'])}`",
        f"- public speedup claims authorized by this packet: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## Decisions",
        "",
        "| App | Path | Decision | Embree sec | OptiX sec | Ratio |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['decision']}` | "
            f"`{_fmt_sec(row['embree_phase_sec'])}` | `{_fmt_sec(row['optix_phase_sec'])}` | "
            f"`{_fmt_ratio(row['raw_ratio_embree_over_optix'])}` |"
        )
    lines.extend(["", "## Candidate Public Wording", ""])
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['app']} / {row['path_name']}",
                "",
                str(row["candidate_public_wording"]),
                "",
                f"Boundary: {row['boundary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Reviewer Questions",
            "",
            "1. Is it correct to promote only road_hazard_screening and hausdorff_distance to bounded reviewed wording?",
            "2. Is it correct to keep database_analytics, graph_analytics, polygon_pair_overlap_area_rows, and polygon_set_jaccard blocked from positive public speedup wording because OptiX is slower than Embree in the accepted evidence?",
            "3. Is the Jaccard caution boundary strong enough given the first-run parity failure before recovery?",
            "4. Are all boundaries narrow enough to avoid whole-app, default-mode, Python postprocess, DBMS, GIS, graph-system, or exact-distance claims?",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Goal1196 public wording decision packet.")
    parser.add_argument("--input-json", default=str(DEFAULT_INTAKE))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    args = parser.parse_args()
    payload = build_packet(Path(args.input_json))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "valid": True,
                "reviewed": payload["proposed_public_wording_reviewed_apps"],
                "blocked": payload["proposed_public_wording_blocked_apps"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
