#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.json"
)
DEFAULT_JSON_OUT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json"
)
DEFAULT_MD_OUT = DEFAULT_JSON_OUT.with_suffix(".md")
EXTERNAL_REVIEW = (
    "docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md"
)
CODEX_CONSENSUS = (
    "docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_claude_supersession_consensus_2026-06-22.md"
)
EXTERNAL_AI_BLOCKED = (
    "docs/reviews/external_ai_blocked_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md"
)
PRIOR_SUBSTITUTE_REVIEW = (
    "docs/reviews/codex_subagent_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-21.md"
)
PRIOR_SUBSTITUTE_CONSENSUS = (
    "docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2ai_consensus_2026-06-21.md"
)
APPROVAL_STATE = "approved_after_claude_external_codex_consensus"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the Phoenix V3 grouped-reduction device-column M7 final review packet."
    )
    parser.add_argument("--source", type=Path, default=SOURCE_PACKET)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args.source)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload if args.pretty else payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0


def build_payload(source: Path = SOURCE_PACKET) -> dict[str, Any]:
    evidence = _read_json(source)
    approved = APPROVAL_STATE == "approved_after_claude_external_codex_consensus"
    rows = [_candidate_row(scale, approved) for scale in evidence["scales"]]
    promoted_rows = [row for row in rows if row["m7_promoted"]]
    return {
        "tool": "v3_phoenix_grouped_reduction_device_column_m7_final_review_packet",
        "version": "phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026_06_21",
        "packet_path": _rel(DEFAULT_MD_OUT),
        "packet_json_path": _rel(DEFAULT_JSON_OUT),
        "status": (
            "grouped_reduction_device_column_scoped_row_evidence_not_release"
            if approved
            else "grouped_reduction_device_column_m7_final_review_pending_external_not_m7"
        ),
        "generic_capability": "grouped_reduction",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": approved,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "m7_promotion_authorized": approved,
        "m7_qualified_release_rows": len(promoted_rows),
        "local_evidence_sufficient_for_external_public_row_review": True,
        "external_review_required_before_m7": True,
        "current_packet_external_review_status": (
            "claude_external_approve_with_required_fixes_p1_applied_2026-06-22"
            if approved
            else "pending_external_review"
        ),
        "current_packet_2ai_consensus_status": (
            "claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22"
            if approved
            else "not_recorded"
        ),
        "external_review": EXTERNAL_REVIEW,
        "codex_consensus": CODEX_CONSENSUS,
        "external_ai_blocked_note": EXTERNAL_AI_BLOCKED,
        "prior_substitute_review": PRIOR_SUBSTITUTE_REVIEW,
        "prior_substitute_consensus": PRIOR_SUBSTITUTE_CONSENSUS,
        "source_packet": _rel(source),
        "source_provenance": _source_provenance(evidence["source_provenance"]),
        "candidate_rows": rows,
        "retained_existing_m7_row": "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
        "classification_counting_basis": (
            "supplemental_new_rows_after_claude_external_review_and_codex_supersession_consensus"
            if approved
            else "supplemental_new_rows_pending_external_review"
        ),
        "summary": {
            "candidate_row_count": len(rows),
            "m7_qualified_release_rows": len(promoted_rows),
            "approved": approved,
            "min_host_packed_over_device_columns_cold_plus_loop_speedup": min(
                row["optix_host_packed_over_device_columns_cold_plus_loop_speedup"]
                for row in rows
            ),
            "max_host_packed_over_device_columns_cold_plus_loop_speedup": max(
                row["optix_host_packed_over_device_columns_cold_plus_loop_speedup"]
                for row in rows
            ),
            "min_embree_over_optix_device_columns_cold_plus_loop_speedup": min(
                row["embree_over_optix_device_columns_cold_plus_loop_speedup"]
                for row in rows
            ),
            "all_cpu_reference_match": all(row["all_match_cpu_reference"] for row in rows),
            "all_device_routes_remove_host_packed_rays": all(
                row["host_packed_ray_count_device_route"] == 0 for row in rows
            ),
        },
        "closed_or_pending_promotion_conditions": _conditions(approved),
        "p1_review_fixes_applied": [
            "approved public wording states that Embree remains host-packed while the OptiX candidate uses cupy_device_columns",
            "approved public wording frames Embree/device-column ratios as same-contract context, not pure backend-only ratios",
            "218.248x appears only as a labeled cold-prepare phase ratio near workload-build/input-path-collapse attribution, not as a headline/public row claim",
            "real Claude external review supersedes the earlier Codex-subagent-only procedural gap",
            "source manifest scope explicitly records that orchestration wrappers are not hashed and that the manifested M28 script is the measured benchmark entry point",
        ]
        if approved
        else [],
        "remaining_non_release_boundaries": [
            "release_authorized remains false",
            "public_speedup_claim_authorized remains false for broad/global V3 claims",
            "whole_app_speedup_claim_authorized remains false",
            "broad_v3_faster_than_v2_claim_authorized remains false",
            "true_zero_copy_authorized remains false",
            "the existing host-packed/scalar-broadcast row is retained and not silently replaced",
        ],
        "approved_row_scoped_public_wording": _approved_wording(rows) if approved else None,
        "draft_public_wording_not_publishable": _approved_wording(rows),
        "forbidden_public_wording": [
            "V3 is 218x faster",
            "RTDL is 218x faster end to end",
            "RayDB is universally accelerated",
            "true zero-copy is proven",
            "all grouped_reduction rows are public claims",
            "the old grouped_reduction M7 row has been replaced",
            "the Embree/device-column ratios are pure backend-only ratios",
        ],
        "goal_level_decision_audit": _decision_audit(approved),
    }


def _candidate_row(scale: dict[str, Any], approved: bool) -> dict[str, Any]:
    return {
        "row_id": scale["candidate_row_id"],
        "generic_capability": "grouped_reduction",
        "operation": "prepared_grouped_sum_i64",
        "ray_batch_layout": "cupy_device_columns",
        "generated_rows": scale["generated_rows"],
        "generated_groups": scale["generated_groups"],
        "logical_ray_count": scale["logical_ray_count"],
        "warmup": scale["warmup"],
        "repeat": scale["repeat"],
        "hardware": scale["exact_row_identity"]["hardware"],
        "backend_pair_context": (
            "Embree remains host-packed; OptiX candidate uses cupy_device_columns. "
            "Embree/OptiX ratios are same-contract context, not pure backend-only ratios."
        ),
        "same_contract": True,
        "all_match_cpu_reference": scale["all_match_cpu_reference"],
        "app_specific_native_engine_logic_allowed": False,
        "native_engine_customization": False,
        "partner_continuation_required": False,
        "true_zero_copy_authorized": False,
        "host_packed_ray_count_device_route": scale["optix_device_columns"]["host_packed_ray_count"],
        "logical_ray_count_device_route": scale["optix_device_columns"]["logical_ray_count"],
        "optix_host_packed_over_device_columns_cold_prepare_speedup": scale[
            "optix_host_packed_over_device_columns_cold_prepare_speedup"
        ],
        "optix_host_packed_over_device_columns_cold_plus_loop_speedup": scale[
            "optix_host_packed_over_device_columns_cold_plus_loop_speedup"
        ],
        "optix_host_packed_over_device_columns_workload_build_speedup": scale[
            "optix_host_packed_over_device_columns_workload_build_speedup"
        ],
        "optix_host_packed_over_device_columns_prepared_ray_batch_speedup": scale[
            "optix_host_packed_over_device_columns_prepared_ray_batch_speedup"
        ],
        "embree_over_optix_device_columns_hot_query_speedup": scale[
            "embree_over_optix_device_columns_hot_query_speedup"
        ],
        "embree_over_optix_device_columns_cold_plus_loop_speedup": scale[
            "embree_over_optix_device_columns_cold_plus_loop_speedup"
        ],
        "optix_device_columns_cold_plus_loop_sec": scale["optix_device_columns"]["cold_plus_loop_sec"],
        "optix_host_packed_cold_plus_loop_sec": scale["optix_host_packed"]["cold_plus_loop_sec"],
        "embree_cold_plus_loop_sec": scale["embree"]["cold_plus_loop_sec"],
        "phase_attribution": scale["phase_attribution"],
        "pre_dedup_hit_events": scale["pre_dedup_hit_events"],
        "source_provenance_disclosed": True,
        "existing_m7_row_retained": scale["exact_row_identity"]["existing_m7_row_retained"],
        "replaces_existing_m7_row": False,
        "local_gate_reading": (
            "m7_row_evidence_scoped_not_release_after_claude_codex_consensus"
            if approved
            else "final_review_pending_external_not_m7"
        ),
        "m7_promoted": approved,
    }


def _conditions(approved: bool) -> list[str]:
    if approved:
        return [
            "external_public_row_review_closed_by_claude_external_review",
            "2_ai_consensus_closed_by_claude_codex",
            "prior_subagent_only_gap_superseded_by_real_claude_review",
            "p1_wording_fix_embree_context_applied",
            "p1_wording_fix_218x_not_headline_applied",
            "p1_source_manifest_orchestration_scope_acknowledged",
            "source_manifest_traceability_recorded",
            "missing_git_head_acknowledged",
            "exact_device_column_row_identities_recorded",
            "phase_attribution_not_only_ray_batch_preparation",
            "whole_app_and_broad_v3_over_v2_claims_remain_false",
        ]
    return [
        "external_public_row_review_pending",
        "2_ai_consensus_pending",
        "source_manifest_traceability_recorded",
        "missing_git_head_acknowledged",
        "exact_device_column_row_identities_recorded",
        "phase_attribution_not_only_ray_batch_preparation",
        "whole_app_and_broad_v3_over_v2_claims_remain_false",
    ]


def _decision_audit(approved: bool) -> dict[str, str]:
    if approved:
        return {
            "decision": (
                "promote both exact cupy_device_columns grouped_sum rows as supplemental "
                "row-scoped M7 evidence after real Claude external review, P1 fixes, and Codex supersession consensus"
            ),
            "was_i_foolish": (
                "No for this corrected decision. It replaces the old Codex-subagent-only procedural gap "
                "with a real Claude external review, applies the required P1 fixes, and still keeps V3 "
                "release, true_zero_copy_authorized, whole-app, and broad V3-over-V2 claims false."
            ),
            "foolish_actions": (
                "It would be foolish to headline the 218.248x cold-prepare phase ratio, call the "
                "Embree/device-column comparison pure backend-only, or imply that two grouped_sum rows "
                "finish the V3 release."
            ),
            "other_path": (
                "Keep the rows pending because the old packet used a Codex subagent. That would be "
                "procedurally safer than pretending subagent review was enough, but now the real Claude "
                "review lets us close the gap directly."
            ),
            "different_path_now": (
                "Record Claude's superseding external review, keep the old subagent route as historical, "
                "promote only the exact rows, update global M7 classification, and continue the generic-engine queue."
            ),
        }
    return {
        "decision": (
            "prepare exact cupy_device_columns grouped_sum rows for final M7 review "
            "without promoting them before external review"
        ),
        "was_i_foolish": "No. This preserves the distinction between strong evidence and an authorized M7 row.",
        "foolish_actions": (
            "It would be foolish to treat the reopened review as promotion, hide the missing "
            "git HEAD/source-manifest provenance, or describe the 218x cold-prepare result "
            "as only ray-batch preparation."
        ),
        "other_path": (
            "Move to the next app. That would leave the strongest current generic-engine "
            "candidate stuck in limbo."
        ),
        "different_path_now": (
            "Ask for final packet review, apply P0/P1 fixes, then decide whether "
            "these exact rows can become supplemental M7 rows."
        ),
    }


def _approved_wording(rows: list[dict[str, Any]]) -> str:
    parts = []
    for row in rows:
        parts.append(
            "For a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada "
            f"Generation pod, {row['generated_rows']:,} rows / {row['generated_groups']:,} groups, "
            f"{row['logical_ray_count']:,} logical rays, warmup=3 and actual repeat=100, "
            "RTDL's OptiX route prepared the ray batch from cupy_device_columns with "
            f"host_packed_ray_count=0. Compared with the host-packed OptiX route, cold "
            f"prepare plus the measured repeat100 loop was {row['optix_host_packed_over_device_columns_cold_plus_loop_speedup']:.3f}x faster. "
            "Embree remains the host-packed route while the OptiX candidate uses cupy_device_columns; "
            f"under that same grouped_sum contract, the OptiX device-column route was {row['embree_over_optix_device_columns_cold_plus_loop_speedup']:.3f}x faster than Embree for cold prepare plus repeat100 loop. "
            "That Embree/device-column ratio is same-contract context, not a pure backend-only ratio. "
            "This is a row-scoped prepared grouped_reduction result, not a whole-app, whole-database, true_zero_copy_authorized, or broad V3-over-V2 speedup claim."
        )
    return "\n\n".join(parts)


def _source_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    out = dict(provenance)
    out.update(
        {
            "source_manifest_does_not_cover_orchestration_wrappers": True,
            "manifested_benchmark_entry_point": "scripts/v3_0_m28_raydb_prepared_grouped_refresh.py",
            "raw_json_version_confirms_manifested_entry_point": True,
            "orchestration_wrappers_not_manifested": [
                "scripts/v3_phoenix_grouped_reduction_device_column_pod_evidence.py",
                "scripts/v3_phoenix_grouped_reduction_device_column_m7_final_review_packet.py",
            ],
            "source_manifest_scope_p1_acknowledgement": (
                "The remote pod directory was not a git checkout. The source manifest hashes the "
                "runtime, benchmark app, VERSION, and measured M28 benchmark entry point, but not "
                "the local orchestration wrappers. Claude accepted this as a traceability gap rather "
                "than an integrity failure for this run; future reruns should expand the manifest scope."
            ),
        }
    )
    return out


def render_markdown(payload: dict[str, Any]) -> str:
    rows = payload["candidate_rows"]
    row_table = "\n".join(
        "| {row_id} | {rows:,} | {groups:,} | {rays:,} | {host_device:.3f}x | {embree_device:.3f}x | {status} |".format(
            row_id=row["row_id"],
            rows=row["generated_rows"],
            groups=row["generated_groups"],
            rays=row["logical_ray_count"],
            host_device=row["optix_host_packed_over_device_columns_cold_plus_loop_speedup"],
            embree_device=row["embree_over_optix_device_columns_cold_plus_loop_speedup"],
            status=row["local_gate_reading"],
        )
        for row in rows
    )
    phase_table = "\n".join(
        "| {row_id} | {build:.3f}x | {ray_batch:.3f}x | {note} |".format(
            row_id=row["row_id"],
            build=row["optix_host_packed_over_device_columns_workload_build_speedup"],
            ray_batch=row["optix_host_packed_over_device_columns_prepared_ray_batch_speedup"],
            note=row["phase_attribution"]["largest_524288_note"],
        )
        for row in rows
    )
    source_entries = "\n".join(payload["source_provenance"]["source_manifest_entries"])
    conditions = "\n".join(f"- `{item}`" for item in payload["closed_or_pending_promotion_conditions"])
    p1_fixes = "\n".join(f"- {item}" for item in payload["p1_review_fixes_applied"]) or "- none recorded"
    boundaries = "\n".join(f"- {item}" for item in payload["remaining_non_release_boundaries"])
    forbidden = "\n".join(f"- Do not claim: {item}" for item in payload["forbidden_public_wording"])
    audit = payload["goal_level_decision_audit"]
    wording = payload["approved_row_scoped_public_wording"] or payload["draft_public_wording_not_publishable"]
    return f"""# Phoenix V3 Grouped-Reduction Device-Column M7 Final Review Packet

Packet path: `{payload['packet_path']}`

Status: {payload['status']}.

```text
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: {str(payload['row_scoped_public_speedup_claim_authorized']).lower()}
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}
Phoenix scoped row-evidence rows from this packet: {payload['m7_qualified_release_rows']}
```

## Candidate Rows

| Candidate row id | Rows | Groups | Logical rays | Host-packed OptiX/device-column OptiX cold+loop | Embree/device-column OptiX cold+loop | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
{row_table}

These rows are exact `cupy_device_columns` prepared grouped_sum candidates. They
do not replace the existing host-packed/scalar-broadcast M7 row.

## Phase Attribution

The cold-prepare win includes workload-build/input-path collapse, ray-batch
preparation, native prepare, and other measured cold setup. It must not be
described as only ray-batch preparation.

| Candidate row id | Host/device workload build | Host/device ray-batch prepare | Note |
| --- | ---: | ---: | --- |
{phase_table}

## Source Provenance

The raw POD evidence JSONs do not have a git HEAD:

```text
{payload['source_provenance']['raw_payload_git_head_values'][0]}
```

Source traceability is therefore:

```text
{payload['source_provenance']['source_manifest_path']}
```

Manifest entries:

```text
{source_entries}
```

Manifest scope note:

```text
{payload['source_provenance']['source_manifest_scope_p1_acknowledgement']}
```

## Public Wording

Current wording status:

```text
{payload['current_packet_external_review_status']}
{payload['current_packet_2ai_consensus_status']}
```

{"Approved wording" if payload["row_scoped_public_speedup_claim_authorized"] else "Draft wording"}:

```text
{wording}
```

## P1 Review Fixes

{p1_fixes}

## Promotion Conditions

{conditions}

## Remaining Boundaries

{boundaries}

## Forbidden Public Wording

{forbidden}

## Review Targets

External review target:

```text
{payload['external_review']}
```

External AI blocked note:

```text
{payload['external_ai_blocked_note']}
```

Codex consensus target:

```text
{payload['codex_consensus']}
```

Prior substitute review, kept as historical but superseded:

```text
{payload['prior_substitute_review']}
{payload['prior_substitute_consensus']}
```

## Goal-Level Decision Audit

Decision: {audit['decision']}

1. Was I foolish?
   {audit['was_i_foolish']}
2. If yes, what actions made the decision foolish?
   {audit['foolish_actions']}
3. Was there another path that would have avoided getting stuck on that idea?
   {audit['other_path']}
4. Can I now try a different path that actually solves the problem?
   {audit['different_path_now']}
"""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
