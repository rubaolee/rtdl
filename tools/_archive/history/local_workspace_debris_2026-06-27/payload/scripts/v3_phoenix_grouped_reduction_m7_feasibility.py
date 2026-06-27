#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    (
        "m4_m28_262144",
        ROOT
        / "docs"
        / "rebuild"
        / "v3"
        / "evidence"
        / "phoenix_v3_m4_grouped_continuation_20260620"
        / "m28_raydb_grouped_reduction_262144.json",
    ),
    (
        "raydb_m28_524288",
        ROOT
        / "docs"
        / "rebuild"
        / "v3"
        / "evidence"
        / "phoenix_v3_raydb_m28_grouped_reduction_20260620"
        / "m28_raydb_grouped_reduction_524288.json",
    ),
)
DEFAULT_JSON_OUT = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.json"
)
DEFAULT_MD_OUT = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md"
)
REPEAT_COUNTS = (1, 2, 5, 10, 25, 50, 100, 500, 1000)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Phoenix V3 grouped-reduction M7 feasibility packet.")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Optional source override as LABEL=PATH. Repeat twice for a fresh rerun intake.",
    )
    parser.add_argument(
        "--fresh-rerun",
        action="store_true",
        help="Classify the sources as a fresh M7 rerun intake instead of pre-run feasibility.",
    )
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()

    payload = build_payload(_parse_sources(args.source) if args.source else SOURCES, fresh_rerun=args.fresh_rerun)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0


def build_payload(sources: tuple[tuple[str, Path], ...] = SOURCES, fresh_rerun: bool = False) -> dict[str, Any]:
    scales = [_scale_summary(label, path) for label, path in sources]
    all_pairs = [pair for scale in scales for pair in scale["pairs"]]
    promoted_pairs = [pair for pair in all_pairs if pair["m7_promoted"]]
    status = (
        "grouped_reduction_m7_post_run_intake_not_promoted"
        if fresh_rerun
        else "grouped_reduction_m7_feasibility_not_promoted"
    )
    blockers = [
        "prepared_query_contract_not_yet_public_tutorial",
        "repeat_count_and_amortization_policy_not_reviewed",
        "cold_setup_costs_must_be_reported_next_to_hot_speedups",
        "no_public_row_level_external_review_for_promoted_wording",
    ]
    if fresh_rerun:
        blockers.append("fresh_rerun_requires_external_review_before_m7_promotion")
    else:
        blockers.insert(3, "no_fresh_m7_pod_rerun_after_feasibility_packet")
    max_hot_query_speedup = max(pair["hot_query_speedup_embree_over_optix"] for pair in all_pairs)
    return {
        "version": "phoenix_v3_grouped_reduction_m7_feasibility_2026_06_20",
        "status": status,
        "generic_capability": "grouped_reduction",
        "fresh_rerun": fresh_rerun,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promoted": False,
        "m7_qualified_release_rows": len(promoted_pairs),
        "source_evidence": [{"label": label, "path": _rel(path)} for label, path in sources],
        "scales": scales,
        "summary": {
            "scale_count": len(scales),
            "pair_count": len(all_pairs),
            "m7_qualified_release_rows": len(promoted_pairs),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "max_hot_query_speedup": max_hot_query_speedup,
            "max_repeat_1_end_to_end_speedup": max(pair["repeat_scenarios"]["1"]["end_to_end_speedup"] for pair in all_pairs),
            "all_cpu_reference_match": all(pair["both_match_cpu_reference"] for pair in all_pairs),
            "all_optix_hot_faster": all(pair["hot_query_speedup_embree_over_optix"] > 1.0 for pair in all_pairs),
            "count_rows_need_repeat_amortization": any(
                pair["mode"] == "count" and pair["break_even_repeat_count"] > 1.0 for pair in all_pairs
            ),
            "any_sum_row_has_large_cold_cost": any(
                pair["max_workload_build_sec"] > 100.0 for pair in all_pairs if pair["mode"] == "sum"
            ),
            "sum_rows_with_large_cold_cost": [
                f"{scale['generated_rows']}/sum"
                for scale in scales
                for pair in scale["pairs"]
                if pair["mode"] == "sum" and pair["max_workload_build_sec"] > 100.0
            ],
        },
        "m7_blockers": tuple(blockers),
        "allowed_internal_reading": (
            "Internal evidence shows the generic prepared grouped-reduction primitive can be much faster "
            "than Embree in the hot prepared-query window, especially for repeated queries or sum mode."
        ),
        "forbidden_public_reading": _forbidden_public_reading(fresh_rerun, max_hot_query_speedup),
        "goal_level_decision_audit": {
            "decision": (
                "classify fresh grouped_reduction M7 rerun evidence without promoting it"
                if fresh_rerun
                else "attempt grouped_reduction M7 feasibility through repeat-aware amortization instead of quoting hot ratios"
            ),
            "was_i_foolish": "No. The packet tests whether the strongest reusable evidence can become a user-responsible row.",
            "foolish_actions": _foolish_actions(fresh_rerun, max_hot_query_speedup),
            "other_path": "Start with Triangle or docs. That remains possible, but grouped_reduction is the cleanest reusable engine candidate.",
            "different_path_now": "Compute repeat-aware end-to-end scenarios and keep M7 promotion false unless the public contract is closed.",
        },
    }


def _scale_summary(label: str, path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    rows = {(row["backend"], row["mode"]): row for row in payload["rows"]}
    pairs = []
    for mode in ("count", "sum"):
        embree = rows[("embree", mode)]
        optix = rows[("optix", mode)]
        pairs.append(_pair_summary(mode, embree, optix, label.startswith("m7_")))
    return {
        "label": label,
        "source": _rel(path),
        "status": payload["status"],
        "generated_rows": payload["parameters"]["generated_rows"],
        "generated_groups": payload["parameters"]["generated_groups"],
        "source_warmup": payload["parameters"]["warmup"],
        "pairs": pairs,
    }


def _parse_sources(values: list[str]) -> tuple[tuple[str, Path], ...]:
    parsed: list[tuple[str, Path]] = []
    for value in values:
        if "=" not in value:
            raise SystemExit(f"--source must be LABEL=PATH, got {value!r}")
        label, raw_path = value.split("=", 1)
        if not label:
            raise SystemExit(f"--source label cannot be empty: {value!r}")
        parsed.append((label, Path(raw_path)))
    if len(parsed) != 2:
        raise SystemExit(f"expected exactly two --source entries, got {len(parsed)}")
    return tuple(parsed)


def _pair_summary(mode: str, embree: dict[str, Any], optix: dict[str, Any], fresh_rerun: bool) -> dict[str, Any]:
    embree_cold = float(embree["cold_prepare_total_sec"])
    optix_cold = float(optix["cold_prepare_total_sec"])
    embree_query = float(embree["elapsed_median_sec"])
    optix_query = float(optix["elapsed_median_sec"])
    hot_speedup = embree_query / optix_query
    break_even = _break_even_repeat_count(embree_cold, optix_cold, embree_query, optix_query)
    repeat_scenarios = {}
    for repeat in REPEAT_COUNTS:
        embree_total = embree_cold + repeat * embree_query
        optix_total = optix_cold + repeat * optix_query
        repeat_scenarios[str(repeat)] = {
            "repeat_count": repeat,
            "embree_total_sec": embree_total,
            "optix_total_sec": optix_total,
            "end_to_end_speedup": embree_total / optix_total,
        }
    embree_workload_build = float(embree["workload_build_sec"])
    optix_workload_build = float(optix["workload_build_sec"])
    min_workload_build = min(embree_workload_build, optix_workload_build)
    max_workload_build = max(embree_workload_build, optix_workload_build)
    return {
        "mode": mode,
        "m7_promoted": False,
        "both_match_cpu_reference": bool(embree["matches_cpu_reference"] and optix["matches_cpu_reference"]),
        "embree_rt_core_accelerated": bool(embree["rt_core_accelerated"]),
        "optix_rt_core_accelerated": bool(optix["rt_core_accelerated"]),
        "embree_cold_prepare_total_sec": embree_cold,
        "optix_cold_prepare_total_sec": optix_cold,
        "embree_hot_query_sec": embree_query,
        "optix_hot_query_sec": optix_query,
        "hot_query_speedup_embree_over_optix": hot_speedup,
        "break_even_repeat_count": break_even,
        "break_even_repeat_count_ceiling": math.ceil(break_even),
        "embree_workload_build_sec": embree_workload_build,
        "optix_workload_build_sec": optix_workload_build,
        "min_workload_build_sec": min_workload_build,
        "max_workload_build_sec": max_workload_build,
        "repeat_scenarios": repeat_scenarios,
        "claim_status": "internal_post_run_intake_not_m7" if fresh_rerun else "internal_feasibility_not_m7",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "m7_blockers": _pair_blockers(mode, break_even, min_workload_build, max_workload_build, fresh_rerun),
    }


def _pair_blockers(
    mode: str,
    break_even: float,
    min_workload_build: float,
    max_workload_build: float,
    fresh_rerun: bool,
) -> list[str]:
    blockers = [
        "prepared_query_contract_not_yet_public_tutorial",
        "repeat_count_and_amortization_policy_not_reviewed",
    ]
    if fresh_rerun:
        blockers.append("fresh_rerun_requires_external_review_before_m7_promotion")
    else:
        blockers.append("no_fresh_m7_pod_rerun_after_feasibility_packet")
    if break_even > 1.0:
        blockers.append("single_query_end_to_end_not_optix_win")
    if mode == "sum" and (min_workload_build > 100.0 or max_workload_build > 100.0):
        blockers.append("large_sum_workload_build_cost_must_be_prominent")
    return blockers


def _break_even_repeat_count(
    embree_cold: float,
    optix_cold: float,
    embree_query: float,
    optix_query: float,
) -> float:
    hot_saving = embree_query - optix_query
    cold_penalty = optix_cold - embree_cold
    if hot_saving <= 0:
        return math.inf
    if cold_penalty <= 0:
        return 1.0
    return cold_penalty / hot_saving


def _forbidden_public_reading(fresh_rerun: bool, max_hot_query_speedup: float) -> str:
    if fresh_rerun:
        return (
            f"Do not claim the fresh grouped_reduction hot-query ratios, up to {max_hot_query_speedup:.3f}x, "
            "are end-to-end speedups; do not claim whole-database speedup; and do not hide cold/setup cost "
            "behind hot-query ratios."
        )
    return (
        "Do not claim RayDB-style V3 is 158x faster end to end, do not claim whole-database speedup, "
        "and do not hide cold/setup cost behind hot-query ratios."
    )


def _foolish_actions(fresh_rerun: bool, max_hot_query_speedup: float) -> str:
    if fresh_rerun:
        return (
            f"It would be foolish to promote the fresh {max_hot_query_speedup:.3f}x hot-query ratio "
            "without cold/setup cost and repeat-count context."
        )
    return (
        "It would be foolish to promote the 158x sum hot-query ratio without cold/setup cost and repeat-count context."
    )


def render_markdown(payload: dict[str, Any]) -> str:
    title = (
        "# Phoenix V3 Grouped-Reduction M7 Post-Run Intake"
        if payload["fresh_rerun"]
        else "# Phoenix V3 Grouped-Reduction M7 Feasibility"
    )
    status_line = "Status: fresh M7 rerun intake, not M7 promotion." if payload["fresh_rerun"] else "Status: feasibility packet, not M7 promotion."
    warmup_values = sorted({scale["source_warmup"] for scale in payload["scales"]})
    if len(warmup_values) == 1:
        warmup_note = (
            f"Both source evidence files used warmup={warmup_values[0]}. "
            "Cross-scale rows still remain post-run intake evidence until external review."
        )
    else:
        warmup_note = (
            "Source evidence files used different warmups: "
            + ", ".join(f"{scale['generated_rows']} rows used warmup={scale['source_warmup']}" for scale in payload["scales"])
            + ". Cross-scale rows are therefore feasibility inputs, not standardized scale-ladder timing."
        )
    lines = [
        title,
        "",
        status_line,
        "",
        "```text",
        f"release_authorized: {_bool(payload['release_authorized'])}",
        f"public_speedup_claim_authorized: {_bool(payload['public_speedup_claim_authorized'])}",
        f"whole_app_speedup_claim_authorized: {_bool(payload['whole_app_speedup_claim_authorized'])}",
        f"M7-qualified release rows: {payload['m7_qualified_release_rows']}",
        "```",
        "",
        "## Verdict",
        "",
        "Grouped reduction is the strongest current reusable V3 performance candidate, but it is not promoted to M7 here.",
        "The reason is precise: hot prepared-query wins are real, while cold/setup and repeat-count policy are not yet a public contract.",
        "",
        "## Source Evidence And Warmups",
        "",
        warmup_note,
        "The workload-build fields below record both Embree and OptiX paths; the cheapest path can hide that the other baseline still pays a large cold/setup cost.",
        "",
        "| Scale | Source warmup | Mode | Embree workload build | OptiX workload build |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for scale in payload["scales"]:
        for pair in scale["pairs"]:
            lines.append(
                f"| `{scale['generated_rows']}` | {scale['source_warmup']} | `{pair['mode']}` | "
                f"{pair['embree_workload_build_sec']:.3f}s | {pair['optix_workload_build_sec']:.3f}s |"
            )
    lines.extend(
        [
            "",
        "## Repeat-Aware Summary",
        "",
        "| Scale | Mode | Hot OptiX/Embree | Break-even repeats | Repeat 1 end-to-end | Repeat 100 end-to-end | Main blocker |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for scale in payload["scales"]:
        for pair in scale["pairs"]:
            repeat_1 = pair["repeat_scenarios"]["1"]["end_to_end_speedup"]
            repeat_100 = pair["repeat_scenarios"]["100"]["end_to_end_speedup"]
            lines.append(
                f"| `{scale['generated_rows']}` | `{pair['mode']}` | "
                f"{pair['hot_query_speedup_embree_over_optix']:.3f}x | "
                f"{pair['break_even_repeat_count_ceiling']} | {repeat_1:.3f}x | "
                f"{repeat_100:.3f}x | `{_display_blocker(pair)}` |"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            payload["allowed_internal_reading"],
            "",
            payload["forbidden_public_reading"],
            "",
            "## M7 Blockers",
            "",
        ]
    )
    for blocker in payload["m7_blockers"]:
        lines.append(f"- `{blocker}`")
    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            "",
            f"   {audit['was_i_foolish']}",
            "",
            "2. If yes, what actions made the decision foolish?",
            "",
            f"   {audit['foolish_actions']}",
            "",
            "3. Was there another path?",
            "",
            f"   {audit['other_path']}",
            "",
            "4. Can I now try a different path that actually solves the problem?",
            "",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _display_blocker(pair: dict[str, Any]) -> str:
    blockers = pair["m7_blockers"]
    if "single_query_end_to_end_not_optix_win" in blockers:
        return "single_query_end_to_end_not_optix_win"
    if "large_sum_workload_build_cost_must_be_prominent" in blockers:
        return "large_sum_workload_build_cost_must_be_prominent"
    return blockers[0]


def _bool(value: bool) -> str:
    return str(bool(value)).lower()


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
