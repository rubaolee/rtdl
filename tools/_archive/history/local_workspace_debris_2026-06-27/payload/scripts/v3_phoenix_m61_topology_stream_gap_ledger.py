#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl import prepared_execution  # noqa: E402
from rtdsl.v3_0_topology_stream_accounting import (  # noqa: E402
    TOPOLOGY_STREAM_M3_PHASES,
    TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT,
    TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT,
)


SCHEMA = "rtdl.phoenix_v3.m61.topology_stream_gap_ledger.v1"
STATUS_OK = "m61_topology_stream_gap_ledger_ready_local_no_pod_not_release"
STATUS_FAIL = "m61_topology_stream_gap_ledger_failed"
INTERNAL_DELTA_LABEL = "internal_routing_delta_not_public_row"
INTERNAL_DELTA_SANITY_MIN_EXCLUSIVE = 1.0
INTERNAL_DELTA_SANITY_MAX_EXCLUSIVE = 10.0
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")
M60_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m60_step2_set_a_selection_3ai_consensus_2026-06-23.md"
)
M3_GAP_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.json"
)
TOPOLOGY_CONTRACT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.json"
)
PREPARED_EXECUTION_SOURCE = ROOT / "src" / "rtdsl" / "prepared_execution.py"
M50_RUNNER = ROOT / "scripts" / "v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py"
M50_SUPERSEDED_TOKEN = "M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED"
M66_ACTIVE_TOKEN = "M66_SOURCE_SIGNATURE_GATED_TOPOLOGY_STREAM_M3_POD_AUTHORIZED"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 M61 topology-stream local gap ledger."
    )
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def build_payload() -> dict[str, Any]:
    m60_consensus = M60_CONSENSUS.read_text(encoding="utf-8")
    m50_source = M50_RUNNER.read_text(encoding="utf-8")
    m3_gap = _read_json(M3_GAP_JSON)
    topology_contract = _read_json(TOPOLOGY_CONTRACT_JSON)
    point_location_probe = _run_point_location_topology_stream_probe_metadata()
    segment_intersection_probe = _run_segment_intersection_topology_stream_probe_metadata()

    large_delta = m3_gap["large_pip_device_resident_delta"]
    phase_bridge = {
        "prepared_execution_required_phases": list(
            prepared_execution.PREPARED_EXECUTION_REQUIRED_PHASES
        ),
        "topology_stream_m3_required_phases": list(TOPOLOGY_STREAM_M3_PHASES),
        "bridge_required": True,
        "bridge_status": "must_map_or_supplement_prepared_execution_report_before_public_row",
        "allowed_bridge_shape": (
            "topology-stream-specific M3 table attached to prepared-session "
            "metadata, not a replacement for PreparedExecutionReport"
        ),
    }
    current_surface = {
        "point_location_runner_callable": callable(
            getattr(prepared_execution, "run_point_location_topology_stream_prepared_session", None)
        ),
        "segment_intersection_runner_callable": callable(
            getattr(prepared_execution, "run_segment_intersection_topology_stream_prepared_session", None)
        ),
        "point_location_m3_phase_table_contract_metadata_value": (
            point_location_probe.get("topology_stream_m3_phase_table_contract")
            == TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT
        ),
        "segment_intersection_m3_phase_table_contract_metadata_value": (
            segment_intersection_probe.get("topology_stream_m3_phase_table_contract")
            == TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT
        ),
        "point_location_m3_bridge_contract_metadata_value": (
            point_location_probe.get("prepared_execution_to_topology_stream_m3_bridge_contract")
            == "prepared_execution_to_topology_stream_m3_bridge_v1"
        ),
        "segment_intersection_m3_bridge_contract_metadata_value": (
            segment_intersection_probe.get("prepared_execution_to_topology_stream_m3_bridge_contract")
            == "prepared_execution_to_topology_stream_m3_bridge_v1"
        ),
        "point_location_m3_bridge_complete_metadata_value": (
            point_location_probe.get("topology_stream_m3_phase_table_complete") is True
        ),
        "segment_intersection_m3_bridge_complete_metadata_value": (
            segment_intersection_probe.get("topology_stream_m3_phase_table_complete") is True
        ),
        "point_location_prepared_handle_contract_metadata_value": (
            point_location_probe.get("topology_stream_prepared_handle_contract")
            == TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT
        ),
        "segment_intersection_prepared_handle_contract_metadata_value": (
            segment_intersection_probe.get("topology_stream_prepared_handle_contract")
            == TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT
        ),
        "point_location_set_a_probe_candidate_metadata_value": (
            point_location_probe.get("set_a_probe_candidate") is True
        ),
        "segment_intersection_set_a_probe_candidate_metadata_value": (
            segment_intersection_probe.get("set_a_probe_candidate") is True
        ),
        "point_location_no_external_device_buffer_interop": (
            point_location_probe.get("external_device_buffer_interop_authorized") is False
        ),
        "segment_intersection_no_external_device_buffer_interop": (
            segment_intersection_probe.get("external_device_buffer_interop_authorized") is False
        ),
        "point_location_no_v4_embedding_or_external_zero_copy": (
            point_location_probe.get("v4_embedding_or_external_zero_copy_authorized") is False
        ),
        "segment_intersection_no_v4_embedding_or_external_zero_copy": (
            segment_intersection_probe.get("v4_embedding_or_external_zero_copy_authorized") is False
        ),
        "point_location_no_true_zero_copy_claim": (
            point_location_probe.get("true_zero_copy_claim_authorized") is False
        ),
        "segment_intersection_no_true_zero_copy_claim": (
            segment_intersection_probe.get("true_zero_copy_claim_authorized") is False
        ),
        "point_location_runtime_trunk_executes_end_to_end": (
            point_location_probe.get("runtime_trunk_executes_end_to_end") is True
        ),
        "segment_intersection_runtime_trunk_executes_end_to_end": (
            segment_intersection_probe.get("runtime_trunk_executes_end_to_end") is True
        ),
    }
    fail_closed = {
        "m66_active_token_present": M66_ACTIVE_TOKEN in m50_source,
        "m50_superseded_token_absent": M50_SUPERSEDED_TOKEN not in m50_source,
        "m50_default_dry_run_present": "if not bool(args.execute)" in m50_source,
        "m50_requires_authorization_token": "authorization_token" in m50_source
        and "AUTHORIZED_EXECUTION_TOKENS" in m50_source
        and "requires explicit" in m50_source
        and "external authorization token" in m50_source,
        "m66_source_signature_preflight_present": "current_topology_stream_source_signature"
        in m50_source
        and "execute_preflight(args)" in m50_source,
        "m50_no_public_claim_flags_present": (
            '"public_speedup_claim_authorized": False' in m50_source
            and '"rtdl_beats_rayjoin_claim_authorized": False' in m50_source
            and '"true_zero_copy_claim_authorized": False' in m50_source
        ),
    }
    internal_delta = {
        "label": INTERNAL_DELTA_LABEL,
        "source": _rel(M3_GAP_JSON),
        "default_host_points_wall_sec": large_delta["default_host_points"]["wall_median_sec"],
        "device_resident_points_wall_sec": large_delta["device_resident_points"]["wall_median_sec"],
        "wall_speedup_vs_default": large_delta["device_resident_wall_speedup_vs_default"],
        "sanity_min_exclusive": INTERNAL_DELTA_SANITY_MIN_EXCLUSIVE,
        "sanity_max_exclusive": INTERNAL_DELTA_SANITY_MAX_EXCLUSIVE,
        "within_sanity_cap": (
            INTERNAL_DELTA_SANITY_MIN_EXCLUSIVE
            < float(large_delta["device_resident_wall_speedup_vs_default"])
            < INTERNAL_DELTA_SANITY_MAX_EXCLUSIVE
        ),
        "counts_match": bool(large_delta["counts_match"]),
        "public_row_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "reading": (
            "This is an internal RTDL routing delta for topology-stream residency, "
            "not a public speedup row."
        ),
    }
    m61_next_contract = {
        "selected_family": "point_location_topology_stream",
        "selected_scope": (
            "generic topology-stream prepared-handle, internal residency, "
            "and full-M3 phase accounting"
        ),
        "m61_may_do": [
            "inspect current prepared-session topology-stream surfaces",
            "define machine-readable prepared-handle/residency contract gaps",
            "define full-M3 phase bridge from prepared execution to topology-stream table",
            "add local gates that reject route tuning, POD execution, and public claims",
        ],
        "m61_must_not_do": [
            "run M50 or any topology-stream POD command",
            "claim public speedup from the 2.282x internal delta",
            "claim RTDL beats RayJoin author timing",
            "call internal residency true zero-copy",
            "add RayJoin-specific native shortcuts",
        ],
    }
    checks = {
        "m60_consensus_accepts_m61_scope": (
            "m60_select_spatial_topology_stream_for_local_set_a_step2_no_pod_no_release"
            in m60_consensus
            and INTERNAL_DELTA_LABEL in m60_consensus
        ),
        "topology_contract_is_not_m7": topology_contract.get("m7_qualified_release_rows_added") == 0,
        "m3_gap_is_not_public_row": m3_gap.get("m7_qualified_release_rows_added") == 0
        and m3_gap.get("true_zero_copy_claim_authorized") is False,
        "internal_delta_labeled_not_public": internal_delta["label"] == INTERNAL_DELTA_LABEL,
        "internal_delta_counts_match": internal_delta["counts_match"],
        "internal_delta_sanity_cap": internal_delta["within_sanity_cap"],
        "internal_delta_not_public_claim": not internal_delta["public_row_authorized"]
        and not internal_delta["rtdl_beats_rayjoin_claim_authorized"]
        and not internal_delta["true_zero_copy_claim_authorized"],
        "prepared_execution_surface_present": all(current_surface.values()),
        "m50_runner_fail_closed": all(fail_closed.values()),
        "phase_bridge_records_mismatch": phase_bridge["prepared_execution_required_phases"]
        != phase_bridge["topology_stream_m3_required_phases"],
        "phase_bridge_requires_mapping": phase_bridge["bridge_required"],
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    return {
        "schema": SCHEMA,
        "status": STATUS_FAIL if failed_checks else STATUS_OK,
        "selected_family": "point_location_topology_stream",
        "selected_from": _rel(M60_CONSENSUS),
        "release_authorized": False,
        "all_app_benchmark_authorized": False,
        "paid_pod_spend_authorized": False,
        "focused_pod_spend_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_work_authorized": False,
        "embedding_work_authorized": False,
        "c_abi_work_authorized": False,
        "watch_row_closure_authorized": False,
        "contracts": {
            "topology_stream_m3_phase_table": TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT,
            "topology_stream_prepared_handle": TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT,
        },
        "internal_delta": internal_delta,
        "phase_bridge": phase_bridge,
        "current_surface": current_surface,
        "current_surface_probe_metadata": {
            "point_location": point_location_probe,
            "segment_intersection": segment_intersection_probe,
        },
        "fail_closed_execution_surface": fail_closed,
        "m61_next_contract": m61_next_contract,
        "checks": checks,
        "failed_checks": failed_checks,
        "summary": {
            "status": STATUS_FAIL if failed_checks else STATUS_OK,
            "failed_check_count": len(failed_checks),
            "selected_family": "point_location_topology_stream",
            "internal_delta_label": INTERNAL_DELTA_LABEL,
            "internal_delta_speedup": internal_delta["wall_speedup_vs_default"],
            "phase_bridge_required": phase_bridge["bridge_required"],
            "pod_authorized": False,
            "public_claim_authorized": False,
        },
        "goal_level_decision_audit": {
            "decision": (
                "Build a local M61 gap ledger that turns M60's Spatial/RayJoin "
                "selection into machine-checkable no-POD topology-stream work."
            ),
            "was_i_foolish": "No.",
            "foolish_actions": (
                "The foolish action would be to start coding or running Spatial/RayJoin "
                "before labeling the internal delta and phase-bridge gap."
            ),
            "other_path": (
                "Run the M50 topology-stream runner now. That is rejected because M60 "
                "authorized only local gap-ledger/design/gate work."
            ),
            "different_path_now": (
                "Use this ledger to constrain M61 implementation to reusable prepared-handle, "
                "internal residency, and full-M3 accounting work."
            ),
        },
    }


class _FakePreparedTopologyStream:
    pass


def _topology_stream_probe_output(
    *,
    family: str,
    output_contract: str,
    query_stream_residency: str,
) -> dict[str, Any]:
    if family == "segment_intersection_topology_stream":
        phases_sec = {
            "static_segment_pack_sec": 0.001,
            "prepare_static_scene_sec": 0.002,
            "prepare_left_set_sec": 0.003,
            "prepared_left_set_sec": 0.004,
            "prepared_query_sec": 0.010,
        }
        native_phase_timings = {
            "left_upload": 0.0,
            "traversal": 0.004,
            "active_scan": 0.001,
            "candidate_download": 0.0,
            "flag_download": 0.0,
            "count_download": 0.0,
            "row_download": 0.0,
        }
    else:
        phases_sec = {
            "static_shape_pack_sec": 0.001,
            "prepare_static_scene_sec": 0.002,
            "query_pack_sec": 0.003,
            "prepare_query_points_sec": 0.004,
            "prepared_query_sec": 0.010,
        }
        native_phase_timings = {
            "point_upload": 0.0,
            "candidate_count_pass": 0.004,
            "candidate_write_pass": 0.001,
            "exact_refine": 0.001,
            "candidate_download": 0.0,
            "flag_download": 0.0,
            "count_download": 0.0,
            "row_download": 0.0,
        }
    return {
        "metadata": {
            "internal_device_residency_between_rtdl_phases": True,
            "hot_path_host_materialization": False,
        },
        "topology_stream_prepared_handle": {
            "contract": TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT,
            "query_stream_prepared": True,
            "query_stream_residency": query_stream_residency,
        },
        "topology_stream_m3_phase_table": {
            "contract": TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT,
        },
        "phases_sec": phases_sec,
        "native_phase_timings": native_phase_timings,
        "summary": {
            "output_contract": output_contract,
        },
    }


def _run_point_location_topology_stream_probe_metadata() -> dict[str, Any]:
    result = prepared_execution.run_point_location_topology_stream_prepared_session(
        query_stream_fingerprint={"kind": "m61_probe_points", "count": 4},
        static_scene_fingerprint={"kind": "m61_probe_shapes", "count": 2},
        output_contract="m61_probe_point_location_count",
        query_count=4,
        shape_count=2,
        backend="optix",
        partner="none",
        cache=prepared_execution.ExplicitPreparedSessionCache(max_entries=1),
        prepare_session=lambda: _FakePreparedTopologyStream(),
        run_topology_stream=lambda _prepared: _topology_stream_probe_output(
            family="point_location_topology_stream",
            output_contract="m61_probe_point_location_count",
            query_stream_residency="device_resident_m61_probe_point_columns",
        ),
    )
    return _stable_topology_stream_probe_metadata(dict(result.to_metadata()))


def _run_segment_intersection_topology_stream_probe_metadata() -> dict[str, Any]:
    result = prepared_execution.run_segment_intersection_topology_stream_prepared_session(
        query_stream_fingerprint={"kind": "m61_probe_left_segments", "count": 4},
        static_scene_fingerprint={"kind": "m61_probe_right_segments", "count": 3},
        output_contract="m61_probe_segment_intersection_count",
        query_count=4,
        right_segment_count=3,
        backend="optix",
        partner="none",
        cache=prepared_execution.ExplicitPreparedSessionCache(max_entries=1),
        prepare_session=lambda: _FakePreparedTopologyStream(),
        run_topology_stream=lambda _prepared: _topology_stream_probe_output(
            family="segment_intersection_topology_stream",
            output_contract="m61_probe_segment_intersection_count",
            query_stream_residency="device_resident_m61_probe_segment_columns",
        ),
    )
    return _stable_topology_stream_probe_metadata(dict(result.to_metadata()))


def _stable_topology_stream_probe_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    stable_keys = (
        "workflow_name",
        "status",
        "runtime_executed",
        "primitive_family",
        "productized_execution_path",
        "continuation_contract",
        "row_contract",
        "set_a_probe_candidate",
        "phoenix_v3_redesign_step",
        "runtime_trunk_family",
        "runtime_trunk_probe_candidate",
        "runtime_trunk_executes_end_to_end",
        "runtime_trunk_phase_sequence",
        "internal_device_residency_between_rtdl_phases",
        "hot_path_host_materialization",
        "native_phase_host_download_seconds",
        "query_stream_residency",
        "topology_stream_prepared_handle_contract",
        "topology_stream_m3_phase_table_contract",
        "prepared_execution_to_topology_stream_m3_bridge_contract",
        "prepared_execution_to_topology_stream_m3_bridge_required",
        "prepared_execution_to_topology_stream_m3_bridge_status",
        "topology_stream_m3_phase_table_complete",
        "topology_stream_m3_phase_seconds",
        "topology_stream_m3_missing_phases_for_public_row",
        "topology_stream_prepared_handle_full_m3_phase_table_complete",
        "external_device_buffer_interop_authorized",
        "v4_embedding_or_external_zero_copy_authorized",
        "true_zero_copy_claim_authorized",
        "focused_material_gain_required_before_all_app",
        "full_all_app_rerun_authorized_by_this_packet",
        "release_authorized",
        "public_speedup_claim_authorized",
        "broad_v3_faster_than_v2_claim_authorized",
    )
    return {key: metadata.get(key) for key in stable_keys}


def render_markdown(payload: dict[str, Any]) -> str:
    delta = payload["internal_delta"]
    bridge = payload["phase_bridge"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 M61 Topology-Stream Gap Ledger",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is a local no-POD ledger for the M60 Spatial/RayJoin selection. It",
        "does not authorize execution, public wording, all-app benchmarking, or",
        "release.",
        "",
        "## Selected Family",
        "",
        f"- Family: `{payload['selected_family']}`",
        "- Scope: generic topology-stream prepared handle, internal RTDL-owned",
        "  residency, and full-M3 phase accounting.",
        "",
        "## Internal Delta Boundary",
        "",
        f"- Required label: `{delta['label']}`",
        f"- Default host-points wall: `{float(delta['default_host_points_wall_sec']):.6f}s`",
        f"- Device-resident points wall: `{float(delta['device_resident_points_wall_sec']):.6f}s`",
        f"- Internal wall delta: `{float(delta['wall_speedup_vs_default']):.3f}x`",
        f"- Counts match: `{str(delta['counts_match']).lower()}`",
        "- Public row authorized: `false`",
        "- RTDL beats RayJoin claim authorized: `false`",
        "- True zero-copy claim authorized: `false`",
        "",
        delta["reading"],
        "",
        "## Phase Bridge",
        "",
        "Prepared-execution phases:",
        "",
        "```text",
        "\n".join(bridge["prepared_execution_required_phases"]),
        "```",
        "",
        "Topology-stream M3 phases:",
        "",
        "```text",
        "\n".join(bridge["topology_stream_m3_required_phases"]),
        "```",
        "",
        f"Bridge required: `{str(bridge['bridge_required']).lower()}`",
        "",
        bridge["allowed_bridge_shape"],
        "",
        "## M61 Next Contract",
        "",
        "M61 may do:",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["m61_next_contract"]["m61_may_do"])
    lines.extend(["", "M61 must not do:", ""])
    lines.extend(f"- {item}" for item in payload["m61_next_contract"]["m61_must_not_do"])
    lines.extend(
        [
            "",
            "## Checks",
            "",
            *[
                f"- `{name}`: `{str(ok).lower()}`"
                for name, ok in payload["checks"].items()
            ],
            "",
            f"Failed checks: `{len(payload['failed_checks'])}`",
            "",
            "## Non-Authorization",
            "",
            "This ledger does not authorize:",
            "",
            "- no V3 release",
            "- no all-app benchmark run",
            "- no paid POD spend",
            "- no focused POD spend",
            "- no public speedup wording",
            "- no broad V3-over-V2 claim",
            "- no whole-app speedup claim",
            "- no paper reproduction claim",
            "- no RTDL-beats-RayJoin claim",
            "- no V4 work",
            "- no embedding",
            "- no C ABI",
            "- no true-zero-copy claim",
            "- no watch-row closure",
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path that actually solves the problem? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
