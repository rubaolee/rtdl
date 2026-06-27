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


BACKEND_LABELS = {
    "embree": "paper_rt_embree",
    "optix": "paper_rt_optix_prepared_grouped_reduction",
}

DEFAULT_REPEAT_OVERRIDES = {
    ("embree", "count"): 400,
    ("embree", "sum"): 10,
    ("optix", "count"): 5000,
    ("optix", "sum"): 1000,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M28 RayDB prepared grouped-reduction refresh evidence."
    )
    parser.add_argument("--generated-rows", type=int, default=262_144)
    parser.add_argument("--generated-groups", type=int, default=1024)
    parser.add_argument("--generated-revenue-mod", type=int, default=64)
    parser.add_argument("--modes", default="count,sum")
    parser.add_argument("--backends", default="embree,optix")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument(
        "--repeat-overrides",
        default="embree:count=400,embree:sum=10,optix:count=5000,optix:sum=1000",
        help="Comma-separated backend:mode=repeat entries.",
    )
    parser.add_argument("--include-iteration-walls", action="store_true")
    parser.add_argument(
        "--optix-ray-batch-layout",
        choices=("host_packed", "cupy_device_columns", "torch_device_columns"),
        default="host_packed",
        help=(
            "Ray-batch layout for the OptiX prepared grouped-reduction route. "
            "Embree always uses host_packed."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4425_v3_0_m28_raydb_prepared_grouped_refresh.json"),
    )
    args = parser.parse_args()

    if args.generated_rows <= 0:
        raise ValueError("--generated-rows must be positive")
    if args.generated_groups <= 0:
        raise ValueError("--generated-groups must be positive")
    if args.generated_revenue_mod <= 0:
        raise ValueError("--generated-revenue-mod must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")

    modes = tuple(item.strip() for item in args.modes.split(",") if item.strip())
    backends = tuple(item.strip() for item in args.backends.split(",") if item.strip())
    if not modes:
        raise ValueError("--modes must include at least one mode")
    if not backends:
        raise ValueError("--backends must include at least one backend")
    unsupported_modes = sorted(set(modes) - {"count", "sum"})
    if unsupported_modes:
        raise ValueError(f"unsupported mode(s): {', '.join(unsupported_modes)}")
    unsupported_backends = sorted(set(backends) - set(BACKEND_LABELS))
    if unsupported_backends:
        raise ValueError(f"unsupported backend(s): {', '.join(unsupported_backends)}")

    repeat_overrides = _parse_repeat_overrides(args.repeat_overrides)
    planned_rows = tuple(
        {
            "backend": backend,
            "backend_label": BACKEND_LABELS[backend],
            "mode": mode,
            "repeat": int(repeat_overrides.get((backend, mode), DEFAULT_REPEAT_OVERRIDES[(backend, mode)])),
            "warmup": int(args.warmup),
            "ray_batch_layout": (
                str(args.optix_ray_batch_layout) if backend == "optix" else "host_packed"
            ),
        }
        for backend in backends
        for mode in modes
    )

    if args.dry_run:
        payload = _base_payload(args=args, modes=modes, backends=backends)
        payload.update(
            {
                "status": "dry_run",
                "planned_rows": planned_rows,
                "rows": (),
                "comparison": {
                    "all_match_cpu_reference": None,
                    "same_contract_backend_pairs": (),
                },
            }
        )
        _write_payload(payload, args.output)
        print(json.dumps({"status": payload["status"], "planned_rows": planned_rows}, indent=2))
        return 0

    from examples.benchmark_apps.raydb_style import (
        rtdl_raydb_style_benchmark_app as raydb,
    )

    rows = []
    for planned in planned_rows:
        result = raydb.run_result_mode(
            str(planned["mode"]),
            backend=str(planned["backend_label"]),
            fixture_kind="generated",
            generated_rows=args.generated_rows,
            generated_groups=args.generated_groups,
            generated_revenue_mod=args.generated_revenue_mod,
            warmup=int(planned["warmup"]),
            repeat=int(planned["repeat"]),
            summary_only_iterations=not args.include_iteration_walls,
            ray_batch_layout=str(planned["ray_batch_layout"]),
        )
        rows.append(
            _compact_row(
                result,
                backend=str(planned["backend"]),
                repeat=int(planned["repeat"]),
                primitive_first_plan=raydb.describe_raydb_v2_5_primitive_first_plan(str(planned["mode"])),
            )
        )

    comparison = _compare_rows(rows)
    payload = _base_payload(args=args, modes=modes, backends=backends)
    payload.update(
        {
            "status": "ok",
            "planned_rows": planned_rows,
            "rows": tuple(rows),
            "comparison": comparison,
        }
    )
    if not comparison["all_match_cpu_reference"]:
        raise RuntimeError("M28 RayDB prepared grouped refresh failed CPU-reference parity")
    _write_payload(payload, args.output)
    print(json.dumps({"status": payload["status"], "comparison": comparison, "rows": rows}, indent=2))
    print(f"wrote {args.output}")
    return 0


def _base_payload(*, args: argparse.Namespace, modes: tuple[str, ...], backends: tuple[str, ...]) -> dict[str, object]:
    return {
        "version": "rtdl.v3_0.raydb_prepared_grouped_refresh.m28",
        "goal": "Goal4425 V3.0 M28 RayDB prepared grouped-reduction refresh",
        "parameters": {
            "generated_rows": int(args.generated_rows),
            "generated_groups": int(args.generated_groups),
            "generated_revenue_mod": int(args.generated_revenue_mod),
            "modes": modes,
            "backends": backends,
            "warmup": int(args.warmup),
            "include_iteration_walls": bool(args.include_iteration_walls),
            "optix_ray_batch_layout": str(args.optix_ray_batch_layout),
        },
        "environment": _environment_snapshot(),
        "claim_boundary": {
            "primitive_first_no_partner_needed": True,
            "partner_continuation_required": False,
            "native_engine_customization": False,
            "app_specific_native_engine_logic_allowed": False,
            "paper_reproduction_claim_authorized": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
        },
    }


def _compact_row(
    result: dict[str, object],
    *,
    backend: str,
    repeat: int,
    primitive_first_plan: dict[str, object],
) -> dict[str, object]:
    metadata = dict(result["metadata"])
    timings = dict(metadata["timings"])
    iteration_summary = dict(metadata.get("prepared_iteration_wall_summary") or {})
    session = dict(metadata.get("v2_4_prepared_session") or {})
    return {
        "backend": backend,
        "backend_label": result["backend"],
        "mode": result["mode"],
        "row_count": int(result["row_count"]),
        "repeat": int(repeat),
        "warmup": int(metadata["prepared_internal_warmup"]),
        "matches_cpu_reference": bool(result["matches_cpu_reference"]),
        "elapsed_median_sec": float(result["elapsed_sec"]),
        "prepared_iteration_total_sec": float(iteration_summary.get("total_sec", 0.0)),
        "prepared_iteration_count": int(iteration_summary.get("count", 0)),
        "workload_build_sec": float(timings.get("workload_build", 0.0)),
        "cold_prepare_total_sec": float(timings.get("cold_prepare_total", 0.0)),
        "prepared_native_total_sec": float(timings.get("prepared_native_total", 0.0)),
        "prepared_ray_batch_sec": float(timings.get("prepared_ray_batch", 0.0)),
        "prepared_ray_batch_layout": metadata.get("prepared_ray_batch_layout", "host_packed"),
        "prepared_ray_batch_column_partner": metadata.get("prepared_ray_batch_column_partner"),
        "prepared_ray_batch_created_from": metadata.get("prepared_ray_batch_created_from"),
        "native_device_column_path_used": bool(metadata.get("native_device_column_path_used", False)),
        "traversal_median_sec": float(timings.get("traversal", 0.0)),
        "native_call_wall_median_sec": float(timings.get("native_call_wall", 0.0)),
        "row_presentation_median_sec": float(timings.get("row_presentation", 0.0)),
        "triangle_count": int(metadata["triangle_count"]),
        "ray_count": int(metadata["ray_count"]),
        "logical_ray_count": int(metadata.get("logical_ray_count", metadata["ray_count"])),
        "host_packed_ray_count": int(metadata.get("host_packed_ray_count", metadata["ray_count"])),
        "ray_materialization": metadata.get("ray_materialization"),
        "hit_event_count_before_dedup": metadata.get("hit_event_count_before_dedup"),
        "contract": metadata["contract"],
        "native_symbol": metadata.get("native_symbol"),
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "prepared_steady_state": bool(metadata.get("prepared_steady_state", False)),
        "prepared_primitive_payload_reused": bool(metadata.get("prepared_primitive_payload_reused", False)),
        "prepared_ray_batch_reused": bool(metadata.get("prepared_ray_batch_reused", False)),
        "v2_5_selected_path": primitive_first_plan["selected_path"],
        "v2_5_selection_reason": primitive_first_plan["selection_reason"],
        "partner_continuation_required": bool(primitive_first_plan["partner_continuation_required"]),
        "partner_continuation_available": bool(primitive_first_plan["partner_continuation_available"]),
        "v2_4_primitive": session.get("primitive"),
        "v2_4_backend": session.get("backend"),
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_authorized": bool(metadata.get("true_zero_copy_authorized", False)),
        },
    }


def _compare_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    by_mode_backend = {(row["mode"], row["backend"]): row for row in rows}
    backend_pairs = []
    for mode in sorted({str(row["mode"]) for row in rows}):
        optix = by_mode_backend.get((mode, "optix"))
        embree = by_mode_backend.get((mode, "embree"))
        if optix is None or embree is None:
            continue
        optix_sec = float(optix["elapsed_median_sec"])
        embree_sec = float(embree["elapsed_median_sec"])
        backend_pairs.append(
            {
                "mode": mode,
                "embree_median_sec": embree_sec,
                "optix_median_sec": optix_sec,
                "embree_over_optix_median": embree_sec / optix_sec if optix_sec > 0.0 else None,
                "same_contract": embree["v2_4_primitive"] == optix["v2_4_primitive"],
                "both_match_cpu_reference": bool(embree["matches_cpu_reference"])
                and bool(optix["matches_cpu_reference"]),
                "comparison_scope": "internal_same_contract_prepared_query_refresh_not_public_speedup",
            }
        )
    return {
        "all_match_cpu_reference": all(bool(row["matches_cpu_reference"]) for row in rows),
        "all_prepared_steady_state": all(bool(row["prepared_steady_state"]) for row in rows),
        "all_primitive_payload_reused": all(bool(row["prepared_primitive_payload_reused"]) for row in rows),
        "all_ray_batch_reused": all(bool(row["prepared_ray_batch_reused"]) for row in rows),
        "no_partner_continuation_required": all(not bool(row["partner_continuation_required"]) for row in rows),
        "same_contract_backend_pairs": tuple(backend_pairs),
        "public_speedup_claim_authorized": False,
    }


def _parse_repeat_overrides(raw: str) -> dict[tuple[str, str], int]:
    parsed: dict[tuple[str, str], int] = {}
    if not raw:
        return parsed
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        key, value = item.split("=", 1)
        backend, mode = key.split(":", 1)
        backend = backend.strip()
        mode = mode.strip()
        repeat = int(value)
        if backend not in BACKEND_LABELS:
            raise ValueError(f"unsupported repeat override backend: {backend}")
        if mode not in {"count", "sum"}:
            raise ValueError(f"unsupported repeat override mode: {mode}")
        if repeat <= 0:
            raise ValueError("repeat override values must be positive")
        parsed[(backend, mode)] = repeat
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
