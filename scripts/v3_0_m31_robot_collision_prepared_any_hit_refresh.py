from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


DEFAULT_REPEATS = {
    "embree": 5,
    "optix": 5,
}

EXPECTED_CONTRACT = "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1"
LOWERING_MODES = ("python_objects", "numpy_arrays")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M31 Robot Collision prepared grouped-segment any-hit refresh evidence."
    )
    parser.add_argument("--dataset", default="scaled")
    parser.add_argument("--pose-count", type=int, default=262_144)
    parser.add_argument("--obstacle-count", type=int, default=8_192)
    parser.add_argument("--link-count", type=int, default=4)
    parser.add_argument("--backends", default="embree,optix")
    parser.add_argument("--lowering-mode", choices=LOWERING_MODES, default="python_objects")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument(
        "--repeat-overrides",
        default="embree=5,optix=5",
        help="Comma-separated backend=repeat entries.",
    )
    parser.add_argument(
        "--validate-probe-reference",
        action="store_true",
        help="Run the exact CPU probe reference. Intended only for small diagnostics.",
    )
    parser.add_argument("--summary-only-runs", action="store_true")
    parser.add_argument(
        "--skip-group-metadata",
        action="store_true",
        help="Do not materialize app-level ProbeGroup metadata during lowering.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4428_v3_0_m31_robot_collision_prepared_any_hit_refresh.json"),
    )
    args = parser.parse_args()

    _validate_args(args)
    backends = tuple(item.strip() for item in args.backends.split(",") if item.strip())
    if not backends:
        raise ValueError("--backends must include at least one backend")
    unsupported = sorted(set(backends) - set(DEFAULT_REPEATS))
    if unsupported:
        raise ValueError(f"unsupported backend(s): {', '.join(unsupported)}")
    repeat_overrides = _parse_repeat_overrides(args.repeat_overrides)
    planned_rows = tuple(
        {
            "backend": backend,
            "dataset": args.dataset,
            "pose_count": int(args.pose_count),
            "obstacle_count": int(args.obstacle_count),
            "link_count": int(args.link_count),
            "warmup": int(args.warmup),
            "repeat": int(repeat_overrides.get(backend, DEFAULT_REPEATS[backend])),
            "reuse_query_buffers": True,
            "lowering_mode": args.lowering_mode,
            "materialize_group_metadata": not bool(args.skip_group_metadata),
        }
        for backend in backends
    )

    if args.dry_run:
        payload = _base_payload(args=args, backends=backends)
        payload.update(
            {
                "status": "dry_run",
                "planned_rows": planned_rows,
                "rows": (),
                "comparison": {
                    "same_contract_backend_pair": None,
                    "all_signature_hashes_match_cross_backend": None,
                },
            }
        )
        _write_payload(payload, args.output)
        print(json.dumps({"status": payload["status"], "planned_rows": planned_rows}, indent=2))
        return 0

    from examples.current.research_benchmarks.robot_collision import (
        rtdl_robot_collision_benchmark_app as robot,
    )

    rows = []
    for planned in planned_rows:
        result = robot.run_prepared_reuse_probe(
            backend=str(planned["backend"]),
            dataset=str(args.dataset),
            pose_count=int(args.pose_count),
            obstacle_count=int(args.obstacle_count),
            link_count=int(args.link_count),
            repeats=int(planned["repeat"]),
            warmup=int(planned["warmup"]),
            reuse_query_buffers=True,
            validate_probe_reference=bool(args.validate_probe_reference),
            summary_only_runs=bool(args.summary_only_runs),
            lowering_mode=str(args.lowering_mode),
            materialize_group_metadata=not bool(args.skip_group_metadata),
        )
        rows.append(_compact_row(result))

    comparison = _compare_rows(rows)
    payload = _base_payload(args=args, backends=backends)
    payload.update(
        {
            "status": "ok",
            "planned_rows": planned_rows,
            "rows": tuple(rows),
            "comparison": comparison,
        }
    )
    if not comparison["all_same_contract"]:
        raise RuntimeError("M31 Robot Collision prepared any-hit refresh found contract mismatch")
    if not comparison["all_signature_hashes_match_cross_backend"]:
        raise RuntimeError("M31 Robot Collision prepared any-hit refresh found flag-signature mismatch")
    _write_payload(payload, args.output)
    print(json.dumps({"status": payload["status"], "comparison": comparison, "rows": rows}, indent=2))
    print(f"wrote {args.output}")
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if args.pose_count <= 0:
        raise ValueError("--pose-count must be positive")
    if args.obstacle_count <= 0:
        raise ValueError("--obstacle-count must be positive")
    if args.link_count <= 0:
        raise ValueError("--link-count must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")


def _base_payload(*, args: argparse.Namespace, backends: tuple[str, ...]) -> dict[str, object]:
    return {
        "version": (
            "rtdl.v3_0.robot_collision_numpy_lowering.m50"
            if args.lowering_mode == "numpy_arrays"
            else "rtdl.v3_0.robot_collision_prepared_any_hit_refresh.m31"
        ),
        "goal": (
            "Goal4446 V3.0 M50 Robot Collision NumPy vectorized query lowering"
            if args.lowering_mode == "numpy_arrays"
            else "Goal4428 V3.0 M31 Robot Collision prepared grouped-segment any-hit refresh"
        ),
        "parameters": {
            "dataset": args.dataset,
            "pose_count": int(args.pose_count),
            "obstacle_count": int(args.obstacle_count),
            "link_count": int(args.link_count),
            "backends": backends,
            "warmup": int(args.warmup),
            "validate_probe_reference": bool(args.validate_probe_reference),
            "reuse_query_buffers": True,
            "lowering_mode": str(args.lowering_mode),
            "summary_only_runs": bool(args.summary_only_runs),
            "skip_group_metadata": bool(args.skip_group_metadata),
        },
        "environment": _environment_snapshot(),
        "claim_boundary": {
            "primitive_first_no_partner_needed": True,
            "partner_continuation_required": False,
            "native_engine_customization": False,
            "app_specific_native_engine_logic_allowed": False,
            "continuous_collision_claim_authorized": False,
            "robot_planner_claim_authorized": False,
            "exact_solid_collision_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }


def _compact_row(result: dict[str, object]) -> dict[str, object]:
    case_shape = dict(result["case_shape"])
    reuse = dict(result["reuse_metadata"])
    summary = dict(result["run_summary"])
    total_summary = dict(summary["total_run_seconds"])
    phase_summary = {
        name: dict(value)
        for name, value in dict(summary["phase_timing_seconds"]).items()
    }
    tail_phases = dict(result["tail_medians"]["phase_timing_seconds"])
    measured_runs = [dict(row) for row in result["runs"] if not bool(row["is_warmup"])]
    signature_hashes = sorted(
        {
            hashlib.sha256(str(row["flags_signature"]).encode("ascii")).hexdigest()
            for row in measured_runs
        }
    )
    flagged_group_counts = sorted({int(row["flagged_group_count"]) for row in measured_runs})
    return {
        "backend": result["backend"],
        "mode": result["mode"],
        "dataset": result["dataset"],
        "contract": result["contract"],
        "case_shape": case_shape,
        "pose_count": int(case_shape["pose_count"]),
        "link_count": int(case_shape["link_count"]),
        "group_count": int(case_shape["group_count"]),
        "segment_count": int(case_shape["segment_count"]),
        "static_obstacle_triangle_count": int(case_shape["static_obstacle_triangle_count"]),
        "repeat": int(result["warmup_protocol"]["repeat_count"]),
        "warmup": int(result["warmup_protocol"]["warmup_count"]),
        "measured_run_count": int(reuse["measured_run_count"]),
        "tail_total_run_median_sec": float(result["tail_medians"]["total_run_seconds"]),
        "tail_total_run_window_sec": float(total_summary["total_sec"]),
        "phase_median_sec": {name: float(value) for name, value in tail_phases.items()},
        "phase_window_sec": {
            name: float(values["total_sec"])
            for name, values in phase_summary.items()
        },
        "flagged_group_count_values": flagged_group_counts,
        "measured_signature_hashes": signature_hashes,
        "all_run_signatures_identical": bool(reuse["all_run_signatures_identical"]),
        "host_query_output_buffers_reused": bool(reuse["host_query_output_buffers_reused"]),
        "native_query_output_buffers_reused": bool(reuse["native_query_output_buffers_reused"]),
        "probe_reference_validated": bool(reuse["probe_reference_validated"]),
        "probe_reference_flagged_group_count": reuse["probe_reference_flagged_group_count"],
        "prepared_scene_reused": bool(reuse["prepared_scene_reused"]),
        "query_input_sequences_reused": bool(reuse["query_input_sequences_reused"]),
        "prepared_run_indices_strictly_increase": bool(reuse["prepared_run_indices_strictly_increase"]),
        "prepared_query_run_indices_strictly_increase": bool(
            reuse["prepared_query_run_indices_strictly_increase"]
        ),
        "prepared_query_descriptor": reuse["prepared_query_descriptor"],
        "app_lowering_seconds": float(result["app_lowering_seconds"]),
        "lowering_mode": result.get("lowering_mode"),
        "group_metadata_materialized": result.get("group_metadata_materialized"),
        "claim_boundary": {
            "primitive_first_no_partner_needed": True,
            "partner_continuation_required": False,
            "native_engine_customization": False,
            "public_speedup_claim_authorized": False,
            "continuous_collision_claim_authorized": False,
            "robot_planner_claim_authorized": False,
            "exact_solid_collision_claim_authorized": False,
        },
    }


def _compare_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    by_backend = {str(row["backend"]): row for row in rows}
    all_same_contract = all(row["contract"] == EXPECTED_CONTRACT for row in rows)
    signature_sets = {tuple(row["measured_signature_hashes"]) for row in rows}
    flagged_count_sets = {tuple(row["flagged_group_count_values"]) for row in rows}
    has_signature_rows = bool(rows) and all(bool(row["measured_signature_hashes"]) for row in rows)
    has_flagged_count_rows = bool(rows) and all(bool(row["flagged_group_count_values"]) for row in rows)
    pair = None
    optix = by_backend.get("optix")
    embree = by_backend.get("embree")
    if optix is not None and embree is not None:
        embree_total = float(embree["tail_total_run_median_sec"])
        optix_total = float(optix["tail_total_run_median_sec"])
        embree_traversal = float(embree["phase_median_sec"]["traversal"])
        optix_traversal = float(optix["phase_median_sec"]["traversal"])
        pair = {
            "embree_total_run_median_sec": embree_total,
            "optix_total_run_median_sec": optix_total,
            "embree_over_optix_total_run_median": embree_total / optix_total if optix_total > 0.0 else None,
            "embree_traversal_median_sec": embree_traversal,
            "optix_traversal_median_sec": optix_traversal,
            "embree_over_optix_traversal_median": embree_traversal / optix_traversal
            if optix_traversal > 0.0
            else None,
            "embree_total_run_window_sec": float(embree["tail_total_run_window_sec"]),
            "optix_total_run_window_sec": float(optix["tail_total_run_window_sec"]),
            "same_contract": embree["contract"] == optix["contract"],
            "same_case_shape": embree["case_shape"] == optix["case_shape"],
            "same_signature_hashes": embree["measured_signature_hashes"] == optix["measured_signature_hashes"],
            "same_flagged_group_counts": embree["flagged_group_count_values"]
            == optix["flagged_group_count_values"],
            "comparison_scope": "internal_same_contract_prepared_grouped_segment_any_hit_refresh_not_public_speedup",
        }
    return {
        "all_same_contract": all_same_contract,
        "all_signature_hashes_match_cross_backend": has_signature_rows and len(signature_sets) == 1,
        "all_flagged_group_counts_match_cross_backend": has_flagged_count_rows and len(flagged_count_sets) == 1,
        "all_primitive_first_no_partner": all(
            not bool(row["claim_boundary"]["partner_continuation_required"]) for row in rows
        ),
        "all_host_buffer_reuse_same_contract": all(
            bool(row["host_query_output_buffers_reused"]) and not bool(row["native_query_output_buffers_reused"])
            for row in rows
        ),
        "same_contract_backend_pair": pair,
        "public_speedup_claim_authorized": False,
    }


def _parse_repeat_overrides(raw: str) -> dict[str, int]:
    parsed: dict[str, int] = {}
    if not raw:
        return parsed
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        backend, value = item.split("=", 1)
        backend = backend.strip()
        if backend not in DEFAULT_REPEATS:
            raise ValueError(f"unsupported repeat override backend: {backend}")
        repeat = int(value)
        if repeat <= 0:
            raise ValueError("repeat override values must be positive")
        parsed[backend] = repeat
    return parsed


def _environment_snapshot() -> dict[str, object]:
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "git_head": _run_text(["git", "rev-parse", "HEAD"], cwd=ROOT).strip(),
        "nvidia_smi": _run_text(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ],
            cwd=ROOT,
        ).strip(),
    }


def _run_text(command: list[str], *, cwd: Path) -> str:
    try:
        completed = subprocess.run(command, cwd=str(cwd), check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (completed.stdout or "") + (completed.stderr or "")


def _write_payload(payload: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
