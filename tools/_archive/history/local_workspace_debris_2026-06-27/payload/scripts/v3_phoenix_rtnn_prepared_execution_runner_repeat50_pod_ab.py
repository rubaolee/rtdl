#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.current.research_benchmarks.rtnn import rtdl_rtnn_benchmark_app as rtnn_app  # noqa: E402
from scripts import goal2348_rtnn_v2_2_external_runner as rtnn_runner  # noqa: E402
from scripts import v3_optix_hardware_gate  # noqa: E402
from rtdsl.prepared_execution import audit_prepared_execution_session_metadata  # noqa: E402


SCHEMA = "rtdl.phoenix_v3.rtnn_prepared_execution_runner_repeat50_pod_ab.v1"
STATUS_NOT_RELEASE = "rtnn_prepared_execution_runner_repeat50_collected_not_release"
SERIOUS_POINT_COUNT_FLOOR = 1_048_576
DEFAULT_OUT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622"
)
LEGACY = "legacy_app_front_door_prepared_optix"
RUNNER = "productized_prepared_execution_runner"
CUPY = "cupy_grid_reference"
FROZEN_SCORECARD_SOURCE = "docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json"
FROZEN_SCORECARD_SHAPES: dict[tuple[str, int], dict[str, Any]] = {
    ("clustered", 262_144): {
        "shape_key": "clustered:262144:rtnn_clustered_262144_ranked_summary",
        "comparison_group": "rtnn_clustered_262144_ranked_summary",
        "shape_geomean_v3_vs_v2": 0.9713694464408821,
        "rows": (
            {
                "backend": "embree",
                "case_id": "rtnn_embree_clustered_262144_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_clustered_262144_ranked_summary|embree|rtnn_embree_clustered_262144_ranked_summary",
                "frozen_v3_speedup_vs_v2": 0.945681958160491,
                "directly_moved_by_this_optix_runner": False,
            },
            {
                "backend": "optix",
                "case_id": "rtnn_optix_clustered_262144_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_clustered_262144_ranked_summary|optix|rtnn_optix_clustered_262144_ranked_summary",
                "frozen_v3_speedup_vs_v2": 0.9977546820436802,
                "directly_moved_by_this_optix_runner": True,
            },
        ),
    },
    ("clustered", 65_536): {
        "shape_key": "clustered:65536:rtnn_clustered_65536_ranked_summary",
        "comparison_group": "rtnn_clustered_65536_ranked_summary",
        "shape_geomean_v3_vs_v2": 1.0828915702991448,
        "rows": (
            {
                "backend": "embree",
                "case_id": "rtnn_embree_clustered_65536_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_clustered_65536_ranked_summary|embree|rtnn_embree_clustered_65536_ranked_summary",
                "frozen_v3_speedup_vs_v2": 1.1490536563341602,
                "directly_moved_by_this_optix_runner": False,
            },
            {
                "backend": "optix",
                "case_id": "rtnn_optix_clustered_65536_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_clustered_65536_ranked_summary|optix|rtnn_optix_clustered_65536_ranked_summary",
                "frozen_v3_speedup_vs_v2": 1.0205390727932415,
                "directly_moved_by_this_optix_runner": True,
            },
        ),
    },
    ("shell", 262_144): {
        "shape_key": "shell:262144:rtnn_shell_262144_ranked_summary",
        "comparison_group": "rtnn_shell_262144_ranked_summary",
        "shape_geomean_v3_vs_v2": 0.9827280606322594,
        "rows": (
            {
                "backend": "embree",
                "case_id": "rtnn_embree_shell_262144_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_shell_262144_ranked_summary|embree|rtnn_embree_shell_262144_ranked_summary",
                "frozen_v3_speedup_vs_v2": 0.9728061884875627,
                "directly_moved_by_this_optix_runner": False,
            },
            {
                "backend": "optix",
                "case_id": "rtnn_optix_shell_262144_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_shell_262144_ranked_summary|optix|rtnn_optix_shell_262144_ranked_summary",
                "frozen_v3_speedup_vs_v2": 0.9927511282134373,
                "directly_moved_by_this_optix_runner": True,
            },
        ),
    },
    ("shell", 65_536): {
        "shape_key": "shell:65536:rtnn_shell_65536_ranked_summary",
        "comparison_group": "rtnn_shell_65536_ranked_summary",
        "shape_geomean_v3_vs_v2": 0.9861020564631944,
        "rows": (
            {
                "backend": "embree",
                "case_id": "rtnn_embree_shell_65536_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_shell_65536_ranked_summary|embree|rtnn_embree_shell_65536_ranked_summary",
                "frozen_v3_speedup_vs_v2": 0.9809269459324993,
                "directly_moved_by_this_optix_runner": False,
            },
            {
                "backend": "optix",
                "case_id": "rtnn_optix_shell_65536_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_shell_65536_ranked_summary|optix|rtnn_optix_shell_65536_ranked_summary",
                "frozen_v3_speedup_vs_v2": 0.9913044695051682,
                "directly_moved_by_this_optix_runner": True,
            },
        ),
    },
    ("uniform", 262_144): {
        "shape_key": "uniform:262144:rtnn_uniform_262144_ranked_summary",
        "comparison_group": "rtnn_uniform_262144_ranked_summary",
        "shape_geomean_v3_vs_v2": 1.0058807519091433,
        "rows": (
            {
                "backend": "optix",
                "case_id": "rtnn_optix_uniform_262144_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_uniform_262144_ranked_summary|optix|rtnn_optix_uniform_262144_ranked_summary",
                "frozen_v3_speedup_vs_v2": 0.9922781332938772,
                "directly_moved_by_this_optix_runner": True,
            },
            {
                "backend": "embree",
                "case_id": "rtnn_embree_uniform_262144_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_uniform_262144_ranked_summary|embree|rtnn_embree_uniform_262144_ranked_summary",
                "frozen_v3_speedup_vs_v2": 1.0196703494749948,
                "directly_moved_by_this_optix_runner": False,
            },
        ),
    },
    ("uniform", 65_536): {
        "shape_key": "uniform:65536:rtnn_uniform_65536_ranked_summary",
        "comparison_group": "rtnn_uniform_65536_ranked_summary",
        "shape_geomean_v3_vs_v2": 0.9974905706824754,
        "rows": (
            {
                "backend": "optix",
                "case_id": "rtnn_optix_uniform_65536_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_uniform_65536_ranked_summary|optix|rtnn_optix_uniform_65536_ranked_summary",
                "frozen_v3_speedup_vs_v2": 0.9943130918505317,
                "directly_moved_by_this_optix_runner": True,
            },
            {
                "backend": "embree",
                "case_id": "rtnn_embree_uniform_65536_ranked_summary",
                "row_id": "goal2636_stress|rtnn|rtnn_uniform_65536_ranked_summary|embree|rtnn_embree_uniform_65536_ranked_summary",
                "frozen_v3_speedup_vs_v2": 1.0006782008550615,
                "directly_moved_by_this_optix_runner": False,
            },
        ),
    },
}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.output_dir = args.output_dir.resolve()
    if args.point_file is not None:
        args.point_file = args.point_file.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = run_packet(args)
    (args.output_dir / "summary.json").write_text(
        json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "README.md").write_text(_readme(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Focused Phoenix V3 RTNN POD A/B: legacy app-front-door prepared OptiX, "
            "new productized prepared-execution runner, and CuPy grid reference. "
            "This collects Step-2 runtime-trunk evidence only; it never authorizes release."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--point-file", type=Path)
    parser.add_argument("--point-count", type=int, default=SERIOUS_POINT_COUNT_FLOOR)
    parser.add_argument("--distribution", choices=("uniform", "clustered", "shell"), default="uniform")
    parser.add_argument("--seed", type=int, default=20260622)
    parser.add_argument("--radius", type=float, default=0.02)
    parser.add_argument("--k-max", type=int, default=50)
    parser.add_argument("--repeat", type=int, default=50)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--max-grid-cells", type=int, default=2_000_000)
    parser.add_argument("--require-rt-hardware", action="store_true")
    parser.add_argument("--allow-non-serious-local-smoke", action="store_true")
    parser.add_argument(
        "--scorecard-bound-shape",
        action="store_true",
        help=(
            "Treat 65,536/262,144 RTNN frozen scorecard shapes as serious "
            "scorecard-bound blocker measurements instead of local smoke."
        ),
    )
    parser.add_argument("--skip-cupy", action="store_true")
    return parser.parse_args(argv)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    environment = environment_payload(require_rt_hardware=bool(args.require_rt_hardware))
    if (
        int(args.point_count) < SERIOUS_POINT_COUNT_FLOOR
        and not bool(args.allow_non_serious_local_smoke)
        and not scorecard_shape_binding(args)
    ):
        raise SystemExit(
            "point-count is below the Phoenix V3 RTNN serious scale floor; pass "
            "--scorecard-bound-shape for frozen scorecard rows or "
            "--allow-non-serious-local-smoke only for local smoke tests"
        )
    if bool(args.require_rt_hardware) and environment["hardware_gate"].get("status") != "pass":
        return build_payload(
            args=args,
            point_manifest=point_manifest_for_plan(args),
            environment=environment,
            variant_payloads={},
            run_errors={
                "optix_hardware_gate": environment["hardware_gate"].get("fail_closed_reason")
                or "OptiX RT hardware gate failed"
            },
        )

    point_manifest = ensure_point_file(args)
    point_file = Path(point_manifest["path"])
    variant_payloads: dict[str, dict[str, Any]] = {}
    run_errors: dict[str, str] = {}
    for variant in (LEGACY, RUNNER, CUPY):
        if variant == CUPY and bool(args.skip_cupy):
            continue
        try:
            print(
                f"[phoenix-v3-rtnn-runner-ab] variant={variant} "
                f"point_count={int(args.point_count)} repeat={int(args.repeat)}",
                flush=True,
            )
            payload = run_variant(args, variant=variant, point_file=point_file)
            variant_payloads[variant] = payload
            (args.output_dir / f"{variant}.json").write_text(
                json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except Exception as exc:  # pragma: no cover - hardware/environment dependent
            run_errors[variant] = repr(exc)
            (args.output_dir / f"{variant}.error.txt").write_text(
                repr(exc) + "\n",
                encoding="utf-8",
            )
    return build_payload(
        args=args,
        point_manifest=point_manifest,
        environment=environment,
        variant_payloads=variant_payloads,
        run_errors=run_errors,
    )


def run_variant(args: argparse.Namespace, *, variant: str, point_file: Path) -> dict[str, Any]:
    point_count = int(args.point_count)
    if variant == LEGACY:
        started = time.perf_counter()
        payload = rtnn_app.rtnn_prepared_optix_ranked_summary_payload(
            point_count=point_count,
            radius=float(args.radius),
            k=int(args.k_max),
            repeat=int(args.repeat),
            query_batch_size=point_count,
            distribution=args.distribution,
            seed=int(args.seed),
            point_file=point_file,
        )
        payload["phoenix_v3_outer_wall_sec"] = time.perf_counter() - started
        return payload
    if variant == RUNNER:
        started = time.perf_counter()
        payload = rtnn_app.rtnn_prepared_execution_ranked_summary_payload(
            point_count=point_count,
            radius=float(args.radius),
            k=int(args.k_max),
            repeat=int(args.repeat),
            warmups=int(args.warmups),
            query_batch_size=point_count,
            distribution=args.distribution,
            seed=int(args.seed),
            point_file=point_file,
        )
        payload["phoenix_v3_outer_wall_sec"] = time.perf_counter() - started
        return payload
    if variant == CUPY:
        started = time.perf_counter()
        payload = rtnn_runner.run_cupy_grid_3d_ranked_summary(
            SimpleNamespace(
                point_file=point_file,
                query_file=None,
                radius=float(args.radius),
                k_max=int(args.k_max),
                dtype="float32",
                max_grid_cells=int(args.max_grid_cells),
                repeat=int(args.repeat),
                point_column_source="csv",
                point_column_file=None,
                row_label="phoenix_v3_rtnn_runner_repeat50_cupy_grid_reference",
                json_out=None,
            )
        )
        payload["phoenix_v3_outer_wall_sec"] = time.perf_counter() - started
        return payload
    raise ValueError(f"unsupported variant: {variant}")


def ensure_point_file(args: argparse.Namespace) -> dict[str, Any]:
    if args.point_file is not None:
        point_file = args.point_file.resolve()
        if not point_file.exists():
            raise FileNotFoundError(f"RTNN point file does not exist: {point_file}")
        return {
            **point_manifest_for_plan(args),
            "path": str(point_file),
            "generated_by_runner": False,
            "runtime_materialized": True,
        }

    point_file = args.output_dir / "rtnn_runner_repeat50_points.csv"
    manifest = rtnn_runner.generate_point_file(
        point_file,
        point_count=int(args.point_count),
        dimension=3,
        seed=int(args.seed),
        distribution=args.distribution,
    )
    manifest["generated_by_runner"] = True
    manifest["runtime_materialized"] = True
    return manifest


def point_manifest_for_plan(args: argparse.Namespace) -> dict[str, Any]:
    point_file = args.point_file or (args.output_dir / "rtnn_runner_repeat50_points.csv")
    return {
        "path": str(point_file),
        "point_count": int(args.point_count),
        "dimension": 3,
        "seed": int(args.seed),
        "distribution": args.distribution,
        "format": "rtnn_csv_xyz",
        "generated_by_runner": args.point_file is None,
        "runtime_materialized": False,
    }


def build_payload(
    *,
    args: argparse.Namespace,
    point_manifest: dict[str, Any],
    environment: dict[str, Any],
    variant_payloads: dict[str, dict[str, Any]],
    run_errors: dict[str, str],
) -> dict[str, Any]:
    phase_rows = {
        variant: phase_summary(variant, payload)
        for variant, payload in sorted(variant_payloads.items())
    }
    parity = parity_summary(variant_payloads)
    comparisons = comparison_summary(phase_rows)
    runner_metadata = (
        variant_payloads.get(RUNNER, {}).get("runner_metadata", {})
        if variant_payloads.get(RUNNER)
        else {}
    )
    runner_step3_audit = (
        audit_prepared_execution_session_metadata(runner_metadata)
        if runner_metadata
        else {}
    )
    serious_scale = int(args.point_count) >= SERIOUS_POINT_COUNT_FLOOR
    repeat50 = int(args.repeat) >= 50
    scorecard_shape = scorecard_shape_binding(args)
    scorecard_bound = bool(scorecard_shape)
    material_config = (serious_scale or scorecard_bound) and repeat50
    checks = {
        "runner_completed_without_errors": not run_errors and bool(variant_payloads),
        "serious_fixture_scale": serious_scale or scorecard_bound or bool(args.allow_non_serious_local_smoke),
        "scorecard_bound_shape_valid": (not bool(args.scorecard_bound_shape)) or scorecard_bound,
        "serious_material_config_or_explicit_smoke": bool(args.allow_non_serious_local_smoke)
        or material_config,
        "legacy_route_present": LEGACY in variant_payloads,
        "runner_route_present": RUNNER in variant_payloads,
        "cupy_reference_present_unless_skipped": bool(args.skip_cupy) or CUPY in variant_payloads,
        "runner_runtime_trunk_executes": bool(runner_metadata.get("runtime_trunk_executes_end_to_end")),
        "runner_internal_residency": bool(
            runner_metadata.get("internal_device_residency_between_rtdl_phases")
        ),
        "runner_step3_residency_default_ready": (
            bool(args.allow_non_serious_local_smoke)
            or bool(runner_step3_audit.get("step3_residency_default_ready"))
        ),
        "runner_repeat50_material_candidate": bool(
            runner_metadata.get("repeat50_material_probe_candidate")
        )
        if material_config and not bool(args.allow_non_serious_local_smoke)
        else True,
        "runner_productized_path": (
            runner_metadata.get("productized_execution_path") == "prepared_execution_session_runner"
        ),
        "same_signature_runner_vs_legacy": bool(parity.get("runner_vs_legacy_signature_match")),
        "same_signature_runner_vs_cupy_unless_skipped": (
            bool(args.skip_cupy) or bool(parity.get("runner_vs_cupy_signature_match"))
        ),
        "all_claim_flags_false": all_claim_flags_false(variant_payloads),
        "no_all_app_authorization": not any(
            bool(payload.get("full_all_app_rerun_authorized_by_this_packet"))
            for payload in variant_payloads.values()
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    scorecard_movement = scorecard_movement_projection(scorecard_shape, comparisons)
    summary = {
        "schema": SCHEMA,
        "status": STATUS_NOT_RELEASE if not failed_checks else "failed_checks_not_release",
        "point_count": int(args.point_count),
        "distribution": args.distribution,
        "seed": int(args.seed),
        "radius": float(args.radius),
        "k_max": int(args.k_max),
        "repeat": int(args.repeat),
        "warmups": int(args.warmups),
        "variants": sorted(variant_payloads),
        "phase_rows": phase_rows,
        "runner_step3_audit": runner_step3_audit,
        "comparisons": comparisons,
        "parity": parity,
        "scorecard_bound_shape": scorecard_shape,
        "scorecard_movement_projection": scorecard_movement,
        "runtime_trunk_executes_end_to_end": bool(
            runner_metadata.get("runtime_trunk_executes_end_to_end")
        ),
        "runtime_sourced_material_gain_candidate": bool(
            not failed_checks
            and (serious_scale or scorecard_bound)
            and repeat50
            and comparisons.get("runner_over_cupy_hot_speedup", 0.0) >= 1.20
            and comparisons.get("runner_over_cupy_runner_wall_speedup", 0.0) >= 1.20
        ),
        "scorecard_bound_runtime_sourced_movement_candidate": bool(
            not failed_checks
            and scorecard_movement.get("direct_optix_runner_wall_moves_any_row", False)
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "full_all_app_rerun_authorized_by_this_packet": False,
    }
    return {
        "schema": SCHEMA,
        "status": summary["status"],
        "summary": summary,
        "checks": checks,
        "failed_checks": failed_checks,
        "point_manifest": point_manifest,
        "environment": environment,
        "run_errors": run_errors,
        "variant_payload_paths": {
            variant: str((args.output_dir / f"{variant}.json").relative_to(ROOT))
            for variant in variant_payloads
        },
        "goal_level_decision_audit": {
            "decision": (
                "Run RTNN as a focused productized-runner repeat50 evidence packet before any all-app run."
            ),
            "was_i_foolish": "No. This directly tests the runtime trunk on a second Set-A family.",
            "foolish_actions": (
                "The foolish action would be to call the old RTNN repeat50 row a V3 runtime-trunk result "
                "without routing it through the productized prepared-execution runner."
            ),
            "other_path": (
                "Retry symbol-cache or all-app runs. Those paths would not prove shared runtime machinery."
            ),
            "different_path_now": (
                "Use this focused A/B to test same-contract legacy parity, scorecard-row movement, runner metadata, "
                "and material repeat50 boundary before spending on larger POD runs."
            ),
        },
        "non_authorization": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "full_all_app_rerun_authorized_by_this_packet": False,
        },
    }


def scorecard_shape_binding(args: argparse.Namespace) -> dict[str, Any]:
    if not bool(getattr(args, "scorecard_bound_shape", False)):
        return {}
    binding = FROZEN_SCORECARD_SHAPES.get((str(args.distribution), int(args.point_count)))
    if not binding:
        return {}
    return {
        "app": "rtnn",
        "set": "A",
        "source": FROZEN_SCORECARD_SOURCE,
        "distribution": str(args.distribution),
        "point_count": int(args.point_count),
        "query_batch_size": int(args.point_count),
        "scorecard_metric": "frozen_row_v3_speedup_vs_v2",
        **binding,
    }


def scorecard_movement_projection(
    scorecard_shape: dict[str, Any],
    comparisons: dict[str, float],
) -> dict[str, Any]:
    if not scorecard_shape:
        return {}
    hot_speedup = float(comparisons.get("runner_vs_legacy_hot_speedup", 0.0))
    cold_speedup = float(comparisons.get("runner_vs_legacy_cold_plus_query_speedup", 0.0))
    wall_speedup = float(comparisons.get("runner_vs_legacy_runner_wall_speedup", 0.0))
    rows = []
    for row in scorecard_shape.get("rows", ()):
        current = float(row["frozen_v3_speedup_vs_v2"])
        direct = bool(row.get("directly_moved_by_this_optix_runner"))
        projected_hot = current * hot_speedup if direct else None
        projected_cold = current * cold_speedup if direct else None
        projected_wall = current * wall_speedup if direct else None
        rows.append(
            {
                **row,
                "projected_hot_v3_speedup_vs_v2": projected_hot,
                "projected_cold_plus_query_v3_speedup_vs_v2": projected_cold,
                "projected_runner_wall_v3_speedup_vs_v2": projected_wall,
                "runner_wall_moves_toward_target": bool(direct and projected_wall and projected_wall > current),
                "runner_wall_crosses_1_05x": bool(direct and projected_wall and projected_wall >= 1.05),
                "hot_crosses_1_05x": bool(direct and projected_hot and projected_hot >= 1.05),
            }
        )
    direct_rows = [row for row in rows if row.get("directly_moved_by_this_optix_runner")]
    direct_wall_moves = [
        row
        for row in direct_rows
        if bool(row.get("runner_wall_moves_toward_target"))
    ]
    direct_wall_crosses = [
        row
        for row in direct_rows
        if bool(row.get("runner_wall_crosses_1_05x"))
    ]
    return {
        "projection_method": (
            "projected row speedup = frozen row v3_speedup_vs_v2 * runner_vs_legacy same-contract speedup"
        ),
        "directly_moves_backend": "optix",
        "runner_vs_legacy_hot_speedup": hot_speedup,
        "runner_vs_legacy_cold_plus_query_speedup": cold_speedup,
        "runner_vs_legacy_runner_wall_speedup": wall_speedup,
        "rows": rows,
        "direct_optix_runner_wall_moves_any_row": bool(direct_wall_moves),
        "direct_optix_runner_wall_crosses_1_05x_any_row": bool(direct_wall_crosses),
        "direct_optix_rows_moved": tuple(row["case_id"] for row in direct_wall_moves),
        "direct_optix_rows_crossing_1_05x": tuple(row["case_id"] for row in direct_wall_crosses),
        "embree_rows_not_moved_by_this_optix_runner": tuple(
            row["case_id"] for row in rows if row.get("backend") == "embree"
        ),
    }


def phase_summary(variant: str, payload: dict[str, Any]) -> dict[str, Any]:
    if variant == LEGACY:
        runner = dict(payload["runner_payload"])
        query_sec = float(runner.get("elapsed_median_sec", 0.0))
        load_sec = float(runner.get("input_load_sec", 0.0))
        pack_sec = float(runner.get("input_pack_sec", 0.0))
        prepare_sec = float(runner.get("execution_prepare_sec", 0.0))
        return {
            "variant": variant,
            "ok": bool(runner.get("ok")),
            "mode": runner.get("result_mode"),
            "query_count": int(runner.get("query_count", 0)),
            "search_count": int(runner.get("search_count", 0)),
            "hot_query_median_sec": query_sec,
            "input_load_sec": load_sec,
            "input_pack_sec": pack_sec,
            "execution_prepare_sec": prepare_sec,
            "cold_plus_query_wall_sec": load_sec + pack_sec + prepare_sec + query_sec,
            "runner_wall_sec": float(payload.get("phoenix_v3_outer_wall_sec", 0.0)),
            "summary": normalize_summary(runner.get("ranked_aggregate_summary", {})),
            "productized_execution_path": "legacy_goal2348_app_front_door",
        }
    if variant == RUNNER:
        metadata = dict(payload["runner_metadata"])
        step3_audit = audit_prepared_execution_session_metadata(metadata)
        timing = dict(payload.get("timing_sec") or {})
        report_summary = dict(metadata.get("prepared_execution_report", {}).get("summary_sec", {}))
        query_sec = float(metadata.get("measured_median_sec", 0.0))
        load_pack_sec = float(timing.get("input_load_pack", 0.0))
        prepare_sec = float(report_summary.get("setup", 0.0))
        return {
            "variant": variant,
            "ok": bool(payload.get("runtime_trunk_executes_end_to_end")),
            "mode": payload.get("mode"),
            "query_count": int(payload.get("point_count", 0)),
            "search_count": int(payload.get("point_count", 0)),
            "hot_query_median_sec": query_sec,
            "input_load_pack_sec": load_pack_sec,
            "execution_prepare_sec": prepare_sec,
            "cold_plus_query_wall_sec": load_pack_sec + prepare_sec + query_sec,
            "runner_wall_sec": float(timing.get("runner_wall", payload.get("phoenix_v3_outer_wall_sec", 0.0))),
            "runner_after_input_load_pack_sec": float(timing.get("runner_after_input_load_pack", 0.0)),
            "summary": normalize_summary(payload.get("runner_payload", {})),
            "productized_execution_path": metadata.get("productized_execution_path"),
            "runtime_trunk_executes_end_to_end": bool(
                metadata.get("runtime_trunk_executes_end_to_end")
            ),
            "repeat50_material_probe_candidate": bool(
                metadata.get("repeat50_material_probe_candidate")
            ),
            "internal_device_residency_between_rtdl_phases": bool(
                metadata.get("internal_device_residency_between_rtdl_phases")
            ),
            "step3_residency_default_ready": bool(
                step3_audit.get("step3_residency_default_ready")
            ),
            "step3_audit_status": step3_audit.get("status"),
            "step3_audit_missing_fields": tuple(
                step3_audit.get("missing_step3_fields", ())
            ),
        }
    if variant == CUPY:
        samples = [float(value) for value in payload.get("elapsed_runs_sec", ())]
        query_sec = statistics.median(samples) if samples else float(payload.get("elapsed_sec", 0.0))
        load_sec = float(payload.get("input_load_sec", 0.0))
        prepare_sec = float(payload.get("grid_prepare_sec", 0.0))
        return {
            "variant": variant,
            "ok": bool(payload.get("ok")),
            "mode": payload.get("mode"),
            "query_count": int(payload.get("query_count", 0)),
            "search_count": int(payload.get("search_count", 0)),
            "hot_query_median_sec": query_sec,
            "input_load_sec": load_sec,
            "grid_prepare_sec": prepare_sec,
            "cold_plus_query_wall_sec": load_sec + prepare_sec + query_sec,
            "runner_wall_sec": float(payload.get("phoenix_v3_outer_wall_sec", 0.0)),
            "summary": normalize_summary(payload.get("summary", {})),
            "productized_execution_path": "cupy_grid_cuda_core_reference",
        }
    raise ValueError(f"unsupported variant: {variant}")


def normalize_summary(summary: Any) -> dict[str, Any]:
    row = dict(summary or {})
    if "row_count" not in row and "query_count" in row:
        row["row_count"] = int(row["query_count"])
    return {
        "row_count": int(row.get("row_count", 0)),
        "bounded_neighbor_count": int(row.get("bounded_neighbor_count", 0)),
        "nearest_id_checksum": int(row.get("nearest_id_checksum", 0)),
        "kth_id_checksum": int(row.get("kth_id_checksum", 0)),
        "sum_distance": float(row.get("sum_distance", 0.0)),
    }


def parity_summary(variant_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    summaries = {
        variant: phase_summary(variant, payload)["summary"]
        for variant, payload in variant_payloads.items()
    }
    parity: dict[str, Any] = {}
    if RUNNER in summaries and LEGACY in summaries:
        parity["runner_vs_legacy"] = signature_delta(summaries[RUNNER], summaries[LEGACY])
        parity["runner_vs_legacy_signature_match"] = signature_match(parity["runner_vs_legacy"])
    else:
        parity["runner_vs_legacy_signature_match"] = False
    if RUNNER in summaries and CUPY in summaries:
        parity["runner_vs_cupy"] = signature_delta(summaries[RUNNER], summaries[CUPY])
        parity["runner_vs_cupy_signature_match"] = signature_match(parity["runner_vs_cupy"])
    else:
        parity["runner_vs_cupy_signature_match"] = False
    return parity


def signature_delta(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_count_delta": int(left["row_count"]) - int(right["row_count"]),
        "bounded_neighbor_count_delta": int(left["bounded_neighbor_count"])
        - int(right["bounded_neighbor_count"]),
        "nearest_id_checksum_delta": int(left["nearest_id_checksum"]) - int(right["nearest_id_checksum"]),
        "kth_id_checksum_delta": int(left["kth_id_checksum"]) - int(right["kth_id_checksum"]),
        "sum_distance_delta": float(left["sum_distance"]) - float(right["sum_distance"]),
        "sum_distance_relative_error": abs(float(left["sum_distance"]) - float(right["sum_distance"]))
        / max(abs(float(right["sum_distance"])), 1.0),
    }


def signature_match(delta: dict[str, Any]) -> bool:
    return bool(
        delta["row_count_delta"] == 0
        and delta["bounded_neighbor_count_delta"] == 0
        and delta["nearest_id_checksum_delta"] == 0
        and delta["kth_id_checksum_delta"] == 0
        and float(delta["sum_distance_relative_error"]) <= 1.0e-4
    )


def comparison_summary(phase_rows: dict[str, dict[str, Any]]) -> dict[str, float]:
    comparisons: dict[str, float] = {}
    if LEGACY in phase_rows and RUNNER in phase_rows:
        comparisons["runner_vs_legacy_hot_speedup"] = speedup(
            phase_rows[LEGACY]["hot_query_median_sec"],
            phase_rows[RUNNER]["hot_query_median_sec"],
        )
        comparisons["runner_vs_legacy_cold_plus_query_speedup"] = speedup(
            phase_rows[LEGACY]["cold_plus_query_wall_sec"],
            phase_rows[RUNNER]["cold_plus_query_wall_sec"],
        )
        comparisons["runner_vs_legacy_runner_wall_speedup"] = speedup(
            phase_rows[LEGACY]["runner_wall_sec"],
            phase_rows[RUNNER]["runner_wall_sec"],
        )
    if CUPY in phase_rows and RUNNER in phase_rows:
        comparisons["runner_over_cupy_hot_speedup"] = speedup(
            phase_rows[CUPY]["hot_query_median_sec"],
            phase_rows[RUNNER]["hot_query_median_sec"],
        )
        comparisons["runner_over_cupy_cold_plus_query_speedup"] = speedup(
            phase_rows[CUPY]["cold_plus_query_wall_sec"],
            phase_rows[RUNNER]["cold_plus_query_wall_sec"],
        )
        comparisons["runner_over_cupy_runner_wall_speedup"] = speedup(
            phase_rows[CUPY]["runner_wall_sec"],
            phase_rows[RUNNER]["runner_wall_sec"],
        )
    return comparisons


def all_claim_flags_false(variant_payloads: dict[str, dict[str, Any]]) -> bool:
    forbidden = (
        "release_authorized",
        "public_speedup_claim_authorized",
        "broad_v3_faster_than_v2_claim_authorized",
        "true_zero_copy_claim_authorized",
        "full_all_app_rerun_authorized_by_this_packet",
    )
    for payload in variant_payloads.values():
        for key in forbidden:
            if bool(payload.get(key, False)):
                return False
        boundary = payload.get("claim_boundary")
        if isinstance(boundary, dict):
            for key in forbidden:
                if bool(boundary.get(key, False)):
                    return False
    runner_metadata = variant_payloads.get(RUNNER, {}).get("runner_metadata", {})
    if isinstance(runner_metadata, dict):
        for key in forbidden:
            if bool(runner_metadata.get(key, False)):
                return False
    return True


def speedup(reference_sec: float, candidate_sec: float) -> float:
    return float(reference_sec) / float(candidate_sec) if float(candidate_sec) > 0.0 else 0.0


def environment_payload(*, require_rt_hardware: bool) -> dict[str, Any]:
    return {
        "python": sys.version,
        "cwd": str(ROOT),
        "git_head": command_output(["git", "rev-parse", "HEAD"], cwd=ROOT).strip(),
        "git_dirty": command_output(["git", "status", "--short"], cwd=ROOT).splitlines(),
        "nvidia_smi": command_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,compute_cap", "--format=csv,noheader"]
        ).strip(),
        "hardware_gate": v3_optix_hardware_gate.build_payload(
            require_rt_hardware=require_rt_hardware,
            sample_nvidia_smi=None,
        ),
    }


def command_output(command: list[str], *, cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd is not None else None,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # pragma: no cover - host tool dependent
        return f"ERROR: {exc!r}"
    text = completed.stdout.strip()
    if completed.stderr.strip():
        text = (text + "\n" if text else "") + completed.stderr.strip()
    return text


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return str(value)
        return value
    return value


def _readme(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Phoenix V3 RTNN Prepared-Execution Runner Repeat50 POD A/B",
        "",
        f"Status: `{summary['status']}`",
        "",
        "This packet is focused runtime-trunk evidence only. It does not authorize release, "
        "all-app reruns, broad V3-over-V2 claims, or public speedup wording.",
        "",
        "## Summary",
        "",
        f"- Point count: `{summary['point_count']}`",
        f"- Repeat: `{summary['repeat']}`",
        f"- Runtime trunk executes: `{summary['runtime_trunk_executes_end_to_end']}`",
        f"- Runtime-sourced material candidate: `{summary['runtime_sourced_material_gain_candidate']}`",
        f"- Scorecard-bound movement candidate: `{summary.get('scorecard_bound_runtime_sourced_movement_candidate', False)}`",
        f"- Failed checks: `{', '.join(payload['failed_checks']) if payload['failed_checks'] else 'none'}`",
        "",
        "## Comparisons",
        "",
    ]
    for key, value in sorted(summary["comparisons"].items()):
        lines.append(f"- `{key}`: `{value:.6f}x`")
    if summary.get("scorecard_bound_shape"):
        lines.extend(
            [
                "",
                "## Scorecard Projection",
                "",
                f"- Shape: `{summary['scorecard_bound_shape']['shape_key']}`",
            ]
        )
        for row in summary.get("scorecard_movement_projection", {}).get("rows", ()):
            if row.get("directly_moved_by_this_optix_runner"):
                lines.append(
                    "- `{case_id}` projected runner-wall V3/V2: `{value:.6f}x`".format(
                        case_id=row["case_id"],
                        value=float(row["projected_runner_wall_v3_speedup_vs_v2"]),
                    )
                )
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "- `release_authorized: false`",
            "- `public_speedup_claim_authorized: false`",
            "- `broad_v3_faster_than_v2_claim_authorized: false`",
            "- `full_all_app_rerun_authorized_by_this_packet: false`",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
