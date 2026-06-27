#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_grouped_reduction_m7_20260620"
DEFAULT_SOURCE = EVIDENCE_ROOT / "m7_grouped_reduction_post_run_intake.json"
DEFAULT_JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.json"
DEFAULT_MD_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md"


def build_payload(source: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    intake = json.loads(source.read_text(encoding="utf-8"))
    candidates = _candidate_rows(intake)
    return {
        "status": "prepared_query_contract_draft_not_release",
        "source_intake": str(source.relative_to(ROOT)),
        "source_intake_status": intake["status"],
        "generic_capability": "grouped_reduction",
        "contract_name": "RTDL grouped_reduction prepared-query contract",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows": 0,
        "sum_repeat100_actual_evidence_supersedes_formula_candidates": True,
        "sum_repeat100_actual_evidence": (
            "docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md"
        ),
        "current_candidate_wording_uses_actual_repeat100": True,
        "user_problem": (
            "Run repeated grouped count/sum queries over a fixed-schema table "
            "with known row and group-key counts, without writing custom native "
            "code for that application."
        ),
        "public_contract": {
            "scope": "prepared repeated grouped reductions over a fixed schema",
            "fixed_before_prepare": (
                "row count, group-key column, number of distinct groups, integer "
                "value column for sum, query/filter shape, backend, operation, and "
                "group capacity"
            ),
            "supported_operations_for_this_packet": ["group_count", "group_sum_i64"],
            "supported_backends_for_this_packet": ["embree", "optix"],
            "partner_continuation_required": False,
            "native_engine_customization_allowed": False,
            "output_contract": (
                "one output row per group key must match the CPU reference exactly "
                "for count and integer sum on the stated table dimensions"
            ),
            "overflow_policy": "fail_closed",
        },
        "timing_contract": {
            "required_fields": [
                "workload_build_sec",
                "cold_prepare_total_sec",
                "elapsed_median_sec",
                "prepared_iteration_count",
                "repeat",
                "warmup",
            ],
            "hot_query_field": "elapsed_median_sec",
            "repeat_end_to_end_formula": "cold_prepare_total_sec + repeat_count * elapsed_median_sec",
            "repeat_scenario_values_are_formula_projections": True,
            "repeat_end_to_end_formula_note": (
                "Repeat-scenario values are computed from measured cold prepare and "
                "the measured hot-query median. They are not independent multi-query "
                "end-to-end runs."
            ),
            "minimum_warmup_for_m7": 3,
            "required_repeat_counts_for_reporting": [1, 2, 5, 10, 25, 50, 100],
            "single_query_required": True,
            "break_even_required": True,
            "cold_cost_must_be_reported_next_to_hot_speedup": True,
        },
        "candidate_rows": candidates,
        "promotion_gates": [
            "fresh_pod_artifacts_copied_back",
            "cpu_reference_match_for_every_promoted_backend_row",
            "same_contract_embree_and_optix_rows",
            "warmup_at_least_3_for_every_promoted_row",
            "cold_prepare_total_sec_reported",
            "hot_query_elapsed_median_sec_reported",
            "repeat_1_end_to_end_reported",
            "break_even_repeat_count_reported",
            "chosen_public_repeat_count_named_in_wording",
            "whole_app_speedup_claim_authorized_false",
            "final_external_public_row_review_required",
        ],
        "draft_candidate_wording_not_publishable": _draft_candidate_wording(candidates),
        "forbidden_claims": [
            "V3 is 224x faster end to end",
            "RayDB is 224x faster end to end",
            "RTDL is a DBMS or SQL engine",
            "grouped_reduction proves broad V3 speedup over V2.x",
            "whole-app or whole-database speedup is authorized",
            "hot prepared-query speedup can be quoted without cold cost and repeat count",
        ],
        "next_actions": [
            "Seek external review of this contract packet.",
            "If accepted, choose whether M7 promotes sum-only repeat-100 grouped_sum prepared-query wording or keeps grouped_reduction internal.",
            "If promotion is attempted, write final public row wording and run another review before editing tutorials.",
        ],
        "goal_level_decision_audit": {
            "decision": "write a public prepared-query contract before any grouped_reduction M7 promotion",
            "was_i_foolish": "No. The contract closes the exact blocker found by the fresh evidence review.",
            "foolish_actions": (
                "It would be foolish to publish the hot-query speedups without a fixed-schema, "
                "cold-cost, and repeat-count user contract."
            ),
            "other_path": (
                "Move to another candidate immediately. That remains available, but grouped_reduction "
                "is closest to a reusable M7 row."
            ),
            "different_path_now": (
                "Make the user contract executable and reviewed before changing public tutorials or wording."
            ),
        },
    }


def _candidate_rows(intake: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scale in intake["scales"]:
        generated_rows = int(scale["generated_rows"])
        generated_groups = int(scale["generated_groups"])
        for pair in scale["pairs"]:
            mode = str(pair["mode"])
            repeat_1 = pair["repeat_scenarios"]["1"]["end_to_end_speedup"]
            repeat_100 = pair["repeat_scenarios"]["100"]["end_to_end_speedup"]
            hot = pair["hot_query_speedup_embree_over_optix"]
            break_even_ceiling = int(pair["break_even_repeat_count_ceiling"])
            repeat_profile = {
                str(repeat_count): pair["repeat_scenarios"][str(repeat_count)]["end_to_end_speedup"]
                for repeat_count in (1, 2, 5, 10, 25, 50, 100)
            }
            status = "candidate_needs_public_row_review_not_m7"
            row_id = f"grouped_reduction_{mode}_repeat100_{generated_rows}"
            blockers = [
                "public_prepared_query_tutorial_not_written",
                "final_public_row_wording_review_required",
                "m7_promotion_authorized_false",
            ]
            if repeat_1 < 1.0:
                blockers.append("repeat_1_end_to_end_not_optix_win")
            elif repeat_1 < 1.10:
                blockers.append("repeat_1_end_to_end_margin_too_small_for_public_claim")
            if mode == "count":
                blockers.append("count_mode_requires_double_digit_repeat_amortization")
                blockers.append("count_mode_high_breakeven_blocks_public_claim")
            recommended_repeat = 100 if mode == "sum" and repeat_100 >= 2.0 and break_even_ceiling <= 5 else None
            rows.append(
                {
                    "row_id": row_id,
                    "promotion_status": status,
                    "generated_rows": generated_rows,
                    "generated_groups": generated_groups,
                    "mode": mode,
                    "operation": "group_count" if mode == "count" else "group_sum_i64",
                    "hot_query_speedup_embree_over_optix": hot,
                    "repeat_1_end_to_end_speedup": repeat_1,
                    "repeat_100_end_to_end_speedup": repeat_100,
                    "repeat_profile": repeat_profile,
                    "repeat_profile_basis": "formula_projection_from_measured_cold_prepare_and_hot_query_median",
                    "break_even_repeat_count_ceiling": break_even_ceiling,
                    "recommended_public_repeat_count_if_promoted": recommended_repeat,
                    "m7_promoted": False,
                    "blockers": blockers,
                }
            )
    return rows


def _draft_candidate_wording(candidates: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for row in candidates:
        if row["mode"] != "sum":
            continue
        lines.append(
            "Draft only: on the RTX 4000 Ada pod, the fixed-schema prepared "
            f"grouped sum row with {row['generated_rows']} rows and {row['generated_groups']} groups "
            f"showed {row['hot_query_speedup_embree_over_optix']:.3f}x hot prepared-query "
            f"OptiX-over-Embree speedup and {row['repeat_100_end_to_end_speedup']:.3f}x "
            "modeled repeat 100 end-to-end speedup after counting cold prepare once "
            "(modeled from measured cold prepare plus 100 times the measured hot-query "
            "median, not from an independently measured 100-query loop). "
            "This wording is not publishable until external public-row review closes."
        )
    return lines


def render_markdown(payload: dict[str, Any]) -> str:
    candidate_lines = []
    repeat_profile_lines = []
    for row in payload["candidate_rows"]:
        candidate_lines.append(
            "| {row_id} | {mode} | {rows:,} | {groups:,} | {hot:.3f}x | {r1:.3f}x | "
            "{r100:.3f}x | {breakeven} | {recommended} | {status} |".format(
                row_id=row["row_id"],
                mode=row["mode"],
                rows=row["generated_rows"],
                groups=row["generated_groups"],
                hot=row["hot_query_speedup_embree_over_optix"],
                r1=row["repeat_1_end_to_end_speedup"],
                r100=row["repeat_100_end_to_end_speedup"],
                breakeven=row["break_even_repeat_count_ceiling"],
                recommended=row["recommended_public_repeat_count_if_promoted"],
                status=row["promotion_status"],
            )
        )
        profile = row["repeat_profile"]
        repeat_profile_lines.append(
            "| {row_id} | {r1:.3f}x | {r2:.3f}x | {r5:.3f}x | {r10:.3f}x | {r25:.3f}x | {r50:.3f}x | {r100:.3f}x |".format(
                row_id=row["row_id"],
                r1=profile["1"],
                r2=profile["2"],
                r5=profile["5"],
                r10=profile["10"],
                r25=profile["25"],
                r50=profile["50"],
                r100=profile["100"],
            )
        )
    gates = "\n".join(f"- `{gate}`" for gate in payload["promotion_gates"])
    forbidden = "\n".join(f"- Do not claim: {claim}" for claim in payload["forbidden_claims"])
    wording = "\n".join(f"- {line}" for line in payload["draft_candidate_wording_not_publishable"])
    audit = payload["goal_level_decision_audit"]
    return f"""# Phoenix V3 Grouped-Reduction Prepared-Query Contract

Status: prepared-query contract draft, not release authorization.

```text
status: {payload['status']}
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

## User Problem

{payload['user_problem']}

This contract exists because the fresh grouped_reduction pod evidence is useful
but not yet user-publishable. A user must be able to tell whether they are
running one query, repeated prepared queries, or a whole database/application
workflow.

## Public Contract Draft

- Scope: {payload['public_contract']['scope']}.
- Fixed before prepare: {payload['public_contract']['fixed_before_prepare']}.
- Operations in this packet: `group_count`, `group_sum_i64`.
- Backends in this packet: `embree`, `optix`.
- Partner continuation required: `false`.
- Native app-engine customization allowed: `false`.
- Output contract: {payload['public_contract']['output_contract']}.
- Overflow policy: `{payload['public_contract']['overflow_policy']}`.

## Timing Contract

- Hot prepared-query field: `{payload['timing_contract']['hot_query_field']}`.
- Repeat end-to-end formula:
  `{payload['timing_contract']['repeat_end_to_end_formula']}`.
- Repeat scenario values are formula projections: `{payload['timing_contract']['repeat_scenario_values_are_formula_projections']}`.
- Projection note: {payload['timing_contract']['repeat_end_to_end_formula_note']}
- Minimum warmup for M7: `{payload['timing_contract']['minimum_warmup_for_m7']}`.
- Required repeat counts for reporting:
  `{payload['timing_contract']['required_repeat_counts_for_reporting']}`.
- Single-query end-to-end timing, break-even repeat count, and cold/setup cost
  must be shown next to any hot-query speedup.

## Supersession Note

The formula-projected repeat profile below is retained as the contract draft's
derivation record. Current sum-only candidate wording is no longer based on
these modeled repeat100 values. It is superseded by actual repeat100 pod
evidence:

```text
{payload['sum_repeat100_actual_evidence']}
```

## Candidate Rows

| Row | Mode | Rows | Groups | Hot OptiX/Embree | Repeat 1 end-to-end | Modeled repeat 100 end-to-end | Break-even repeats | Recommended public repeat | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
{chr(10).join(candidate_lines)}

## Repeat Profile

These values are formula projections from measured cold prepare and measured
hot-query median. They are not independently measured multi-query loops.

| Row | Repeat 1 | Repeat 2 | Repeat 5 | Repeat 10 | Repeat 25 | Repeat 50 | Repeat 100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(repeat_profile_lines)}

## Promotion Gates

{gates}

## Draft Candidate Wording

The following wording is not publishable. It is here so reviewers can decide
whether a prepared repeated-query row is a real user-facing V3 row.

{wording}

## Forbidden Claims

{forbidden}

## Next Actions

- Seek external review of this contract packet.
- If accepted, choose whether M7 promotes a repeat 100 grouped_sum prepared-query row or keeps grouped_reduction internal.
- If promotion is attempted, write final public row wording and run another review before editing tutorials.

## Goal-Level Decision Audit

Decision: {audit['decision']}

1. Was I foolish?

   {audit['was_i_foolish']}

2. If yes, what actions made the decision foolish?

   {audit['foolish_actions']}

3. Was there another path?

   {audit['other_path']}

4. Can I now try a different path that actually solves the problem?

   {audit['different_path_now']}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Phoenix V3 grouped_reduction prepared-query contract packet.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source if args.source.is_absolute() else ROOT / args.source
    payload = build_payload(source)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "json_out": str(args.json_out), "md_out": str(args.md_out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
