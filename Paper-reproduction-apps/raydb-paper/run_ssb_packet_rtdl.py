from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Sequence


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_sha256(path: Path, expected: str, *, label: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"{label} SHA-256 mismatch: expected {expected}, got {actual}")
    return actual


def _same_input_grouped_rows_claimed(
    *,
    same_packet_bytes_as_author: bool,
    author_matches_oracle: bool | None,
    author_rows,
    rtdl_rows,
    expected_rows,
) -> bool:
    return bool(
        same_packet_bytes_as_author
        and author_matches_oracle is True
        and rtdl_rows == expected_rows
        and author_rows == expected_rows
    )


def _multiply_packet_i32_columns_to_i64(left, right):
    """Multiply packet int32 columns without allowing an intermediate i64 wrap."""
    import numpy as np

    left_array = np.asarray(left)
    right_array = np.asarray(right)
    expected_dtype = np.dtype("<i4")
    if left_array.dtype != expected_dtype or right_array.dtype != expected_dtype:
        raise TypeError("complex aggregate multiplication requires signed int32 packet columns")
    # |int32 * int32| <= 2^62, so an int64 output is mathematically exact.
    return np.multiply(left_array, right_array, dtype=np.int64)


def _observed_gpu_identity() -> str | None:
    expected = os.environ.get("RTDL_EVIDENCE_GPU_IDENTITY")
    if expected is None:
        return None
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=uuid,name,pci.bus_id",
            "--format=csv,noheader,nounits",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    observed = completed.stdout.strip()
    if completed.returncode != 0 or not observed:
        raise RuntimeError("RTDL runner could not observe the cohort GPU identity")
    if observed != expected:
        raise RuntimeError(
            f"RTDL runner GPU identity mismatch: expected {expected!r}, got {observed!r}"
        )
    return observed


def _route_phase_timing(
    *,
    partitioned: bool,
    lowering_seconds: float,
    host_pack_seconds: float,
    partition_pack_seconds: float,
    route_seconds: float,
    native_phase_timing,
) -> tuple[dict[str, float], dict[str, object]]:
    phases = {
        "app_lowering": float(lowering_seconds),
        (
            "host_pack_rays_only"
            if partitioned
            else "host_pack_full_triangles_and_rays"
        ): float(host_pack_seconds),
        "route_total_including_partition_triangle_pack": float(route_seconds),
        **{key: float(value) for key, value in dict(native_phase_timing).items()},
    }
    if partitioned:
        phases["partition_triangle_pack_nested_within_route_total"] = float(
            partition_pack_seconds
        )
    denominators = {
        "route_total_includes_partition_triangle_pack": partitioned,
        "partition_triangle_pack_is_nested_not_additive": partitioned,
        "host_pack_scope": "rays_only" if partitioned else "full_triangles_and_rays",
        "nesting_graph": {
            "schema": "rtdl.timing.nesting_graph.v1",
            "roots": ["app_lowering", "host_pack", "route_total"],
            "edges": (
                [
                    {
                        "parent": "route_total",
                        "child": "partition_triangle_pack",
                        "relationship": "inclusive_nested",
                    },
                    {
                        "parent": "route_total",
                        "child": "native_partition_phases",
                        "relationship": "inclusive_nested",
                    },
                ]
                if partitioned
                else [
                    {
                        "parent": "route_total",
                        "child": "native_prepared_phases",
                        "relationship": "inclusive_nested",
                    }
                ]
            ),
            "additive_warning": (
                "Only root phases may be added. Native and partition-pack phases are "
                "diagnostic children of route_total and overlap generic wrapper timings."
            ),
        },
    }
    return phases, denominators


def _parse_predicate(predicate_path: Path, predicate_count: int):
    lines = predicate_path.read_text(encoding="ascii").splitlines()
    if len(lines) != predicate_count + 1:
        raise ValueError("predicate file must contain one line per scan dimension plus the scan-type line")
    raw_values = [tuple(int(value) for value in line.split(",")) for line in lines[:-1]]
    scan_types = tuple(int(value) for value in lines[-1].split(","))
    if len(scan_types) != predicate_count:
        raise ValueError("scan-type count must match predicate dimensions")
    for index, (values, scan_type) in enumerate(zip(raw_values, scan_types)):
        expected_values = 2 if scan_type == 0 else scan_type
        if scan_type < 0 or len(values) != expected_values:
            raise ValueError(f"predicate dimension {index} does not match its scan type")
    return raw_values, scan_types


def _ordinal(unique_values, raw_value: int, *, dimension: int) -> int:
    import numpy as np

    index = int(np.searchsorted(unique_values, raw_value))
    if index >= len(unique_values) or int(unique_values[index]) != int(raw_value):
        raise ValueError(f"scan dimension {dimension} literal {raw_value} is absent from the packet")
    return index


def _build_rays(
    *,
    min_aggregate: int,
    max_aggregate: int,
    group_count: int,
    scan_unique_values,
    raw_predicates,
    scan_types,
    interval_x: int,
    interval_y: int,
):
    import numpy as np
    from rtdsl import pack_rays_3d_from_arrays

    ordinal_predicates = []
    for dimension, (unique_values, raw_values, scan_type) in enumerate(
        zip(scan_unique_values, raw_predicates, scan_types)
    ):
        ordinals = tuple(_ordinal(unique_values, value, dimension=dimension) for value in raw_values)
        if scan_type == 0 and ordinals[0] > ordinals[1]:
            raise ValueError(f"scan dimension {dimension} has a descending range")
        ordinal_predicates.append(ordinals)

    choices = []
    last_index = len(ordinal_predicates) - 1
    for dimension, (ordinals, scan_type) in enumerate(zip(ordinal_predicates, scan_types)):
        if scan_type == 0:
            if dimension == last_index:
                choices.append((ordinals[0],))
            else:
                choices.append(tuple(range(ordinals[0], ordinals[1] + 1)))
        else:
            choices.append(ordinals)
    predicate_combinations = tuple(itertools.product(*choices))
    if not predicate_combinations:
        raise ValueError("predicate lowering produced no ray-depth combinations")
    z_bases = []
    for combination in predicate_combinations:
        merged = 0
        for ordinal_value, unique_values in zip(combination, scan_unique_values):
            merged = merged * len(unique_values) + int(ordinal_value)
        z_bases.append(merged)

    width = (max_aggregate - min_aggregate + interval_x) // interval_x + 1
    group_range = group_count - 1
    height = (group_range + interval_y) // interval_y
    if group_range % interval_y:
        height += 1
    height = max(1, height)
    depth = len(z_bases)
    ray_count = width * height * depth
    x_grid = min_aggregate + np.arange(width, dtype=np.float64) * float(interval_x)
    y_grid = (np.arange(height, dtype=np.float64) + 1.0) * float(interval_y)
    x_origins = np.tile(x_grid, height * depth)
    y_origins = np.tile(np.repeat(y_grid, width), depth)
    z_origins = np.repeat(np.asarray(z_bases, dtype=np.float64) - 0.5, width * height)
    last_tmax = (
        ordinal_predicates[-1][1] - ordinal_predicates[-1][0] + 1
        if scan_types[-1] == 0
        else 1
    )
    packed = pack_rays_3d_from_arrays(
        np.arange(ray_count, dtype=np.uint32),
        x_origins,
        y_origins,
        z_origins,
        np.zeros(ray_count, dtype=np.float64),
        np.zeros(ray_count, dtype=np.float64),
        np.ones(ray_count, dtype=np.float64),
        np.full(ray_count, float(last_tmax), dtype=np.float64),
    )
    return packed, {
        "width": width,
        "height": height,
        "depth": depth,
        "ray_count": ray_count,
        "ray_tmax": last_tmax,
        "ordinal_predicates": [list(values) for values in ordinal_predicates],
    }


def run_packet(
    packet_path: Path,
    *,
    author_result_path: Path | None = None,
    prepared_ray_batch: bool = False,
    partition_rows: int | None = None,
) -> dict[str, object]:
    import numpy as np
    from rtdsl import pack_triangles_3d_from_arrays
    from rtdsl import prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d
    from rtdsl import run_partitioned_generic_ray_triangle_primitive_grouped_i64_reduction_3d

    if partition_rows is not None and int(partition_rows) <= 0:
        raise ValueError("partition_rows must be positive when provided")

    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet_json_sha256 = sha256_file(packet_path)
    row_count = int(packet["row_count"])
    group_dimension_count = int(packet["group_dimension_count"])
    predicate_dimension_count = int(packet["predicate_dimension_count"])
    column_count = int(packet["column_count"])
    data_path = Path(packet["data_path"])
    predicate_path = Path(packet["predicate_path"])
    expected_rows_path = Path(packet["expected_rows_path"])
    expected_size = row_count * column_count * np.dtype("<i4").itemsize
    if data_path.stat().st_size != expected_size:
        raise ValueError(f"packet size mismatch: expected {expected_size}, got {data_path.stat().st_size}")
    data_sha256 = _require_sha256(data_path, packet["data_sha256"], label="data packet")
    predicate_sha256 = _require_sha256(predicate_path, packet["predicate_sha256"], label="predicate")
    expected_rows_sha256 = _require_sha256(
        expected_rows_path, packet["expected_rows_sha256"], label="expected rows"
    )
    raw_predicates, scan_types = _parse_predicate(predicate_path, predicate_dimension_count)
    if list(scan_types) != list(packet["scan_types"]):
        raise ValueError("predicate scan types differ from the packet manifest")

    registered_primary_start = time.perf_counter()
    lowering_start = registered_primary_start
    columns = np.memmap(data_path, dtype="<i4", mode="r", shape=(column_count, row_count))
    aggregate_values = columns[0]
    group_columns = [columns[1 + index] for index in range(group_dimension_count)]
    scan_offset = 1 + group_dimension_count
    scan_columns = [columns[scan_offset + index] for index in range(predicate_dimension_count)]
    extra_multiplier = columns[-1] if packet["complex_aggregate"] else None

    group_matrix = np.column_stack(group_columns)
    unique_groups, group_ids = np.unique(group_matrix, axis=0, return_inverse=True)
    group_ids = group_ids.astype(np.uint32, copy=False)
    group_count = int(len(unique_groups))
    scan_unique_values = []
    merged_scan = None
    scan_cardinalities = []
    for scan_column in scan_columns:
        unique_values = np.unique(scan_column)
        ordinals = np.searchsorted(unique_values, scan_column).astype(np.uint64, copy=False)
        merged_scan = ordinals if merged_scan is None else merged_scan * len(unique_values) + ordinals
        scan_unique_values.append(unique_values)
        scan_cardinalities.append(int(len(unique_values)))
    if merged_scan is None:
        raise ValueError("at least one scan dimension is required")
    primitive_values = aggregate_values.astype(np.int64)
    primitive_value_derivation = {
        "contract": "signed_i32_product_exact_in_signed_i64.v1",
        "complex_aggregate": bool(extra_multiplier is not None),
        "source_dtype": str(aggregate_values.dtype),
        "overflow_fail_closed_before_multiplication": True,
    }
    if extra_multiplier is not None:
        primitive_values = _multiply_packet_i32_columns_to_i64(
            aggregate_values,
            extra_multiplier,
        )
    lowering_seconds = time.perf_counter() - lowering_start

    pack_start = time.perf_counter()
    packed_triangles = None
    if partition_rows is None:
        primitive_ids = np.arange(row_count, dtype=np.uint32)
        packed_triangles = pack_triangles_3d_from_arrays(
            primitive_ids,
            aggregate_values,
            group_ids,
            merged_scan,
            aggregate_values.astype(np.int64) + 2 * int(packet["interval_x"]),
            group_ids,
            merged_scan,
            aggregate_values,
            group_ids.astype(np.int64) + 2 * int(packet["interval_y"]),
            merged_scan,
        )
    packed_rays, ray_grid = _build_rays(
        min_aggregate=int(aggregate_values.min()),
        max_aggregate=int(aggregate_values.max()),
        group_count=group_count,
        scan_unique_values=scan_unique_values,
        raw_predicates=raw_predicates,
        scan_types=scan_types,
        interval_x=int(packet["interval_x"]),
        interval_y=int(packet["interval_y"]),
    )
    pack_seconds = time.perf_counter() - pack_start

    partition_pack_stats = {"seconds": 0.0, "count": 0}

    def primitive_partitions():
        resolved_partition_rows = int(partition_rows or row_count)
        for start in range(0, row_count, resolved_partition_rows):
            stop = min(row_count, start + resolved_partition_rows)
            partition_pack_start = time.perf_counter()
            primitive_ids = np.arange(start, stop, dtype=np.uint32)
            triangles = pack_triangles_3d_from_arrays(
                primitive_ids,
                aggregate_values[start:stop],
                group_ids[start:stop],
                merged_scan[start:stop],
                aggregate_values[start:stop].astype(np.int64) + 2 * int(packet["interval_x"]),
                group_ids[start:stop],
                merged_scan[start:stop],
                aggregate_values[start:stop],
                group_ids[start:stop].astype(np.int64) + 2 * int(packet["interval_y"]),
                merged_scan[start:stop],
            )
            partition_pack_stats["seconds"] += time.perf_counter() - partition_pack_start
            partition_pack_stats["count"] += 1
            yield {
                "primitive_id_start": start,
                "triangles": triangles,
                "primitive_group_ids": group_ids[start:stop],
                "primitive_values": primitive_values[start:stop],
            }

    route_start = time.perf_counter()
    if partition_rows is not None:
        native_result = run_partitioned_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
            packed_rays,
            primitive_partitions(),
            group_count=group_count,
            expected_primitive_count=row_count,
            reduction="sum",
            backend="optix",
        )
    else:
        with prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
            packed_triangles,
            primitive_group_ids=group_ids,
            primitive_values=primitive_values,
            group_count=group_count,
            backend="optix",
        ) as prepared:
            if prepared_ray_batch:
                with prepared.prepare_ray_batch(packed_rays) as prepared_rays:
                    native_result = prepared.run_prepared_rays(prepared_rays, reduction="sum")
            else:
                native_result = prepared.run(packed_rays, reduction="sum")
    route_seconds = time.perf_counter() - route_start

    rtdl_rows = [
        {
            "group": [int(value) for value in unique_groups[int(row["group_id"])].tolist()],
            "value": int(row["sum"]),
        }
        for row in native_result["rows"]
    ]
    registered_primary_elapsed_seconds = (
        time.perf_counter() - registered_primary_start
    )
    expected_rows = json.loads(expected_rows_path.read_text(encoding="utf-8"))
    author_rows = None
    author_matches_oracle = None
    same_packet_bytes_as_author = False
    author_result_sha256 = None
    author_evidence_verified = False
    if author_result_path is not None:
        author_result = json.loads(author_result_path.read_text(encoding="utf-8"))
        author_result_sha256 = sha256_file(author_result_path)
        author_rows = author_result.get("author_rows")
        author_matches_oracle = bool(author_result.get("author_matches_cpu_oracle"))
        observed_hashes = {
            "data_sha256": data_sha256,
            "predicate_sha256": predicate_sha256,
            "expected_rows_sha256": expected_rows_sha256,
        }
        author_evidence_verified = bool(
            author_result.get("schema")
            == "rtdl.paper_reproduction.raydb.author_packet_gate.v2"
            and author_result.get("packet_schema") == packet.get("schema")
            and author_result.get("packet_json_sha256") == packet_json_sha256
            and author_result.get("packet_files_stable_during_author_run") is True
            and author_result.get("packet_file_hashes_before") == observed_hashes
            and author_result.get("packet_file_hashes_after") == observed_hashes
            and author_result.get("expected_rows") == expected_rows
            and author_result.get("query_id") == packet.get("query_id")
            and int(author_result.get("scale_factor", -1))
            == int(packet.get("scale_factor", -2))
            and int(author_result.get("row_count", -1)) == row_count
        )
        same_packet_bytes_as_author = (
            author_evidence_verified
            and author_result.get("data_sha256") == data_sha256
            and author_result.get("predicate_sha256") == predicate_sha256
            and author_result.get("expected_rows_sha256") == expected_rows_sha256
        )
    grouped_rows_claimed = _same_input_grouped_rows_claimed(
        same_packet_bytes_as_author=same_packet_bytes_as_author,
        author_matches_oracle=author_matches_oracle,
        author_rows=author_rows,
        rtdl_rows=rtdl_rows,
        expected_rows=expected_rows,
    )
    partitioned = partition_rows is not None
    phase_timing_seconds, timing_denominators = _route_phase_timing(
        partitioned=partitioned,
        lowering_seconds=lowering_seconds,
        host_pack_seconds=pack_seconds,
        partition_pack_seconds=float(partition_pack_stats["seconds"]),
        route_seconds=route_seconds,
        native_phase_timing=native_result.get("phase_timing_seconds", {}),
    )
    workspace_root = Path(__file__).resolve().parents[2]
    native_library_path = Path(os.environ.get("RTDL_OPTIX_LIB", ""))
    native_library_sha256 = (
        sha256_file(native_library_path) if native_library_path.is_file() else None
    )
    generic_primitives_path = workspace_root / "src" / "rtdsl" / "generic_primitives.py"
    optix_runtime_path = workspace_root / "src" / "rtdsl" / "optix_runtime.py"
    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_packet_rtdl_gate.v3",
        "packet_schema": packet.get("schema"),
        "packet_json_sha256": packet_json_sha256,
        "author_result_sha256": author_result_sha256,
        "author_evidence_verified": author_evidence_verified,
        "runner_sha256": sha256_file(Path(__file__)),
        "generic_primitives_sha256": sha256_file(generic_primitives_path),
        "optix_runtime_sha256": sha256_file(optix_runtime_path),
        "native_library_path": str(native_library_path) if native_library_path else None,
        "native_library_sha256": native_library_sha256,
        "execution_identity": {
            "evidence_cohort_id": os.environ.get("RTDL_EVIDENCE_COHORT_ID"),
            "host": socket.gethostname(),
            "gpu_identity": _observed_gpu_identity(),
            "matrix_runner_sha256": os.environ.get(
                "RTDL_EVIDENCE_MATRIX_RUNNER_SHA256"
            ),
        },
        "case_id": packet["case_id"],
        "query_id": packet["query_id"],
        "host": socket.gethostname(),
        "backend": "optix",
        "prepared_ray_batch_requested": bool(prepared_ray_batch),
        "partitioned_execution_requested": partition_rows is not None,
        "partition_rows": int(partition_rows) if partition_rows is not None else None,
        "scale_factor": int(packet.get("scale_factor", 1)),
        "input_identity_level": packet["input_identity_level"],
        "same_packet_bytes_as_author": same_packet_bytes_as_author,
        "row_count": row_count,
        "data_sha256": data_sha256,
        "predicate_sha256": predicate_sha256,
        "expected_rows_sha256": expected_rows_sha256,
        "group_count": group_count,
        "scan_cardinalities": scan_cardinalities,
        "ray_grid": ray_grid,
        "triangle_count": row_count,
        "primitive_value_derivation": primitive_value_derivation,
        "rtdl_rows": rtdl_rows,
        "expected_rows": expected_rows,
        "author_rows": author_rows,
        "rtdl_matches_oracle": rtdl_rows == expected_rows,
        "author_matches_oracle": author_matches_oracle,
        "author_matches_rtdl": author_rows == rtdl_rows if author_rows is not None else None,
        "missing_rows": [row for row in expected_rows if row not in rtdl_rows],
        "unexpected_rows": [row for row in rtdl_rows if row not in expected_rows],
        "native_symbol": native_result.get("native_symbol"),
        "native_symbols": list(native_result.get("native_symbols", ())),
        "partition_count": int(native_result.get("partition_count", 1)),
        "expected_primitive_count": int(
            native_result.get("expected_primitive_count", row_count)
        ),
        "peak_partition_primitive_count": int(
            native_result.get("peak_partition_primitive_count", row_count)
        ),
        "prepared_ray_batch_reused_across_partitions": bool(
            native_result.get("prepared_ray_batch_reused_across_partitions", False)
        ),
        "partition_ledger": list(native_result.get("partition_ledger", ())),
        "partition_ledger_schema": native_result.get("partition_ledger_schema"),
        "phase_timing_contract": native_result.get("phase_timing_contract"),
        "hit_event_count_before_dedup": int(native_result["hit_event_count_before_dedup"]),
        "phase_timing_seconds": phase_timing_seconds,
        "registered_primary_timing": {
            "contract_id": "loaded_sf10_tables_to_canonical_group_rows__lower_prepare_twelve_partitions_project",
            "elapsed_seconds": registered_primary_elapsed_seconds,
            "starts_after_input_hash_verification": True,
            "ends_before_correctness_comparator": True,
            "includes_app_lowering": True,
            "includes_result_projection": True,
            "partition_triangle_pack_nested_within_route_total": partitioned,
        },
        "timing_denominators": timing_denominators,
        "transfer_metadata": native_result.get("transfer_metadata", {}),
        "partition_execution_contract": native_result.get("partition_execution_contract"),
        "claim_boundary": {
            "single_same_input_grouped_rows_claimed": grouped_rows_claimed,
            "all_13_queries_at_this_scale_claimed": False,
            "exact_paper_input_claimed": False,
            "paper_performance_claimed": False,
            "author_algorithm_equivalence_claimed": False,
            "true_zero_copy_claimed": False,
            "bounded_live_scene_execution_claimed": partition_rows is not None,
            "zero_sum_group_semantics": (
                "generic RTDL grouped-i64 preserves hit groups whose exact sum is zero; "
                "RayDB author text comparison is restricted to this SSB matrix, whose "
                "expected result contains no zero-sum group"
            ),
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one RayDB SSB packet through generic packed RTDL OptiX primitives")
    parser.add_argument("--packet-json", type=Path, required=True)
    parser.add_argument("--author-result", type=Path)
    parser.add_argument(
        "--prepared-ray-batch",
        action="store_true",
        help="Prepare query rays once on device before the measured grouped reduction call",
    )
    parser.add_argument(
        "--partition-rows",
        type=int,
        help="Bound live primitive-scene rows and exactly merge grouped results across partitions",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_packet(
        args.packet_json,
        author_result_path=args.author_result,
        prepared_ray_batch=args.prepared_ray_batch,
        partition_rows=args.partition_rows,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output_json.with_name(args.output_json.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output_json)
    print(json.dumps({key: value for key, value in result.items() if key not in {"rtdl_rows", "expected_rows", "author_rows"}}, indent=2))
    return 0 if (
        result["rtdl_matches_oracle"]
        and result["author_matches_rtdl"] is not False
        and not result["missing_rows"]
        and not result["unexpected_rows"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
