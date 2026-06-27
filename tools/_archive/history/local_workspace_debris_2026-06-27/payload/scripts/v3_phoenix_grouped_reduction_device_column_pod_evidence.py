#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_grouped_reduction_device_columns_20260621"
)
DEFAULT_JSON_OUT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.json"
)
DEFAULT_MD_OUT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.md"
)
SCALES = (262144, 524288)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 grouped-reduction device-column pod evidence packet."
    )
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args.evidence_dir)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0


def build_payload(evidence_dir: Path = DEFAULT_EVIDENCE_DIR) -> dict[str, Any]:
    scales = [_scale_summary(evidence_dir, scale) for scale in SCALES]
    source_provenance = _source_provenance(evidence_dir, scales)
    checks = {
        "all_sources_exist": all(scale["source_files_exist"] for scale in scales),
        "all_payloads_ok": all(scale["status"] == "ok" for scale in scales),
        "all_cpu_reference_match": all(scale["all_match_cpu_reference"] for scale in scales),
        "all_warmup3_repeat100": all(scale["warmup"] == 3 and scale["repeat"] == 100 for scale in scales),
        "all_device_columns_used": all(scale["device_columns_route_ok"] for scale in scales),
        "all_host_packed_baselines_used": all(scale["host_packed_baseline_ok"] for scale in scales),
        "all_logical_ray_counts_match": all(scale["logical_ray_counts_match"] for scale in scales),
        "all_host_packed_rays_eliminated_on_device_route": all(
            scale["host_packed_rays_eliminated_on_device_route"] for scale in scales
        ),
        "all_host_to_device_cold_prepare_material": all(
            scale["optix_host_packed_over_device_columns_cold_prepare_speedup"] >= 5.0
            for scale in scales
        ),
        "all_host_to_device_cold_plus_loop_material": all(
            scale["optix_host_packed_over_device_columns_cold_plus_loop_speedup"] >= 3.0
            for scale in scales
        ),
        "all_embree_to_device_hot_material": all(
            scale["embree_over_optix_device_columns_hot_query_speedup"] >= 100.0 for scale in scales
        ),
        "run_status_zero": _read_optional(evidence_dir / "run_device_columns_repeat100.status").strip() == "0",
        "hardware_manifest_present": (evidence_dir / "nvidia-smi.txt").exists(),
        "source_manifest_present": (evidence_dir / "source_manifest.sha256").exists(),
        "source_manifest_bound_to_packet": source_provenance["source_manifest_is_traceability_record"],
        "raw_git_head_gap_acknowledged": source_provenance["git_head_missing_acknowledged"],
        "exact_row_identities_defined": all(scale["candidate_row_id"] for scale in scales),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    m7_reopen_candidate = not failed_checks
    return {
        "tool": "v3_phoenix_grouped_reduction_device_column_pod_evidence",
        "version": "phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026_06_21",
        "status": (
            "grouped_reduction_device_column_ray_batch_pod_evidence_pending_2ai_not_m7"
            if m7_reopen_candidate
            else "grouped_reduction_device_column_ray_batch_pod_evidence_failed_not_m7"
        ),
        "generic_capability": "grouped_reduction",
        "candidate_scope": (
            "generic prepared grouped_sum ray-batch input route: cupy device columns "
            "versus host-packed OptiX rays, with Embree same-contract context"
        ),
        "source_candidate_packet": (
            "docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_candidate_2026-06-21.md"
        ),
        "evidence_dir": _rel(evidence_dir),
        "source_provenance": source_provenance,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "m7_promoted": False,
        "m7_reopen_candidate_pending_2ai_review": m7_reopen_candidate,
        "candidate_exact_rows": [scale["exact_row_identity"] for scale in scales],
        "scales": scales,
        "summary": {
            "scale_count": len(scales),
            "m7_reopen_candidate_pending_2ai_review": m7_reopen_candidate,
            "min_host_packed_over_device_columns_cold_prepare_speedup": min(
                scale["optix_host_packed_over_device_columns_cold_prepare_speedup"] for scale in scales
            ),
            "min_host_packed_over_device_columns_cold_plus_loop_speedup": min(
                scale["optix_host_packed_over_device_columns_cold_plus_loop_speedup"] for scale in scales
            ),
            "max_host_packed_over_device_columns_cold_plus_loop_speedup": max(
                scale["optix_host_packed_over_device_columns_cold_plus_loop_speedup"] for scale in scales
            ),
            "min_embree_over_optix_device_columns_hot_query_speedup": min(
                scale["embree_over_optix_device_columns_hot_query_speedup"] for scale in scales
            ),
            "min_embree_over_optix_device_columns_cold_plus_loop_speedup": min(
                scale["embree_over_optix_device_columns_cold_plus_loop_speedup"] for scale in scales
            ),
            "all_cpu_reference_match": all(scale["all_match_cpu_reference"] for scale in scales),
            "all_host_packed_rays_eliminated_on_device_route": all(
                scale["host_packed_rays_eliminated_on_device_route"] for scale in scales
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "public_copy_rules": [
            "Say this is a grouped_sum prepared-query route candidate, not whole RayDB.",
            "Say cupy_device_columns avoids host-packed ray-record materialization on the OptiX route.",
            "Report host-packed OptiX versus device-column OptiX before quoting Embree/OptiX ratios.",
            "Report cold prepare and cold-plus-loop next to hot prepared-query timing.",
            "Say the cold-prepare win includes workload-build/input-path collapse, not only ray-batch preparation.",
            "State that Embree and OptiX pre-dedup hit-event counts can differ while CPU-reference reduction still matches.",
            "Name the RTX 4000 Ada pod, generated row count, logical ray count, warmup, and repeat.",
            "Keep public release wording blocked until 2-AI review closes.",
        ],
        "forbidden_public_wording": [
            "release wording for V3",
            "broad V3-over-V2 win",
            "RayDB is universally accelerated",
            "This proves true zero-copy",
            "This is an M7-qualified row before 2-AI review",
            "All grouped_reduction rows are now public claims",
        ],
        "next_actions": [
            "Send this packet to Claude/Gemini for critical review.",
            "If review approves, treat this as a new exact row candidate keyed by cupy_device_columns, not an implicit replacement of the current grouped_reduction M7 row.",
            "Update the public grouped_sum tutorial only after the review-bound wording is closed.",
            "Continue the next generic-engine queue item if review rejects or scopes this as internal only.",
        ],
        "goal_level_decision_audit": {
            "decision": (
                "convert the POD device-column grouped_reduction results into a pending-2AI "
                "M7 reopen candidate instead of promoting it immediately"
            ),
            "was_i_foolish": "No. The measured gains are material, but public promotion still needs review.",
            "foolish_actions": (
                "It would be foolish to advertise the 173x/203x hot query ratios alone, "
                "or to call the device-column route true zero-copy, or to skip the host-packed "
                "OptiX baseline that explains why V3 changed technically."
            ),
            "other_path": (
                "Promote the existing 262,144-row M7 result and keep polishing docs. "
                "That would avoid risk but would not answer the user's performance-first concern."
            ),
            "different_path_now": (
                "Treat this as a generic engine improvement: prove host packing is removed, "
                "show cold-plus-loop speedups, then ask external review whether the row can "
                "enter the V3 release surface."
            ),
        },
    }


def _scale_summary(evidence_dir: Path, scale: int) -> dict[str, Any]:
    device_path = evidence_dir / f"grouped_sum_device_columns_{scale}_repeat100.json"
    host_path = evidence_dir / f"grouped_sum_host_packed_optix_{scale}_repeat100.json"
    device_payload = _read_json(device_path)
    host_payload = _read_json(host_path)
    rows = {(row["backend"], row["mode"]): row for row in device_payload["rows"]}
    embree = rows[("embree", "sum")]
    device_optix = rows[("optix", "sum")]
    host_optix = host_payload["rows"][0]

    embree_cold_plus_loop = _cold_plus_loop(embree)
    device_cold_plus_loop = _cold_plus_loop(device_optix)
    host_cold_plus_loop = _cold_plus_loop(host_optix)
    logical_ray_counts_match = (
        int(embree["logical_ray_count"])
        == int(device_optix["logical_ray_count"])
        == int(host_optix["logical_ray_count"])
    )
    repeat = int(device_optix["repeat"])
    warmup = int(device_optix["warmup"])
    groups = int(device_payload["parameters"]["generated_groups"])
    logical_ray_count = int(device_optix["logical_ray_count"])
    candidate_row_id = f"grouped_reduction_sum_cupy_device_columns_repeat100_{scale}_rows_{groups}_groups"
    return {
        "candidate_row_id": candidate_row_id,
        "exact_row_identity": {
            "row_id": candidate_row_id,
            "promotion_status": "m7_reopen_candidate_pending_2ai_review_not_m7",
            "generic_capability": "grouped_reduction",
            "operation": "prepared_grouped_sum_i64",
            "ray_batch_layout": "cupy_device_columns",
            "generated_rows": scale,
            "generated_groups": groups,
            "logical_ray_count": logical_ray_count,
            "warmup": warmup,
            "repeat": repeat,
            "hardware": device_payload["environment"]["nvidia_smi"],
            "scope": "prepared grouped_sum only; not RayDB whole-app and not all grouped_reduction rows",
            "replaces_existing_m7_row": False,
            "existing_m7_row_retained": "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
        },
        "generated_rows": scale,
        "generated_groups": groups,
        "logical_ray_count": logical_ray_count,
        "repeat": repeat,
        "warmup": warmup,
        "status": device_payload["status"],
        "environment_git_heads": {
            "device_columns_payload": device_payload["environment"].get("git_head", ""),
            "host_packed_payload": host_payload["environment"].get("git_head", ""),
        },
        "source_files": {
            "device_columns": _rel(device_path),
            "host_packed_optix": _rel(host_path),
        },
        "source_files_exist": device_path.exists() and host_path.exists(),
        "all_match_cpu_reference": bool(
            device_payload["comparison"]["all_match_cpu_reference"]
            and host_payload["comparison"]["all_match_cpu_reference"]
            and embree["matches_cpu_reference"]
            and device_optix["matches_cpu_reference"]
            and host_optix["matches_cpu_reference"]
        ),
        "device_columns_route_ok": bool(
            device_optix["prepared_ray_batch_layout"] == "cupy_device_columns"
            and device_optix["prepared_ray_batch_created_from"] == "partner_device_columns"
            and device_optix["prepared_ray_batch_column_partner"] == "cupy"
            and device_optix["native_device_column_path_used"]
        ),
        "host_packed_baseline_ok": bool(
            host_optix["prepared_ray_batch_layout"] == "host_packed"
            and host_optix["prepared_ray_batch_created_from"] == "host_packed_rays"
            and not host_optix["native_device_column_path_used"]
        ),
        "logical_ray_counts_match": logical_ray_counts_match,
        "host_packed_rays_eliminated_on_device_route": bool(
            int(device_optix["host_packed_ray_count"]) == 0
            and int(host_optix["host_packed_ray_count"]) == int(device_optix["logical_ray_count"])
        ),
        "embree": _row_metrics(embree, embree_cold_plus_loop),
        "optix_device_columns": _row_metrics(device_optix, device_cold_plus_loop),
        "optix_host_packed": _row_metrics(host_optix, host_cold_plus_loop),
        "pre_dedup_hit_events": {
            "embree": int(embree["hit_event_count_before_dedup"]),
            "optix_device_columns": int(device_optix["hit_event_count_before_dedup"]),
            "optix_host_packed": int(host_optix["hit_event_count_before_dedup"]),
            "interpretation": (
                "pre-dedup hit-event counts can differ across Embree and OptiX, "
                "but all rows match the CPU reference after grouped reduction"
            ),
        },
        "phase_attribution": {
            "cold_prepare_speedup_includes": [
                "workload_build_sec",
                "prepared_ray_batch_sec",
                "native_prepare_sec",
                "other measured cold setup",
            ],
            "not_only_ray_batch_prepare": True,
            "largest_524288_note": (
                "At 524,288 rows the largest cold-prepare win is mostly workload_build_sec "
                "collapsing from host-packed ray materialization to deferred device columns."
            )
            if scale == 524288
            else "At 262,144 rows both workload_build_sec and prepared_ray_batch_sec improve materially.",
        },
        "optix_host_packed_over_device_columns_cold_prepare_speedup": _ratio(
            host_optix["cold_prepare_total_sec"], device_optix["cold_prepare_total_sec"]
        ),
        "optix_host_packed_over_device_columns_prepared_ray_batch_speedup": _ratio(
            host_optix["prepared_ray_batch_sec"], device_optix["prepared_ray_batch_sec"]
        ),
        "optix_host_packed_over_device_columns_workload_build_speedup": _ratio(
            host_optix["workload_build_sec"], device_optix["workload_build_sec"]
        ),
        "optix_host_packed_over_device_columns_hot_loop_speedup": _ratio(
            host_optix["prepared_iteration_total_sec"], device_optix["prepared_iteration_total_sec"]
        ),
        "optix_host_packed_over_device_columns_cold_plus_loop_speedup": _ratio(
            host_cold_plus_loop, device_cold_plus_loop
        ),
        "embree_over_optix_device_columns_hot_query_speedup": _ratio(
            embree["elapsed_median_sec"], device_optix["elapsed_median_sec"]
        ),
        "embree_over_optix_device_columns_repeat100_loop_speedup": _ratio(
            embree["prepared_iteration_total_sec"], device_optix["prepared_iteration_total_sec"]
        ),
        "embree_over_optix_device_columns_cold_plus_loop_speedup": _ratio(
            embree_cold_plus_loop, device_cold_plus_loop
        ),
        "claim_status": "pending_2ai_review_not_m7",
    }


def _row_metrics(row: dict[str, Any], cold_plus_loop: float) -> dict[str, Any]:
    return {
        "backend": row["backend"],
        "layout": row["prepared_ray_batch_layout"],
        "created_from": row.get("prepared_ray_batch_created_from"),
        "native_device_column_path_used": bool(row["native_device_column_path_used"]),
        "host_packed_ray_count": int(row["host_packed_ray_count"]),
        "logical_ray_count": int(row["logical_ray_count"]),
        "workload_build_sec": float(row["workload_build_sec"]),
        "cold_prepare_total_sec": float(row["cold_prepare_total_sec"]),
        "prepared_ray_batch_sec": float(row["prepared_ray_batch_sec"]),
        "prepared_iteration_total_sec": float(row["prepared_iteration_total_sec"]),
        "elapsed_median_sec": float(row["elapsed_median_sec"]),
        "cold_plus_loop_sec": cold_plus_loop,
        "matches_cpu_reference": bool(row["matches_cpu_reference"]),
        "rt_core_accelerated": bool(row["rt_core_accelerated"]),
    }


def _source_provenance(evidence_dir: Path, scales: list[dict[str, Any]]) -> dict[str, Any]:
    source_manifest_path = evidence_dir / "source_manifest.sha256"
    source_manifest_lines = [
        line.strip()
        for line in _read_optional(source_manifest_path).splitlines()
        if line.strip()
    ]
    raw_git_heads = sorted(
        {
            value
            for scale in scales
            for value in scale["environment_git_heads"].values()
            if value
        }
    )
    git_head_missing = any("fatal: not a git repository" in value for value in raw_git_heads)
    return {
        "source_manifest_path": _rel(source_manifest_path),
        "source_manifest_entries": source_manifest_lines,
        "source_manifest_is_traceability_record": bool(source_manifest_lines),
        "raw_payload_git_head_values": raw_git_heads,
        "remote_worktree_git_head_available": not git_head_missing,
        "git_head_missing_acknowledged": git_head_missing,
        "provenance_interpretation": (
            "The remote POD run directory was not a git checkout, so raw evidence JSONs "
            "record git_head as unavailable. The SHA256 source manifest is therefore the "
            "source traceability record for this packet."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    candidate_rows = "\n".join(
        "| {row_id} | {rows:,} | {groups:,} | {rays:,} | {layout} | {warmup} | {repeat} | {replaces} |".format(
            row_id=row["row_id"],
            rows=row["generated_rows"],
            groups=row["generated_groups"],
            rays=row["logical_ray_count"],
            layout=row["ray_batch_layout"],
            warmup=row["warmup"],
            repeat=row["repeat"],
            replaces=str(row["replaces_existing_m7_row"]).lower(),
        )
        for row in payload["candidate_exact_rows"]
    )
    scale_rows = "\n".join(
        "| {rows:,} | {rays:,} | {cold:.3f}x | {ray_batch:.3f}x | {cold_loop:.3f}x | {emb_hot:.3f}x | {emb_cold:.3f}x | {status} |".format(
            rows=scale["generated_rows"],
            rays=scale["logical_ray_count"],
            cold=scale["optix_host_packed_over_device_columns_cold_prepare_speedup"],
            ray_batch=scale["optix_host_packed_over_device_columns_prepared_ray_batch_speedup"],
            cold_loop=scale["optix_host_packed_over_device_columns_cold_plus_loop_speedup"],
            emb_hot=scale["embree_over_optix_device_columns_hot_query_speedup"],
            emb_cold=scale["embree_over_optix_device_columns_cold_plus_loop_speedup"],
            status=scale["claim_status"],
        )
        for scale in payload["scales"]
    )
    phase_rows = "\n".join(
        "| {rows:,} | {dev_build:.3f}s | {host_build:.3f}s | {build_ratio:.3f}x | {dev_ray:.3f}s | {host_ray:.3f}s | {ray_ratio:.3f}x | {dev_cold:.3f}s | {host_cold:.3f}s |".format(
            rows=scale["generated_rows"],
            dev_build=scale["optix_device_columns"]["workload_build_sec"],
            host_build=scale["optix_host_packed"]["workload_build_sec"],
            build_ratio=scale["optix_host_packed_over_device_columns_workload_build_speedup"],
            dev_ray=scale["optix_device_columns"]["prepared_ray_batch_sec"],
            host_ray=scale["optix_host_packed"]["prepared_ray_batch_sec"],
            ray_ratio=scale["optix_host_packed_over_device_columns_prepared_ray_batch_speedup"],
            dev_cold=scale["optix_device_columns"]["cold_prepare_total_sec"],
            host_cold=scale["optix_host_packed"]["cold_prepare_total_sec"],
        )
        for scale in payload["scales"]
    )
    hit_rows = "\n".join(
        "| {rows:,} | {embree:,} | {device:,} | {host:,} | {ok} |".format(
            rows=scale["generated_rows"],
            embree=scale["pre_dedup_hit_events"]["embree"],
            device=scale["pre_dedup_hit_events"]["optix_device_columns"],
            host=scale["pre_dedup_hit_events"]["optix_host_packed"],
            ok=str(scale["all_match_cpu_reference"]).lower(),
        )
        for scale in payload["scales"]
    )
    source = payload["source_provenance"]
    source_entries = "\n".join(source["source_manifest_entries"])
    git_heads = "\n".join(source["raw_payload_git_head_values"])
    route_rows = "\n".join(
        "| {rows:,} | {layout} | {created} | {native} | {host_count:,} | {logical:,} | {ok} |".format(
            rows=scale["generated_rows"],
            layout=scale["optix_device_columns"]["layout"],
            created=scale["optix_device_columns"]["created_from"],
            native=str(scale["optix_device_columns"]["native_device_column_path_used"]).lower(),
            host_count=scale["optix_device_columns"]["host_packed_ray_count"],
            logical=scale["logical_ray_count"],
            ok=str(scale["host_packed_rays_eliminated_on_device_route"]).lower(),
        )
        for scale in payload["scales"]
    )
    copy_rules = "\n".join(f"- {rule}" for rule in payload["public_copy_rules"])
    forbidden = "\n".join(f"- Do not claim: {rule}" for rule in payload["forbidden_public_wording"])
    next_actions = "\n".join(f"- {action}" for action in payload["next_actions"])
    audit = payload["goal_level_decision_audit"]
    failed = ", ".join(payload["failed_checks"]) if payload["failed_checks"] else "none"

    return f"""# Phoenix V3 Grouped-Reduction Device-Column Ray-Batch Pod Evidence

Status: pending 2-AI review, not M7 promotion and not release authorization.

```text
status: {payload['status']}
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
m7_promoted: false
m7_reopen_candidate_pending_2ai_review: {str(payload['m7_reopen_candidate_pending_2ai_review']).lower()}
failed_checks: {failed}
```

## What This Tests

This packet tests a generic V3 engine route, not a RayDB-specific native
engine: OptiX prepared grouped_sum can prepare its ray batch from
`cupy_device_columns` instead of materializing host-packed ray records first.
The same generated rows, logical ray count, warmup, repeat, and CPU-reference
checks are used for the host-packed OptiX baseline.

## Summary

- Minimum OptiX host-packed / device-column cold-prepare speedup:
  `{summary['min_host_packed_over_device_columns_cold_prepare_speedup']:.3f}x`
- Minimum OptiX host-packed / device-column cold-plus-loop speedup:
  `{summary['min_host_packed_over_device_columns_cold_plus_loop_speedup']:.3f}x`
- Maximum OptiX host-packed / device-column cold-plus-loop speedup:
  `{summary['max_host_packed_over_device_columns_cold_plus_loop_speedup']:.3f}x`
- Minimum Embree / OptiX-device-columns hot-query speedup:
  `{summary['min_embree_over_optix_device_columns_hot_query_speedup']:.3f}x`
- Minimum Embree / OptiX-device-columns cold-plus-loop speedup:
  `{summary['min_embree_over_optix_device_columns_cold_plus_loop_speedup']:.3f}x`
- All CPU references match: `{str(summary['all_cpu_reference_match']).lower()}`
- Host-packed rays eliminated on device route:
  `{str(summary['all_host_packed_rays_eliminated_on_device_route']).lower()}`

## Candidate Exact Rows

These rows are candidates for M7 reopening only. They do not replace the
already approved host-packed/scalar-broadcast row.

| Candidate row id | Rows | Groups | Logical rays | Layout | Warmup | Repeat | Replaces existing M7 row |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
{candidate_rows}

## Route Integrity

| Rows | OptiX route layout | Created from | Native device-column path | Host-packed rays on device route | Logical rays | Eliminated |
| ---: | --- | --- | --- | ---: | ---: | --- |
{route_rows}

## Performance Table

| Rows | Logical rays | Host/device cold prepare | Host/device ray-batch prepare | Host/device cold+loop | Embree/device hot query | Embree/device cold+loop | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
{scale_rows}

## Phase Table

The cold-prepare speedup includes workload-build/input-path collapse,
ray-batch preparation, native prepare, and other measured cold setup. It must
not be described as only ray-batch preparation.

| Rows | Device workload build | Host workload build | Host/device build | Device ray-batch prepare | Host ray-batch prepare | Host/device ray-batch | Device cold prepare | Host cold prepare |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{phase_rows}

## Pre-Dedup Hit Events

Embree and OptiX pre-dedup hit-event counts can differ. The semantic gate is
the grouped reduction result, and all rows match the CPU reference.

| Rows | Embree pre-dedup hits | OptiX device-column pre-dedup hits | OptiX host-packed pre-dedup hits | CPU reference match |
| ---: | ---: | ---: | ---: | --- |
{hit_rows}

## Interpretation

This is a material V3 engine optimization candidate because it attacks the
prepared grouped-reduction input path itself. The 524,288-row baseline shows
why earlier V3 wording was not enough: host-packed ray materialization can
dominate the story even when the hot RT query is fast. The device-column route
keeps the hot query essentially comparable while removing host-packed ray
records from the OptiX candidate path.

The Embree/device-column ratios are same-contract backend context, not pure
backend-only ratios, because the Embree route remains host-packed while the
OptiX candidate uses `cupy_device_columns`.

This is still not release wording. It needs external review before it can
supersede or expand the existing grouped_reduction M7 row.

## Public Copy Rules

{copy_rules}

## Forbidden Public Wording

{forbidden}

## Next Actions

{next_actions}

## Source Evidence

Source candidate packet:

```text
{payload['source_candidate_packet']}
```

POD artifact directory:

```text
{payload['evidence_dir']}
```

Source traceability record:

```text
{source['source_manifest_path']}
```

Source manifest entries:

```text
{source_entries}
```

Raw evidence git-head values:

```text
{git_heads}
```

Interpretation:

{source['provenance_interpretation']}

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


def _read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _ratio(numerator: Any, denominator: Any) -> float:
    return float(numerator) / float(denominator)


def _cold_plus_loop(row: dict[str, Any]) -> float:
    return float(row["cold_prepare_total_sec"]) + float(row["prepared_iteration_total_sec"])


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
