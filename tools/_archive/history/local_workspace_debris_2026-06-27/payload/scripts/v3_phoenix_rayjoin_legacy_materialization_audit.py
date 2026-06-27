#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "current" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rayjoin_legacy_materialization_audit_2026-06-22.json"
OUT_MD = OUT_JSON.with_suffix(".md")


def build_payload() -> dict[str, Any]:
    source_text = SOURCE.read_text(encoding="utf-8")
    source_checks = {
        "default_lsi_host_left_route_present": "prepared_right_host_left_exact_count" in source_text,
        "pip_partial_host_refine_boundary_recorded": (
            "partial_exact_prepared_points" in source_text
            and "downloads candidates and refines membership on the host" in source_text
        ),
        "pip_relation_status_device_executor_present": (
            "validated_relation_status_corrected_executor" in source_text
            and "row_stream_materialized" in source_text
            and "native_exact_device_scalar_count_produced" in source_text
        ),
        "lsi_dense_device_column_route_present": "dense_left_id_count_device_column_complete" in source_text,
        "overlay_device_continuation_route_present": (
            "shape_pair_active_count_prepared_left_executor_device_continuation_probe" in source_text
            and "only the scalar count is copied back" in source_text
        ),
        "claim_boundaries_present": (
            "rtdl_beats_rayjoin_claim_authorized" in source_text
            and "true_zero_copy_claim_authorized" in source_text
        ),
    }
    failed_checks = [name for name, ok in source_checks.items() if not ok]
    route_assessments = [
        {
            "route": "pip_exact_prepared_points",
            "source": "host_candidate_download_and_host_exact_refine",
            "evidence": "device_resident_continuation_status says exact authority still downloads candidates and refines membership on host.",
            "v3_runtime_source_exists": True,
            "immediate_material_probe": False,
            "reason": "It has a host boundary, but it is also the validation authority path. It should not be used as a speed claim without a validated device replacement.",
        },
        {
            "route": "pip_relation_status_corrected_executor",
            "source": "device_resident_scalar_count_executor",
            "evidence": "native_phase_timings record row_stream_materialized false, candidate_download 0.0, and native_exact_device_scalar_count_produced.",
            "v3_runtime_source_exists": True,
            "immediate_material_probe": True,
            "reason": "This is the cleanest RayJoin topology-stream candidate to productize through the prepared execution runner.",
        },
        {
            "route": "lsi_default_count",
            "source": "host_packed_left_exact_count",
            "evidence": "default count metadata labels route prepared_right_host_left_exact_count.",
            "v3_runtime_source_exists": True,
            "immediate_material_probe": False,
            "reason": "A better LSI route already exists through prepared-left/dense device columns, so this is a baseline source, not the next trunk target.",
        },
        {
            "route": "lsi_dense_left_id_count",
            "source": "device_resident_left_id_count_column",
            "evidence": "device_resident_continuation_status says count[index] remains CUDA-resident and prepared-left upload is paid once.",
            "v3_runtime_source_exists": False,
            "immediate_material_probe": False,
            "reason": "The current hot route already removed the host boundary; wrapping it alone risks another RTDBSCAN-like parity result.",
        },
        {
            "route": "overlay_active_count_device_continuation",
            "source": "device_resident_shape_pair_active_count_executor",
            "evidence": "device continuation says relation flags stay on device and only scalar count is copied back.",
            "v3_runtime_source_exists": False,
            "immediate_material_probe": False,
            "reason": "The current hot route is already device-continuation based; it is a later generalization target, not the first material probe.",
        },
    ]
    return {
        "artifact": "phoenix_v3_rayjoin_legacy_materialization_audit_2026-06-22",
        "status": "rayjoin_materialization_audit_complete_not_release",
        "date": "2026-06-22",
        "scope": "Phoenix V3 RayJoin Step G1 local/source audit",
        "source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "external_embedding_or_zero_copy_claim_authorized": False,
        "all_app_pod_spend_authorized": False,
        "focused_pod_spend_authorized": False,
        "rayjoin_as_whole_app_target": False,
        "rayjoin_topology_stream_family_target": True,
        "host_materialization_source_exists": True,
        "current_hot_routes_already_eliminate_many_host_boundaries": True,
        "recommended_next_probe": "pip_relation_status_corrected_executor_through_prepared_execution_runner",
        "recommended_next_probe_scope": (
            "Productize the existing point_location_topology_stream relation-status corrected scalar-count "
            "route through the shared prepared execution/session runner. Do not present this as full RayJoin."
        ),
        "pod_decision": (
            "No pod yet. First add local runner metadata/tests and confirm the comparison basis: "
            "runner-vs-legacy/current-legacy path for productization credit, and V3 runner vs V2.14 "
            "for release-score evidence."
        ),
        "route_assessments": route_assessments,
        "source_checks": source_checks,
        "failed_checks": failed_checks,
        "exit_criteria": {
            "legacy_host_boundary_identified": True,
            "current_hot_route_risk_identified": True,
            "next_scope_is_runtime_family_not_app": True,
            "pod_blocked_until_runner_wiring": True,
            "release_gate_stays_redo_required": True,
        },
        "goal_level_decision_audit": {
            "decision": "Use RayJoin only as a point-location topology-stream family candidate, not as a full-app pod target.",
            "was_i_foolish": "No. This avoids direct pod spend before identifying where a real host-boundary source exists.",
            "foolish_actions": (
                "It would be foolish to run full RayJoin or quote old large OptiX-over-Embree ratios without "
                "separating host-boundary sources from routes that are already device resident."
            ),
            "other_path": (
                "Run the RayJoin pod immediately. That would be faster administratively, but likely repeats "
                "RTDBSCAN's failure mode if the selected hot route already removed the host boundary."
            ),
            "different_path_now": (
                "Productize one topology-stream route through the shared runner first, then spend pod time only "
                "on a focused runner-vs-legacy comparison."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 RayJoin Legacy Materialization Audit",
        "",
        "Date: 2026-06-22",
        f"Status: `{payload['status']}`",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"broad_v3_faster_than_v2_claim_authorized: {str(payload['broad_v3_faster_than_v2_claim_authorized']).lower()}",
        f"all_app_pod_spend_authorized: {str(payload['all_app_pod_spend_authorized']).lower()}",
        f"focused_pod_spend_authorized: {str(payload['focused_pod_spend_authorized']).lower()}",
        "```",
        "",
        "## Decision",
        "",
        "RayJoin is a valid next Phoenix V3 family only as a",
        "`point_location_topology_stream` runtime-family probe. It is not a",
        "whole-app target and it does not authorize pod spend yet.",
        "",
        f"Recommended next probe: `{payload['recommended_next_probe']}`",
        "",
        payload["recommended_next_probe_scope"],
        "",
        "## Route Assessment",
        "",
        "| Route | Source | V3 Source Exists | Immediate Probe | Reading |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for route in payload["route_assessments"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{route['route']}`",
                    route["source"],
                    str(route["v3_runtime_source_exists"]).lower(),
                    str(route["immediate_material_probe"]).lower(),
                    route["reason"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Pod Decision",
            "",
            payload["pod_decision"],
            "",
            "## Checks",
            "",
        ]
    )
    for name, ok in payload["source_checks"].items():
        lines.append(f"- `{name}`: `{str(ok).lower()}`")
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
            "## Non-Authorization",
            "",
            "This audit authorizes no release, no public speedup wording, no broad",
            "V3-over-V2.x wording, no true-zero-copy wording, no external embedding",
            "wording, and no pod spend. Release remains `redo_required`.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit RayJoin host-boundary sources before pod spend.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload["exit_criteria"], indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
