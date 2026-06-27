#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.json"
DEFAULT_ACTUAL_DIR = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_grouped_reduction_repeat100_actual_20260620"
DEFAULT_CLEAN_ACTUAL_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_grouped_reduction_repeat100_actual_524288_clean_20260620"
)
DEFAULT_SCALAR_BROADCAST_ACTUAL_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620"
)
DEFAULT_JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.json"
DEFAULT_MD_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md"


def build_payload(
    contract_path: Path = DEFAULT_CONTRACT,
    actual_dir: Path = DEFAULT_ACTUAL_DIR,
    clean_actual_dir: Path = DEFAULT_CLEAN_ACTUAL_DIR,
    scalar_broadcast_actual_dir: Path = DEFAULT_SCALAR_BROADCAST_ACTUAL_DIR,
) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    sum_rows = [row for row in contract["candidate_rows"] if row["mode"] == "sum"]
    count_rows = [row for row in contract["candidate_rows"] if row["mode"] == "count"]
    actual_by_rows = _actual_repeat100_rows(actual_dir)
    clean_by_rows = _actual_repeat100_rows(clean_actual_dir) if clean_actual_dir.exists() else {}
    clean_overrides = tuple(sorted(set(actual_by_rows) & set(clean_by_rows)))
    actual_by_rows.update(clean_by_rows)
    scalar_broadcast_by_rows = (
        _actual_repeat100_rows(scalar_broadcast_actual_dir)
        if scalar_broadcast_actual_dir.exists()
        else {}
    )
    scalar_broadcast_overrides = tuple(sorted(set(actual_by_rows) & set(scalar_broadcast_by_rows)))
    actual_by_rows.update(scalar_broadcast_by_rows)
    rows = [_wording_row(row, actual_by_rows[int(row["generated_rows"])]) for row in sum_rows]
    return {
        "status": "sum_only_actual_repeat100_candidate_wording_not_release",
        "source_contract": str(contract_path.relative_to(ROOT)),
        "source_contract_status": contract["status"],
        "source_actual_repeat100_evidence_dir": str(actual_dir.relative_to(ROOT)),
        "source_actual_repeat100_clean_evidence_dir": (
            str(clean_actual_dir.relative_to(ROOT)) if clean_actual_dir.exists() else None
        ),
        "source_actual_repeat100_scalar_broadcast_evidence_dir": (
            str(scalar_broadcast_actual_dir.relative_to(ROOT))
            if scalar_broadcast_actual_dir.exists()
            else None
        ),
        "actual_repeat100_clean_override_rows": clean_overrides,
        "actual_repeat100_scalar_broadcast_override_rows": scalar_broadcast_overrides,
        "actual_repeat100_evidence_status": "ok" if actual_by_rows else "missing",
        "generic_capability": "grouped_reduction",
        "candidate_scope": "sum-only actual-repeat100 prepared grouped-reduction public wording candidate",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "current_packet_external_review_status": "blocked_current_packet",
        "current_packet_2ai_consensus_status": "not_recorded_for_this_packet",
        "external_review_blockage": (
            "docs/reviews/external_review_blocked_phoenix_v3_grouped_reduction_scalar_broadcast_optimization_2026-06-20.md"
        ),
        "m7_candidate_rows": len(rows),
        "m7_qualified_release_rows": 0,
        "rows": rows,
        "excluded_rows": [_excluded_count_row(row) for row in count_rows],
        "supersedes_modeled_repeat100_packet": True,
        "supersession_reason": (
            "A pod rerun measured repeat=100 directly for grouped_sum on the same "
            "Embree/OptiX contract. A clean 524,288-row rerun then confirmed the "
            "large cold cost. The current packet then applied the generic scalar "
            "broadcast ray-packer optimization and reran actual repeat100; those "
            "optimized actual-repeat100 artifacts now supply the current candidate "
            "numbers. Public candidate wording must use actual repeat100 loop and "
            "cold-plus-loop values instead of formula projections."
        ),
        "public_copy_rules": [
            "Say fixed-schema prepared grouped-sum workload.",
            "Name hardware, row count, group count, backend pair, warmup, and repeat count.",
            "Say actual repeat 100 when quoting repeat-100 evidence.",
            "Report both actual 100-query loop speedup and cold-plus-loop speedup.",
            "Use the scalar-broadcast optimized repeat100 rerun when quoting current values.",
            "Do not quote the older modeled repeat 100 values as current candidate wording.",
            "Always show cold prepare cost next to repeat-100 wording.",
            "Keep whole-app and whole-database speedup unauthorized.",
        ],
        "forbidden_public_wording": [
            "V3 is 224x faster",
            "RayDB is 224x faster",
            "RTDL is 33x faster end to end",
            "RTDL accelerates database workloads broadly",
            "count rows are public grouped_reduction speedup rows",
            "repeat 100 is only modeled",
            "whole-app speedup is authorized",
        ],
        "next_review_questions": [
            "Is actual repeat-100 wording acceptable if cold prepare is shown beside loop timing?",
            "Should the 262,144-row sum row become M7-qualified after final external review?",
            "Should the 524,288-row sum row remain candidate despite its large cold prepare cost?",
            "Is the public wording understandable without project history?",
            "Are the count-row exclusions still strong enough?",
        ],
        "goal_level_decision_audit": {
            "decision": "replace modeled repeat100 candidate wording with actual repeat100 pod evidence",
            "was_i_foolish": (
            "Partly. The earlier modeled wording was honest about being modeled, "
            "but it was weaker than V3 should accept once pod time was available. "
            "The first actual 524,288-row run also needed a clean confirmation because "
            "the launch had a quoting mistake around artifact placement. After that, "
            "leaving the 76M-ray scalar-field allocations in place would have left a "
            "fixable generic packer cost in the V3 candidate path."
        ),
            "foolish_actions": (
            "It would be foolish to keep presenting modeled 32x/33x repeat100 "
            "numbers as the current candidate after measuring actual repeat100, "
            "to quote the first 524,288-row run without recording the clean rerun, "
            "or to keep using the pre-optimization evidence after the scalar-broadcast "
            "packer rerun succeeded."
        ),
            "other_path": (
                "Wait for external review of the modeled wording. That would leave "
                "a known measurement gap in the strongest V3 candidate."
            ),
            "different_path_now": (
            "Use the actual repeat100 pod artifacts as current candidate evidence "
            "with the scalar-broadcast optimized repeat100 rerun as the current "
            "source for both scales, and keep release authorization false until "
            "final external review."
        ),
        },
    }


def _actual_repeat100_rows(actual_dir: Path) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for path in sorted(actual_dir.glob("grouped_sum*repeat100*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        generated_rows = int(payload["parameters"]["generated_rows"])
        by_backend = {row["backend"]: row for row in payload["rows"]}
        embree = by_backend["embree"]
        optix = by_backend["optix"]
        embree_loop = float(embree["prepared_iteration_total_sec"])
        optix_loop = float(optix["prepared_iteration_total_sec"])
        embree_cold_plus_loop = float(embree["cold_prepare_total_sec"]) + embree_loop
        optix_cold_plus_loop = float(optix["cold_prepare_total_sec"]) + optix_loop
        rows[generated_rows] = {
            "source_actual_file": str(path.relative_to(ROOT)),
            "status": payload["status"],
            "generated_rows": generated_rows,
            "generated_groups": int(payload["parameters"]["generated_groups"]),
            "warmup": int(payload["parameters"]["warmup"]),
            "repeat": int(embree["repeat"]),
            "all_match_cpu_reference": bool(payload["comparison"]["all_match_cpu_reference"]),
            "same_contract": bool(payload["comparison"]["same_contract_backend_pairs"][0]["same_contract"]),
            "embree_hot_median_sec": float(embree["elapsed_median_sec"]),
            "optix_hot_median_sec": float(optix["elapsed_median_sec"]),
            "hot_query_speedup_embree_over_optix": float(payload["comparison"]["same_contract_backend_pairs"][0]["embree_over_optix_median"]),
            "embree_actual_loop_total_sec": embree_loop,
            "optix_actual_loop_total_sec": optix_loop,
            "actual_repeat100_loop_speedup": embree_loop / optix_loop,
            "embree_cold_prepare_total_sec": float(embree["cold_prepare_total_sec"]),
            "optix_cold_prepare_total_sec": float(optix["cold_prepare_total_sec"]),
            "embree_cold_plus_loop_sec": embree_cold_plus_loop,
            "optix_cold_plus_loop_sec": optix_cold_plus_loop,
            "actual_repeat100_cold_plus_loop_speedup": embree_cold_plus_loop / optix_cold_plus_loop,
            "claim_boundary": payload["claim_boundary"],
        }
    return rows


def _wording_row(modeled_row: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    scale = f"{actual['generated_rows']:,} rows / {actual['generated_groups']:,} groups"
    optimized_row_id = f"grouped_reduction_sum_scalar_broadcast_repeat100_{actual['generated_rows']}"
    blockers = [
        "final_public_row_wording_review_required",
        "m7_promotion_authorized_false",
        "external_review_required",
        "whole_app_speedup_claim_authorized_false",
    ]
    if actual["actual_repeat100_cold_plus_loop_speedup"] < 5.0:
        blockers.append("large_cold_prepare_cost_limits_public_claim")
    return {
        "row_id": optimized_row_id,
        "previous_actual_row_id": f"grouped_reduction_sum_repeat100_actual_{actual['generated_rows']}",
        "previous_modeled_row_id": modeled_row["row_id"],
        "candidate_public_row_id": f"{optimized_row_id}_public_wording_candidate",
        "promotion_status": "sum_only_actual_repeat100_candidate_needs_final_review",
        "generated_rows": actual["generated_rows"],
        "generated_groups": actual["generated_groups"],
        "operation": "group_sum_i64",
        "recommended_public_repeat_count": 100,
        "warmup": actual["warmup"],
        "repeat": actual["repeat"],
        "hot_query_speedup_embree_over_optix": actual["hot_query_speedup_embree_over_optix"],
        "actual_repeat100_loop_speedup": actual["actual_repeat100_loop_speedup"],
        "actual_repeat100_cold_plus_loop_speedup": actual["actual_repeat100_cold_plus_loop_speedup"],
        "embree_actual_loop_total_sec": actual["embree_actual_loop_total_sec"],
        "optix_actual_loop_total_sec": actual["optix_actual_loop_total_sec"],
        "embree_cold_plus_loop_sec": actual["embree_cold_plus_loop_sec"],
        "optix_cold_plus_loop_sec": actual["optix_cold_plus_loop_sec"],
        "embree_cold_prepare_total_sec": actual["embree_cold_prepare_total_sec"],
        "optix_cold_prepare_total_sec": actual["optix_cold_prepare_total_sec"],
        "source_actual_file": actual["source_actual_file"],
        "source_previous_modeled_repeat100_end_to_end_speedup": modeled_row["repeat_100_end_to_end_speedup"],
        "actual_evidence_supersedes_modeled_value": True,
        "all_match_cpu_reference": actual["all_match_cpu_reference"],
        "same_contract": actual["same_contract"],
        "m7_promoted": False,
        "blockers": blockers,
        "draft_public_wording_not_publishable": (
            "Draft only: for a fixed-schema prepared grouped-sum workload on an "
            f"NVIDIA RTX 4000 Ada Generation pod ({scale}), actual repeat=100 "
            f"measurement showed {actual['actual_repeat100_loop_speedup']:.3f}x "
            "OptiX-over-Embree speedup for the 100-query prepared loop. Counting "
            "cold prepare once plus the measured 100-query loop, the speedup was "
            f"{actual['actual_repeat100_cold_plus_loop_speedup']:.3f}x. The hot "
            f"prepared-query median ratio was {actual['hot_query_speedup_embree_over_optix']:.3f}x. "
            "This is not a whole-app or whole-database speedup claim, and it is "
            "not publishable until final external public-row review."
        ),
    }


def _excluded_count_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_id": row["row_id"],
        "reason": "count row kept internal because break-even requires double-digit repeats",
        "break_even_repeat_count_ceiling": row["break_even_repeat_count_ceiling"],
        "modeled_repeat_100_end_to_end_speedup": row["repeat_100_end_to_end_speedup"],
        "blockers": row["blockers"],
        "m7_promoted": False,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {row_id} | {rows:,} | {groups:,} | {hot:.3f}x | {loop:.3f}x | {cold:.3f}x | {emb_loop:.3f}s | {opt_loop:.3f}s | {status} |".format(
            row_id=row["row_id"],
            rows=row["generated_rows"],
            groups=row["generated_groups"],
            hot=row["hot_query_speedup_embree_over_optix"],
            loop=row["actual_repeat100_loop_speedup"],
            cold=row["actual_repeat100_cold_plus_loop_speedup"],
            emb_loop=row["embree_actual_loop_total_sec"],
            opt_loop=row["optix_actual_loop_total_sec"],
            status=row["promotion_status"],
        )
        for row in payload["rows"]
    )
    cold_rows = "\n".join(
        "| {row_id} | {emb_cold:.3f}s | {opt_cold:.3f}s | {emb_total:.3f}s | {opt_total:.3f}s |".format(
            row_id=row["row_id"],
            emb_cold=row["embree_cold_prepare_total_sec"],
            opt_cold=row["optix_cold_prepare_total_sec"],
            emb_total=row["embree_cold_plus_loop_sec"],
            opt_total=row["optix_cold_plus_loop_sec"],
        )
        for row in payload["rows"]
    )
    wording = "\n".join(f"- {row['draft_public_wording_not_publishable']}" for row in payload["rows"])
    excluded = "\n".join(
        "| {row_id} | {be} | {r100:.3f}x | {reason} |".format(
            row_id=row["row_id"],
            be=row["break_even_repeat_count_ceiling"],
            r100=row["modeled_repeat_100_end_to_end_speedup"],
            reason=row["reason"],
        )
        for row in payload["excluded_rows"]
    )
    rules = "\n".join(f"- {rule}" for rule in payload["public_copy_rules"])
    forbidden = "\n".join(f"- Do not claim: {rule}" for rule in payload["forbidden_public_wording"])
    audit = payload["goal_level_decision_audit"]
    clean_source = payload.get("source_actual_repeat100_clean_evidence_dir")
    scalar_source = payload.get("source_actual_repeat100_scalar_broadcast_evidence_dir")
    clean_source_block = (
        f"""
Clean rerun source for the 524,288-row candidate:

```text
{clean_source}
```
"""
        if clean_source
        else ""
    )
    scalar_source_block = (
        f"""
Current scalar-broadcast optimized repeat100 source:

```text
{scalar_source}
```
"""
        if scalar_source
        else ""
    )
    return f"""# Phoenix V3 Grouped-Reduction Sum M7 Candidate Wording

Status: actual repeat100 sum-only M7 candidate wording, not release authorization.

```text
status: {payload['status']}
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
current_packet_external_review_status: {payload['current_packet_external_review_status']}
current_packet_2ai_consensus_status: {payload['current_packet_2ai_consensus_status']}
M7 candidate rows: {payload['m7_candidate_rows']}
Phoenix M7-qualified release rows: 0
```

## Scope

This packet only considers grouped sum rows from the reviewed prepared-query
contract. Count rows are excluded from public promotion.

The earlier modeled repeat100 wording is superseded by actual repeat100 pod
evidence:

```text
{payload['source_actual_repeat100_evidence_dir']}
```
{clean_source_block}
{scalar_source_block}

Source contract:

```text
{payload['source_contract']}
```

## Candidate Rows

| Row | Rows | Groups | Hot OptiX/Embree | Actual repeat100 loop | Actual cold plus loop | Embree loop | OptiX loop | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
{rows}

## Cold Cost

Cold prepare is part of the user contract. The 524,288-row case is much less
impressive after cold prepare is counted, so it must not be quoted as a 33x
end-to-end row.

| Row | Embree cold prepare | OptiX cold prepare | Embree cold plus loop | OptiX cold plus loop |
| --- | ---: | ---: | ---: | ---: |
{cold_rows}

## Draft Public Wording

The following wording is not publishable until final external public-row review.

{wording}

## Excluded Count Rows

| Row | Break-even repeats | Modeled repeat 100 end-to-end | Reason |
| --- | ---: | ---: | --- |
{excluded}

## Public Copy Rules

{rules}

## Forbidden Public Wording

{forbidden}

## Next Review Questions

{chr(10).join(f'- {question}' for question in payload['next_review_questions'])}

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
    parser = argparse.ArgumentParser(description="Build sum-only grouped_reduction M7 candidate wording.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--actual-dir", type=Path, default=DEFAULT_ACTUAL_DIR)
    parser.add_argument("--clean-actual-dir", type=Path, default=DEFAULT_CLEAN_ACTUAL_DIR)
    parser.add_argument("--scalar-broadcast-actual-dir", type=Path, default=DEFAULT_SCALAR_BROADCAST_ACTUAL_DIR)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract_path = args.contract if args.contract.is_absolute() else ROOT / args.contract
    actual_dir = args.actual_dir if args.actual_dir.is_absolute() else ROOT / args.actual_dir
    clean_actual_dir = args.clean_actual_dir if args.clean_actual_dir.is_absolute() else ROOT / args.clean_actual_dir
    scalar_broadcast_actual_dir = (
        args.scalar_broadcast_actual_dir
        if args.scalar_broadcast_actual_dir.is_absolute()
        else ROOT / args.scalar_broadcast_actual_dir
    )
    payload = build_payload(contract_path, actual_dir, clean_actual_dir, scalar_broadcast_actual_dir)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "json_out": str(args.json_out), "md_out": str(args.md_out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
