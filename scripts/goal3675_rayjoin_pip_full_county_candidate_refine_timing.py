from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402


SCHEMA = "rtdl.goal3675.rayjoin_pip_full_county_candidate_refine_timing.v1"


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _dirty() -> bool:
    try:
        return bool(_command_output(["git", "status", "--short"]))
    except Exception:
        return True


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_default_route_authorized": False,
    }


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot summarize an empty timing series")
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return float((ordered[middle - 1] + ordered[middle]) / 2.0)


def _pair_counter(rows: tuple[dict[str, int], ...]) -> Counter[tuple[int, int]]:
    return Counter((int(row["point_id"]), int(row["shape_id"])) for row in rows)


def _device_pairs(cp: Any, columns: dict[str, Any]) -> Counter[tuple[int, int]]:
    return Counter(
        zip(
            (int(value) for value in cp.asnumpy(columns["point_id"]).tolist()),
            (int(value) for value in cp.asnumpy(columns["shape_id"]).tolist()),
        )
    )


def _time_repeated(
    *,
    label: str,
    warmup: int,
    repeat: int,
    synchronize: Callable[[], None],
    fn: Callable[[], dict[str, Any]],
    stability_key: str,
) -> dict[str, Any]:
    measured: list[float] = []
    values: list[int] = []
    runs: list[dict[str, Any]] = []
    for index in range(warmup + repeat):
        synchronize()
        start = time.perf_counter()
        result = fn()
        synchronize()
        elapsed = time.perf_counter() - start
        value = int(result[stability_key])
        is_warmup = index < warmup
        print(
            f"[goal3675] {label} {'warmup' if is_warmup else 'repeat'} "
            f"{index + 1}/{warmup + repeat} elapsed={elapsed:.6f}s {stability_key}={value}",
            flush=True,
        )
        runs.append(
            {
                "iteration": index,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                stability_key: value,
                **{key: val for key, val in result.items() if key != stability_key},
            }
        )
        if not is_warmup:
            measured.append(elapsed)
            values.append(value)
    if len(set(values)) != 1:
        raise RuntimeError(f"{label} changed {stability_key} across repeats: {values}")
    return {
        "hot_median_sec": _median(measured),
        "hot_total_sec": float(sum(measured)),
        "hot_repeat_secs": measured,
        "hot_repeat": repeat,
        "hot_warmup": warmup,
        "stability_key": stability_key,
        "stability_value": values[-1] if values else None,
        "runs": runs,
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    dataset = rt.load_cdb(args.dataset)
    points = tuple(rt.chains_to_probe_points(dataset))
    shapes = tuple(rt.chains_to_polygons(dataset))

    print(
        f"[goal3675] loaded dataset points={len(points)} shapes={len(shapes)} "
        f"eps={os.environ.get('RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS')}",
        flush=True,
    )
    prepare_start = time.perf_counter()
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    prepare_static_scene_sec = time.perf_counter() - prepare_start
    refiner_start = time.perf_counter()
    refiner = rt.prepare_closed_shape_membership_candidate_refiner_exact_cupy(
        points,
        shapes,
        point_eps=float(args.point_eps),
    )
    prepare_cupy_refiner_sec = time.perf_counter() - refiner_start
    prepared_points_start = time.perf_counter()
    prepared_points = prepared.prepare_point_probe_columns(points)
    prepare_point_columns_sec = time.perf_counter() - prepared_points_start

    try:
        print("[goal3675] generating exact oracle once", flush=True)
        exact_start = time.perf_counter()
        exact_rows = tuple(prepared.run(points))
        exact_sec = time.perf_counter() - exact_start
        exact_pairs = _pair_counter(exact_rows)
        exact_count = len(exact_rows)

        def sync() -> None:
            cp.cuda.Stream.null.synchronize()

        def device_filtered_count_once() -> dict[str, Any]:
            count = prepared.count_device_filtered_prepared_points(prepared_points)
            return {"row_count": int(count)}

        device_filtered_timing = _time_repeated(
            label="prepared_points_device_filtered_count",
            warmup=int(args.warmup),
            repeat=int(args.repeat),
            synchronize=sync,
            fn=device_filtered_count_once,
            stability_key="row_count",
        )

        last_candidate_count = 0
        last_dropped_count = 0
        last_candidate_metadata: dict[str, Any] = {}

        def candidate_refine_once() -> dict[str, Any]:
            nonlocal last_candidate_count, last_dropped_count, last_candidate_metadata
            columns = prepared.candidate_device_columns(points, max_rows=int(args.max_rows))
            try:
                metadata = columns.to_metadata()
                refined = refiner.refine(columns, sort_output=False)
                row_count = int(refined["row_count"])
                candidate_count = int(refined["candidate_row_count"])
                dropped_count = int(refined["dropped_candidate_row_count"])
                last_candidate_count = candidate_count
                last_dropped_count = dropped_count
                last_candidate_metadata = metadata
                return {
                    "row_count": row_count,
                    "candidate_row_count": candidate_count,
                    "dropped_candidate_row_count": dropped_count,
                    "native_traversal_seconds": float(metadata.get("runtime", {}).get("traversal_seconds", 0.0)),
                }
            finally:
                columns.close()

        candidate_refine_timing = _time_repeated(
            label="candidate_columns_plus_prepared_cupy_refine",
            warmup=int(args.warmup),
            repeat=int(args.repeat),
            synchronize=sync,
            fn=candidate_refine_once,
            stability_key="row_count",
        )
        candidate_correctness_start = time.perf_counter()
        candidate_correctness_columns = prepared.candidate_device_columns(points, max_rows=int(args.max_rows))
        try:
            candidate_correctness_metadata = candidate_correctness_columns.to_metadata()
            candidate_correctness_refined = refiner.refine(candidate_correctness_columns, sort_output=False)
            last_refined_pairs = _device_pairs(cp, candidate_correctness_refined)
            last_candidate_count = int(candidate_correctness_refined["candidate_row_count"])
            last_dropped_count = int(candidate_correctness_refined["dropped_candidate_row_count"])
            last_candidate_metadata = candidate_correctness_metadata
        finally:
            candidate_correctness_columns.close()
        sync()
        candidate_correctness_materialization_sec = time.perf_counter() - candidate_correctness_start
        missing = exact_pairs - last_refined_pairs
        extra = last_refined_pairs - exact_pairs

        last_boundary_candidate_count = 0
        last_boundary_dropped_count = 0
        last_boundary_metadata: dict[str, Any] = {}

        def boundary_contact_refine_once() -> dict[str, Any]:
            nonlocal last_boundary_candidate_count, last_boundary_dropped_count, last_boundary_metadata
            columns = prepared.candidate_device_columns(points, max_rows=int(args.max_rows))
            try:
                metadata = columns.to_metadata()
                refined = refiner.refine_boundary_contacts(
                    columns,
                    sort_output=False,
                    validate_columns=False,
                )
                row_count = int(refined["row_count"])
                candidate_count = int(refined["candidate_row_count"])
                dropped_count = int(refined["dropped_candidate_row_count"])
                last_boundary_candidate_count = candidate_count
                last_boundary_dropped_count = dropped_count
                last_boundary_metadata = metadata
                return {
                    "row_count": row_count,
                    "candidate_row_count": candidate_count,
                    "dropped_candidate_row_count": dropped_count,
                    "native_traversal_seconds": float(metadata.get("runtime", {}).get("traversal_seconds", 0.0)),
                }
            finally:
                columns.close()

        boundary_contact_refine_timing = _time_repeated(
            label="candidate_columns_plus_boundary_contact_refine",
            warmup=int(args.warmup),
            repeat=int(args.repeat),
            synchronize=sync,
            fn=boundary_contact_refine_once,
            stability_key="row_count",
        )
        boundary_correctness_start = time.perf_counter()
        boundary_correctness_columns = prepared.candidate_device_columns(points, max_rows=int(args.max_rows))
        try:
            boundary_correctness_metadata = boundary_correctness_columns.to_metadata()
            boundary_correctness_refined = refiner.refine_boundary_contacts(boundary_correctness_columns, sort_output=False)
            last_boundary_refined_pairs = _device_pairs(cp, boundary_correctness_refined)
            last_boundary_candidate_count = int(boundary_correctness_refined["candidate_row_count"])
            last_boundary_dropped_count = int(boundary_correctness_refined["dropped_candidate_row_count"])
            last_boundary_metadata = boundary_correctness_metadata
        finally:
            boundary_correctness_columns.close()
        sync()
        boundary_correctness_materialization_sec = time.perf_counter() - boundary_correctness_start
        boundary_missing = exact_pairs - last_boundary_refined_pairs
        boundary_extra = last_boundary_refined_pairs - exact_pairs

        last_numba_count_candidate_count = 0
        last_numba_count_dropped_count = 0
        last_numba_count_metadata: dict[str, Any] = {}
        numba_count_timing: dict[str, Any] | None = None
        numba_count_error: str | None = None

        def boundary_contact_numba_count_once() -> dict[str, Any]:
            nonlocal last_numba_count_candidate_count, last_numba_count_dropped_count, last_numba_count_metadata
            columns = prepared.candidate_device_columns(points, max_rows=int(args.max_rows))
            try:
                metadata = columns.to_metadata()
                counted = refiner.count_boundary_contacts_numba(
                    columns,
                    validate_columns=False,
                )
                row_count = int(counted["row_count"])
                candidate_count = int(counted["candidate_row_count"])
                dropped_count = int(counted["dropped_candidate_row_count"])
                last_numba_count_candidate_count = candidate_count
                last_numba_count_dropped_count = dropped_count
                last_numba_count_metadata = metadata
                return {
                    "row_count": row_count,
                    "candidate_row_count": candidate_count,
                    "dropped_candidate_row_count": dropped_count,
                    "native_traversal_seconds": float(metadata.get("runtime", {}).get("traversal_seconds", 0.0)),
                }
            finally:
                columns.close()

        try:
            numba_count_timing = _time_repeated(
                label="candidate_columns_plus_boundary_contact_numba_count",
                warmup=int(args.warmup),
                repeat=int(args.repeat),
                synchronize=sync,
                fn=boundary_contact_numba_count_once,
                stability_key="row_count",
            )
        except Exception as exc:
            numba_count_error = repr(exc)
            print(f"[goal3675] numba boundary-contact count unavailable: {numba_count_error}", flush=True)

        resident_numba_count_timing: dict[str, Any] | None = None
        resident_numba_count_error: str | None = None
        resident_candidate_metadata: dict[str, Any] = {}
        resident_candidate_row_count = 0
        if numba_count_timing is not None:
            resident_columns = prepared.candidate_device_columns(points, max_rows=int(args.max_rows))
            try:
                resident_candidate_metadata = resident_columns.to_metadata()
                resident_candidate_row_count = int(getattr(resident_columns, "row_count", 0))

                def resident_boundary_contact_numba_count_once() -> dict[str, Any]:
                    counted = refiner.count_boundary_contacts_numba(
                        resident_columns,
                        validate_columns=False,
                    )
                    return {
                        "row_count": int(counted["row_count"]),
                        "candidate_row_count": int(counted["candidate_row_count"]),
                        "dropped_candidate_row_count": int(counted["dropped_candidate_row_count"]),
                        "native_traversal_seconds": 0.0,
                    }

                resident_numba_count_timing = _time_repeated(
                    label="resident_candidate_columns_plus_boundary_contact_numba_count",
                    warmup=int(args.warmup),
                    repeat=int(args.repeat),
                    synchronize=sync,
                    fn=resident_boundary_contact_numba_count_once,
                    stability_key="row_count",
                )
            except Exception as exc:
                resident_numba_count_error = repr(exc)
                print(
                    f"[goal3675] resident numba boundary-contact count unavailable: {resident_numba_count_error}",
                    flush=True,
                )
            finally:
                resident_columns.close()

        status_probe_start = time.perf_counter()
        status_columns = prepared.candidate_device_columns(points, max_rows=int(args.max_rows))
        try:
            cupy_columns = status_columns.as_cupy_columns()
            relation_status_counts: dict[str, int] = {}
            boundary_ordinal_summary: dict[str, Any] = {}
            if "relation_status" in cupy_columns:
                statuses, counts = cp.unique(cupy_columns["relation_status"], return_counts=True)
                relation_status_counts = {
                    str(int(status)): int(count)
                    for status, count in zip(cp.asnumpy(statuses).tolist(), cp.asnumpy(counts).tolist())
                }
            if "relation_boundary_ordinal" in cupy_columns:
                boundary_ordinals = cupy_columns["relation_boundary_ordinal"]
                sentinel = (1 << 32) - 1
                sentinel_count = int(cp.count_nonzero(boundary_ordinals == sentinel).get())
                unique_ordinals = cp.unique(boundary_ordinals[boundary_ordinals != sentinel])
                boundary_ordinal_summary = {
                    "sentinel_value": sentinel,
                    "sentinel_row_count": sentinel_count,
                    "unique_non_sentinel_count": int(unique_ordinals.size),
                    "non_sentinel_sample": [
                        int(value)
                        for value in cp.asnumpy(unique_ordinals[:20]).tolist()
                    ],
                }
        finally:
            status_columns.close()
        sync()
        relation_status_probe_sec = time.perf_counter() - status_probe_start

        return {
            "schema": SCHEMA,
            "goal": 3675,
            "commit": _command_output(["git", "rev-parse", "HEAD"]),
            "has_uncommitted_patch": _dirty(),
            "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
            "dataset": str(args.dataset.resolve()),
            "device_predicate_eps": os.environ.get("RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS"),
            "cupy_refiner_point_eps": float(args.point_eps),
            "point_count": len(points),
            "shape_count": len(shapes),
            "prepare_static_scene_sec": prepare_static_scene_sec,
            "prepare_cupy_refiner_sec": prepare_cupy_refiner_sec,
            "prepare_point_columns_sec": prepare_point_columns_sec,
            "exact_row_count": exact_count,
            "exact_once_sec": exact_sec,
            "device_filtered_prepared_points": {
                **device_filtered_timing,
                "matches_exact_count": int(device_filtered_timing["stability_value"]) == exact_count,
                "count_delta_vs_exact": int(device_filtered_timing["stability_value"]) - exact_count,
            },
            "candidate_columns_plus_prepared_cupy_refine": {
                **candidate_refine_timing,
                "candidate_row_count": last_candidate_count,
                "dropped_candidate_row_count": last_dropped_count,
                "matches_exact_multiset": last_refined_pairs == exact_pairs,
                "missing_exact_row_count": int(sum(missing.values())),
                "extra_row_count": int(sum(extra.values())),
                "missing_sample": [[int(p), int(s), int(c)] for (p, s), c in list(missing.items())[:20]],
                "extra_sample": [[int(p), int(s), int(c)] for (p, s), c in list(extra.items())[:20]],
                "candidate_metadata": last_candidate_metadata,
                "correctness_materialization_sec": candidate_correctness_materialization_sec,
            },
            "candidate_columns_plus_boundary_contact_refine": {
                **boundary_contact_refine_timing,
                "candidate_row_count": last_boundary_candidate_count,
                "dropped_candidate_row_count": last_boundary_dropped_count,
                "matches_exact_multiset": last_boundary_refined_pairs == exact_pairs,
                "missing_exact_row_count": int(sum(boundary_missing.values())),
                "extra_row_count": int(sum(boundary_extra.values())),
                "missing_sample": [
                    [int(p), int(s), int(c)]
                    for (p, s), c in list(boundary_missing.items())[:20]
                ],
                "extra_sample": [
                    [int(p), int(s), int(c)]
                    for (p, s), c in list(boundary_extra.items())[:20]
                ],
                "candidate_metadata": last_boundary_metadata,
                "correctness_materialization_sec": boundary_correctness_materialization_sec,
            },
            "candidate_columns_plus_boundary_contact_numba_count": (
                {
                    **numba_count_timing,
                    "candidate_row_count": last_numba_count_candidate_count,
                    "dropped_candidate_row_count": last_numba_count_dropped_count,
                    "matches_exact_count": int(numba_count_timing["stability_value"]) == exact_count,
                    "count_delta_vs_exact": int(numba_count_timing["stability_value"]) - exact_count,
                    "candidate_metadata": last_numba_count_metadata,
                    "partner": "numba",
                    "row_stream_materialized": False,
                    "trusted_native_stream_fast_path": True,
                }
                if numba_count_timing is not None
                else {
                    "available": False,
                    "error": numba_count_error,
                    "partner": "numba",
                }
            ),
            "resident_candidate_columns_plus_boundary_contact_numba_count": (
                {
                    **resident_numba_count_timing,
                    "resident_candidate_row_count": resident_candidate_row_count,
                    "matches_exact_count": int(resident_numba_count_timing["stability_value"]) == exact_count,
                    "count_delta_vs_exact": int(resident_numba_count_timing["stability_value"]) - exact_count,
                    "candidate_metadata": resident_candidate_metadata,
                    "partner": "numba",
                    "row_stream_materialized": False,
                    "resident_candidate_stream_reused": True,
                    "trusted_native_stream_fast_path": True,
                }
                if resident_numba_count_timing is not None
                else {
                    "available": False,
                    "error": resident_numba_count_error,
                    "partner": "numba",
                    "resident_candidate_stream_reused": True,
                }
            ),
            "relation_status_probe": {
                "relation_status_counts": relation_status_counts,
                "probe_sec": relation_status_probe_sec,
                "boundary_status_candidate_row_count": int(relation_status_counts.get("2", 0)),
                "boundary_status_selectivity_ratio": (
                    int(relation_status_counts.get("2", 0)) / last_candidate_count
                    if last_candidate_count
                    else None
                ),
                "boundary_ordinal_summary": boundary_ordinal_summary,
                "boundary_status_is_sparse_for_this_dataset": int(relation_status_counts.get("2", 0))
                <= max(100, int(0.10 * last_candidate_count)),
            },
            "comparison": {
                "candidate_refine_vs_exact_once_sec_ratio": (
                    float(candidate_refine_timing["hot_median_sec"]) / exact_sec if exact_sec > 0 else None
                ),
                "candidate_refine_speedup_vs_exact_once": (
                    exact_sec / float(candidate_refine_timing["hot_median_sec"])
                    if float(candidate_refine_timing["hot_median_sec"]) > 0
                    else None
                ),
                "candidate_refine_vs_device_filtered_sec_ratio": (
                    float(candidate_refine_timing["hot_median_sec"])
                    / float(device_filtered_timing["hot_median_sec"])
                    if float(device_filtered_timing["hot_median_sec"]) > 0
                    else None
                ),
                "boundary_contact_refine_vs_exact_once_sec_ratio": (
                    float(boundary_contact_refine_timing["hot_median_sec"]) / exact_sec if exact_sec > 0 else None
                ),
                "boundary_contact_refine_speedup_vs_exact_once": (
                    exact_sec / float(boundary_contact_refine_timing["hot_median_sec"])
                    if float(boundary_contact_refine_timing["hot_median_sec"]) > 0
                    else None
                ),
                "boundary_contact_refine_vs_full_cupy_refine_sec_ratio": (
                    float(boundary_contact_refine_timing["hot_median_sec"])
                    / float(candidate_refine_timing["hot_median_sec"])
                    if float(candidate_refine_timing["hot_median_sec"]) > 0
                    else None
                ),
                "boundary_contact_refine_vs_device_filtered_sec_ratio": (
                    float(boundary_contact_refine_timing["hot_median_sec"])
                    / float(device_filtered_timing["hot_median_sec"])
                    if float(device_filtered_timing["hot_median_sec"]) > 0
                    else None
                ),
                "boundary_contact_numba_count_vs_exact_once_sec_ratio": (
                    float(numba_count_timing["hot_median_sec"]) / exact_sec
                    if numba_count_timing is not None and exact_sec > 0
                    else None
                ),
                "boundary_contact_numba_count_speedup_vs_exact_once": (
                    exact_sec / float(numba_count_timing["hot_median_sec"])
                    if numba_count_timing is not None and float(numba_count_timing["hot_median_sec"]) > 0
                    else None
                ),
                "boundary_contact_numba_count_vs_device_filtered_sec_ratio": (
                    float(numba_count_timing["hot_median_sec"])
                    / float(device_filtered_timing["hot_median_sec"])
                    if numba_count_timing is not None and float(device_filtered_timing["hot_median_sec"]) > 0
                    else None
                ),
                "boundary_contact_numba_count_vs_full_cupy_refine_sec_ratio": (
                    float(numba_count_timing["hot_median_sec"])
                    / float(candidate_refine_timing["hot_median_sec"])
                    if numba_count_timing is not None and float(candidate_refine_timing["hot_median_sec"]) > 0
                    else None
                ),
                "resident_boundary_contact_numba_count_vs_device_filtered_sec_ratio": (
                    float(resident_numba_count_timing["hot_median_sec"])
                    / float(device_filtered_timing["hot_median_sec"])
                    if resident_numba_count_timing is not None
                    and float(device_filtered_timing["hot_median_sec"]) > 0
                    else None
                ),
                "resident_boundary_contact_numba_count_vs_full_cupy_refine_sec_ratio": (
                    float(resident_numba_count_timing["hot_median_sec"])
                    / float(candidate_refine_timing["hot_median_sec"])
                    if resident_numba_count_timing is not None
                    and float(candidate_refine_timing["hot_median_sec"]) > 0
                    else None
                ),
            },
            "native_engine_boundary": (
                "RTDL/OptiX emits generic point/closed-shape candidate columns with instance ordinals; "
                "CuPy refines the candidate stream with a generic simple-ring predicate; RayJoin/CDB "
                "policy stays outside the native engine."
            ),
            "interpretation": (
                "Timing and correctness scout for the full-county exact candidate-refinement route. "
                "This packet evaluates whether an existing generic OptiX candidate stream plus prepared "
                "CuPy refiner is a viable exact route before adding new native primitives."
            ),
            "claim_boundary": _claim_boundary(),
        }
    finally:
        prepared_points.close()
        prepared.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3675 full-county RayJoin PIP candidate-refine timing.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start0_count16545.cdb",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repeat", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--max-rows", type=int, default=1_000_000)
    parser.add_argument("--point-eps", type=float, default=1.0e-9)
    args = parser.parse_args()
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.max_rows <= 0:
        raise ValueError("--max-rows must be positive")
    return args


def main() -> int:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3675] wrote {args.output}", flush=True)
    print(json.dumps(payload["comparison"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
