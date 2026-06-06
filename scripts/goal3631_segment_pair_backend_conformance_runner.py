#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.reference import Segment  # noqa: E402
from rtdsl.segment_pair_contracts import (  # noqa: E402
    SEGMENT_PAIR_CONTRACT_VERSION,
    SEGMENT_PAIR_STRICT_DENOMINATOR_EPSILON,
    SEGMENT_PAIR_TYPED_OUTPUT_RESIDENCY_VERSION,
    Segment2DContractInput,
    segment_pair_contract_adversarial_cases,
    segment_pair_left_id_dense_count_output_residency_contract,
    segment_pair_left_id_dense_counts_reference,
    validate_segment_pair_output_residency_contract,
)


SCHEMA = "rtdl.goal3631.segment_pair_backend_conformance_a5000.v1"
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3631_segment_pair_backend_conformance_a5000"
    / "summary.json"
)


SEGMENT_PAIR_FLAGS_KERNEL = r"""
static __device__ bool rtdl_goal3631_segment_pair_hit(
    double ax0, double ay0, double ax1, double ay1,
    double bx0, double by0, double bx1, double by1)
{
    const double rx = ax1 - ax0;
    const double ry = ay1 - ay0;
    const double sx = bx1 - bx0;
    const double sy = by1 - by0;
    const double denom = rx * sy - ry * sx;
    if (fabs(denom) < 1.0e-7) return false;
    const double qpx = bx0 - ax0;
    const double qpy = by0 - ay0;
    const double t = (qpx * sy - qpy * sx) / denom;
    const double u = (qpx * ry - qpy * rx) / denom;
    return t >= 0.0 && t <= 1.0 && u >= 0.0 && u <= 1.0;
}

extern "C" __global__
void rtdl_goal3631_segment_pair_flags(
    const double* left,
    const double* right,
    const long long left_count,
    const long long right_count,
    unsigned char* flags)
{
    const long long idx = (long long)blockDim.x * (long long)blockIdx.x + (long long)threadIdx.x;
    const long long total = left_count * right_count;
    if (idx >= total) return;
    const long long li = idx / right_count;
    const long long ri = idx - li * right_count;
    const double ax0 = left[li * 4 + 0];
    const double ay0 = left[li * 4 + 1];
    const double ax1 = left[li * 4 + 2];
    const double ay1 = left[li * 4 + 3];
    const double bx0 = right[ri * 4 + 0];
    const double by0 = right[ri * 4 + 1];
    const double bx1 = right[ri * 4 + 2];
    const double by1 = right[ri * 4 + 3];
    if (rtdl_goal3631_segment_pair_hit(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1)) {
        flags[idx] = 1;
    }
}
"""


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "native_default_route_authorized": False,
    }


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _print(message: str) -> None:
    print(f"[goal3631] {message}", flush=True)


def _as_contract(segment: Segment) -> Segment2DContractInput:
    return Segment2DContractInput(segment.x0, segment.y0, segment.x1, segment.y1)


def _as_rt_segments(inputs: Iterable[Segment2DContractInput]) -> tuple[Segment, ...]:
    return tuple(
        Segment(
            id=index,
            x0=item.x0,
            y0=item.y0,
            x1=item.x1,
            y1=item.y1,
        )
        for index, item in enumerate(inputs)
    )


def _segments_to_numpy(segments: tuple[Segment, ...]):
    import numpy as np

    return np.asarray(
        [[segment.x0, segment.y0, segment.x1, segment.y1] for segment in segments],
        dtype=np.float64,
    )


def _count_rows_by_left_id(rows: tuple[dict[str, object], ...], group_capacity: int) -> list[int]:
    counts = [0 for _ in range(group_capacity)]
    for row in rows:
        left_id = int(row["left_id"])
        if 0 <= left_id < group_capacity:
            counts[left_id] += 1
    return counts


def _python_reference_case(left: tuple[Segment, ...], right: tuple[Segment, ...]) -> dict[str, object]:
    start = time.perf_counter()
    reference = segment_pair_left_id_dense_counts_reference(
        tuple(_as_contract(segment) for segment in left),
        tuple(_as_contract(segment) for segment in right),
        group_capacity=len(left),
    )
    elapsed = time.perf_counter() - start
    return {
        "counts": list(reference.counts),
        "hit_pair_count": reference.hit_pair_count,
        "ambiguous_pair_count": reference.ambiguous_pair_count,
        "rejected_pair_count": reference.rejected_pair_count,
        "decision_reasons": list(reference.decision_reasons),
        "seconds": elapsed,
    }


def _cupy_dense_counts_case(left: tuple[Segment, ...], right: tuple[Segment, ...]) -> dict[str, object]:
    import cupy as cp

    left_np = _segments_to_numpy(left)
    right_np = _segments_to_numpy(right)
    left_count = int(left_np.shape[0])
    right_count = int(right_np.shape[0])
    pair_count = left_count * right_count

    start = time.perf_counter()
    left_gpu = cp.asarray(left_np)
    right_gpu = cp.asarray(right_np)
    flags = cp.zeros((pair_count,), dtype=cp.uint8)
    cp.cuda.Stream.null.synchronize()
    upload_alloc_seconds = time.perf_counter() - start

    kernel = cp.RawKernel(SEGMENT_PAIR_FLAGS_KERNEL, "rtdl_goal3631_segment_pair_flags")
    threads = 256
    blocks = (pair_count + threads - 1) // threads
    kernel_start = time.perf_counter()
    kernel(
        (blocks,),
        (threads,),
        (
            left_gpu,
            right_gpu,
            left_count,
            right_count,
            flags,
        ),
    )
    cp.cuda.Stream.null.synchronize()
    kernel_seconds = time.perf_counter() - kernel_start

    reduce_start = time.perf_counter()
    counts = cp.asnumpy(flags.reshape((left_count, right_count)).sum(axis=1)).astype("int64")
    reduce_seconds = time.perf_counter() - reduce_start
    total = int(counts.sum())

    del flags
    cp.get_default_memory_pool().free_all_blocks()
    return {
        "available": True,
        "counts": [int(value) for value in counts.tolist()],
        "hit_pair_count": total,
        "seconds": {
            "upload_alloc": upload_alloc_seconds,
            "dense_kernel": kernel_seconds,
            "count_reduce_validation_download": reduce_seconds,
        },
        "validation_download_only": True,
        "kernel_contract": "strict_v0_absolute_denominator_endpoint_inclusive",
    }


def _optix_case(
    left: tuple[Segment, ...],
    right: tuple[Segment, ...],
    *,
    include_rows: bool,
    include_ambiguity_status: bool,
    expected_ambiguous_count: int,
    prepack_left_for_dense_route: bool,
    prepare_left_set_for_dense_route: bool,
) -> dict[str, object]:
    import cupy as cp
    from rtdsl.optix_runtime import (
        pack_segments,
        prepare_segment_pair_intersection_optix,
        prepare_segment_pair_left_set_optix,
    )

    if prepare_left_set_for_dense_route and include_ambiguity_status:
        raise ValueError("prepared-left route does not yet expose optional ambiguity status")

    group_capacity = len(left)
    prepare_start = time.perf_counter()
    prepared = prepare_segment_pair_intersection_optix(right)
    prepare_seconds = time.perf_counter() - prepare_start
    try:
        left_for_dense = left
        left_prepack_seconds = None
        prepared_left = None
        prepared_left_seconds = None
        if prepack_left_for_dense_route:
            left_prepack_start = time.perf_counter()
            left_for_dense = pack_segments(records=left)
            left_prepack_seconds = time.perf_counter() - left_prepack_start
        if prepare_left_set_for_dense_route:
            prepared_left_start = time.perf_counter()
            prepared_left = prepare_segment_pair_left_set_optix(left)
            prepared_left_seconds = time.perf_counter() - prepared_left_start

        row_counts = None
        row_total = None
        row_seconds = None
        scalar_count = None
        scalar_count_seconds = None
        if include_rows:
            row_start = time.perf_counter()
            rows = prepared.run(left)
            row_seconds = time.perf_counter() - row_start
            row_counts = _count_rows_by_left_id(rows, group_capacity)
            row_total = sum(row_counts)

            scalar_start = time.perf_counter()
            scalar_count = prepared.count(left)
            scalar_count_seconds = time.perf_counter() - scalar_start

        dense_start = time.perf_counter()
        if prepared_left is not None:
            dense = prepared.left_id_count_prepared_left_device_columns(
                prepared_left,
                group_capacity=group_capacity,
            )
        else:
            dense = prepared.left_id_count_device_columns(
                left_for_dense,
                group_capacity=group_capacity,
                include_ambiguity_status=include_ambiguity_status,
            )
        try:
            counts_gpu = dense.as_cupy_counts()
            source_row_count_gpu = dense.as_cupy_source_row_count()
            overflow_gpu = dense.as_cupy_overflow_status()
            ambiguous_gpu = (
                dense.as_cupy_ambiguous_count()
                if int(dense.ambiguous_count_device_ptr) > 0
                else None
            )
            cp.cuda.Stream.null.synchronize()
            counts = cp.asnumpy(counts_gpu).astype("int64")
            source_row_count_status = int(cp.asnumpy(source_row_count_gpu).astype("uint64")[0])
            overflow_status = int(cp.asnumpy(overflow_gpu).astype("uint32")[0])
            ambiguous_status = (
                int(cp.asnumpy(ambiguous_gpu).astype("uint64")[0])
                if ambiguous_gpu is not None
                else None
            )
            dense_total = int(counts.sum())
            dense_seconds = time.perf_counter() - dense_start
            counts_device_ptr = int(dense.counts_device_ptr)
            overflow_device_ptr = int(dense.overflow_device_ptr)
            ambiguous_count_device_ptr = int(dense.ambiguous_count_device_ptr)
            dense_metadata = dense.to_metadata()
        finally:
            dense.close()

        residency_contract = segment_pair_left_id_dense_count_output_residency_contract(
            group_capacity=group_capacity,
            counts_device_ptr=counts_device_ptr,
            overflow_device_ptr=overflow_device_ptr,
            ambiguous_count_device_ptr=ambiguous_count_device_ptr,
            stream_ordering="host_synchronized_before_consumer",
            device_id=int(dense_metadata["device_ordinal"]),
        )
        residency_validation = validate_segment_pair_output_residency_contract(residency_contract)
        return {
            "available": True,
            "prepare_seconds": prepare_seconds,
            "left_prepacked_for_dense_route": prepack_left_for_dense_route,
            "left_prepack_seconds": left_prepack_seconds,
            "prepared_left_set_for_dense_route": prepare_left_set_for_dense_route,
            "prepared_left_set_seconds": prepared_left_seconds,
            "row_route": {
                "executed": include_rows,
                "counts": row_counts,
                "hit_pair_count": row_total,
                "seconds": row_seconds,
                "scalar_count": scalar_count,
                "scalar_count_seconds": scalar_count_seconds,
            },
            "dense_device_count_route": {
                "counts": [int(value) for value in counts.tolist()],
                "hit_pair_count": dense_total,
                "source_row_count_from_device_status": source_row_count_status,
                "overflow_from_device_status": overflow_status,
                "ambiguous_count_from_device_status": ambiguous_status,
                "include_ambiguity_status": include_ambiguity_status,
                "status_device_columns_valid": (
                    source_row_count_status == dense_total
                    and overflow_status == int(bool(dense_metadata["overflow"]))
                ),
                "ambiguity_device_status_valid": (
                    ambiguous_status == int(expected_ambiguous_count)
                    if include_ambiguity_status
                    else None
                ),
                "seconds": dense_seconds,
                "metadata": dense_metadata,
                "residency_contract_valid": bool(residency_validation["valid"]),
                "residency_contract": residency_contract,
                "validation_download_only": True,
            },
            "last_phase_timings": prepared.last_phase_timings(),
        }
    finally:
        if "prepared_left" in locals() and prepared_left is not None:
            prepared_left.close()
        prepared.close()


def _make_adversarial_case() -> tuple[tuple[Segment, ...], tuple[Segment, ...], str]:
    cases = segment_pair_contract_adversarial_cases()
    return (
        _as_rt_segments(tuple(case.left for case in cases)),
        _as_rt_segments(tuple(case.right for case in cases)),
        "adversarial strict-v0 segment-pair fixture cross-product",
    )


def _make_crossing_grid_case(size: int) -> tuple[tuple[Segment, ...], tuple[Segment, ...], str]:
    if size <= 0:
        raise ValueError("size must be positive")
    step = 1.0 / float(size + 1)
    left = tuple(
        Segment(
            id=index,
            x0=(index + 1) * step,
            y0=-0.25,
            x1=(index + 1) * step,
            y1=1.25,
        )
        for index in range(size)
    )
    right = tuple(
        Segment(
            id=index,
            x0=-0.25,
            y0=(index + 1) * step,
            x1=1.25,
            y1=(index + 1) * step,
        )
        for index in range(size)
    )
    return left, right, f"synthetic crossing grid with {size} x {size} proper intersections"


def _make_sparse_diagonal_grid_case(size: int) -> tuple[tuple[Segment, ...], tuple[Segment, ...], str]:
    if size <= 0:
        raise ValueError("size must be positive")
    left = tuple(
        Segment(
            id=index,
            x0=float(index),
            y0=-1.0,
            x1=float(index),
            y1=1.0,
        )
        for index in range(size)
    )
    right = tuple(
        Segment(
            id=index,
            x0=float(index) - 0.25,
            y0=0.0,
            x1=float(index) + 0.25,
            y1=0.0,
        )
        for index in range(size)
    )
    return left, right, f"synthetic sparse diagonal grid with {size} isolated proper intersections"


def _expected_grid_counts(size: int) -> dict[str, object]:
    return {
        "counts": [size for _ in range(size)],
        "hit_pair_count": size * size,
        "ambiguous_pair_count": 0,
        "rejected_pair_count": 0,
        "decision_reasons": ["non_collinear_endpoint_inclusive_hit"],
        "source": "analytic_crossing_grid",
    }


def _expected_sparse_diagonal_counts(size: int) -> dict[str, object]:
    return {
        "counts": [1 for _ in range(size)],
        "hit_pair_count": size,
        "ambiguous_pair_count": 0,
        "rejected_pair_count": size * size - size,
        "decision_reasons": ["non_collinear_endpoint_inclusive_hit", "outside_parametric_bounds"],
        "source": "analytic_sparse_diagonal_grid",
    }


def _compare_counts(expected: list[int], actual: list[int]) -> dict[str, object]:
    diffs = [
        {"index": index, "expected": int(exp), "actual": int(act), "delta": int(act) - int(exp)}
        for index, (exp, act) in enumerate(zip(expected, actual))
        if int(exp) != int(act)
    ]
    length_match = len(expected) == len(actual)
    return {
        "match": length_match and not diffs,
        "length_match": length_match,
        "diff_count": len(diffs),
        "diff_sample": diffs[:12],
        "expected_total": int(sum(expected)),
        "actual_total": int(sum(actual)),
    }


def _trim_counts_payload(payload: dict[str, object], max_counts_output: int | None) -> dict[str, object]:
    counts = payload.get("counts")
    if not isinstance(counts, list):
        return payload
    limit = None if max_counts_output is None else int(max_counts_output)
    if limit is None or limit < 0 or len(counts) <= limit:
        output = dict(payload)
        output.setdefault("counts_truncated", False)
        output.setdefault("counts_full_length", len(counts))
        return output
    output = dict(payload)
    output["counts"] = counts[:limit]
    output["counts_truncated"] = True
    output["counts_full_length"] = len(counts)
    output["counts_truncation_note"] = "counts truncated after comparisons; totals and diff checks used full vectors"
    return output


def _run_one_case(
    name: str,
    left: tuple[Segment, ...],
    right: tuple[Segment, ...],
    note: str,
    *,
    include_ambiguity_status: bool,
    max_counts_output: int | None,
    prepack_left_for_dense_route: bool,
    prepare_left_set_for_dense_route: bool,
) -> dict[str, object]:
    _print(f"case={name} left={len(left)} right={len(right)} pairs={len(left) * len(right)}")
    if name == "adversarial":
        _print("run Python strict-v0 oracle")
        expected = _python_reference_case(left, right)
    elif name.startswith("sparse_diagonal_grid_"):
        expected = _expected_sparse_diagonal_counts(len(left))
    else:
        size = len(left)
        expected = _expected_grid_counts(size)

    _print("run CuPy strict-v0 dense baseline")
    cupy_result = _cupy_dense_counts_case(left, right)

    include_rows = len(left) * len(right) <= 4096
    _print("run OptiX prepared dense count route")
    optix_result = _optix_case(
        left,
        right,
        include_rows=include_rows,
        include_ambiguity_status=include_ambiguity_status,
        expected_ambiguous_count=int(expected["ambiguous_pair_count"]),
        prepack_left_for_dense_route=prepack_left_for_dense_route,
        prepare_left_set_for_dense_route=prepare_left_set_for_dense_route,
    )

    expected_counts = [int(value) for value in expected["counts"]]
    cupy_counts = [int(value) for value in cupy_result["counts"]]
    optix_dense_counts = [
        int(value)
        for value in optix_result["dense_device_count_route"]["counts"]
    ]
    row_counts = optix_result["row_route"]["counts"]
    comparisons = {
        "cupy_vs_reference": _compare_counts(expected_counts, cupy_counts),
        "optix_dense_vs_reference": _compare_counts(expected_counts, optix_dense_counts),
        "optix_dense_vs_cupy": _compare_counts(cupy_counts, optix_dense_counts),
    }
    if row_counts is not None:
        comparisons["optix_row_vs_reference"] = _compare_counts(expected_counts, [int(value) for value in row_counts])

    all_match = all(bool(item["match"]) for item in comparisons.values())
    dense_route = dict(optix_result["dense_device_count_route"])
    dense_route = _trim_counts_payload(dense_route, max_counts_output)
    optix_output = dict(optix_result)
    optix_output["dense_device_count_route"] = dense_route
    if row_counts is not None:
        row_route = dict(optix_output["row_route"])
        row_route = _trim_counts_payload(row_route, max_counts_output)
        optix_output["row_route"] = row_route
    return {
        "name": name,
        "note": note,
        "contract_version": SEGMENT_PAIR_CONTRACT_VERSION,
        "left_count": len(left),
        "right_count": len(right),
        "candidate_pair_count": len(left) * len(right),
        "reference": _trim_counts_payload(expected, max_counts_output),
        "cupy_dense_same_contract": _trim_counts_payload(cupy_result, max_counts_output),
        "optix": optix_output,
        "comparisons": comparisons,
        "all_same_contract_counts_match": all_match,
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    selected_cases: list[tuple[str, tuple[Segment, ...], tuple[Segment, ...], str]] = []
    left, right, note = _make_adversarial_case()
    selected_cases.append(("adversarial", left, right, note))
    for size in args.grid_sizes:
        left, right, note = _make_crossing_grid_case(size)
        selected_cases.append((f"crossing_grid_{size}", left, right, note))
    for size in args.sparse_grid_sizes:
        left, right, note = _make_sparse_diagonal_grid_case(size)
        selected_cases.append((f"sparse_diagonal_grid_{size}", left, right, note))

    case_results = [
        _run_one_case(
            name,
            left,
            right,
            note,
            include_ambiguity_status=bool(args.include_ambiguity_status),
            max_counts_output=args.max_counts_output,
            prepack_left_for_dense_route=bool(args.prepack_left_for_optix),
            prepare_left_set_for_dense_route=bool(args.prepare_left_set_for_optix),
        )
        for name, left, right, note in selected_cases
    ]
    all_match = all(bool(case["all_same_contract_counts_match"]) for case in case_results)
    return {
        "schema": SCHEMA,
        "goal": 3631,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "git_tracked_status_short": _command_output(["git", "status", "--short", "--untracked-files=no"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,compute_cap,driver_version", "--format=csv,noheader"]),
        "contract_version": SEGMENT_PAIR_CONTRACT_VERSION,
        "typed_output_residency_version": SEGMENT_PAIR_TYPED_OUTPUT_RESIDENCY_VERSION,
        "denominator_epsilon": SEGMENT_PAIR_STRICT_DENOMINATOR_EPSILON,
        "include_ambiguity_status": bool(args.include_ambiguity_status),
        "prepack_left_for_optix": bool(args.prepack_left_for_optix),
        "prepare_left_set_for_optix": bool(args.prepare_left_set_for_optix),
        "max_counts_output": args.max_counts_output,
        "case_count": len(case_results),
        "cases": case_results,
        "all_same_contract_counts_match": all_match,
        "pod_validation_succeeded": all_match,
        "claim_boundary": _claim_boundary(),
        "interpretation": (
            "A5000 backend conformance evidence for the candidate generic segment-pair "
            "left-id dense count contract. Validation downloads device columns only to "
            "compare counts; this does not authorize release, public speedup, broad "
            "RT-core, true-zero-copy, or RayJoin paper-reproduction claims."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3631 segment-pair backend conformance runner.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--grid-sizes", type=int, nargs="*", default=(64, 256, 1024))
    parser.add_argument("--sparse-grid-sizes", type=int, nargs="*", default=())
    parser.add_argument(
        "--max-counts-output",
        type=int,
        default=4096,
        help="Maximum count-vector entries to store in JSON after full-vector comparisons; use -1 to keep all.",
    )
    parser.add_argument(
        "--include-ambiguity-status",
        action="store_true",
        help="Use the optional strict-audit route that also returns ambiguous_count as a device status pointer.",
    )
    parser.add_argument(
        "--prepack-left-for-optix",
        action="store_true",
        help="Pack left segments once before timing the OptiX dense count route.",
    )
    parser.add_argument(
        "--prepare-left-set-for-optix",
        action="store_true",
        help="Prepare/upload left segments once before timing the OptiX dense count route.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    _print(f"wrote {args.output}")
    _print(json.dumps({
        "case_count": payload["case_count"],
        "all_same_contract_counts_match": payload["all_same_contract_counts_match"],
        "pod_validation_succeeded": payload["pod_validation_succeeded"],
    }, indent=2))
    return 0 if payload["all_same_contract_counts_match"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
