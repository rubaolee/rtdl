from __future__ import annotations

import argparse
import hashlib
import json
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


def _dense_ordinal(column, *, label: str):
    import numpy as np

    unique_values = np.unique(column)
    ordinals = np.searchsorted(unique_values, column).astype(np.uint32, copy=False)
    if unique_values.size == 0:
        raise ValueError(f"{label} must not be empty")
    return unique_values, ordinals


def _ordinal_for_literal(unique_values, raw_value: int, *, label: str) -> int:
    import numpy as np

    index = int(np.searchsorted(unique_values, raw_value))
    if index >= len(unique_values) or int(unique_values[index]) != int(raw_value):
        raise ValueError(f"{label} literal {raw_value} is absent from the input column")
    return index


def _build_q11_rays(
    *,
    min_aggregate: int,
    max_aggregate: int,
    year_values,
    discount_values,
    quantity_values,
    interval_x: int = 6,
    interval_y: int = 1,
):
    import numpy as np
    from rtdsl import pack_rays_3d_from_arrays

    year_ordinal = _ordinal_for_literal(year_values, 1993, label="year")
    discount_low = _ordinal_for_literal(discount_values, 1, label="discount")
    discount_high = _ordinal_for_literal(discount_values, 3, label="discount")
    quantity_low = _ordinal_for_literal(quantity_values, 1, label="quantity")
    quantity_high = _ordinal_for_literal(quantity_values, 24, label="quantity")

    width = (max_aggregate - min_aggregate + interval_x) // interval_x + 1
    height = 1
    depth = discount_high - discount_low + 1
    ray_count = width * height * depth
    x_origins = np.tile(
        min_aggregate + np.arange(width, dtype=np.float64) * float(interval_x),
        depth,
    )
    z_bases = []
    quantity_count = int(len(quantity_values))
    discount_count = int(len(discount_values))
    for discount_ordinal in range(discount_low, discount_high + 1):
        merged = (
            year_ordinal * discount_count * quantity_count
            + discount_ordinal * quantity_count
            + quantity_low
        )
        z_bases.append(merged)
    z_origins = np.repeat(np.asarray(z_bases, dtype=np.float64) - 0.5, width)
    if len(x_origins) != ray_count or len(z_origins) != ray_count:
        raise AssertionError("Q1.1 ray-grid construction produced an inconsistent count")
    packed = pack_rays_3d_from_arrays(
        np.arange(ray_count, dtype=np.uint32),
        x_origins,
        np.full(ray_count, float(interval_y), dtype=np.float64),
        z_origins,
        np.zeros(ray_count, dtype=np.float64),
        np.zeros(ray_count, dtype=np.float64),
        np.ones(ray_count, dtype=np.float64),
        np.full(ray_count, float(quantity_high - quantity_low + 1), dtype=np.float64),
    )
    return packed, {
        "width": width,
        "height": height,
        "depth": depth,
        "ray_count": ray_count,
        "year_ordinal": year_ordinal,
        "discount_ordinal_range": [discount_low, discount_high],
        "quantity_ordinal_range": [quantity_low, quantity_high],
        "ray_tmax": quantity_high - quantity_low + 1,
    }


def run_q11_rtdl(
    packet_json_path: Path,
    data_path: Path,
    predicate_path: Path,
    expected_rows_path: Path,
    *,
    author_result_path: Path | None = None,
    prepared_ray_batch: bool = False,
) -> dict[str, object]:
    import numpy as np
    from rtdsl import pack_triangles_3d_from_arrays
    from rtdsl import prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d

    packet = json.loads(packet_json_path.read_text(encoding="utf-8"))
    if packet.get("case_id") != "ssb_sf1_q11":
        raise ValueError("run_ssb_q11_rtdl only accepts the ssb_sf1_q11 packet")
    row_count = int(packet["row_count"])
    expected_bytes = 6 * row_count * np.dtype("<i4").itemsize
    if data_path.stat().st_size != expected_bytes:
        raise ValueError(
            f"Q1.1 packet byte length mismatch: expected {expected_bytes}, got {data_path.stat().st_size}"
        )
    data_sha256 = _require_sha256(
        data_path,
        str(packet["data_sha256"]),
        label="Q1.1 data packet",
    )
    predicate_sha256 = _require_sha256(
        predicate_path,
        str(packet["predicate_sha256"]),
        label="Q1.1 predicate",
    )
    expected_rows_sha256 = _require_sha256(
        expected_rows_path,
        str(packet["expected_rows_sha256"]),
        label="Q1.1 expected rows",
    )
    if predicate_path.read_text(encoding="ascii").splitlines() != ["1993", "1,3", "1,24", "1,0,0"]:
        raise ValueError("Q1.1 predicate contents do not match the pinned author contract")

    phase_start = time.perf_counter()
    columns = np.memmap(data_path, dtype="<i4", mode="r", shape=(6, row_count))
    aggregate_values = columns[0]
    group_values = columns[1]
    scan_year = columns[2]
    scan_discount = columns[3]
    scan_quantity = columns[4]
    extra_multiplier = columns[5]
    if bool(np.any(group_values != 0)):
        raise ValueError("Q1.1 packet requires the single constant group value 0")
    year_values, year_ordinals = _dense_ordinal(scan_year, label="year")
    discount_values, discount_ordinals = _dense_ordinal(scan_discount, label="discount")
    quantity_values, quantity_ordinals = _dense_ordinal(scan_quantity, label="quantity")
    merged_scan = (
        year_ordinals.astype(np.uint64) * len(discount_values) * len(quantity_values)
        + discount_ordinals.astype(np.uint64) * len(quantity_values)
        + quantity_ordinals.astype(np.uint64)
    )
    lowering_seconds = time.perf_counter() - phase_start

    pack_start = time.perf_counter()
    primitive_ids = np.arange(row_count, dtype=np.uint32)
    zero_groups = np.zeros(row_count, dtype=np.uint32)
    primitive_values = aggregate_values.astype(np.uint64) * extra_multiplier.astype(np.uint64)
    packed_triangles = pack_triangles_3d_from_arrays(
        primitive_ids,
        aggregate_values,
        group_values,
        merged_scan,
        aggregate_values.astype(np.int64) + 12,
        group_values,
        merged_scan,
        aggregate_values,
        group_values.astype(np.int64) + 2,
        merged_scan,
    )
    packed_rays, ray_grid = _build_q11_rays(
        min_aggregate=int(aggregate_values.min()),
        max_aggregate=int(aggregate_values.max()),
        year_values=year_values,
        discount_values=discount_values,
        quantity_values=quantity_values,
    )
    pack_seconds = time.perf_counter() - pack_start

    route_start = time.perf_counter()
    with prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
        packed_triangles,
        primitive_group_ids=zero_groups,
        primitive_values=primitive_values,
        group_count=1,
        backend="optix",
    ) as prepared:
        if prepared_ray_batch:
            with prepared.prepare_ray_batch(packed_rays) as prepared_rays:
                native_result = prepared.run_prepared_rays(prepared_rays, reduction="sum")
        else:
            native_result = prepared.run(packed_rays, reduction="sum")
    route_seconds = time.perf_counter() - route_start

    rtdl_rows = [
        {"group": [int(row["group_id"])], "value": int(row["sum"])}
        for row in native_result["rows"]
    ]
    expected_rows = json.loads(expected_rows_path.read_text(encoding="utf-8"))
    author_rows = None
    author_matches_oracle = None
    if author_result_path is not None:
        author_result = json.loads(author_result_path.read_text(encoding="utf-8"))
        author_rows = author_result.get("author_rows")
        author_matches_oracle = bool(author_result.get("author_matches_cpu_oracle"))
    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_sf1_q11_rtdl_gate.v1",
        "case_id": "ssb_sf1_q11",
        "host": "lx1",
        "backend": "optix",
        "prepared_ray_batch_requested": bool(prepared_ray_batch),
        "input_identity_level": packet["input_identity_level"],
        "same_packet_bytes_as_author": author_result_path is not None,
        "row_count": row_count,
        "data_sha256": data_sha256,
        "predicate_sha256": predicate_sha256,
        "expected_rows_sha256": expected_rows_sha256,
        "dense_scan_cardinalities": {
            "year": int(len(year_values)),
            "discount": int(len(discount_values)),
            "quantity": int(len(quantity_values)),
        },
        "ray_grid": ray_grid,
        "triangle_count": int(packed_triangles.count),
        "primitive_value_contract": "aggregate_value_times_extra_multiplier_uint64",
        "rtdl_rows": rtdl_rows,
        "expected_rows": expected_rows,
        "author_rows": author_rows,
        "rtdl_matches_oracle": rtdl_rows == expected_rows,
        "author_matches_oracle": author_matches_oracle,
        "author_matches_rtdl": author_rows == rtdl_rows if author_rows is not None else None,
        "native_symbol": native_result.get("native_symbol"),
        "hit_event_count_before_dedup": int(native_result["hit_event_count_before_dedup"]),
        "phase_timing_seconds": {
            "app_lowering": lowering_seconds,
            "host_pack_triangles_and_rays": pack_seconds,
            "prepared_route_total": route_seconds,
            **{key: float(value) for key, value in native_result.get("phase_timing_seconds", {}).items()},
        },
        "transfer_metadata": native_result.get("transfer_metadata", {}),
        "claim_boundary": {
            "ssb_sf1_q11_same_input_grouped_rows_claimed": True,
            "all_13_ssb_sf1_queries_claimed": False,
            "exact_paper_input_claimed": False,
            "paper_performance_claimed": False,
            "author_algorithm_equivalence_claimed": False,
            "true_zero_copy_claimed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run RayDB SSB SF1 Q1.1 through generic RTDL packed OptiX primitives")
    parser.add_argument("--packet-json", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--predicate", type=Path, required=True)
    parser.add_argument("--expected-rows", type=Path, required=True)
    parser.add_argument("--author-result", type=Path)
    parser.add_argument(
        "--prepared-ray-batch",
        action="store_true",
        help="Prepare query rays once on device before the measured grouped reduction call",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_q11_rtdl(
        args.packet_json,
        args.data,
        args.predicate,
        args.expected_rows,
        author_result_path=args.author_result,
        prepared_ray_batch=args.prepared_ray_batch,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["rtdl_matches_oracle"] and result["author_matches_rtdl"] is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
