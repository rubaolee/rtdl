#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _git_value(*args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _hardware() -> dict[str, object]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,compute_cap",
        "--format=csv,noheader",
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return {"nvidia_smi_available": False}
    line = (completed.stdout or "").strip().splitlines()
    if not line:
        return {"nvidia_smi_available": False, "stderr": completed.stderr}
    parts = [part.strip() for part in line[0].split(",")]
    return {
        "nvidia_smi_available": True,
        "gpu": parts[0] if len(parts) > 0 else "unknown",
        "driver": parts[1] if len(parts) > 1 else "unknown",
        "memory": parts[2] if len(parts) > 2 else "unknown",
        "compute_capability": parts[3] if len(parts) > 3 else "unknown",
    }


def _stream_ptr(stream) -> int:
    handle = getattr(stream, "handle", None)
    value = getattr(handle, "value", handle)
    return int(value or 0)


def _device_ptr(column: object) -> int:
    cuda_array = getattr(column, "__cuda_array_interface__", None)
    if not isinstance(cuda_array, dict):
        raise TypeError("Numba probe expected a CUDA Array Interface column")
    return int(cuda_array["data"][0])


def _case(
    name: str,
    *,
    search_xy: list[tuple[float, float]],
    query_xy: list[tuple[float, float]],
    radius: float,
    threshold: int,
) -> dict[str, object]:
    return {
        "name": name,
        "search_xy": search_xy,
        "query_xy": query_xy,
        "radius": float(radius),
        "threshold": int(threshold),
    }


def _cases() -> list[dict[str, object]]:
    rng = np.random.default_rng(11)
    search = rng.uniform(-2.0, 2.0, size=(9, 2))
    query = rng.uniform(-2.0, 2.0, size=(6, 2))
    return [
        _case(
            "smoke",
            search_xy=[(0.0, 0.0), (4.0, 0.0), (9.0, 9.0)],
            query_xy=[(0.0, 0.0), (4.0, 0.0), (1.5, 1.5)],
            radius=1.1,
            threshold=1,
        ),
        _case(
            "threshold_two",
            search_xy=[(0.0, 0.0), (0.2, 0.0), (2.0, 0.0), (3.0, 3.0)],
            query_xy=[(0.0, 0.0), (3.0, 3.0)],
            radius=0.5,
            threshold=2,
        ),
        _case(
            "boundary_inclusive",
            search_xy=[(1.0, 0.0), (0.0, 2.0)],
            query_xy=[(0.0, 0.0), (0.0, 1.0)],
            radius=1.0,
            threshold=1,
        ),
        _case(
            "random_seed_11",
            search_xy=[tuple(map(float, row)) for row in search],
            query_xy=[tuple(map(float, row)) for row in query],
            radius=0.75,
            threshold=2,
        ),
    ]


def _ids(count: int, *, offset: int) -> list[int]:
    return [offset + i for i in range(count)]


def _cpu_reference(case: dict[str, object]) -> dict[str, list[int]]:
    search_xy = np.asarray(case["search_xy"], dtype=np.float64)
    query_xy = np.asarray(case["query_xy"], dtype=np.float64)
    radius = float(case["radius"])
    threshold = int(case["threshold"])
    query_ids = _ids(len(query_xy), offset=1)
    radius_sq = radius * radius
    counts: list[int] = []
    flags: list[int] = []
    for query in query_xy:
        delta = search_xy - query
        actual = int(np.count_nonzero(np.sum(delta * delta, axis=1) <= radius_sq + 1e-12))
        counts.append(min(actual, threshold) if threshold > 0 else actual)
        flags.append(1 if threshold > 0 and actual >= threshold else 0)
    return {
        "query_ids": query_ids,
        "neighbor_counts": counts,
        "threshold_flags": flags,
    }


def _to_device_columns(cuda, stream, ids: list[int], xy: list[tuple[float, float]]) -> dict[str, object]:
    arr = np.asarray(xy, dtype=np.float64).reshape((len(xy), 2))
    return {
        "ids": cuda.to_device(np.asarray(ids, dtype=np.uint32), stream=stream),
        "x": cuda.to_device(np.ascontiguousarray(arr[:, 0]), stream=stream),
        "y": cuda.to_device(np.ascontiguousarray(arr[:, 1]), stream=stream),
    }


def _outputs(cuda, stream, count: int) -> dict[str, object]:
    return {
        "query_ids": cuda.device_array((count,), dtype=np.uint32, stream=stream),
        "neighbor_counts": cuda.device_array((count,), dtype=np.uint32, stream=stream),
        "threshold_flags": cuda.device_array((count,), dtype=np.uint32, stream=stream),
    }


def _host_outputs(outputs: dict[str, object], stream) -> dict[str, list[int]]:
    return {
        name: [int(value) for value in column.copy_to_host(stream=stream).tolist()]
        for name, column in outputs.items()
    }


def _checksum_kernel(cuda):
    @cuda.jit
    def checksum_kernel(query_ids, neighbor_counts, threshold_flags, checksum):
        total = 0
        for i in range(query_ids.size):
            total += query_ids[i] * 100 + neighbor_counts[i] * 10 + threshold_flags[i]
        checksum[0] = total

    return checksum_kernel


def _expected_checksum(expected: dict[str, list[int]]) -> int:
    return int(
        sum(
            query_id * 100 + count * 10 + flag
            for query_id, count, flag in zip(
                expected["query_ids"],
                expected["neighbor_counts"],
                expected["threshold_flags"],
            )
        )
    )


def _plan_pointer_matches(metadata: dict[str, object], columns: dict[str, dict[str, object]]) -> dict[str, bool]:
    borrowed = metadata["v4_plan"]["borrowed_device_pointers"]
    matches: dict[str, bool] = {}
    for prefix, group in columns.items():
        for name, column in group.items():
            key = f"{prefix}.{name}"
            matches[key] = int(borrowed[key]) == _device_ptr(column)
    return matches


def _native_pointer_matches(metadata: dict[str, object], columns: dict[str, dict[str, object]]) -> dict[str, bool]:
    echo = metadata["native_call_device_pointer_echo"]
    matches: dict[str, bool] = {}
    for prefix, group in columns.items():
        for name, column in group.items():
            key = f"{prefix}.{name}"
            matches[key] = int(echo[key]) == _device_ptr(column)
    return matches


def run_probe() -> dict[str, object]:
    from numba import cuda
    import rtdsl

    if not cuda.is_available():
        raise RuntimeError("Numba CUDA is not available")

    stream = cuda.stream()
    stream_handle = _stream_ptr(stream)
    checksum_kernel = _checksum_kernel(cuda)
    case_results = []
    pointer_match_sets = []

    for case in _cases():
        search_xy = list(case["search_xy"])
        query_xy = list(case["query_xy"])
        search = _to_device_columns(cuda, stream, _ids(len(search_xy), offset=10), search_xy)
        query = _to_device_columns(cuda, stream, _ids(len(query_xy), offset=1), query_xy)
        outputs = _outputs(cuda, stream, len(query_xy))
        expected = _cpu_reference(case)

        result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            radius=float(case["radius"]),
            threshold=int(case["threshold"]),
            partner="numba",
            output_columns=outputs,
            stream=stream,
            return_metadata=True,
        )

        checksum = cuda.device_array((1,), dtype=np.uint64, stream=stream)
        checksum_kernel[1, 1, stream](
            outputs["query_ids"],
            outputs["neighbor_counts"],
            outputs["threshold_flags"],
            checksum,
        )
        observed = _host_outputs(outputs, stream)
        observed_checksum = int(checksum.copy_to_host(stream=stream)[0])
        stream.synchronize()
        expected_checksum = _expected_checksum(expected)
        if observed != expected:
            raise AssertionError(
                f"Numba V4 M1 parity failed for {case['name']}: "
                f"observed={observed!r} expected={expected!r}"
            )
        if observed_checksum != expected_checksum:
            raise AssertionError(
                f"Numba consumer checksum failed for {case['name']}: "
                f"observed={observed_checksum} expected={expected_checksum}"
            )

        metadata = result["metadata"]
        columns = {"search": search, "query": query, "output": outputs}
        plan_matches = _plan_pointer_matches(metadata, columns)
        native_matches = _native_pointer_matches(metadata, columns)
        pointer_match_sets.append({"plan": plan_matches, "native": native_matches})
        if not all(plan_matches.values()):
            raise AssertionError(f"V4 plan pointer mismatch for {case['name']}: {plan_matches!r}")
        if not all(native_matches.values()):
            raise AssertionError(f"native pointer echo mismatch for {case['name']}: {native_matches!r}")
        if int(metadata["caller_stream_handle"]) != stream_handle:
            raise AssertionError("metadata did not preserve Numba caller stream handle")
        if int(metadata["prepare_stream_handle"]) != stream_handle:
            raise AssertionError("metadata did not preserve Numba prepare stream handle")

        case_results.append(
            {
                "name": case["name"],
                "radius": float(case["radius"]),
                "threshold": int(case["threshold"]),
                "query_count": len(query_xy),
                "search_count": len(search_xy),
                "observed": observed,
                "expected": expected,
                "observed_checksum": observed_checksum,
                "expected_checksum": expected_checksum,
                "passed": True,
                "same_stream_consumer_kernel_checksum_passed": True,
                "plan_pointer_match_complete": all(plan_matches.values()),
                "native_pointer_echo_match_complete": all(native_matches.values()),
                "source_protocols": list(metadata["v4_plan"]["source_protocols"]),
                "native_async_ready": bool(metadata["native_async_ready"]),
                "v4_true_zero_copy_claim_authorized": bool(metadata["v4_true_zero_copy_claim_authorized"]),
            }
        )

    prepared_case = _case(
        "prepared_reuse_lifetime",
        search_xy=[(0.0, 0.0), (2.0, 0.0), (4.0, 0.0)],
        query_xy=[(0.0, 0.0), (4.0, 0.0)],
        radius=1.0,
        threshold=1,
    )
    prepared_search_xy = list(prepared_case["search_xy"])
    prepared_search = _to_device_columns(
        cuda,
        stream,
        _ids(len(prepared_search_xy), offset=50),
        prepared_search_xy,
    )
    prepared = rtdsl.prepare_v4_fixed_radius_count_threshold_2d(
        prepared_search,
        max_radius=float(prepared_case["radius"]),
        partner="numba",
        stream=stream,
    )
    prepared_pointer_echoes = []
    prepared_outputs = []
    try:
        for offset, query_xy in enumerate(
            [
                list(prepared_case["query_xy"]),
                [(2.0, 0.0), (9.0, 9.0)],
            ]
        ):
            case = {
                **prepared_case,
                "name": f"prepared_reuse_{offset}",
                "query_xy": query_xy,
            }
            query = _to_device_columns(cuda, stream, _ids(len(query_xy), offset=1 + 10 * offset), query_xy)
            outputs = _outputs(cuda, stream, len(query_xy))
            expected = _cpu_reference(case)
            result = prepared.run(
                query,
                radius=float(prepared_case["radius"]),
                threshold=int(prepared_case["threshold"]),
                output_columns=outputs,
                stream=stream,
                return_metadata=True,
            )
            observed = _host_outputs(outputs, stream)
            stream.synchronize()
            if observed != expected:
                raise AssertionError(
                    f"Numba prepared reuse failed for {case['name']}: "
                    f"observed={observed!r} expected={expected!r}"
                )
            metadata = result["metadata"]
            prepared_pointer_echoes.append(
                {
                    name: int(metadata["native_call_device_pointer_echo"][f"search.{name}"])
                    for name in ("ids", "x", "y")
                }
            )
            prepared_outputs.append({"name": case["name"], "observed": observed, "expected": expected})
    finally:
        prepared.close()

    expected_search_pointers = {name: _device_ptr(column) for name, column in prepared_search.items()}
    prepared_search_pointer_stable = all(
        echo == expected_search_pointers for echo in prepared_pointer_echoes
    )
    if not prepared_search_pointer_stable:
        raise AssertionError(
            "prepared handle did not preserve the expected borrowed Numba search pointers"
        )

    return {
        "status": "pass-with-boundary",
        "report_id": "v4_0_m1_fixed_radius_numba_partner_surface_probe_2026-06-19",
        "route_id": "fixed_radius_count_threshold_2d",
        "framework": "numba",
        "protocol": "cuda_array_interface",
        "evidence_code_commit": _git_value("rev-parse", "HEAD"),
        "evidence_code_tree": _git_value("rev-parse", "HEAD^{tree}"),
        "hardware": _hardware(),
        "case_count": len(case_results),
        "pass_count": sum(1 for row in case_results if row["passed"]),
        "cases": case_results,
        "same_stream_contract": {
            "ordering_scope": "same_nondefault_numba_stream_producer_rtdl_consumer",
            "numba_stream_handle": stream_handle,
            "rtdl_prepare_stream_ptr": stream_handle,
            "rtdl_query_stream_ptr": stream_handle,
            "consumer_kernel_on_same_stream": True,
            "consumer_checksum_validated": True,
            "cross_stream_event_wait_validated": False,
        },
        "pointer_identity": {
            "plan_pointer_match_complete": all(
                all(row["plan"].values()) for row in pointer_match_sets
            ),
            "native_pointer_echo_match_complete": all(
                all(row["native"].values()) for row in pointer_match_sets
            ),
            "checked_column_keys": sorted(pointer_match_sets[0]["native"]) if pointer_match_sets else [],
        },
        "prepared_handle_lifetime_contract": {
            "prepared_reuse_run_count": len(prepared_outputs),
            "caller_kept_search_columns_alive_until_operator_close": True,
            "search_column_borrowed_pointers_stable_across_runs": prepared_search_pointer_stable,
            "outputs": prepared_outputs,
            "required_user_rule": (
                "Numba search columns are caller-owned borrowed device arrays and must outlive "
                "the prepared V4 operator handle."
            ),
        },
        "claim_boundaries": {
            "numba_m1_devicearray_partner_surface_claim_authorized": True,
            "numba_device_array_route_claim_authorized": True,
            "numba_cuda_array_interface_claim_authorized": True,
            "numba_prepared_reuse_claim_authorized": True,
            "numba_full_partner_surface_claim_authorized": False,
            "cross_stream_event_wait_claim_authorized": False,
            "pytorch_route_claim_authorized": False,
            "dlpack_route_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "allowed_wording": (
                "V4 M1 validates the fixed-radius route with Numba DeviceNDArray columns "
                "through __cuda_array_interface__, including parity, same-stream propagation, "
                "pointer echo, caller-owned outputs, and prepared-handle reuse while search "
                "columns remain alive."
            ),
            "forbidden_wording": [
                "all Numba programs are accelerated",
                "full arbitrary Numba partner surface",
                "PyTorch route support",
                "DLPack route support",
                "cross-stream event wait support",
                "async execution",
                "true zero-copy",
                "RT-core speedup",
                "RTX speedup",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 M1 Numba partner-surface probe.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    result = run_probe()
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
