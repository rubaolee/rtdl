from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


DEFAULT_LEFT = Path("data/rayjoin_public_cdb/br_county_start256_count512.cdb")
DEFAULT_RIGHT = Path("data/rayjoin_public_cdb/br_soil_start256_count512.cdb")
OUTPUT_CONTRACT = "overlay_active_pair_dependency_count"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M33 Spatial RayJoin overlay active-count same-contract evidence."
    )
    parser.add_argument("--left-cdb", type=Path, default=DEFAULT_LEFT)
    parser.add_argument("--right-cdb", type=Path, default=DEFAULT_RIGHT)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=25)
    parser.add_argument("--embree-threads", default="auto")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4430_v3_0_m33_rayjoin_overlay_active_count_same_contract.json"),
    )
    args = parser.parse_args()

    _validate_args(args)
    planned = {
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "embree_threads": str(args.embree_threads),
        "output_contract": OUTPUT_CONTRACT,
        "same_contract_backends": ("embree", "optix"),
    }
    if args.dry_run:
        payload = _base_payload(args)
        payload.update(
            {
                "status": "dry_run",
                "planned": planned,
                "rows": (),
                "comparison": {
                    "same_output_contract": None,
                    "active_counts_match": None,
                    "old_raw_relation_row_contract_rejected": True,
                },
            }
        )
        _write_payload(payload, args.output)
        print(json.dumps({"status": payload["status"], "planned": planned}, indent=2))
        return 0

    from rtdsl.datasets import chains_to_polygons
    from rtdsl.datasets import load_cdb

    left_path = _resolve_path(args.left_cdb)
    right_path = _resolve_path(args.right_cdb)
    left_dataset = load_cdb(left_path)
    right_dataset = load_cdb(right_path)
    left_shapes = tuple(chains_to_polygons(left_dataset))
    right_shapes = tuple(chains_to_polygons(right_dataset))

    rows = [
        _run_embree(
            left_shapes=left_shapes,
            right_shapes=right_shapes,
            args=args,
        ),
        _run_optix(
            left_shapes=left_shapes,
            right_shapes=right_shapes,
            args=args,
        ),
    ]
    comparison = _compare_rows(rows)
    payload = _base_payload(args)
    payload.update(
        {
            "status": "ok",
            "planned": planned,
            "case_shape": {
                "left_shape_count": len(left_shapes),
                "right_shape_count": len(right_shapes),
                "left_cdb": str(left_path),
                "right_cdb": str(right_path),
            },
            "rows": tuple(rows),
            "comparison": comparison,
        }
    )
    if not comparison["same_output_contract"]:
        raise RuntimeError("M33 overlay active-count comparison found output-contract mismatch")
    if not comparison["active_counts_match"]:
        raise RuntimeError("M33 overlay active-count comparison found active-count mismatch")
    _write_payload(payload, args.output)
    print(json.dumps({"status": payload["status"], "comparison": comparison, "rows": rows}, indent=2))
    print(f"wrote {args.output}")
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")


def _base_payload(args: argparse.Namespace) -> dict[str, object]:
    return {
        "version": "rtdl.v3_0.spatial_rayjoin_overlay_active_count_same_contract.m33",
        "goal": "Goal4430 V3.0 M33 Spatial RayJoin overlay active-count same-contract refresh",
        "parameters": {
            "left_cdb": str(args.left_cdb),
            "right_cdb": str(args.right_cdb),
            "warmup": int(args.warmup),
            "repeat": int(args.repeat),
            "embree_threads": str(args.embree_threads),
        },
        "environment": _environment_snapshot(),
        "claim_boundary": {
            "benchmark_app": "spatial_rayjoin",
            "workload": "overlay_seed",
            "same_contract_active_count_only": True,
            "full_polygon_overlay_claim_authorized": False,
            "rayjoin_section57_full_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }


def _run_embree(*, left_shapes: tuple[object, ...], right_shapes: tuple[object, ...], args: argparse.Namespace) -> dict[str, object]:
    import rtdsl as rt
    from rtdsl.embree_runtime import pack_polygons

    rt.configure_embree(threads=str(args.embree_threads))
    setup_started = perf_counter()
    packed_left = pack_polygons(records=left_shapes)
    prepared = rt.prepare_embree_shape_pair_active_count_2d(right_shapes)
    setup_sec = perf_counter() - setup_started
    try:
        durations = []
        counts = []
        traversal_seconds = []
        for index in range(int(args.warmup) + int(args.repeat)):
            started = perf_counter()
            result = prepared.count_active_packed(packed_left)
            elapsed = perf_counter() - started
            if index >= int(args.warmup):
                durations.append(elapsed)
                counts.append(int(result["active_count"]))
                traversal_seconds.append(float(result["traversal_seconds"]))
        return {
            "backend": "embree",
            "execution_route": "prepared_embree_shape_pair_active_count_2d",
            "native_symbol": "rtdl_embree_shape_pair_active_count_2d_count",
            "output_contract": OUTPUT_CONTRACT,
            "active_count": counts[-1],
            "counts_stable": len(set(counts)) == 1,
            "left_shape_count": len(left_shapes),
            "right_shape_count": len(right_shapes),
            "setup_sec": float(setup_sec),
            "warmup": int(args.warmup),
            "repeat": int(args.repeat),
            "timed_total_sec": float(sum(durations)),
            "timed_median_sec": float(statistics.median(durations)),
            "timed_min_sec": float(min(durations)),
            "timed_max_sec": float(max(durations)),
            "native_traversal_median_sec": float(statistics.median(traversal_seconds)),
            "row_materialization_avoided": True,
            "threads": str(args.embree_threads),
            "claim_boundary": _row_claim_boundary(),
        }
    finally:
        prepared.close()


def _run_optix(*, left_shapes: tuple[object, ...], right_shapes: tuple[object, ...], args: argparse.Namespace) -> dict[str, object]:
    from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (
        pack_rayjoin_optix_shape_pair_active_count_left_shapes,
        prepare_rayjoin_optix_shape_pair_active_count,
    )

    setup_started = perf_counter()
    prepared = prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal4430 same-contract overlay active-count refresh.",
    )
    packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
    setup_sec = perf_counter() - setup_started
    try:
        payload = prepared.run_packed_left(
            packed_left,
            query_repeat=int(args.repeat),
            warmup=int(args.warmup),
        )
        phases = dict(payload["phases_sec"])
        return {
            "backend": "optix",
            "execution_route": payload["execution_route"],
            "native_symbol": payload["prepared_active_count_executor"]["native_run_symbol"],
            "output_contract": payload["summary"]["output_contract"],
            "active_count": int(payload["row_count"]),
            "counts_stable": True,
            "left_shape_count": len(left_shapes),
            "right_shape_count": len(right_shapes),
            "setup_sec": float(setup_sec),
            "warmup": int(args.warmup),
            "repeat": int(args.repeat),
            "timed_total_sec": float(phases["prepared_query_sec_total_sec"]),
            "timed_median_sec": float(phases["prepared_query_sec"]),
            "native_traversal_median_sec": float(phases["active_count_device_continuation_sec"]),
            "prepare_active_count_executor_sec": float(phases["prepare_active_count_executor_sec"]),
            "row_materialization_avoided": True,
            "threads": None,
            "claim_boundary": _row_claim_boundary(),
        }
    finally:
        packed_left.close()
        prepared.close()


def _compare_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    by_backend = {str(row["backend"]): row for row in rows}
    embree = by_backend["embree"]
    optix = by_backend["optix"]
    embree_median = float(embree["timed_median_sec"])
    optix_median = float(optix["timed_median_sec"])
    return {
        "same_backends": tuple(sorted(by_backend)),
        "same_output_contract": embree["output_contract"] == optix["output_contract"] == OUTPUT_CONTRACT,
        "active_counts_match": int(embree["active_count"]) == int(optix["active_count"]),
        "active_count": int(optix["active_count"]),
        "all_counts_stable": all(bool(row["counts_stable"]) for row in rows),
        "all_row_materialization_avoided": all(bool(row["row_materialization_avoided"]) for row in rows),
        "old_raw_relation_row_contract_rejected": True,
        "old_embree_raw_relation_row_contract": "generic_row_count_raw_view_no_python_dicts",
        "old_raw_relation_row_count_not_comparable": True,
        "old_embree_raw_relation_row_count_not_comparable": True,
        "embree_over_optix_timed_median": embree_median / optix_median if optix_median else None,
        "optix_over_embree_timed_median": optix_median / embree_median if embree_median else None,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }


def _row_claim_boundary() -> dict[str, bool]:
    return {
        "full_polygon_overlay_claim_authorized": False,
        "rayjoin_section57_full_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
    }


def _resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _environment_snapshot() -> dict[str, object]:
    return {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "git_head": _git_head(),
    }


def _git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _write_payload(payload: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
