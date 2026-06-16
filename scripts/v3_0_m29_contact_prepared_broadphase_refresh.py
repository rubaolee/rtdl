from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


DEFAULT_REPEATS = {
    "embree": 20,
    "optix": 20,
}

EXPECTED_DISCOVERY_PRIMITIVE = "AABB_INDEX_QUERY_2D"
EXPECTED_DISCOVERY_CONTRACT = "generic_aabb_intersection_pair_rows_2d"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M29 contact prepared AABB broadphase refresh evidence."
    )
    parser.add_argument("--dataset", default="jittered_grid")
    parser.add_argument("--grid-count", type=int, default=65_536)
    parser.add_argument("--witness-capacity", type=int, default=None)
    parser.add_argument("--resolution", type=int, default=None)
    parser.add_argument("--discovery-row-capacity", type=int, default=None)
    parser.add_argument("--backends", default="embree,optix")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument(
        "--repeat-overrides",
        default="embree=20,optix=20",
        help="Comma-separated backend=repeat entries.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4426_v3_0_m29_contact_prepared_broadphase_refresh.json"),
    )
    args = parser.parse_args()

    if args.grid_count <= 0:
        raise ValueError("--grid-count must be positive")
    if args.witness_capacity is not None and args.witness_capacity <= 0:
        raise ValueError("--witness-capacity must be positive when provided")
    if args.resolution is not None and args.resolution <= 0:
        raise ValueError("--resolution must be positive when provided")
    if args.discovery_row_capacity is not None and args.discovery_row_capacity <= 0:
        raise ValueError("--discovery-row-capacity must be positive when provided")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")

    backends = tuple(item.strip() for item in args.backends.split(",") if item.strip())
    if not backends:
        raise ValueError("--backends must include at least one backend")
    unsupported = sorted(set(backends) - set(DEFAULT_REPEATS))
    if unsupported:
        raise ValueError(f"unsupported backend(s): {', '.join(unsupported)}")

    repeat_overrides = _parse_repeat_overrides(args.repeat_overrides)
    witness_capacity = int(args.witness_capacity or args.grid_count)
    planned_rows = tuple(
        {
            "backend": backend,
            "dataset": args.dataset,
            "grid_count": int(args.grid_count),
            "witness_capacity": witness_capacity,
            "warmup": int(args.warmup),
            "repeat": int(repeat_overrides.get(backend, DEFAULT_REPEATS[backend])),
        }
        for backend in backends
    )

    if args.dry_run:
        payload = _base_payload(args=args, backends=backends, witness_capacity=witness_capacity)
        payload.update(
            {
                "status": "dry_run",
                "planned_rows": planned_rows,
                "rows": (),
                "comparison": {
                    "all_match_cpu_reference": None,
                    "same_contract_backend_pair": None,
                },
            }
        )
        _write_payload(payload, args.output)
        print(json.dumps({"status": payload["status"], "planned_rows": planned_rows}, indent=2))
        return 0

    from examples.current.research_benchmarks.contact_manifold import (
        rtdl_contact_manifold_benchmark_app as contact,
    )

    rows = []
    for planned in planned_rows:
        result = contact.aabb_broadphase_collect_k_payload(
            dataset=str(args.dataset),
            witness_capacity=witness_capacity,
            grid_count=int(args.grid_count),
            resolution=args.resolution,
            backend="cpu_python_reference",
            discovery_backend=str(planned["backend"]),
            discovery_row_capacity=args.discovery_row_capacity,
            discovery_warmup_count=int(planned["warmup"]),
            discovery_repeat_count=int(planned["repeat"]),
        )
        rows.append(
            _compact_row(
                result,
                repeat=int(planned["repeat"]),
                warmup=int(planned["warmup"]),
                grid_count=int(args.grid_count),
            )
        )

    comparison = _compare_rows(rows)
    payload = _base_payload(args=args, backends=backends, witness_capacity=witness_capacity)
    payload.update(
        {
            "status": "ok",
            "planned_rows": planned_rows,
            "rows": tuple(rows),
            "comparison": comparison,
        }
    )
    if not comparison["all_match_cpu_reference"]:
        raise RuntimeError("M29 contact prepared broadphase refresh failed CPU-reference parity")
    if not comparison["all_complete_candidate_coverage"]:
        raise RuntimeError("M29 contact prepared broadphase refresh lost candidate coverage")
    _write_payload(payload, args.output)
    print(json.dumps({"status": payload["status"], "comparison": comparison, "rows": rows}, indent=2))
    print(f"wrote {args.output}")
    return 0


def _base_payload(
    *,
    args: argparse.Namespace,
    backends: tuple[str, ...],
    witness_capacity: int,
) -> dict[str, object]:
    return {
        "version": "rtdl.v3_0.contact_prepared_broadphase_refresh.m29",
        "goal": "Goal4426 V3.0 M29 contact prepared AABB broadphase refresh",
        "parameters": {
            "dataset": args.dataset,
            "grid_count": int(args.grid_count),
            "witness_capacity": int(witness_capacity),
            "resolution": args.resolution,
            "discovery_row_capacity": args.discovery_row_capacity,
            "backends": backends,
            "warmup": int(args.warmup),
        },
        "environment": _environment_snapshot(),
        "claim_boundary": {
            "primitive_first_no_partner_needed": True,
            "partner_continuation_required": False,
            "native_engine_customization": False,
            "app_specific_native_engine_logic_allowed": False,
            "full_contact_manifold_solver_claim_authorized": False,
            "continuous_collision_detection_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
    }


def _compact_row(
    result: dict[str, object],
    *,
    repeat: int,
    warmup: int,
    grid_count: int,
) -> dict[str, object]:
    phases = dict(result["run_phases"])
    all_pairs_count = int(result["all_pairs_count"])
    candidate_count = int(result["aabb_candidate_pair_count"])
    valid_count = int(result["valid_count"])
    query_median_sec = float(phases.get("emit_aabb_intersection_pair_rows_2d_median_sec", 0.0))
    query_total_sec = float(phases.get("emit_aabb_intersection_pair_rows_2d_total_sec", query_median_sec))
    collect_sec = float(phases.get("collect_k_bounded_rows_sec", 0.0))
    refinement_sec = float(phases.get("python_exact_refinement_sec", 0.0))
    session = dict(result.get("v2_4_prepared_session") or {})
    phase_timing = dict(result.get("v2_4_phase_timing") or {})
    return {
        "backend": result["candidate_discovery_backend"],
        "mode": result["mode"],
        "dataset": result["dataset"],
        "grid_count": int(grid_count),
        "scene_triangle_count": int(grid_count),
        "query_triangle_count": int(grid_count),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "matches_cpu_reference": bool(result["matches_cpu_reference"]),
        "complete_candidate_coverage": bool(result["complete_candidate_coverage"]),
        "overflowed": bool(result["overflowed"]),
        "candidate_discovery_primitive": result["candidate_discovery_primitive"],
        "candidate_discovery_contract": result["candidate_discovery_contract"],
        "primitive_under_test": result["primitive_under_test"],
        "v2_4_primitive": session.get("primitive"),
        "v2_4_backend": session.get("backend"),
        "v2_4_phase_timing": phase_timing,
        "witness_capacity": int(result["witness_capacity"]),
        "discovery_row_capacity": result["discovery_row_capacity"],
        "resolution": int(result["resolution"]),
        "resolution_policy": result["resolution_policy"],
        "all_pairs_count": all_pairs_count,
        "aabb_candidate_pair_count": candidate_count,
        "valid_count": valid_count,
        "candidate_compactness": candidate_count / all_pairs_count if all_pairs_count else None,
        "all_pairs_per_candidate": all_pairs_count / candidate_count if candidate_count else None,
        "candidate_to_valid_ratio": candidate_count / valid_count if valid_count else None,
        "exact_refinement_checks": int(result["exact_refinement_checks"]),
        "exact_refinement_checks_avoided": int(result["exact_refinement_checks_avoided"]),
        "prepare_aabb_index_2d_sec": float(phases.get("prepare_aabb_index_2d_sec", 0.0)),
        "query_median_sec": query_median_sec,
        "query_total_sec": query_total_sec,
        "query_min_sec": float(phases.get("emit_aabb_intersection_pair_rows_2d_min_sec", 0.0)),
        "query_max_sec": float(phases.get("emit_aabb_intersection_pair_rows_2d_max_sec", 0.0)),
        "query_measured_count": int(phases.get("emit_aabb_intersection_pair_rows_2d_measured_count", repeat)),
        "generic_aabb_broadphase_wall_sec": float(phases.get("generic_aabb_broadphase_wall_sec", 0.0)),
        "python_exact_refinement_sec": refinement_sec,
        "collect_k_bounded_rows_sec": collect_sec,
        "hot_query_plus_refinement_plus_collect_sec": query_median_sec + refinement_sec + collect_sec,
        "claim_boundary": {
            "primitive_first_no_partner_needed": True,
            "partner_continuation_required": False,
            "native_engine_customization": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "full_contact_manifold_solver_claim_authorized": False,
        },
    }


def _compare_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    by_backend = {str(row["backend"]): row for row in rows}
    pair = None
    optix = by_backend.get("optix")
    embree = by_backend.get("embree")
    if optix is not None and embree is not None:
        optix_query = float(optix["query_median_sec"])
        embree_query = float(embree["query_median_sec"])
        optix_hot = float(optix["hot_query_plus_refinement_plus_collect_sec"])
        embree_hot = float(embree["hot_query_plus_refinement_plus_collect_sec"])
        pair = {
            "embree_query_median_sec": embree_query,
            "optix_query_median_sec": optix_query,
            "embree_over_optix_query_median": embree_query / optix_query if optix_query > 0.0 else None,
            "embree_hot_sec": embree_hot,
            "optix_hot_sec": optix_hot,
            "embree_over_optix_hot": embree_hot / optix_hot if optix_hot > 0.0 else None,
            "same_contract": embree["candidate_discovery_contract"] == optix["candidate_discovery_contract"]
            and embree["v2_4_primitive"] == optix["v2_4_primitive"],
            "same_dataset": embree["dataset"] == optix["dataset"],
            "same_candidate_count": embree["aabb_candidate_pair_count"] == optix["aabb_candidate_pair_count"],
            "both_match_cpu_reference": bool(embree["matches_cpu_reference"])
            and bool(optix["matches_cpu_reference"]),
            "comparison_scope": "internal_same_contract_prepared_broadphase_refresh_not_public_speedup",
        }
    return {
        "all_match_cpu_reference": all(bool(row["matches_cpu_reference"]) for row in rows),
        "all_complete_candidate_coverage": all(bool(row["complete_candidate_coverage"]) for row in rows),
        "all_non_overflowed": all(not bool(row["overflowed"]) for row in rows),
        "no_partner_continuation_required": True,
        "same_contract_backend_pair": pair,
        "candidate_compactness_consistent": len({row["aabb_candidate_pair_count"] for row in rows}) <= 1,
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
