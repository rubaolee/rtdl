#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
DEFAULT_INTAKE = ROOT / "docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.json"
DEFAULT_OUTPUT_JSON = ROOT / "docs/reports/goal1224_resolve_remaining_public_wording_rows_2026-05-01.json"
DEFAULT_OUTPUT_MD = ROOT / "docs/reports/goal1224_resolve_remaining_public_wording_rows_2026-05-01.md"
MIN_PUBLIC_RATIO = 1.2

TARGET_APPS = (
    "graph_analytics",
    "polygon_pair_overlap_area_rows",
    "hausdorff_distance",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_sec(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _fmt_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}x"


def _decision_for_pair(row: dict[str, Any]) -> dict[str, Any]:
    app = row["app"]
    ratio = row.get("raw_phase_ratio_embree_over_optix")
    schema_ready = bool(row.get("same_contract_pair_schema_valid"))
    timing_ready = bool(row.get("timing_floor_pair_met"))
    review_ready = bool(row.get("public_wording_review_ready"))
    positive = bool(
        schema_ready
        and timing_ready
        and review_ready
        and ratio is not None
        and ratio >= MIN_PUBLIC_RATIO
    )

    if app == "graph_analytics":
        path_name = "graph_visibility_edges"
        boundary = (
            "Only the bounded graph visibility_edges any-hit traversal sub-path is covered; "
            "BFS frontier bookkeeping, triangle set-intersection, shortest-path logic, graph "
            "database behavior, distributed analytics, Python setup, and whole-app graph speedup "
            "remain outside this wording."
        )
        reviewed = (
            "RTDL's graph visibility_edges RTX sub-path has valid same-contract evidence, "
            f"but measured {_fmt_sec(row.get('optix_phase_sec'))} s versus "
            f"{_fmt_sec(row.get('embree_phase_sec'))} s for Embree, so the raw "
            f"Embree-over-OptiX ratio is {_fmt_ratio(ratio)} and no positive public "
            "RTX speedup wording is authorized."
        )
    elif app == "polygon_pair_overlap_area_rows":
        path_name = "native_assisted_lsi_pip_candidate_discovery"
        boundary = (
            "Only native-assisted LSI/PIP candidate discovery is covered; exact polygon-area "
            "continuation, row materialization, Python setup, arbitrary polygon geometry, and "
            "whole-app polygon-overlap speedup remain outside this wording."
        )
        reviewed = (
            "RTDL's polygon-pair candidate-discovery RTX sub-path has valid same-contract "
            f"evidence, but measured {_fmt_sec(row.get('optix_phase_sec'))} s versus "
            f"{_fmt_sec(row.get('embree_phase_sec'))} s for Embree, so the raw "
            f"Embree-over-OptiX ratio is {_fmt_ratio(ratio)} and no positive public "
            "RTX speedup wording is authorized."
        )
    elif app == "hausdorff_distance":
        path_name = "directed_threshold_prepared"
        boundary = (
            "Only the prepared Hausdorff <= radius threshold-decision traversal sub-path is "
            "covered; exact Hausdorff distance, KNN rows, nearest-neighbor ranking, violating-ID "
            "witness output, Python setup, validation, and whole-app speedup remain outside this wording."
        )
        reviewed = (
            "RTDL's prepared Hausdorff threshold-decision RTX sub-path measured "
            f"{_fmt_sec(row.get('optix_phase_sec'))} s and {_fmt_ratio(ratio)} versus the "
            "reviewed same-contract Embree directed-summary sub-path."
        )
    else:  # pragma: no cover - guarded by TARGET_APPS.
        raise ValueError(f"unexpected app {app}")

    return {
        "app": app,
        "path_name": path_name,
        "schema_ready": schema_ready,
        "timing_ready": timing_ready,
        "review_ready": review_ready,
        "embree_phase_sec": row.get("embree_phase_sec"),
        "optix_phase_sec": row.get("optix_phase_sec"),
        "raw_ratio_embree_over_optix": ratio,
        "decision": "public_wording_reviewed" if positive else "public_wording_blocked",
        "positive_public_speedup": positive,
        "reviewed_wording": reviewed,
        "boundary": boundary,
    }


def build_packet(intake_path: Path = DEFAULT_INTAKE) -> dict[str, Any]:
    intake = _load(intake_path)
    if not intake.get("valid"):
        raise ValueError(f"{intake_path} is not a valid final intake")
    pairs = {row["app"]: row for row in intake["pairs"]}
    missing = [app for app in TARGET_APPS if app not in pairs]
    if missing:
        raise ValueError(f"missing target apps in intake: {missing}")
    rows = [_decision_for_pair(pairs[app]) for app in TARGET_APPS]
    return {
        "goal": "Goal1224 resolve remaining public wording rows",
        "date": DATE,
        "source_intake": str(intake_path.relative_to(ROOT)),
        "min_public_ratio": MIN_PUBLIC_RATIO,
        "target_apps": list(TARGET_APPS),
        "valid": all(row["schema_ready"] and row["timing_ready"] and row["review_ready"] for row in rows),
        "promote_to_public_wording_reviewed": [row["app"] for row in rows if row["decision"] == "public_wording_reviewed"],
        "mark_public_wording_blocked": [row["app"] for row in rows if row["decision"] == "public_wording_blocked"],
        "rows": rows,
        "boundary": (
            "This packet resolves the remaining not-public-reviewed rows from valid Goal1194/Goal1193 "
            "same-contract evidence. It authorizes only source-of-truth status changes after external "
            "AI review; it does not move the v0.9.8 release tag and does not authorize whole-app claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1224 Resolve Remaining Public Wording Rows",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- source intake: `{payload['source_intake']}`",
        f"- minimum positive public ratio: `{payload['min_public_ratio']}`",
        f"- valid: `{payload['valid']}`",
        f"- promote to reviewed: `{', '.join(payload['promote_to_public_wording_reviewed']) or 'none'}`",
        f"- mark blocked after review: `{', '.join(payload['mark_public_wording_blocked']) or 'none'}`",
        "",
        "## Decisions",
        "",
        "| App | Path | Embree phase sec | OptiX phase sec | Ratio | Decision |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{_fmt_sec(row['embree_phase_sec'])}` | "
            f"`{_fmt_sec(row['optix_phase_sec'])}` | `{_fmt_ratio(row['raw_ratio_embree_over_optix'])}` | "
            f"`{row['decision']}` |"
        )
    lines.extend(["", "## Wording And Boundaries", ""])
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['app']} / {row['path_name']}",
                "",
                row["reviewed_wording"],
                "",
                f"Boundary: {row['boundary']}",
                "",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve remaining public wording rows from final Goal1194 intake.")
    parser.add_argument("--input-json", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    payload = build_packet(args.input_json)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "reviewed": payload["promote_to_public_wording_reviewed"], "blocked": payload["mark_public_wording_blocked"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
