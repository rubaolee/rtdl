from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .v4_goal4749_final_rt_core_protocol import VERSION_ORDER
from .v4_goal4749_final_rt_core_protocol import build_protocol


SCHEMA = "rtdl.v4.goal4750.unified_rt_core_runner.v1"
STATUS = "goal4750_unified_runner_dry_run_rows_emitted_command_binding_in_progress"
DATE = "2026-06-26"

POD = {
    "host": "194.68.245.170",
    "port": 22089,
    "ssh_key": "~/.ssh/id_ed25519_rtdl_codex_current_pod",
    "gpu": "NVIDIA RTX A5000",
    "driver": "570.195.03",
}

VERSION_ROOTS = {
    "v2_14": "/root/rtdl_v2_14_tag",
    "v3_0_2": "/root/rtdl_v3_0_2_tag",
    "v4_0": "/root/rtdl_v4_candidate_pod",
}

PYTHON = "/root/rtdl_v4_venv/bin/python"

RUN_READY = "ready_for_goal4750_command_binding"
RUN_BLOCKED_REPAIR = "blocked_until_v4_0_compatibility_repair"

TRIANGLE_FIXTURE = "/root/v4_goal4753_final_matrix/k4_32768.edgebin"
MATRIX_OUTPUT_ROOT = "/root/v4_goal4753_final_matrix"
SPATIAL_SHAPE_PAIR_SERIOUS_DATASET = (
    "/root/v4_goal4753_final_matrix/spatial_shape_pair_serious_left_grid64.cdb + "
    "/root/v4_goal4753_final_matrix/spatial_shape_pair_serious_right_grid64.cdb"
)
SPATIAL_SHAPE_PAIR_SMOKE_DATASET = (
    "/root/v4_goal4753_final_matrix/spatial_shape_pair_smoke_left_grid32.cdb + "
    "/root/v4_goal4753_final_matrix/spatial_shape_pair_smoke_right_grid32.cdb"
)


SERIOUS_PROFILE = {
    "rt_dbscan_point_count": 262144,
    "rt_dbscan_repeat": 5,
    "rt_dbscan_warmup": 1,
    "raydb_rows": 131072,
    "raydb_groups": 1024,
    "raydb_repeat": 7,
    "raydb_warmup": 2,
    "triangle_repeat": 201,
    "triangle_warmup": 20,
    "librts_boxes": 1_000_000,
    "librts_queries": 1000,
    "librts_repeat": 240,
    "librts_warmup": 1,
    "hausdorff_copies": 65536,
    "hausdorff_repeat": 9,
    "hausdorff_warmup": 5,
    "rtnn_point_count": 262144,
    "rtnn_repeat": 5,
    "rtnn_warmups": 1,
    "robot_pose_count": 8192,
    "robot_obstacle_count": 2048,
    "robot_link_count": 2,
    "robot_repeats": 51,
    "robot_warmup": 5,
    "contact_grid_count": 512,
    "contact_witness_capacity": 512,
    "contact_repeat": 5,
    "contact_discovery_repeat": 5,
    "contact_discovery_warmup": 1,
    "spatial_repeat": 25,
    "spatial_warmup": 3,
    "spatial_dataset": SPATIAL_SHAPE_PAIR_SERIOUS_DATASET,
    "barnes_body_count": 32768,
    "barnes_repeat": 7,
    "barnes_warmup": 2,
}

SMOKE_PROFILE = {
    **SERIOUS_PROFILE,
    "rt_dbscan_point_count": 2048,
    "rt_dbscan_repeat": 1,
    "rt_dbscan_warmup": 0,
    "raydb_rows": 2048,
    "raydb_groups": 64,
    "raydb_repeat": 1,
    "raydb_warmup": 0,
    "triangle_repeat": 1,
    "triangle_warmup": 0,
    "librts_boxes": 2048,
    "librts_queries": 32,
    "librts_repeat": 1,
    "librts_warmup": 0,
    "hausdorff_copies": 1024,
    "hausdorff_repeat": 1,
    "hausdorff_warmup": 0,
    "rtnn_point_count": 2048,
    "rtnn_repeat": 1,
    "rtnn_warmups": 0,
    "robot_pose_count": 128,
    "robot_obstacle_count": 128,
    "robot_repeats": 1,
    "robot_warmup": 0,
    "contact_grid_count": 16,
    "contact_witness_capacity": 32,
    "contact_repeat": 1,
    "contact_discovery_repeat": 1,
    "contact_discovery_warmup": 0,
    "spatial_repeat": 1,
    "spatial_warmup": 0,
    "spatial_dataset": SPATIAL_SHAPE_PAIR_SMOKE_DATASET,
    "barnes_body_count": 1024,
    "barnes_repeat": 1,
    "barnes_warmup": 0,
}

PROFILES = {
    "smoke": SMOKE_PROFILE,
    "serious": SERIOUS_PROFILE,
}

PROFILE = SERIOUS_PROFILE


def _env_contract(version: str) -> dict[str, str]:
    root = VERSION_ROOTS[version]
    cuda_prefix = "/root/rtdl_v4_venv/lib/python3.12/site-packages/nvidia/cuda_nvcc"
    nvvm_lib = f"{cuda_prefix}/nvvm/lib64"
    if version == "v4_0":
        optix = f"{root}/build/librtdl_optix.so"
    else:
        optix = f"{root}/build/librtdl_optix.v4compat.so"
    return {
        "PYTHONPATH": f"{root}/src:{root}",
        "RTDL_OPTIX_LIB": optix,
        "RTDL_OPTIX_LIBRARY": optix,
        "CUDA_HOME": cuda_prefix,
        "CUDA_PATH": cuda_prefix,
        "NUMBA_CUDA_PREFIX": cuda_prefix,
        "NUMBA_CUDA_NVVM": f"{nvvm_lib}/libnvvm.so",
        "LD_LIBRARY_PATH": nvvm_lib,
    }


def _version_script_path(script: str) -> str:
    return f"{VERSION_ROOTS['v4_0']}/{script}"


def _command_for(app: str, version: str, profile: dict[str, int]) -> tuple[list[str], tuple[str, ...]]:
    py = PYTHON
    fixtures: list[str] = []
    if app == "rt_dbscan":
        mode = (
            "optix_rt_core_grouped_stream_numba_column_signature_3d"
            if version == "v4_0"
            else "optix_rt_core_grouped_stream_cupy_column_signature_3d"
        )
        partner = "numba" if version == "v4_0" else "cupy"
        return (
            [
                py,
                "examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
                "--mode",
                mode,
                "--dataset",
                "clustered3d",
                "--point-count",
                str(profile["rt_dbscan_point_count"]),
                "--radius",
                "3.0",
                "--min-neighbors",
                "4",
                "--partner",
                partner,
                "--repeat",
                str(profile["rt_dbscan_repeat"]),
                "--warmup",
                str(profile["rt_dbscan_warmup"]),
                "--no-validation",
            ],
            tuple(fixtures),
        )
    if app == "raydb_style":
        backend = (
            "paper_rt_v4_cupy_device_grouped_reduction"
            if version == "v4_0"
            else "paper_rt_optix_prepared_grouped_reduction"
        )
        return (
            [
                py,
                "examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py",
                "--mode",
                "sum",
                "--backend",
                backend,
                "--fixture-kind",
                "generated",
                "--generated-rows",
                str(profile["raydb_rows"]),
                "--generated-groups",
                str(profile["raydb_groups"]),
                "--repeat",
                str(profile["raydb_repeat"]),
                "--warmup",
                str(profile["raydb_warmup"]),
                "--summary-only-iterations",
            ],
            tuple(fixtures),
        )
    if app == "triangle_counting":
        mode = "rt_graph_2a1_segmented_generic_rt" if version != "v2_14" else "rt_graph_2a1_generic_rt"
        command = [
            py,
            "examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
            "--mode",
            mode,
            "--edge-file",
            TRIANGLE_FIXTURE,
            "--edge-format",
            "binary",
            "--backend",
            "optix",
            "--detail",
            "summary",
            "--partner",
            "cupy",
            "--warmup",
            str(profile["triangle_warmup"]),
            "--repeat",
            str(profile["triangle_repeat"]),
        ]
        if mode == "rt_graph_2a1_segmented_generic_rt":
            command.extend(
                [
                    "--segment-ray-representation",
                    "unique_weighted",
                    "--segment-query-schedule",
                    "prepared_segment_replay",
                    "--validate-oracle",
                ]
            )
        return command, (f"generate_triangle_fixture:{TRIANGLE_FIXTURE}",)
    if app == "librts_spatial_index":
        return (
            [
                py,
                "examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
                "--mode",
                "optix_aabb_index",
                "--dataset",
                "uniform",
                "--operation",
                "all",
                "--box-count",
                str(profile["librts_boxes"]),
                "--query-count",
                str(profile["librts_queries"]),
                "--repeat",
                str(profile["librts_repeat"]),
                "--warmup",
                str(profile["librts_warmup"]),
                "--skip-counts",
            ],
            tuple(fixtures),
        )
    if app == "hausdorff_xhd":
        return (
            [
                py,
                "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
                "--backend",
                "optix",
                "--optix-summary-mode",
                "directed_threshold_prepared",
                "--hausdorff-threshold",
                "0.4",
                "--require-rt-core",
                "--copies",
                str(profile["hausdorff_copies"]),
                "--repeat",
                str(profile["hausdorff_repeat"]),
                "--warmup",
                str(profile["hausdorff_warmup"]),
            ],
            tuple(fixtures),
        )
    if app == "robot_collision":
        command = [
                py,
                "examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py",
                "--mode",
                "optix_prepared_device_buffers",
                "--dataset",
                "scaled",
                "--pose-count",
                str(profile["robot_pose_count"]),
                "--obstacle-count",
                str(profile["robot_obstacle_count"]),
                "--link-count",
                str(profile["robot_link_count"]),
                "--repeats",
                str(profile["robot_repeats"]),
                "--warmup",
                str(profile["robot_warmup"]),
                "--summary-only-runs",
                "--no-probe-reference",
        ]
        if version != "v2_14":
            command.extend(["--lowering-mode", "numpy_arrays", "--skip-group-metadata"])
        return command, tuple(fixtures)
    if app == "contact_manifold":
        return (
            [
                py,
                "examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
                "--mode",
                "aabb_broadphase_collect_k",
                "--dataset",
                "grid",
                "--grid-count",
                str(profile["contact_grid_count"]),
                "--witness-capacity",
                str(profile["contact_witness_capacity"]),
                "--backend",
                "optix",
                "--discovery-backend",
                "optix",
                "--repeat-count",
                str(profile["contact_repeat"]),
                "--discovery-repeat",
                str(profile["contact_discovery_repeat"]),
                "--discovery-warmup",
                str(profile["contact_discovery_warmup"]),
            ],
            tuple(fixtures),
        )
    if app == "rtnn":
        mode = "prepared_execution_ranked_summary" if version == "v4_0" else "prepared_optix_ranked_summary"
        command = [
                py,
                "examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py",
                "--mode",
                mode,
                "--point-count",
                str(profile["rtnn_point_count"]),
                "--radius",
                "0.02",
                "--k",
                "50",
                "--repeat",
                str(profile["rtnn_repeat"]),
                "--distribution",
                "uniform",
        ]
        if version != "v2_14":
            command.extend(["--warmups", str(profile["rtnn_warmups"])])
        return command, tuple(fixtures)
    if app == "spatial_rayjoin":
        return (
            [
                py,
                "examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
                "--workload",
                "overlay_seed",
                "--backend",
                "optix",
                "--execution-route",
                "prepared_optix_shape_pair_active_count",
                "--result-mode",
                "count",
                "--dataset",
                str(profile["spatial_dataset"]),
                "--repeat",
                str(profile["spatial_repeat"]),
                "--warmup",
                str(profile["spatial_warmup"]),
                "--no-rows",
            ],
            tuple(fixtures),
        )
    if app == "barnes_hut":
        route = {
            "v2_14": "v2_14_optix_host_frontier_numba_cpu_continuation",
            "v3_0_2": "v3_0_2_device_columns_explicit_partner_continuation",
            "v4_0": "v4_candidate_runner_explicit_partner_continuation",
        }[version]
        return (
            [
                py,
                _version_script_path("scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py"),
                "--worker",
                "--route",
                route,
                "--body-count",
                str(profile["barnes_body_count"]),
                "--theta",
                "0.5",
                "--bucket-size",
                "32",
                "--max-depth",
                "32",
                "--repeat",
                str(profile["barnes_repeat"]),
                "--warmup",
                str(profile["barnes_warmup"]),
                "--frontier-capacity-multiplier",
                "700",
                "--partner",
                "cupy",
                "--skip-validation",
            ],
            tuple(fixtures),
        )
    raise ValueError(f"unknown app: {app}")


def build_dry_run(protocol: dict[str, Any] | None = None, *, profile: str = "serious") -> dict[str, Any]:
    protocol = build_protocol() if protocol is None else protocol
    if profile not in PROFILES:
        raise ValueError(f"unknown runner profile: {profile}")
    profile_values = PROFILES[profile]
    rows: list[dict[str, Any]] = []
    for app_row in protocol["rows"]:
        for version in VERSION_ORDER:
            route = app_row["versions"][version]
            route_status = route["route_status"]
            blocked = route_status == "v4_0_repair_required_before_final_timing"
            command, fixture_requirements = _command_for(app_row["app"], version, profile_values)
            rows.append(
                {
                    "app": app_row["app"],
                    "version": version,
                    "root": VERSION_ROOTS[version],
                    "python": PYTHON,
                    "semantic_contract": app_row["semantic_contract"],
                    "correctness_oracle": app_row["correctness_oracle"],
                    "primary_metrics": app_row["primary_metrics"],
                    "backend": route["backend"],
                    "partner": route["partner"],
                    "route": route["route"],
                    "route_status": route_status,
                    "run_state": RUN_BLOCKED_REPAIR if blocked else RUN_READY,
                    "blocker": route["blocker"],
                    "command_binding_status": (
                        "blocked_by_v4_0_repair" if blocked else "command_template_bound_for_goal4753_pod"
                    ),
                    "command": [] if blocked else command,
                    "fixture_requirements": list(fixture_requirements),
                    "stdout_json": f"{MATRIX_OUTPUT_ROOT}/raw/{version}_{app_row['app']}.json",
                    "stderr": f"{MATRIX_OUTPUT_ROOT}/raw/{version}_{app_row['app']}.stderr.txt",
                    "env_contract": _env_contract(version),
                    "embree_primary_denominator_authorized": False,
                    "rt_core_primary_required": True,
                    "same_semantics_required": True,
                    "correctness_required_before_speed_credit": True,
                }
            )
    ready = sum(1 for row in rows if row["run_state"] == RUN_READY)
    blocked = sum(1 for row in rows if row["run_state"] == RUN_BLOCKED_REPAIR)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "date": DATE,
        "source_protocol_schema": protocol["schema"],
        "profile": profile,
        "profile_values": dict(profile_values),
        "pod": POD,
        "version_roots": VERSION_ROOTS,
        "python": PYTHON,
        "row_count": len(rows),
        "ready_for_command_binding_count": ready,
        "blocked_until_repair_count": blocked,
        "rows": rows,
        "claim_boundary": {
            "pod_timing_executed": False,
            "release_authorized": False,
            "public_speed_claim_authorized": False,
            "whole_app_high_performance_claim_authorized": False,
            "all_benchmark_speedup_claim_authorized": False,
        },
    }


def _contains_na(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"n/a", "na", "not applicable"}
    if isinstance(value, dict):
        return any(_contains_na(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_na(v) for v in value)
    return False


def validate_dry_run(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = build_dry_run() if payload is None else payload
    errors: list[str] = []
    rows = payload.get("rows", [])
    if payload.get("row_count") != 30 or len(rows) != 30:
        errors.append("dry-run must emit exactly 30 app/version rows")
    if _contains_na(payload):
        errors.append("dry-run contains an n/a-style value")
    for row in rows:
        label = f"{row.get('app')}/{row.get('version')}"
        if row.get("version") not in VERSION_ORDER:
            errors.append(f"{label}: invalid version")
        if row.get("backend") != "optix_rt_core":
            errors.append(f"{label}: primary backend must be optix_rt_core")
        if row.get("embree_primary_denominator_authorized") is not False:
            errors.append(f"{label}: Embree primary denominator must be false")
        if row.get("rt_core_primary_required") is not True:
            errors.append(f"{label}: RT-core primary must be true")
        env = row.get("env_contract", {})
        if row.get("version") in {"v2_14", "v3_0_2"}:
            optix_lib = env.get("RTDL_OPTIX_LIB", "")
            optix_library = env.get("RTDL_OPTIX_LIBRARY", "")
            if not optix_lib.endswith("librtdl_optix.v4compat.so"):
                errors.append(f"{label}: old tag must set RTDL_OPTIX_LIB to v4compat library")
            if optix_lib != optix_library:
                errors.append(f"{label}: old tag RTDL_OPTIX_LIB and RTDL_OPTIX_LIBRARY must match")
        if row.get("run_state") == RUN_BLOCKED_REPAIR and not row.get("blocker"):
            errors.append(f"{label}: blocked row must name blocker")
        if row.get("run_state") == RUN_READY and not row.get("command"):
            errors.append(f"{label}: ready row must bind a command")
        if row.get("run_state") == RUN_READY and row.get("command", [""])[0] != PYTHON:
            errors.append(f"{label}: command must use the recorded POD Python")
    return {
        "schema": f"{SCHEMA}.validation",
        "status": "passed" if not errors else "failed",
        "error_count": len(errors),
        "errors": errors,
    }


def write_dry_run_artifacts(*, evidence_path: Path, report_path: Path) -> dict[str, Any]:
    payload = build_dry_run()
    validation = validate_dry_run(payload)
    payload = {**payload, "validation": validation}
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(payload), encoding="utf-8")
    return payload


def _render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# V4 Goal4750 Unified RT-Core Runner Dry Run",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is the command-binding dry run for the final V2.14/V3.0.2/V4.0 POD matrix.",
        "It does not execute timing and does not authorize release claims.",
        "",
        "## Counts",
        "",
        f"- rows: `{payload['row_count']}`",
        f"- ready_for_command_binding: `{payload['ready_for_command_binding_count']}`",
        f"- blocked_until_repair: `{payload['blocked_until_repair_count']}`",
        "",
        "## POD",
        "",
        f"- host: `{payload['pod']['host']}`",
        f"- port: `{payload['pod']['port']}`",
        f"- key: `{payload['pod']['ssh_key']}`",
        f"- gpu: `{payload['pod']['gpu']}`",
        "",
        "## Blocked Rows",
        "",
    ]
    blocked_rows = [row for row in payload["rows"] if row["run_state"] == RUN_BLOCKED_REPAIR]
    if blocked_rows:
        for row in blocked_rows:
            lines.append(f"- `{row['app']}/{row['version']}`: {row['blocker']}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- status: `{payload['validation']['status']}`",
            f"- error_count: `{payload['validation']['error_count']}`",
            "",
            "## Next",
            "",
            "Generate required fixtures, smoke the bound commands, then run Goal4753 on the RTX POD.",
            "",
        ]
    )
    return "\n".join(lines)


__all__ = ["PROFILE", "PROFILES", "build_dry_run", "validate_dry_run", "write_dry_run_artifacts"]
