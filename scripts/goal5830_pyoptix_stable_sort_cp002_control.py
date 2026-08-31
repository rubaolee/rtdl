#!/usr/bin/env python3
"""Run the stable-sort fixture through valid and CP002-broken PyOptiX code.

This is an intentionally small, untimed control.  It never imports RTDL.  The
two CUDA programs differ in exactly one expression:

    item.item_id       -- the application's nominal record identity
    primitive_index    -- the GAS's physical primitive position

Both values are U32, so ordinary CUDA/OptiX validation cannot distinguish
their application meaning.  A deranged physical order makes the substitution
observable in the stable-sort relation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sys

import cupy as cp
from cuda.bindings import runtime as cuda_runtime
import numpy as np


VALUES = (2, 1, 2, 0)
ORDER_CODES = (10, 6, 12, 3)
INDEXED_ORDER = (2, 0, 3, 1)
SOURCE_ORDER = (3, 2, 1, 0)
EXPECTED_ROWS = (
    (0, 0), (0, 1), (0, 3),
    (1, 1), (1, 3),
    (2, 0), (2, 1), (2, 2), (2, 3),
    (3, 3),
)
EXPECTED_CP002_ROWS = (
    (0, 1), (0, 2), (0, 3),
    (1, 2), (1, 3),
    (2, 0), (2, 1), (2, 2), (2, 3),
    (3, 2),
)
EXPECTED_STABLE_RECORDS = ((0, 3), (1, 1), (2, 0), (2, 2))
VALID_EXPRESSION = "optixReportIntersection(0.0f, 0u, item.item_id);"
CP002_EXPRESSION = "optixReportIntersection(0.0f, 0u, primitive_index);"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_baseline(path: Path):
    spec = importlib.util.spec_from_file_location(
        "goal5830_pyoptix_baseline", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load PyOptiX baseline from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def device_variants(base_source: bytes) -> dict[str, bytes]:
    text = base_source.decode("utf-8")
    if text.count(VALID_EXPRESSION) != 1:
        raise RuntimeError("the nominal-item-id source anchor is not unique")
    broken = text.replace(VALID_EXPRESSION, CP002_EXPRESSION, 1)
    valid_lines = text.splitlines()
    broken_lines = broken.splitlines()
    changed = [
        (index + 1, before, after)
        for index, (before, after) in enumerate(zip(valid_lines, broken_lines))
        if before != after
    ]
    if len(valid_lines) != len(broken_lines) or changed != [
        (
            next(index + 1 for index, line in enumerate(valid_lines)
                 if VALID_EXPRESSION in line),
            next(line for line in valid_lines if VALID_EXPRESSION in line),
            next(line for line in broken_lines if CP002_EXPRESSION in line),
        )
    ]:
        raise RuntimeError("CP002 program must be an exact one-line mutation")
    return {
        "valid_nominal_item_id": text.encode("utf-8"),
        "cp002_physical_primitive_index": broken.encode("utf-8"),
    }


def compile_ptx(
    baseline,
    source: bytes,
    *,
    source_name: str,
    optix_include: Path,
    cuda_include: Path,
) -> bytes:
    from cuda.bindings import nvrtc

    program = baseline.check_nvrtc(nvrtc.nvrtcCreateProgram(
        source, source_name.encode("utf-8"), 0, [], []))
    options = [
        b"--std=c++17",
        b"--device-as-default-execution-space",
        b"--relocatable-device-code=true",
        f"-I{optix_include}".encode("utf-8"),
        f"-I{cuda_include}".encode("utf-8"),
        f"-I{cuda_include / 'nv'}".encode("utf-8"),
    ]
    baseline.check_nvrtc(
        nvrtc.nvrtcCompileProgram(program, len(options), options), program)
    size = baseline.check_nvrtc(nvrtc.nvrtcGetPTXSize(program))
    ptx = b" " * size
    baseline.check_nvrtc(nvrtc.nvrtcGetPTX(program, ptx))
    return ptx


def sorting_fixture() -> dict[str, object]:
    upper = float(max(ORDER_CODES) + 1)
    indexed = [
        [float(ORDER_CODES[item_id]), 0.0, upper, 1.0, item_id]
        for item_id in INDEXED_ORDER
    ]
    sources = [
        [
            float(ORDER_CODES[item_id]), 0.0,
            float(ORDER_CODES[item_id]) + 0.25, 1.0,
            item_id,
        ]
        for item_id in SOURCE_ORDER
    ]
    return {
        "id": "STABLE_SORT_DUPLICATE_DERANGED",
        "indexed": indexed,
        "sources": sources,
        "minimum_overlap": 0.25,
        "capacity": len(EXPECTED_ROWS),
    }


def run_forward_relation(baseline, context, pipeline, sbt, fixture):
    """Run the one sufficient orientation for this suffix-box construction."""

    indexed = baseline.boxes_array(fixture["indexed"])
    sources = baseline.boxes_array(fixture["sources"])
    d_indexed = baseline.to_device(indexed)
    d_sources = baseline.to_device(sources)
    raw_capacity = max(1, 2 * len(indexed) * len(sources))
    d_rows = cp.zeros(raw_capacity * 2, dtype=np.uint32)
    d_count = cp.zeros(1, dtype=np.uint32)
    d_overflow = cp.zeros(1, dtype=np.uint32)
    d_status = cp.zeros(1, dtype=np.uint32)
    handle, gas_keepalive = baseline.build_custom_gas(context, indexed)
    params = np.zeros(1, dtype=baseline.PARAM_DTYPE)
    params[0] = (
        handle,
        d_indexed.ptr,
        d_sources.ptr,
        d_rows.data.ptr,
        d_count.data.ptr,
        d_overflow.data.ptr,
        len(indexed),
        len(sources),
        raw_capacity,
        0,
        np.float32(fixture["minimum_overlap"]),
        np.float32(0.0),
        np.float32(1.0),
        0,
        0,
        0,
        0,
        0,
        d_status.data.ptr,
    )
    device_params = baseline.launch(pipeline, sbt, params, len(sources))
    keepalive = [
        d_indexed, d_sources, d_rows, d_count, d_overflow, d_status,
        device_params, *gas_keepalive,
    ]
    raw_count = int(cp.asnumpy(d_count)[0])
    overflow = int(cp.asnumpy(d_overflow)[0])
    status = int(cp.asnumpy(d_status)[0])
    if overflow or status or raw_count > raw_capacity:
        raise RuntimeError(
            f"relation device failure: count={raw_count}, "
            f"overflow={overflow}, status={status}")
    raw = cp.asnumpy(d_rows[: raw_count * 2]).reshape((-1, 2))
    rows = tuple(sorted({(int(row[0]), int(row[1])) for row in raw}))
    del keepalive
    return rows, {
        "raw_event_count": raw_count,
        "unique_row_count": len(rows),
        "duplicate_count": raw_count - len(rows),
        "device_overflow": overflow,
        "device_status": status,
        "launch_count": 1,
    }


def consume_sort_relation(rows: tuple[tuple[int, int], ...]):
    """Derive rank by nominal self identity; no comparison sort is used."""

    by_source: list[list[int]] = [[] for _ in VALUES]
    for source_id, predecessor_id in rows:
        if source_id >= len(VALUES) or predecessor_id >= len(VALUES):
            raise ValueError("relation contains an unknown application item id")
        by_source[source_id].append(predecessor_id)
    ranks = []
    for item_id, predecessors in enumerate(by_source):
        if predecessors.count(item_id) != 1:
            raise ValueError(f"item {item_id} must have exactly one self relation")
        ranks.append(sum(value != item_id for value in predecessors))
    if set(ranks) != set(range(len(VALUES))):
        raise ValueError("relation does not define unique ranks")
    records: list[tuple[int, int] | None] = [None] * len(VALUES)
    for item_id, rank in enumerate(ranks):
        records[rank] = (VALUES[item_id], item_id)
    if any(record is None for record in records):
        raise ValueError("rank scatter is incomplete")
    return tuple(ranks), tuple(record for record in records if record is not None)


def application_observation(rows: tuple[tuple[int, int], ...]) -> dict[str, object]:
    try:
        ranks, records = consume_sort_relation(rows)
    except ValueError as error:
        return {
            "status": "REJECTED_BY_APPLICATION_POSTCHECK",
            "reason": str(error),
            "matches_stable_sort_oracle": False,
        }
    return {
        "status": "RETURNED",
        "ranks_by_item_id": ranks,
        "sorted_records": records,
        "matches_stable_sort_oracle": records == EXPECTED_STABLE_RECORDS,
    }


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pyoptix-baseline", type=Path, required=True)
    parser.add_argument("--base-device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--expected-optix-api-version", default="9.0.0")
    parser.add_argument("--compatibility-authority", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    if args.output.exists() or args.evidence_dir.exists():
        raise FileExistsError("Goal5830 PyOptiX evidence is create-only")
    for path in (
        args.pyoptix_baseline,
        args.base_device_source,
        args.compatibility_authority,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    baseline = load_baseline(args.pyoptix_baseline.resolve())
    observed_version = tuple(int(value) for value in baseline.optix.version())
    expected_version = tuple(
        int(value) for value in args.expected_optix_api_version.split("."))
    if observed_version != expected_version:
        raise RuntimeError(
            f"OptiX API mismatch: {observed_version} != {expected_version}")

    base_source = args.base_device_source.read_bytes()
    variants = device_variants(base_source)
    args.evidence_dir.mkdir(parents=True)
    sources_dir = args.evidence_dir / "device_sources"
    ptx_dir = args.evidence_dir / "ptx"
    sources_dir.mkdir()
    ptx_dir.mkdir()

    context, logger = baseline.make_context()
    compiled = {}
    keepalive = []
    for name, source in variants.items():
        source_path = sources_dir / f"{name}.cu"
        source_path.write_bytes(source)
        ptx = compile_ptx(
            baseline,
            source,
            source_name=source_path.name,
            optix_include=args.optix_include,
            cuda_include=args.cuda_include,
        )
        ptx_path = ptx_dir / f"{name}.ptx"
        ptx_path.write_bytes(ptx)
        pipeline, groups, logs = baseline.build_pipeline(
            context, ptx, task="relation")
        sbt, sbt_keepalive = baseline.make_sbt(groups)
        keepalive.append((pipeline, groups, sbt, sbt_keepalive))
        compiled[name] = {
            "pipeline": pipeline,
            "sbt": sbt,
            "pipeline_logs": logs,
            "device_source_sha256": sha256_bytes(source),
            "loaded_ptx_sha256": sha256_bytes(ptx),
        }

    fixture = sorting_fixture()
    valid_rows, valid_diagnostics = run_forward_relation(
        baseline,
        context,
        compiled["valid_nominal_item_id"]["pipeline"],
        compiled["valid_nominal_item_id"]["sbt"],
        fixture,
    )
    broken_rows, broken_diagnostics = run_forward_relation(
        baseline,
        context,
        compiled["cp002_physical_primitive_index"]["pipeline"],
        compiled["cp002_physical_primitive_index"]["sbt"],
        fixture,
    )
    if valid_rows != EXPECTED_ROWS:
        raise RuntimeError(f"valid relation mismatch: {valid_rows!r}")
    if broken_rows != EXPECTED_CP002_ROWS:
        raise RuntimeError(f"CP002 relation mismatch: {broken_rows!r}")
    valid_application = application_observation(valid_rows)
    broken_application = application_observation(broken_rows)
    if valid_application.get("matches_stable_sort_oracle") is not True:
        raise RuntimeError("valid relation did not produce the stable order")
    if broken_application.get("matches_stable_sort_oracle") is not False:
        raise RuntimeError("CP002 mutation did not break the sorting protocol")

    cuda_error = int(cuda_runtime.cudaGetLastError()[0].value)
    validation_errors = [
        message for message in logger.messages if int(message["level"]) <= 2
    ]
    if cuda_error != 0 or validation_errors:
        raise RuntimeError(
            f"platform diagnostic fired: cuda={cuda_error}, "
            f"optix={validation_errors!r}")

    result = {
        "schema": "rtdl.goal5830.pyoptix_stable_sort_cp002_control.v1",
        "status": "PASS",
        "question": (
            "Can CUDA/OptiX distinguish application item identity from a "
            "same-width physical primitive index in this sorting protocol?"
        ),
        "answer": "NO__BROKEN_PROGRAM_LAUNCHED_AND_RETURNED_SILENT_WRONG_RELATION",
        "fixture": {
            "values": VALUES,
            "order_codes": ORDER_CODES,
            "indexed_physical_order": INDEXED_ORDER,
            "source_launch_order": SOURCE_ORDER,
            "expected_stable_records": EXPECTED_STABLE_RECORDS,
            **fixture,
        },
        "exact_single_line_mutation": {
            "before": VALID_EXPRESSION,
            "after": CP002_EXPRESSION,
            "changed_line_count": 1,
            "projection_type_before": "U32",
            "projection_type_after": "U32",
        },
        "valid_program": {
            "relation_rows": valid_rows,
            "diagnostics": valid_diagnostics,
            "application": valid_application,
        },
        "cp002_broken_program": {
            "relation_rows": broken_rows,
            "diagnostics": broken_diagnostics,
            "platform_exception": None,
            "application": broken_application,
            "silent_wrong_before_application_postcheck": True,
        },
        "platform_diagnostics": {
            "cuda_last_error": "SUCCESS",
            "cuda_last_error_code": cuda_error,
            "optix_validation": "NO_FATAL_OR_ERROR_MESSAGES",
            "optix_validation_error_message_count": len(validation_errors),
            "all_optix_context_messages": logger.messages,
            "pipeline_build_logs": {
                name: row["pipeline_logs"] for name, row in compiled.items()
            },
            "process_exit_code_if_result_written": 0,
        },
        "identities": {
            name: {
                key: value for key, value in row.items()
                if key in ("device_source_sha256", "loaded_ptx_sha256")
            }
            for name, row in compiled.items()
        },
        "environment": {
            "pyoptix_repository_commit": baseline.PYOPTIX_COMMIT,
            "pyoptix_distribution_version": importlib.metadata.version("pyoptix"),
            "optix_api_version": ".".join(map(str, observed_version)),
            "compatibility_authority_sha256": sha256_bytes(
                args.compatibility_authority.read_bytes()),
            "pyoptix_baseline_sha256": sha256_bytes(
                args.pyoptix_baseline.read_bytes()),
            "base_device_source_sha256": sha256_bytes(base_source),
        },
        "scope": {
            "imports_rtdl": False,
            "one_forward_launch_is_complete_for_this_suffix_box_fixture": True,
            "sorting_algorithm_invented_by_rtdl": False,
            "application_mapping_verified_by_rtdl": False,
            "general_sorting_claimed": False,
            "performance_claimed": False,
            "registered_performance_timing_count": 0,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
