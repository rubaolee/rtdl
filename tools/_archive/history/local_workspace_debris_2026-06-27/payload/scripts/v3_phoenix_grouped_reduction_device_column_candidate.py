#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

RAYDB_APP = ROOT / "examples" / "current" / "research_benchmarks" / "raydb_style" / "rtdl_raydb_style_benchmark_app.py"
M28_RUNNER = ROOT / "scripts" / "v3_0_m28_raydb_prepared_grouped_refresh.py"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
GROUPED_M7_PACKET = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.json"
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    app_source = _read_text(RAYDB_APP)
    runner_source = _read_text(M28_RUNNER)
    runtime_source = _read_text(OPTIX_RUNTIME)
    grouped_packet = _load_json(GROUPED_M7_PACKET)

    checks = {
        "raydb_route_has_explicit_layout": "ray_batch_layout" in app_source,
        "raydb_route_can_defer_host_rays": "materialize_rays=ray_batch_layout == \"host_packed\"" in app_source,
        "raydb_route_can_prepare_device_columns": "prepared.prepare_ray_batch_device_columns" in app_source,
        "raydb_route_records_device_column_metadata": "\"native_device_column_path_used\": ray_batch_layout != \"host_packed\"" in app_source,
        "runner_exposes_optix_layout_switch": "--optix-ray-batch-layout" in runner_source,
        "runner_keeps_embree_host_packed": "if backend == \"optix\" else \"host_packed\"" in runner_source,
        "runner_records_host_packed_ray_count": "host_packed_ray_count" in runner_source,
        "runtime_has_generic_device_column_ray_batch": "prepare_ray_batch_device_columns" in runtime_source,
        "runtime_triangle_scalar_broadcast_added": "triangle field {name} length must match ids length" in runtime_source,
        "current_m7_packet_still_single_row": grouped_packet.get("m7_qualified_release_rows") == 1,
        "current_m7_packet_release_false": grouped_packet.get("release_authorized") is False,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "grouped_reduction_device_column_ray_batch_candidate_pending_pod_not_m7"

    rerun_command = (
        "py -3 scripts/v3_0_m28_raydb_prepared_grouped_refresh.py "
        "--generated-rows 524288 --generated-groups 2048 --generated-revenue-mod 64 "
        "--modes sum --backends embree,optix --warmup 3 "
        "--repeat-overrides embree:sum=100,optix:sum=100 "
        "--optix-ray-batch-layout cupy_device_columns "
        "--output docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_YYYYMMDD/"
        "grouped_sum_device_columns_524288_repeat100.json"
    )

    return {
        "tool": "v3_phoenix_grouped_reduction_device_column_candidate",
        "status": status,
        "generic_capability": "grouped_reduction",
        "candidate": "prepared_grouped_reduction_cupy_device_column_ray_batch",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "existing_m7_row_unchanged": "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
        "default_route_unchanged": True,
        "why_this_is_generic_engine_work": (
            "The candidate reuses RTDL's generic prepared ray-batch device-column ABI "
            "and generic ray/triangle grouped i64 reduction. RayDB remains only the "
            "evidence harness that supplies columns and checks the CPU oracle."
        ),
        "what_changed": [
            "RayDB prepared grouped reduction accepts explicit ray_batch_layout.",
            "host_packed remains the default and the current M7 evidence path.",
            "cupy_device_columns can defer Python host ray-record materialization and prepare the OptiX ray batch from partner-owned CUDA columns.",
            "The M28 runner records prepared_ray_batch_layout, native_device_column_path_used, logical_ray_count, and host_packed_ray_count.",
            "The generic 3-D triangle packer now accepts scalar fields just like the 3-D ray packer.",
        ],
        "modified_sources": [
            "examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py",
            "scripts/v3_0_m28_raydb_prepared_grouped_refresh.py",
            "src/rtdsl/optix_runtime.py",
        ],
        "required_pod_evidence_before_any_promotion": [
            "same RTX/RT-core host for Embree and OptiX",
            "same generated_rows/generated_groups/mode/repeat/warmup",
            "CPU-reference parity for both backends",
            "prepared_ray_batch_layout=cupy_device_columns on OptiX rows",
            "native_device_column_path_used=true on OptiX rows",
            "host_packed_ray_count=0 and logical_ray_count>0 on OptiX candidate rows",
            "cold_prepare_total_sec, workload_build_sec, prepared_ray_batch_sec, prepared_iteration_total_sec, and native_call_wall_median_sec recorded",
            "source manifest and 2-AI review before any M7 reopening",
        ],
        "rerun_command": rerun_command,
        "forbidden_wording": [
            "Do not claim the device-column candidate is faster before pod evidence exists.",
            "Do not replace the current grouped_reduction M7 row with this candidate without fresh M7 review.",
            "Do not call this true zero-copy; it is an explicit V3 partner-device ray-column route, not V4 interop.",
            "Do not promote whole RayDB or count rows from this code change alone.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "add an explicit device-column ray-batch candidate for grouped-reduction prepare amortization, with release flags false",
            "was_i_foolish": "No. The current 524,288-row blocker is dominated by host ray-record construction and ray-batch preparation, so the next honest path is to test an existing generic device-column ABI instead of polishing prose.",
            "foolish_actions": "It would be foolish to call this a V3 performance win before the pod rerun, or to hide that the current M7 row remains only the 262,144-row host-packed repeat100 case.",
            "other_path": "Keep tuning RayDB-specific encoding or rewrite a native database operator. That would violate the Phoenix requirement that apps are evidence harnesses, not V3 products.",
            "different_path_now": "Run the explicit cupy_device_columns candidate on the RT hardware pod, compare against the host-packed/current route, and only reopen M7 if wall and cold-plus-loop evidence materially improves.",
        },
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 Grouped-Reduction Device-Column Ray-Batch Candidate",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This is a candidate for the `grouped_reduction_prepare_amortization`",
        "queue item. It is not release authorization and not an M7 promotion.",
        "",
        "Current flags:",
        "",
        f"- `release_authorized: {str(payload['release_authorized']).lower()}`",
        f"- `public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}`",
        f"- `whole_app_speedup_claim_authorized: {str(payload['whole_app_speedup_claim_authorized']).lower()}`",
        f"- `m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}`",
        f"- `default_route_unchanged: {str(payload['default_route_unchanged']).lower()}`",
        "",
        "Why this is generic engine work:",
        "",
        payload["why_this_is_generic_engine_work"],
        "",
        "## What Changed",
        "",
    ]
    for item in payload["what_changed"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Required Pod Evidence", ""])
    for item in payload["required_pod_evidence_before_any_promotion"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Rerun Command", "", "```powershell", payload["rerun_command"], "```"])

    lines.extend(["", "## Forbidden Wording", ""])
    for item in payload["forbidden_wording"]:
        lines.append(f"- {item}")

    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            f"   {audit['was_i_foolish']}",
            "2. If yes, what actions made the decision foolish?",
            f"   {audit['foolish_actions']}",
            "3. Was there another path?",
            f"   {audit['other_path']}",
            "4. Can I now try a different path that actually solves the problem?",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit the Phoenix V3 grouped-reduction device-column ray-batch candidate packet."
    )
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(_render_markdown(payload), encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "grouped_reduction_device_column_ray_batch_candidate_pending_pod_not_m7" else 2


if __name__ == "__main__":
    raise SystemExit(main())
