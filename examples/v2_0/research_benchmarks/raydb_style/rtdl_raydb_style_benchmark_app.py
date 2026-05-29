from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time
import statistics
from typing import Any

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt

CPU_RESULT_MODES = ("count", "sum", "min", "max", "avg_as_sum_count")
EMBREE_RESULT_MODES = ("count", "sum")
OPTIX_RESULT_MODES = ("count", "sum")
OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND = "optix_partner_resident_experimental"
OPTIX_PARTNER_RESIDENT_RESULT_MODES = ("count", "sum", "min", "max", "avg_as_sum_count")
PAPER_RT_CPU_REFERENCE_BACKEND = "paper_rt_cpu_reference"
PAPER_RT_EMBREE_BACKEND = "paper_rt_embree"
PAPER_RT_OPTIX_BACKEND = "paper_rt_optix"
PAPER_RT_EMBREE_HIT_STREAM_TRITON_BACKEND = "paper_rt_embree_hit_stream_triton"
PAPER_RT_OPTIX_HIT_STREAM_TRITON_BACKEND = "paper_rt_optix_hit_stream_triton"
PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND = "paper_rt_optix_device_hit_stream_triton"
PAPER_RT_RESULT_MODES = CPU_RESULT_MODES
RAYDB_REFERENCE_REPO = "https://github.com/rubaolee/RayDB-i0"
RAYDB_REFERENCE_BRANCH = "fin"
RAYDB_REFERENCE_COMMIT = "a610c00d7334d8907435cc0a124f9ca8392ee456"
GENERIC_RAY_TRIANGLE_GROUPED_REDUCTION_3D_SYMBOL = (
    "generic_ray_triangle_primitive_grouped_i64_reduction_3d"
)
GENERIC_RAY_TRIANGLE_GROUPED_REDUCTION_3D_PREPARED_PRIMITIVE = (
    "ray_triangle_grouped_i64_reduction_3d"
)
RAYDB_V2_5_CONTINUATION_STATUS_DESCRIPTOR_ONLY = "descriptor_only_pending_cuda_integration"
RAYDB_V2_5_CONTINUATION_STATUS_ADAPTER_FRONT_DOOR_PREVIEW = (
    "adapter_front_door_preview_not_promoted"
)
RAYDB_V2_5_CONTINUATION_STATUS_BLOCKED = "blocked_missing_v2_5_partner_operation"
BACKENDS = (
    "cpu_python_reference",
    "embree",
    "optix",
    OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,
    PAPER_RT_CPU_REFERENCE_BACKEND,
    PAPER_RT_EMBREE_BACKEND,
    PAPER_RT_OPTIX_BACKEND,
    PAPER_RT_EMBREE_HIT_STREAM_TRITON_BACKEND,
    PAPER_RT_OPTIX_HIT_STREAM_TRITON_BACKEND,
    PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND,
)
RESULT_MODES = CPU_RESULT_MODES
DEFAULT_GENERATED_ROW_COUNT = 100_000
DEFAULT_GENERATED_GROUP_COUNT = 128
DEFAULT_GENERATED_REVENUE_MOD = 64


def make_fixture(copies: int = 1) -> dict[str, Any]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    base = {
        "row_ids": (1, 2, 3, 4, 5, 6, 7, 8),
        "columns": {
            "region_id": (0, 1, 0, 1, 2, 2, 1, 0),
            "ship_year": (1994, 1994, 1995, 1996, 1994, 1995, 1995, 1994),
            "discount": (5, 6, 3, 5, 7, 4, 5, 6),
            "quantity": (10, 20, 15, 9, 30, 18, 28, 12),
            "revenue": (100, 200, 150, 50, 300, 80, 120, 90),
        },
    }
    if copies == 1:
        return base
    row_count = len(base["row_ids"])
    row_ids: list[int] = []
    columns: dict[str, list[int]] = {name: [] for name in base["columns"]}
    for copy_index in range(copies):
        offset = copy_index * row_count
        row_ids.extend(offset + int(row_id) for row_id in base["row_ids"])
        for name, values in base["columns"].items():
            columns[name].extend(int(value) for value in values)
    return {
        "row_ids": tuple(row_ids),
        "columns": {name: tuple(values) for name, values in columns.items()},
    }


def make_generated_fixture(
    row_count: int = DEFAULT_GENERATED_ROW_COUNT,
    *,
    group_count: int = DEFAULT_GENERATED_GROUP_COUNT,
    revenue_mod: int = DEFAULT_GENERATED_REVENUE_MOD,
    ship_year_mod: int = 64,
    discount_mod: int = 16,
    quantity_mod: int = 64,
) -> dict[str, Any]:
    """Build a deterministic higher-diversity RayDB-style fixture.

    `make_fixture(copies=...)` intentionally repeats 8 base rows. That is a
    good regression fixture but a poor RT-core stressor because it collapses
    millions of triangles onto very few coordinates. This fixture keeps the
    same schema and query contract while spreading rows across many groups,
    predicate tuples, and aggregate values.
    """
    if row_count <= 0:
        raise ValueError("row_count must be positive")
    for name, value in (
        ("group_count", group_count),
        ("revenue_mod", revenue_mod),
        ("ship_year_mod", ship_year_mod),
        ("discount_mod", discount_mod),
        ("quantity_mod", quantity_mod),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - local fallback for minimal Python envs.
        row_ids = tuple(range(1, row_count + 1))
        indices = tuple(range(row_count))
        return {
            "row_ids": row_ids,
            "columns": {
                "region_id": tuple((index * 17 + index // 97) % group_count for index in indices),
                "ship_year": tuple(1990 + ((index * 7 + index // 13) % ship_year_mod) for index in indices),
                "discount": tuple(1 + ((index * 5 + index // 17) % discount_mod) for index in indices),
                "quantity": tuple(1 + ((index * 11 + index // 23) % quantity_mod) for index in indices),
                "revenue": tuple(1 + ((index * 13 + index // 29) % revenue_mod) for index in indices),
            },
            "fixture_kind": "generated_deterministic",
            "generation": {
                "row_count": int(row_count),
                "group_count": int(group_count),
                "revenue_mod": int(revenue_mod),
                "ship_year_mod": int(ship_year_mod),
                "discount_mod": int(discount_mod),
                "quantity_mod": int(quantity_mod),
            },
        }

    indices = np.arange(row_count, dtype=np.int64)
    return {
        "row_ids": np.arange(1, row_count + 1, dtype=np.int64),
        "columns": {
            "region_id": ((indices * 17 + indices // 97) % int(group_count)).astype(np.int64, copy=False),
            "ship_year": (1990 + ((indices * 7 + indices // 13) % int(ship_year_mod))).astype(np.int64, copy=False),
            "discount": (1 + ((indices * 5 + indices // 17) % int(discount_mod))).astype(np.int64, copy=False),
            "quantity": (1 + ((indices * 11 + indices // 23) % int(quantity_mod))).astype(np.int64, copy=False),
            "revenue": (1 + ((indices * 13 + indices // 29) % int(revenue_mod))).astype(np.int64, copy=False),
        },
        "fixture_kind": "generated_deterministic",
        "generation": {
            "row_count": int(row_count),
            "group_count": int(group_count),
            "revenue_mod": int(revenue_mod),
            "ship_year_mod": int(ship_year_mod),
            "discount_mod": int(discount_mod),
            "quantity_mod": int(quantity_mod),
        },
    }


def make_benchmark_fixture(
    *,
    fixture_kind: str = "repeated",
    copies: int = 1,
    generated_rows: int = DEFAULT_GENERATED_ROW_COUNT,
    generated_groups: int = DEFAULT_GENERATED_GROUP_COUNT,
    generated_revenue_mod: int = DEFAULT_GENERATED_REVENUE_MOD,
) -> dict[str, Any]:
    if fixture_kind == "repeated":
        fixture = make_fixture(copies=copies)
        return {
            **fixture,
            "fixture_kind": "tiny_repeated",
            "generation": {"copies": int(copies), "base_rows": 8},
        }
    if fixture_kind == "generated":
        return make_generated_fixture(
            row_count=generated_rows,
            group_count=generated_groups,
            revenue_mod=generated_revenue_mod,
        )
    raise ValueError("fixture_kind must be 'repeated' or 'generated'")


def make_plan(mode: str) -> dict[str, Any]:
    if mode not in RESULT_MODES:
        raise ValueError(f"unsupported result mode: {mode}")
    plan: dict[str, Any] = {
        "predicates": (
            ("ship_year", "between", 1994, 1995),
            ("discount", "between", 4, 6),
            ("quantity", "lt", 25),
        ),
        "group_keys": ("region_id",),
        "aggregate": mode,
    }
    if mode != "count":
        plan["value_field"] = "revenue"
    return plan


def run_result_mode(
    mode: str,
    *,
    backend: str = "cpu_python_reference",
    copies: int = 1,
    repeat: int = 1,
    warmup: int = 0,
    fixture_kind: str = "repeated",
    generated_rows: int = DEFAULT_GENERATED_ROW_COUNT,
    generated_groups: int = DEFAULT_GENERATED_GROUP_COUNT,
    generated_revenue_mod: int = DEFAULT_GENERATED_REVENUE_MOD,
) -> dict[str, Any]:
    if repeat <= 0:
        raise ValueError("repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    fixture = make_benchmark_fixture(
        fixture_kind=fixture_kind,
        copies=copies,
        generated_rows=generated_rows,
        generated_groups=generated_groups,
        generated_revenue_mod=generated_revenue_mod,
    )
    plan = make_plan(mode)
    if backend == PAPER_RT_CPU_REFERENCE_BACKEND:
        return _run_paper_rt_cpu_reference_result_mode(
            fixture=fixture,
            plan=plan,
            mode=mode,
            copies=copies,
        )
    if backend == PAPER_RT_EMBREE_BACKEND:
        return _run_paper_rt_native_result_mode(
            fixture=fixture,
            plan=plan,
            mode=mode,
            copies=copies,
            backend="embree",
            backend_label=PAPER_RT_EMBREE_BACKEND,
        )
    if backend == PAPER_RT_OPTIX_BACKEND:
        return _run_paper_rt_native_result_mode(
            fixture=fixture,
            plan=plan,
            mode=mode,
            copies=copies,
            backend="optix",
            backend_label=PAPER_RT_OPTIX_BACKEND,
        )
    if backend == PAPER_RT_EMBREE_HIT_STREAM_TRITON_BACKEND:
        return _run_paper_rt_hit_stream_triton_result_mode(
            fixture=fixture,
            plan=plan,
            mode=mode,
            copies=copies,
            backend="embree",
            backend_label=PAPER_RT_EMBREE_HIT_STREAM_TRITON_BACKEND,
        )
    if backend == PAPER_RT_OPTIX_HIT_STREAM_TRITON_BACKEND:
        return _run_paper_rt_hit_stream_triton_result_mode(
            fixture=fixture,
            plan=plan,
            mode=mode,
            copies=copies,
            backend="optix",
            backend_label=PAPER_RT_OPTIX_HIT_STREAM_TRITON_BACKEND,
        )
    if backend == PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND:
        return _run_paper_rt_device_hit_stream_triton_result_mode(
            fixture=fixture,
            plan=plan,
            mode=mode,
            copies=copies,
            backend="optix",
            backend_label=PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND,
        )
    if backend == "embree":
        return _run_native_result_mode(
            backend="embree",
            fixture=fixture,
            plan=plan,
            mode=mode,
            prepare_dataset=rt.prepare_embree_columnar_record_set,
            result_modes=EMBREE_RESULT_MODES,
            contract="columnar_grouped_aggregate_embree_columnar_payload",
            rt_core_accelerated=False,
            copies=copies,
        )
    if backend == "optix":
        return _run_native_result_mode(
            backend="optix",
            fixture=fixture,
            plan=plan,
            mode=mode,
            prepare_dataset=rt.prepare_optix_columnar_record_set,
            result_modes=OPTIX_RESULT_MODES,
            contract="columnar_grouped_aggregate_optix_columnar_payload",
            rt_core_accelerated=False,
            copies=copies,
        )
    if backend == OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND:
        return _run_optix_partner_resident_experimental_result_mode(
            fixture=fixture,
            plan=plan,
            mode=mode,
            copies=copies,
            repeat=repeat,
            warmup=warmup,
        )
    if backend != "cpu_python_reference":
        raise ValueError(f"unsupported backend: {backend}")
    started = time.perf_counter()
    result = rt.evaluate_columnar_grouped_aggregate(fixture, plan)
    elapsed_sec = time.perf_counter() - started
    lowering_plan = rt.plan_columnar_aggregate_lowering(backend).to_dict()
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": elapsed_sec,
        "rows": list(result.rows),
        "metadata": {
            **result.metadata,
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {"cpu_reference_sec": elapsed_sec},
            **_fixture_metadata(fixture),
            "lowering_plan": lowering_plan,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "rt_core_accelerated": False,
            "claim_boundary": (
                "RayDB-style CPU reference fixture only. This validates a generic "
                "columnar grouped aggregate contract; it does not reproduce RayDB, "
                "time authors code, or authorize performance wording."
            ),
        },
    }


def _predicate_accepts(value: int, predicate: tuple[Any, ...]) -> bool:
    operator, *bounds = predicate
    if operator == "between":
        low, high = bounds
        return int(low) <= int(value) <= int(high)
    if operator == "lt":
        (limit,) = bounds
        return int(value) < int(limit)
    raise ValueError(f"unsupported predicate operator for paper RT reference: {operator}")


def _fixture_records(fixture: dict[str, Any]) -> tuple[dict[str, int], ...]:
    row_ids = tuple(int(row_id) for row_id in fixture["row_ids"])
    columns = fixture["columns"]
    return tuple(
        {
            "row_id": row_id,
            **{name: int(values[index]) for name, values in columns.items()},
        }
        for index, row_id in enumerate(row_ids)
    )


def _record_matches_plan(record: dict[str, int], plan: dict[str, Any]) -> bool:
    return all(_predicate_accepts(record[field], predicate) for field, *predicate in plan["predicates"])


def _dense_value_maps(
    records: tuple[dict[str, int], ...],
    fields: tuple[str, ...],
) -> dict[str, dict[int, int]]:
    return {
        field: {value: ordinal for ordinal, value in enumerate(sorted({int(record[field]) for record in records}))}
        for field in fields
    }


def _mixed_radix_multipliers(value_maps: dict[str, dict[int, int]], fields: tuple[str, ...]) -> dict[str, int]:
    multiplier = 1
    multipliers: dict[str, int] = {}
    for field in reversed(fields):
        multipliers[field] = multiplier
        multiplier *= max(1, len(value_maps[field]))
    return multipliers


def _encode_scan_value(
    record: dict[str, int],
    *,
    fields: tuple[str, ...],
    value_maps: dict[str, dict[int, int]],
    multipliers: dict[str, int],
) -> int:
    return sum(value_maps[field][int(record[field])] * multipliers[field] for field in fields)


def _make_paper_rt_encoded_workload(
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    *,
    sx: float = 1.0,
    sy: float = 1.0,
    z_bias: float = 0.25,
) -> dict[str, Any]:
    if sx <= 0.0 or sy <= 0.0 or z_bias <= 0.0:
        raise ValueError("sx, sy, and z_bias must be positive")
    if mode not in PAPER_RT_RESULT_MODES:
        raise ValueError(f"unsupported paper RT result mode: {mode}")

    records = _fixture_records(fixture)
    scan_fields = tuple(str(predicate[0]) for predicate in plan["predicates"])
    group_keys = tuple(str(field) for field in plan["group_keys"])
    if len(group_keys) != 1:
        raise ValueError("paper RT reference currently supports one dense group key")

    scan_value_maps = _dense_value_maps(records, scan_fields)
    scan_multipliers = _mixed_radix_multipliers(scan_value_maps, scan_fields)
    group_tuples = sorted({tuple(int(record[field]) for field in group_keys) for record in records})
    group_to_id = {group_tuple: index for index, group_tuple in enumerate(group_tuples)}
    matched_scan_values = sorted(
        {
            _encode_scan_value(
                record,
                fields=scan_fields,
                value_maps=scan_value_maps,
                multipliers=scan_multipliers,
            )
            for record in records
            if _record_matches_plan(record, plan)
        }
    )

    primitive_records: list[dict[str, Any]] = []
    triangles: list[rt.Triangle3D] = []
    for record in records:
        group_tuple = tuple(int(record[field]) for field in group_keys)
        group_id = group_to_id[group_tuple]
        scan_z = _encode_scan_value(
            record,
            fields=scan_fields,
            value_maps=scan_value_maps,
            multipliers=scan_multipliers,
        )
        aggregate_value = 1 if mode == "count" else int(record[plan["value_field"]])
        x_coord = float(aggregate_value)
        y_coord = float(group_id)
        z_coord = float(scan_z)
        row_id = int(record["row_id"])
        primitive = {
            "row_id": row_id,
            "group_id": group_id,
            "group_tuple": group_tuple,
            "scan_z": scan_z,
            "aggregate_value": aggregate_value,
            "x_coord": x_coord,
            "y_coord": y_coord,
            "record": record,
        }
        primitive_records.append(primitive)
        triangles.append(
            rt.Triangle3D(
                id=row_id,
                x0=x_coord,
                y0=y_coord,
                z0=z_coord,
                x1=x_coord + sx,
                y1=y_coord,
                z1=z_coord,
                x2=x_coord,
                y2=y_coord + sy,
                z2=z_coord,
            )
        )

    if primitive_records:
        interval_x = sx / 2.0
        interval_y = sy / 2.0
        min_x = min(float(primitive["x_coord"]) for primitive in primitive_records)
        max_x = max(float(primitive["x_coord"]) for primitive in primitive_records) + sx
        x_count = int(math.floor((max_x - min_x) / interval_x)) + 1
        y_count = max(1, len(group_tuples) * 2)
    else:
        interval_x = sx / 2.0
        interval_y = sy / 2.0
        min_x = 0.0
        x_count = 0
        y_count = 0

    rays: list[rt.Ray3D] = []
    ray_id = 0
    for scan_z in matched_scan_values:
        for y_index in range(y_count):
            y_coord = (y_index + 1) * interval_y
            for x_index in range(x_count):
                rays.append(
                    rt.Ray3D(
                        id=ray_id,
                        ox=min_x + x_index * interval_x,
                        oy=y_coord,
                        oz=float(scan_z) - z_bias,
                        dx=0.0,
                        dy=0.0,
                        dz=1.0,
                        tmax=2.0 * z_bias,
                    )
                )
                ray_id += 1

    return {
        "scan_fields": scan_fields,
        "scan_value_maps": scan_value_maps,
        "scan_multipliers": scan_multipliers,
        "group_keys": group_keys,
        "group_tuples": tuple(group_tuples),
        "query_scan_values": tuple(matched_scan_values),
        "primitive_records": tuple(primitive_records),
        "triangles": tuple(triangles),
        "rays": tuple(rays),
        "sx": sx,
        "sy": sy,
        "z_bias": z_bias,
        "min_x": min_x,
        "interval_x": interval_x,
        "interval_y": interval_y,
        "x_count": x_count,
        "y_count": y_count,
    }


def _dense_numpy_codes_and_map(values: Any, *, dtype: Any) -> tuple[dict[int, int], Any]:
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        raise RuntimeError("packed RayDB paper RT workload requires numpy")

    unique_values, inverse = np.unique(np.asarray(values), return_inverse=True)
    mapping = {int(value): int(index) for index, value in enumerate(unique_values.tolist())}
    return mapping, inverse.astype(dtype, copy=False)


def prepare_paper_rt_encoded_table_descriptor(
    fixture: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    """Prepare RayDB-owned table encoding reused by multiple RTDL queries.

    This is intentionally app-level lowering, not an RTDL engine primitive. It
    computes dense scan/group encodings once, then hands mode-specific typed
    buffers to the generic ray/triangle grouped reduction primitive.
    """
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("prepared RayDB table descriptor requires numpy") from exc

    row_ids = np.asarray(fixture["row_ids"], dtype=np.uint32)
    row_count = int(len(row_ids))
    columns = {name: np.asarray(values) for name, values in fixture["columns"].items()}
    scan_fields = tuple(str(predicate[0]) for predicate in plan["predicates"])
    group_keys = tuple(str(field) for field in plan["group_keys"])
    if len(group_keys) != 1:
        raise ValueError("paper RT table descriptor currently supports one dense group key")

    scan_value_maps: dict[str, dict[int, int]] = {}
    scan_dense_codes: dict[str, Any] = {}
    for field in scan_fields:
        scan_value_maps[field], scan_dense_codes[field] = _dense_numpy_codes_and_map(
            columns[field],
            dtype=np.int64,
        )
    scan_multipliers = _mixed_radix_multipliers(scan_value_maps, scan_fields)
    scan_z = np.zeros(row_count, dtype=np.int64)
    for field in scan_fields:
        scan_z += scan_dense_codes[field] * int(scan_multipliers[field])

    match_mask = np.ones(row_count, dtype=bool)
    for field, *predicate in plan["predicates"]:
        operator, *bounds = predicate
        values = columns[str(field)].astype(np.int64, copy=False)
        if operator == "between":
            low, high = bounds
            match_mask &= (values >= int(low)) & (values <= int(high))
        elif operator == "lt":
            (limit,) = bounds
            match_mask &= values < int(limit)
        else:
            raise ValueError(f"unsupported predicate operator for paper RT reference: {operator}")
    matched_scan_values = tuple(int(value) for value in np.unique(scan_z[match_mask]).tolist())

    group_key = group_keys[0]
    group_values = columns[group_key].astype(np.int64, copy=False)
    group_to_id, group_ids = _dense_numpy_codes_and_map(group_values, dtype=np.uint32)
    group_tuples = tuple((value,) for value in group_to_id)

    return {
        "contract": "RAYDB_APP_PREPARED_ENCODED_TABLE_DESCRIPTOR_V1",
        "row_ids": row_ids,
        "row_count": row_count,
        "columns": columns,
        "scan_fields": scan_fields,
        "scan_value_maps": scan_value_maps,
        "scan_multipliers": scan_multipliers,
        "scan_z": scan_z,
        "match_mask": match_mask,
        "query_scan_values": matched_scan_values,
        "group_keys": group_keys,
        "group_to_id": group_to_id,
        "group_ids": group_ids,
        "group_tuples": group_tuples,
        "app_owned_descriptor": True,
        "engine_boundary": (
            "RayDB table encoding is app-owned. RTDL native execution receives only "
            "generic typed rays, triangles, group ids, payload values, and reductions."
        ),
    }


def _make_paper_rt_encoded_packed_workload(
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    *,
    sx: float = 1.0,
    sy: float = 1.0,
    z_bias: float = 0.25,
    table_descriptor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the RayDB paper shape with typed buffers instead of Python objects."""
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        workload = _make_paper_rt_encoded_workload(fixture, plan, mode, sx=sx, sy=sy, z_bias=z_bias)
        return {
            **workload,
            "primitive_group_ids": tuple(int(primitive["group_id"]) for primitive in workload["primitive_records"]),
            "primitive_values": tuple(int(primitive["aggregate_value"]) for primitive in workload["primitive_records"]),
            "packed_host_buffers": False,
        }
    if sx <= 0.0 or sy <= 0.0 or z_bias <= 0.0:
        raise ValueError("sx, sy, and z_bias must be positive")
    if mode not in PAPER_RT_RESULT_MODES:
        raise ValueError(f"unsupported paper RT result mode: {mode}")

    if table_descriptor is None:
        table_descriptor = prepare_paper_rt_encoded_table_descriptor(fixture, plan)
    row_ids = table_descriptor["row_ids"]
    row_count = int(table_descriptor["row_count"])
    columns = table_descriptor["columns"]
    scan_fields = tuple(table_descriptor["scan_fields"])
    group_keys = tuple(table_descriptor["group_keys"])
    if scan_fields != tuple(str(predicate[0]) for predicate in plan["predicates"]):
        raise ValueError("table descriptor scan fields do not match plan")
    if group_keys != tuple(str(field) for field in plan["group_keys"]):
        raise ValueError("table descriptor group keys do not match plan")
    scan_value_maps = table_descriptor["scan_value_maps"]
    scan_multipliers = table_descriptor["scan_multipliers"]
    scan_z = table_descriptor["scan_z"]
    matched_scan_values = tuple(int(value) for value in table_descriptor["query_scan_values"])
    group_ids = table_descriptor["group_ids"]
    group_tuples = tuple(table_descriptor["group_tuples"])
    aggregate_values = (
        np.ones(row_count, dtype=np.uint64)
        if mode == "count"
        else columns[str(plan["value_field"])].astype(np.uint64, copy=False)
    )

    x0 = aggregate_values.astype(np.float64)
    y0 = group_ids.astype(np.float64)
    z0 = scan_z.astype(np.float64)
    triangles = rt.pack_triangles_3d_from_arrays(
        row_ids,
        x0,
        y0,
        z0,
        x0 + float(sx),
        y0,
        z0,
        x0,
        y0 + float(sy),
        z0,
    )

    if row_count:
        interval_x = sx / 2.0
        interval_y = sy / 2.0
        min_x = float(x0.min())
        max_x = float(x0.max()) + sx
        x_count = int(math.floor((max_x - min_x) / interval_x)) + 1
        y_count = max(1, len(group_tuples) * 2)
    else:
        interval_x = sx / 2.0
        interval_y = sy / 2.0
        min_x = 0.0
        x_count = 0
        y_count = 0

    if matched_scan_values and x_count and y_count:
        xs = min_x + np.arange(x_count, dtype=np.float64) * interval_x
        ys = (np.arange(y_count, dtype=np.float64) + 1.0) * interval_y
        grid_y, grid_x = np.meshgrid(ys, xs, indexing="ij")
        base_ox = grid_x.ravel()
        base_oy = grid_y.ravel()
        base_count = len(base_ox)
        scan_array = np.asarray(matched_scan_values, dtype=np.float64)
        ox = np.tile(base_ox, len(scan_array))
        oy = np.tile(base_oy, len(scan_array))
        oz = np.repeat(scan_array - float(z_bias), base_count)
        ray_count = len(ox)
        rays = rt.pack_rays_3d_from_arrays(
            np.arange(ray_count, dtype=np.uint32),
            ox,
            oy,
            oz,
            np.zeros(ray_count, dtype=np.float64),
            np.zeros(ray_count, dtype=np.float64),
            np.ones(ray_count, dtype=np.float64),
            np.full(ray_count, 2.0 * float(z_bias), dtype=np.float64),
        )
    else:
        rays = rt.pack_rays_3d_from_arrays((), (), (), (), (), (), (), ())

    return {
        "scan_fields": scan_fields,
        "scan_value_maps": scan_value_maps,
        "scan_multipliers": scan_multipliers,
        "group_keys": group_keys,
        "group_tuples": group_tuples,
        "query_scan_values": matched_scan_values,
        "primitive_group_ids": group_ids,
        "primitive_values": aggregate_values,
        "triangles": triangles,
        "rays": rays,
        "sx": sx,
        "sy": sy,
        "z_bias": z_bias,
        "min_x": min_x,
        "interval_x": interval_x,
        "interval_y": interval_y,
        "x_count": x_count,
        "y_count": y_count,
        "packed_host_buffers": True,
        "prepared_table_descriptor_used": bool(table_descriptor.get("app_owned_descriptor", False)),
        "table_descriptor_contract": table_descriptor.get("contract"),
    }


def _make_paper_rt_partner_ray_columns(
    workload: dict[str, Any],
    *,
    partner: str = "triton",
) -> dict[str, Any]:
    """Build RayDB paper query rays as partner-owned device columns.

    The app still owns RayDB predicate-to-ray-grid semantics. The runtime only
    receives generic 3-D ray columns. In v2.5, `partner="triton"` uses CUDA
    Torch tensors only as the launch carrier; Torch is not the app partner.
    """
    x_count = int(workload.get("x_count", 0))
    y_count = int(workload.get("y_count", 0))
    scan_values = tuple(int(value) for value in workload.get("query_scan_values", ()))
    if partner == "cupy":
        try:
            import cupy as cp
        except ImportError as exc:  # pragma: no cover - pod-only optional dependency
            raise RuntimeError("CuPy is required for partner-owned paper RT query ray columns") from exc

        if not scan_values or x_count <= 0 or y_count <= 0:
            empty_f64 = cp.asarray((), dtype=cp.float64)
            return {
                "ids": cp.asarray((), dtype=cp.uint32),
                "ox": empty_f64,
                "oy": empty_f64,
                "oz": empty_f64,
                "dx": empty_f64,
                "dy": empty_f64,
                "dz": empty_f64,
                "tmax": empty_f64,
            }

        xs = float(workload.get("min_x", 0.0)) + float(workload["interval_x"]) * cp.arange(x_count, dtype=cp.float64)
        ys = (cp.arange(y_count, dtype=cp.float64) + 1.0) * float(workload["interval_y"])
        grid_y, grid_x = cp.meshgrid(ys, xs, indexing="ij")
        base_ox = grid_x.ravel()
        base_oy = grid_y.ravel()
        base_count = int(base_ox.shape[0])
        scan_array = cp.asarray(scan_values, dtype=cp.float64)
        ox = cp.tile(base_ox, len(scan_values))
        oy = cp.tile(base_oy, len(scan_values))
        oz = cp.repeat(scan_array - float(workload["z_bias"]), base_count)
        ray_count = int(ox.shape[0])
        return {
            "ids": cp.arange(ray_count, dtype=cp.uint32),
            "ox": ox,
            "oy": oy,
            "oz": oz,
            "dx": cp.zeros(ray_count, dtype=cp.float64),
            "dy": cp.zeros(ray_count, dtype=cp.float64),
            "dz": cp.ones(ray_count, dtype=cp.float64),
            "tmax": cp.full(ray_count, 2.0 * float(workload["z_bias"]), dtype=cp.float64),
        }
    if partner in {"triton", "torch"}:
        try:
            import torch
        except ImportError as exc:  # pragma: no cover - pod-only optional dependency
            raise RuntimeError("Triton RayDB paper RT query columns require a CUDA tensor carrier") from exc
        if not torch.cuda.is_available():
            raise RuntimeError("Triton RayDB paper RT query columns require CUDA")
        device = torch.device("cuda:0")
        if not scan_values or x_count <= 0 or y_count <= 0:
            empty_f64 = torch.empty((0,), dtype=torch.float64, device=device)
            return {
                "ids": torch.empty((0,), dtype=torch.uint32, device=device),
                "ox": empty_f64,
                "oy": empty_f64,
                "oz": empty_f64,
                "dx": empty_f64,
                "dy": empty_f64,
                "dz": empty_f64,
                "tmax": empty_f64,
            }

        xs = float(workload.get("min_x", 0.0)) + float(workload["interval_x"]) * torch.arange(
            x_count, dtype=torch.float64, device=device
        )
        ys = (torch.arange(y_count, dtype=torch.float64, device=device) + 1.0) * float(workload["interval_y"])
        grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")
        base_ox = grid_x.reshape(-1).contiguous()
        base_oy = grid_y.reshape(-1).contiguous()
        base_count = int(base_ox.shape[0])
        scan_array = torch.tensor(scan_values, dtype=torch.float64, device=device)
        ox = base_ox.repeat(len(scan_values)).contiguous()
        oy = base_oy.repeat(len(scan_values)).contiguous()
        oz = (scan_array - float(workload["z_bias"])).repeat_interleave(base_count).contiguous()
        ray_count = int(ox.shape[0])
        return {
            "ids": torch.arange(ray_count, dtype=torch.int64, device=device).to(torch.uint32),
            "ox": ox,
            "oy": oy,
            "oz": oz,
            "dx": torch.zeros(ray_count, dtype=torch.float64, device=device),
            "dy": torch.zeros(ray_count, dtype=torch.float64, device=device),
            "dz": torch.ones(ray_count, dtype=torch.float64, device=device),
            "tmax": torch.full((ray_count,), 2.0 * float(workload["z_bias"]), dtype=torch.float64, device=device),
        }
    raise ValueError("paper RT partner ray columns currently support partner='triton', 'cupy', or 'torch'")


def describe_paper_rt_v2_4_prepared_session(
    workload: dict[str, Any],
    *,
    backend: str,
    mode: str,
) -> dict[str, Any]:
    """Describe the RayDB-shaped prepared path with generic v2.4 descriptors.

    The descriptor is intentionally protocol-only. It records the generic
    ray/triangle grouped-reduction buffers that RTDL sees, while RayDB predicate
    encoding and result interpretation stay app-owned.
    """

    normalized_backend = str(backend).strip().lower()
    if normalized_backend not in {"embree", "optix"}:
        raise ValueError("v2.4 RayDB prepared-session descriptor supports embree or optix")
    native_symbol = (
        "rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction"
        if normalized_backend == "embree"
        else "rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction"
    )
    session = rt.RtdlPreparedSessionDescriptor(
        session_id=f"generic_ray_triangle_grouped_i64_reduction_3d_{normalized_backend}_{mode}",
        backend=normalized_backend,
        primitive=GENERIC_RAY_TRIANGLE_GROUPED_REDUCTION_3D_PREPARED_PRIMITIVE,
        input_buffers=(
            _v2_4_packed_buffer_descriptor("rays", workload["rays"]),
            _v2_4_packed_buffer_descriptor("triangles", workload["triangles"]),
            _v2_4_array_buffer_descriptor("primitive_group_ids", workload["primitive_group_ids"], fallback_dtype="uint32"),
            _v2_4_array_buffer_descriptor("primitive_values", workload["primitive_values"], fallback_dtype="uint64"),
        ),
        reusable_scene=True,
        reusable_query_buffers=True,
        reusable_output_buffers=False,
        phase_contract="prepared_query",
        native_symbols=(native_symbol,),
    )
    return {
        **session.to_metadata(),
        "v2_4_protocol_version": rt.V2_4_PARTNER_PROTOCOL_VERSION,
        "performance_basis_hardware": rt.V2_4_PERFORMANCE_BASIS_HARDWARE,
        "same_phase_contract_as_basis_required": True,
        "protocol_overhead_audit_required": False,
        "descriptor_only": True,
        "app_owned_lowering": (
            "RayDB predicate/group encoding remains Python app code. RTDL sees only "
            "generic rays, triangles, primitive group ids, primitive values, and a reduction."
        ),
    }


def describe_raydb_v2_5_partner_continuation(mode: str) -> dict[str, Any]:
    """Describe RayDB's post-RT v2.5 continuation without claiming promotion.

    RayDB-specific predicate encoding remains app code. The continuation plan
    records only generic grouped operations that can run after RT traversal has
    produced group ids and payload values.
    """

    if mode not in PAPER_RT_RESULT_MODES:
        raise ValueError(f"unsupported paper RT result mode: {mode}")

    if mode == "count":
        operations = ("segmented_count_i64",)
    elif mode == "sum":
        operations = ("segmented_sum_f64",)
    elif mode == "min":
        operations = ("segmented_min_f64",)
    elif mode == "max":
        operations = ("segmented_max_f64",)
    elif mode == "avg_as_sum_count":
        operations = ("segmented_sum_f64", "segmented_count_i64")
    else:
        operations = ()

    status = (
        RAYDB_V2_5_CONTINUATION_STATUS_ADAPTER_FRONT_DOOR_PREVIEW
        if operations
        else RAYDB_V2_5_CONTINUATION_STATUS_BLOCKED
    )
    triton_descriptors = []
    numba_descriptors = []
    for operation in operations:
        triton_descriptors.append(rt.describe_triton_partner_continuation(operation))
        if operation == "segmented_count_i64":
            numba_descriptors.append(rt.describe_numba_segmented_count_i64())
        elif operation == "segmented_sum_f64":
            numba_descriptors.append(rt.describe_numba_segmented_sum_f64())
        else:
            numba_descriptors.append(
                rt.RtdlPartnerContinuationSpec(
                    operation=operation,
                    partner="numba",
                    status=rt.V2_5_STATUS_PARTNER_DESCRIPTOR_ONLY,
                ).to_metadata()
            )

    return {
        "contract_version": rt.V2_5_PARTNER_CONTINUATION_VERSION,
        "status": status,
        "mode": mode,
        "operations": operations,
        "preferred_partner": "triton",
        "fallback_partner": "numba",
        "continuation_phase": "partner_continuation",
        "post_rt_continuation_only": True,
        "replaces_rt_traversal": False,
        "promoted_performance_path": False,
        "rt_core_speedup_claim_authorized": False,
        "raw_kernel_required": False,
        "uses_cupy_partner": False,
        "uses_pytorch_partner": False,
        "tensor_carrier": rt.TRITON_TENSOR_CARRIER,
        "tensor_carrier_is_partner": False,
        "triton_executable_preview_available": bool(operations) and all(
            operation in rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS
            for operation in operations
        ),
        "adapter_front_door_integrated": bool(operations),
        "benchmark_path_integrated": bool(operations),
        "descriptor_only": False,
        "front_door_api": (
            "partner_group_count_by_key",
            "partner_group_sum_by_key",
            "partner_group_min_by_key",
            "partner_group_max_by_key",
        ),
        "triton_descriptors": tuple(triton_descriptors),
        "numba_descriptors": tuple(numba_descriptors),
        "blocked_reason": (
            "unsupported RayDB mode"
            if not operations
            else None
        ),
        "app_owned_lowering": (
            "RayDB predicate encoding and result interpretation remain app code. "
            "The v2.5 partner continuation sees only group ids and numeric values."
        ),
    }


def _run_raydb_v2_5_reference_fallback(
    mode: str,
    inputs: dict[str, Any],
    *,
    operations: tuple[str, ...],
    block_size: int,
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    _ = block_size
    results = tuple(
        rt.execute_v2_5_partner_continuation_reference(
            operation,
            inputs,
        )
        for operation in operations
    )
    outputs: dict[str, Any] = {}
    for result in results:
        outputs.update(result["outputs"])
    return outputs, results


def _raydb_v2_5_present_group_outputs(keys, group_count: int):
    import torch

    counts = rt.partner_group_count_by_key(keys, group_count, partner="triton")
    present_mask = counts.to(torch.int64) > 0
    return {
        "present_counts": counts,
        "group_ids": torch.nonzero(present_mask, as_tuple=False).reshape(-1).to(torch.int64),
        "missing_group_ids": torch.nonzero(~present_mask, as_tuple=False).reshape(-1).to(torch.int64),
        "present_mask": present_mask,
    }


def _run_raydb_v2_5_triton_front_door(
    mode: str,
    inputs: dict[str, Any],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    group_ids = inputs["group_ids"]
    group_count = int(inputs["group_count"])
    values = inputs.get("values")
    outputs: dict[str, Any]
    continuation_results: list[dict[str, Any]] = []

    if mode == "count":
        counts = rt.partner_group_count_by_key(group_ids, group_count, partner="triton")
        outputs = {"counts": counts}
        continuation_results.append(
            {"operation": "segmented_count_i64", "path": "partner_adapter_front_door", "outputs": outputs}
        )
    elif mode == "sum":
        if values is None:
            raise ValueError("RayDB v2.5 sum continuation requires values")
        sums = rt.partner_group_sum_by_key(group_ids, values, group_count, partner="triton")
        outputs = {"sums": sums}
        continuation_results.append(
            {"operation": "segmented_sum_f64", "path": "partner_adapter_front_door", "outputs": outputs}
        )
    elif mode == "min":
        if values is None:
            raise ValueError("RayDB v2.5 min continuation requires values")
        present = _raydb_v2_5_present_group_outputs(group_ids, group_count)
        dense_mins = rt.partner_group_min_by_key(
            group_ids,
            values,
            group_count,
            partner="triton",
            initial=math.inf,
        )
        outputs = {
            "group_ids": present["group_ids"],
            "mins": dense_mins[present["present_mask"]],
            "missing_group_ids": present["missing_group_ids"],
            "dense_mins": dense_mins,
            "present_counts": present["present_counts"],
        }
        continuation_results.append(
            {"operation": "segmented_min_f64", "path": "partner_adapter_front_door", "outputs": outputs}
        )
    elif mode == "max":
        if values is None:
            raise ValueError("RayDB v2.5 max continuation requires values")
        present = _raydb_v2_5_present_group_outputs(group_ids, group_count)
        dense_maxes = rt.partner_group_max_by_key(
            group_ids,
            values,
            group_count,
            partner="triton",
            initial=-math.inf,
        )
        outputs = {
            "group_ids": present["group_ids"],
            "maxes": dense_maxes[present["present_mask"]],
            "missing_group_ids": present["missing_group_ids"],
            "dense_maxes": dense_maxes,
            "present_counts": present["present_counts"],
        }
        continuation_results.append(
            {"operation": "segmented_max_f64", "path": "partner_adapter_front_door", "outputs": outputs}
        )
    elif mode == "avg_as_sum_count":
        if values is None:
            raise ValueError("RayDB v2.5 avg_as_sum_count continuation requires values")
        sums = rt.partner_group_sum_by_key(group_ids, values, group_count, partner="triton")
        counts = rt.partner_group_count_by_key(group_ids, group_count, partner="triton")
        outputs = {"sums": sums, "counts": counts}
        continuation_results.extend(
            (
                {
                    "operation": "segmented_sum_f64",
                    "path": "partner_adapter_front_door",
                    "outputs": {"sums": sums},
                },
                {
                    "operation": "segmented_count_i64",
                    "path": "partner_adapter_front_door",
                    "outputs": {"counts": counts},
                },
            )
        )
    else:
        raise ValueError(f"unsupported RayDB v2.5 continuation mode: {mode}")

    return outputs, tuple(continuation_results)


def run_raydb_v2_5_partner_continuation_preview(
    mode: str,
    inputs: dict[str, Any],
    *,
    partner: str = "triton",
    block_size: int = 256,
    allow_reference_fallback: bool = False,
) -> dict[str, Any]:
    """Run RayDB's generic v2.5 post-RT continuation preview.

    This function expects app-lowered generic inputs after RT traversal:
    `group_ids`, optional `values`, and `group_count`. It does not encode SQL
    predicates or replace RT traversal.
    """

    if partner != "triton":
        raise ValueError("RayDB v2.5 continuation preview is Triton-first; use partner='triton'")
    plan = describe_raydb_v2_5_partner_continuation(mode)
    operations = tuple(plan["operations"])
    if not operations:
        raise ValueError(f"unsupported RayDB v2.5 continuation mode: {mode}")

    if allow_reference_fallback:
        outputs, results = _run_raydb_v2_5_reference_fallback(
            mode,
            inputs,
            operations=operations,
            block_size=block_size,
        )
        execution_path = "reference_fallback"
    else:
        outputs, results = _run_raydb_v2_5_triton_front_door(mode, inputs)
        execution_path = "partner_adapter_front_door"
    return {
        "app": "raydb_style_columnar_aggregate",
        "mode": mode,
        "partner": "triton",
        "status": "preview_not_promoted",
        "operations": operations,
        "outputs": outputs,
        "continuation_results": tuple(results),
        "metadata": {
            "v2_5_partner_continuation": plan,
            "execution_path": execution_path,
            "adapter_front_door_integrated": True,
            "post_rt_continuation_only": True,
            "replaces_rt_traversal": False,
            "promoted_performance_path": False,
            "rt_core_speedup_claim_authorized": False,
            "uses_cupy_partner": False,
            "uses_pytorch_partner": False,
            "tensor_carrier": rt.TRITON_TENSOR_CARRIER,
            "tensor_carrier_is_partner": False,
        },
    }


def _v2_4_packed_buffer_descriptor(name: str, packed: Any) -> rt.RtdlBufferDescriptor:
    owner = getattr(packed, "owner", None)
    count = _packed_or_sequence_count(packed)
    dimension = int(getattr(packed, "dimension", 3))
    dtype = f"rtdl_packed_{name.rstrip('s')}_{dimension}d"
    return rt.RtdlBufferDescriptor(
        name=name,
        dtype=dtype,
        shape=(count,),
        device_type="cpu",
        data_ptr=_array_like_data_ptr(owner),
        strides_bytes=_array_like_strides(owner),
        access_mode="read",
        source_protocol="rtdl_packed_host_buffer",
        lifetime="session_retained",
        capacity_elements=count,
        owner=owner,
    )


def _v2_4_array_buffer_descriptor(
    name: str,
    values: Any,
    *,
    fallback_dtype: str,
) -> rt.RtdlBufferDescriptor:
    shape = getattr(values, "shape", None)
    if shape is None:
        shape = (len(values),)
    normalized_shape = tuple(int(dim) for dim in shape)
    dtype = str(getattr(values, "dtype", fallback_dtype))
    return rt.RtdlBufferDescriptor(
        name=name,
        dtype=dtype,
        shape=normalized_shape,
        device_type="cpu",
        data_ptr=_array_like_data_ptr(values),
        strides_bytes=_array_like_strides(values),
        access_mode="read",
        source_protocol="numpy_or_python_host",
        lifetime="session_retained",
        capacity_elements=int(math.prod(normalized_shape)) if normalized_shape else 1,
        owner=values,
    )


def _array_like_data_ptr(values: Any) -> int | None:
    interface = getattr(values, "__array_interface__", None)
    if isinstance(interface, dict):
        data = interface.get("data")
        if isinstance(data, tuple) and data:
            return int(data[0])
    return None


def _array_like_strides(values: Any) -> tuple[int, ...] | None:
    strides = getattr(values, "strides", None)
    if strides is None:
        return None
    return tuple(int(stride) for stride in strides)


def _paper_rows_from_generic_grouped_rows(
    generic_rows: tuple[dict[str, int], ...],
    *,
    group_keys: tuple[str, ...],
    group_tuples: tuple[tuple[int, ...], ...],
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for generic_row in generic_rows:
        group_id = int(generic_row["group_id"])
        group_tuple = group_tuples[group_id]
        row = {group_keys[index]: int(group_tuple[index]) for index in range(len(group_keys))}
        for key, value in generic_row.items():
            if key != "group_id":
                row[key] = int(value)
        rows.append(row)
    return rows


def _packed_or_sequence_count(records: Any) -> int:
    count = getattr(records, "count", None)
    return int(count) if count is not None and not callable(count) else len(records)


def _fixture_metadata(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture": str(fixture.get("fixture_kind", "tiny_denormalized_columnar")),
        "fixture_generation": fixture.get("generation", {}),
    }


def _run_paper_rt_cpu_reference_result_mode(
    *,
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    copies: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    workload = _make_paper_rt_encoded_workload(fixture, plan, mode)
    primitive_result = rt.run_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
        workload["rays"],
        workload["triangles"],
        primitive_group_ids=tuple(int(primitive["group_id"]) for primitive in workload["primitive_records"]),
        primitive_values=tuple(int(primitive["aggregate_value"]) for primitive in workload["primitive_records"]),
        reduction="sum_count" if mode == "avg_as_sum_count" else mode,
        deduplicate_primitives=True,
        backend="cpu",
        include_hit_primitive_indices=True,
    )
    hit_primitive_indices = tuple(int(index) for index in primitive_result["hit_primitive_indices"])
    hit_row_ids = {
        int(workload["primitive_records"][primitive_index]["row_id"])
        for primitive_index in hit_primitive_indices
    }
    rows = _paper_rows_from_generic_grouped_rows(
        primitive_result["rows"],
        group_keys=workload["group_keys"],
        group_tuples=workload["group_tuples"],
    )
    elapsed_sec = time.perf_counter() - started

    cpu_rows = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
    expected_hit_ids = {
        int(record["row_id"])
        for record in _fixture_records(fixture)
        if _record_matches_plan(record, plan)
    }
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": PAPER_RT_CPU_REFERENCE_BACKEND,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": elapsed_sec,
        "rows": rows,
        "matches_cpu_reference": tuple(rows) == tuple(cpu_rows),
        "metadata": {
            "contract": "raydb_paper_triangle_scan_grouped_aggregate_cpu_reference",
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {"cpu_paper_rt_reference_sec": elapsed_sec},
            **_fixture_metadata(fixture),
            "paper_reproduction": "paper_shaped_rt_contract_reference",
            "authors_code_comparison": False,
            "raydb_reference_repo": RAYDB_REFERENCE_REPO,
            "raydb_reference_branch": RAYDB_REFERENCE_BRANCH,
            "raydb_reference_commit": RAYDB_REFERENCE_COMMIT,
            "reference_execution_shape": {
                "row_encoding": "one data row becomes one right Triangle3D primitive",
                "scan_axis": "mixed-radix predicate tuple encoded on Z",
                "group_axis": "dense group id encoded on Y",
                "aggregate_axis": "aggregate payload encoded on X",
                "ray_direction": "+Z",
                "ray_spacing": "Sx/2 by Sy/2, matching the paper/reference-code guarantee",
                "deduplication": "deduplicate primitive ids before grouped reduction",
            },
            "primitive_contract_required_for_native": GENERIC_RAY_TRIANGLE_GROUPED_REDUCTION_3D_SYMBOL,
            "native_rt_core_lowering_ready": "code_added_pending_pod_validation",
            "native_rt_core_lowering_blocker": "CUDA/OptiX pod build and runtime validation pending.",
            "rt_core_accelerated": False,
            "rt_core_claim_authorized": False,
            "scan_fields": list(workload["scan_fields"]),
            "group_keys": list(workload["group_keys"]),
            "triangle_count": _packed_or_sequence_count(workload["triangles"]),
            "ray_count": _packed_or_sequence_count(workload["rays"]),
            "query_scan_value_count": len(workload["query_scan_values"]),
            "hit_event_count_before_dedup": primitive_result["hit_event_count_before_dedup"],
            "deduplicated_primitive_hit_count": len(hit_row_ids),
            "expected_predicate_row_count": len(expected_hit_ids),
            "hit_id_set_matches_predicate": hit_row_ids == expected_hit_ids,
            "generic_primitive_used": primitive_result["primitive"],
            "generic_primitive_reduction": primitive_result["reduction"],
            "engine_boundary": (
                "Python owns RayDB query encoding and result interpretation. The needed native "
                "engine primitive must only know rays, triangles, primitive ids, group ids, "
                "payload values, deduplication, and reductions; it must not contain RayDB, SQL, "
                "table, SSB, or database vocabulary."
            ),
            "claim_boundary": (
                "This is a paper-shaped RayDB RT CPU contract reference derived from the "
                "authors' ray/triangle any-hit design. It does not use RT cores yet and does "
                "not authorize performance wording."
            ),
        },
    }


def _run_paper_rt_native_result_mode(
    *,
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    copies: int,
    backend: str,
    backend_label: str,
) -> dict[str, Any]:
    if mode not in PAPER_RT_RESULT_MODES:
        raise ValueError(f"unsupported paper RT result mode: {mode}")
    if backend not in {"embree", "optix"}:
        raise ValueError("paper RT native backend must be embree or optix")
    started = time.perf_counter()
    workload = _make_paper_rt_encoded_packed_workload(fixture, plan, mode)
    workload_built = time.perf_counter()
    primitive_result = rt.run_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
        workload["rays"],
        workload["triangles"],
        primitive_group_ids=workload["primitive_group_ids"],
        primitive_values=workload["primitive_values"],
        reduction="sum_count" if mode == "avg_as_sum_count" else mode,
        deduplicate_primitives=True,
        backend=backend,
    )
    primitive_done = time.perf_counter()
    rows = _paper_rows_from_generic_grouped_rows(
        primitive_result["rows"],
        group_keys=workload["group_keys"],
        group_tuples=workload["group_tuples"],
    )
    rows_done = time.perf_counter()
    elapsed_sec = rows_done - started
    cpu_rows = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
    raw_phase_timing = primitive_result.get("phase_timing_seconds", {})
    scene_build_sec = float(raw_phase_timing.get("prepare_build", 0.0))
    query_pack_sec = float(raw_phase_timing.get("query_pack", 0.0))
    rt_traversal_sec = float(raw_phase_timing.get("traversal", primitive_done - workload_built))
    query_preparation_sec = (workload_built - started) + query_pack_sec
    materialization_sec = max(
        0.0,
        elapsed_sec - query_preparation_sec - scene_build_sec - rt_traversal_sec,
    )
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend_label,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": elapsed_sec,
        "rows": rows,
        "matches_cpu_reference": tuple(rows) == tuple(cpu_rows),
        "metadata": {
            "contract": f"raydb_paper_triangle_scan_grouped_aggregate_{backend}",
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {
                "elapsed_sec": elapsed_sec,
                **raw_phase_timing,
            },
            **_fixture_metadata(fixture),
            "paper_reproduction": f"paper_shaped_rt_contract_{backend}_lowering",
            "authors_code_comparison": False,
            "raydb_reference_repo": RAYDB_REFERENCE_REPO,
            "raydb_reference_branch": RAYDB_REFERENCE_BRANCH,
            "raydb_reference_commit": RAYDB_REFERENCE_COMMIT,
            "primitive_contract_required_for_native": GENERIC_RAY_TRIANGLE_GROUPED_REDUCTION_3D_SYMBOL,
            "v2_4_prepared_session": describe_paper_rt_v2_4_prepared_session(
                workload,
                backend=backend,
                mode=mode,
            ),
            "v2_5_partner_continuation": describe_raydb_v2_5_partner_continuation(mode),
            "v2_4_phase_timing": rt.v2_4_phase_timing_metadata(
                {
                    "query_preparation": query_preparation_sec,
                    "scene_build": scene_build_sec,
                    "rt_traversal": rt_traversal_sec,
                    "materialization": materialization_sec,
                },
                promoted_performance_path=True,
                same_phase_contract_as_basis=True,
                source=f"raydb_style.paper_rt_native_result_mode.{backend}.{mode}",
            ),
            "native_symbol": primitive_result.get("native_symbol"),
            "native_rt_core_lowering_ready": True,
            "rt_core_accelerated": bool(primitive_result.get("rt_core_accelerated", False)),
            "embree_same_contract_baseline": backend == "embree",
            "rt_core_claim_authorized": False,
            "scan_fields": list(workload["scan_fields"]),
            "group_keys": list(workload["group_keys"]),
            "triangle_count": _packed_or_sequence_count(workload["triangles"]),
            "ray_count": _packed_or_sequence_count(workload["rays"]),
            "packed_host_buffers": bool(workload.get("packed_host_buffers", False)),
            "query_scan_value_count": len(workload["query_scan_values"]),
            "hit_event_count_before_dedup": primitive_result.get("hit_event_count_before_dedup"),
            "generic_primitive_used": primitive_result.get("primitive"),
            "generic_primitive_reduction": primitive_result.get("reduction"),
            "engine_boundary": (
                "Python owns RayDB query encoding and result interpretation. Native execution "
                "uses a generic ray/triangle primitive-id grouped i64 reduction with no RayDB, "
                "SQL, table, SSB, or database vocabulary."
            ),
            "claim_boundary": (
                f"This is the paper-shaped RayDB RT lowering through a generic {backend.title()} "
                "primitive. Correctness/performance claims require same-contract evidence and review."
            ),
        },
    }


def _sequence_from_partner_output(values: Any) -> list[Any]:
    if hasattr(values, "detach"):
        return values.detach().cpu().tolist()
    if hasattr(values, "cpu") and hasattr(values.cpu(), "tolist"):
        return values.cpu().tolist()
    if hasattr(values, "tolist"):
        result = values.tolist()
        return result if isinstance(result, list) else [result]
    return list(values)


def _paper_rows_from_v2_5_outputs(
    mode: str,
    outputs: dict[str, Any],
    *,
    group_keys: tuple[str, ...],
    group_tuples: tuple[tuple[int, ...], ...],
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    if mode == "count":
        counts = _sequence_from_partner_output(outputs["counts"])
        for group_id, count in enumerate(counts):
            count_value = int(count)
            if count_value:
                group_tuple = group_tuples[group_id]
                row = {group_keys[index]: int(group_tuple[index]) for index in range(len(group_keys))}
                row["count"] = count_value
                rows.append(row)
        return rows
    if mode == "sum":
        sums = _sequence_from_partner_output(outputs["sums"])
        for group_id, sum_value_raw in enumerate(sums):
            sum_value = int(round(float(sum_value_raw)))
            if sum_value:
                group_tuple = group_tuples[group_id]
                row = {group_keys[index]: int(group_tuple[index]) for index in range(len(group_keys))}
                row["sum"] = sum_value
                rows.append(row)
        return rows
    if mode == "avg_as_sum_count":
        sums = _sequence_from_partner_output(outputs["sums"])
        counts = _sequence_from_partner_output(outputs["counts"])
        for group_id, count in enumerate(counts):
            count_value = int(count)
            if count_value:
                group_tuple = group_tuples[group_id]
                row = {group_keys[index]: int(group_tuple[index]) for index in range(len(group_keys))}
                row["sum"] = int(round(float(sums[group_id])))
                row["count"] = count_value
                rows.append(row)
        return rows
    value_key = "mins" if mode == "min" else "maxes"
    output_key = "min" if mode == "min" else "max"
    group_ids = _sequence_from_partner_output(outputs["group_ids"])
    values = _sequence_from_partner_output(outputs[value_key])
    for group_id_raw, value_raw in zip(group_ids, values):
        group_id = int(group_id_raw)
        group_tuple = group_tuples[group_id]
        row = {group_keys[index]: int(group_tuple[index]) for index in range(len(group_keys))}
        row[output_key] = int(round(float(value_raw)))
        rows.append(row)
    return rows


def _run_raydb_v2_5_triton_or_reference(
    mode: str,
    inputs: dict[str, Any],
    *,
    allow_reference_fallback: bool,
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...], str]:
    if allow_reference_fallback:
        plan = describe_raydb_v2_5_partner_continuation(mode)
        outputs, results = _run_raydb_v2_5_reference_fallback(
            mode,
            inputs,
            operations=tuple(plan["operations"]),
            block_size=256,
        )
        return outputs, results, "reference_fallback"
    outputs, results = _run_raydb_v2_5_triton_front_door(mode, inputs)
    return outputs, results, "partner_adapter_front_door"


def _run_paper_rt_hit_stream_triton_result_mode(
    *,
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    copies: int,
    backend: str,
    backend_label: str,
    allow_reference_fallback: bool = False,
) -> dict[str, Any]:
    if mode not in PAPER_RT_RESULT_MODES:
        raise ValueError(f"unsupported paper RT result mode: {mode}")
    if backend not in {"cpu", "embree", "optix"}:
        raise ValueError("paper RT hit-stream backend must be cpu, embree, or optix")
    started = time.perf_counter()
    workload = _make_paper_rt_encoded_packed_workload(fixture, plan, mode)
    workload_built = time.perf_counter()
    max_rows = _packed_or_sequence_count(workload["triangles"])
    hit_stream_started = time.perf_counter()
    hit_stream = rt.run_generic_ray_triangle_hit_stream_3d(
        workload["rays"],
        workload["triangles"],
        max_rows=max_rows,
        deduplicate_primitives=True,
        backend=backend,
    )
    hit_stream_done = time.perf_counter()
    if hit_stream.get("overflow"):
        raise RuntimeError("RayDB hit-stream overflowed despite primitive-count capacity")

    primitive_ids = [int(row["primitive_id"]) for row in hit_stream["rows"]]
    group_count = len(workload["group_tuples"])
    map_started = time.perf_counter()
    if allow_reference_fallback:
        continuation_inputs = {
            "group_ids": tuple(int(workload["primitive_group_ids"][index]) for index in primitive_ids),
            "values": tuple(float(workload["primitive_values"][index]) for index in primitive_ids),
            "group_count": group_count,
        }
    else:
        import torch

        if not rt.triton_partner_available():
            raise RuntimeError("Triton/Torch CUDA is unavailable; rerun on a GPU pod or allow reference fallback")
        device = torch.device("cuda:0")
        primitive_index_tensor = torch.tensor(primitive_ids, dtype=torch.int64, device=device)
        all_group_ids = torch.as_tensor(workload["primitive_group_ids"], dtype=torch.int64, device=device)
        all_values = torch.as_tensor(workload["primitive_values"], dtype=torch.float64, device=device)
        continuation_inputs = {
            "group_ids": all_group_ids[primitive_index_tensor],
            "values": all_values[primitive_index_tensor],
            "group_count": group_count,
        }
    map_done = time.perf_counter()
    continuation_started = time.perf_counter()
    outputs, continuation_results, execution_path = _run_raydb_v2_5_triton_or_reference(
        mode,
        continuation_inputs,
        allow_reference_fallback=allow_reference_fallback,
    )
    continuation_done = time.perf_counter()
    rows = _paper_rows_from_v2_5_outputs(
        mode,
        outputs,
        group_keys=workload["group_keys"],
        group_tuples=workload["group_tuples"],
    )
    rows_done = time.perf_counter()
    cpu_rows = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
    hit_phase_timing = hit_stream.get("phase_timing_seconds", {})
    elapsed_sec = rows_done - started
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend_label,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": elapsed_sec,
        "rows": rows,
        "matches_cpu_reference": tuple(rows) == tuple(cpu_rows),
        "metadata": {
            "contract": f"raydb_paper_triangle_scan_hit_stream_triton_{backend}",
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {
                "elapsed_sec": elapsed_sec,
                "workload_build": workload_built - started,
                "rt_hit_stream_total": hit_stream_done - hit_stream_started,
                "hit_stream_to_partner_input": map_done - map_started,
                "triton_continuation": continuation_done - continuation_started,
                "row_presentation": rows_done - continuation_done,
                **{f"hit_stream_{key}": value for key, value in hit_phase_timing.items()},
            },
            **_fixture_metadata(fixture),
            "paper_reproduction": f"paper_shaped_rt_hit_stream_triton_{backend}",
            "authors_code_comparison": False,
            "raydb_reference_repo": RAYDB_REFERENCE_REPO,
            "raydb_reference_branch": RAYDB_REFERENCE_BRANCH,
            "raydb_reference_commit": RAYDB_REFERENCE_COMMIT,
            "primitive_contract_required_for_native": rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE,
            "v2_5_partner_continuation": describe_raydb_v2_5_partner_continuation(mode),
            "v2_4_phase_timing": rt.v2_4_phase_timing_metadata(
                {
                    "query_preparation": workload_built - started,
                    "scene_build": float(hit_phase_timing.get("prepare_build", 0.0)),
                    "rt_traversal": float(hit_phase_timing.get("traversal", 0.0)),
                    "materialization": float(hit_phase_timing.get("hit_stream_materialization", 0.0)),
                    "partner_continuation": continuation_done - continuation_started,
                },
                promoted_performance_path=False,
                same_phase_contract_as_basis=True,
                source=f"raydb_style.paper_rt_hit_stream_triton.{backend}.{mode}",
            ),
            "native_symbol": hit_stream.get("native_symbol"),
            "native_rt_core_lowering_ready": True,
            "rt_core_accelerated": bool(hit_stream.get("rt_core_accelerated", False)),
            "embree_same_contract_baseline": backend == "embree",
            "rt_core_claim_authorized": False,
            "scan_fields": list(workload["scan_fields"]),
            "group_keys": list(workload["group_keys"]),
            "triangle_count": _packed_or_sequence_count(workload["triangles"]),
            "ray_count": _packed_or_sequence_count(workload["rays"]),
            "hit_stream_row_schema": list(rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA),
            "hit_stream_row_count": int(hit_stream.get("row_count", 0)),
            "hit_stream_overflow": bool(hit_stream.get("overflow", False)),
            "hit_event_count_before_dedup": hit_stream.get("hit_event_count_before_dedup"),
            "continuation_execution_path": execution_path,
            "generic_primitive_used": hit_stream.get("primitive"),
            "engine_boundary": (
                "Native execution emits only generic ray_id/primitive_id hit rows. Python app code "
                "maps primitive ids to RayDB group/value columns, then Triton performs generic "
                "grouped count/sum/min/max continuation. No RayDB, SQL, table, or database "
                "semantics are embedded in the native engine."
            ),
            "claim_boundary": (
                "This is Goal2684 full RT hit-stream plus Triton continuation evidence. "
                "It is not a public speedup claim until pod artifacts and external review exist."
            ),
        },
    }


def _run_paper_rt_device_hit_stream_triton_result_mode(
    *,
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    copies: int,
    backend: str,
    backend_label: str,
    allow_reference_fallback: bool = False,
) -> dict[str, Any]:
    if mode not in PAPER_RT_RESULT_MODES:
        raise ValueError(f"unsupported paper RT result mode: {mode}")
    if backend not in {"cpu", "embree", "optix"}:
        raise ValueError("paper RT device hit-stream backend must be cpu, embree, or optix")
    started = time.perf_counter()
    workload = _make_paper_rt_encoded_packed_workload(fixture, plan, mode)
    workload_built = time.perf_counter()
    max_rows = _packed_or_sequence_count(workload["triangles"])
    hit_stream_started = time.perf_counter()
    hit_stream = rt.run_generic_ray_triangle_hit_stream_3d(
        workload["rays"],
        workload["triangles"],
        max_rows=max_rows,
        deduplicate_primitives=True,
        backend=backend,
    )
    hit_stream_done = time.perf_counter()
    if hit_stream.get("overflow"):
        raise RuntimeError("RayDB hit-stream overflowed despite primitive-count capacity")

    group_count = len(workload["group_tuples"])
    handoff_started = time.perf_counter()
    require_device = not allow_reference_fallback
    hit_stream_columns = rt.prepare_generic_hit_stream_columns_from_rows(
        hit_stream,
        prefer_torch_cuda=require_device,
        require_torch_cuda=require_device,
    )
    payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
        workload["primitive_group_ids"],
        workload["primitive_values"],
        primitive_count=_packed_or_sequence_count(workload["triangles"]),
        group_count=group_count,
        prefer_torch_cuda=require_device,
        require_torch_cuda=require_device,
        device_like=hit_stream_columns.primitive_ids,
    )
    continuation_inputs, handoff_metadata = rt.gather_typed_payload_columns_for_hit_stream(
        hit_stream_columns,
        payload_columns,
    )
    handoff_done = time.perf_counter()
    continuation_started = time.perf_counter()
    outputs, continuation_results, execution_path = _run_raydb_v2_5_triton_or_reference(
        mode,
        continuation_inputs,
        allow_reference_fallback=allow_reference_fallback,
    )
    continuation_done = time.perf_counter()
    rows = _paper_rows_from_v2_5_outputs(
        mode,
        outputs,
        group_keys=workload["group_keys"],
        group_tuples=workload["group_tuples"],
    )
    rows_done = time.perf_counter()
    cpu_rows = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
    hit_phase_timing = hit_stream.get("phase_timing_seconds", {})
    elapsed_sec = rows_done - started
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend_label,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": elapsed_sec,
        "rows": rows,
        "matches_cpu_reference": tuple(rows) == tuple(cpu_rows),
        "metadata": {
            "contract": f"raydb_paper_triangle_scan_device_hit_stream_triton_{backend}",
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {
                "elapsed_sec": elapsed_sec,
                "workload_build": workload_built - started,
                "rt_hit_stream_total": hit_stream_done - hit_stream_started,
                "hit_stream_column_handoff": handoff_done - handoff_started,
                "typed_payload_gather": float(handoff_metadata["typed_payload_gather_sec"]),
                "triton_continuation": continuation_done - continuation_started,
                "row_presentation": rows_done - continuation_done,
                **{f"hit_stream_{key}": value for key, value in hit_phase_timing.items()},
            },
            **_fixture_metadata(fixture),
            "paper_reproduction": f"paper_shaped_rt_device_hit_stream_triton_{backend}",
            "authors_code_comparison": False,
            "raydb_reference_repo": RAYDB_REFERENCE_REPO,
            "raydb_reference_branch": RAYDB_REFERENCE_BRANCH,
            "raydb_reference_commit": RAYDB_REFERENCE_COMMIT,
            "primitive_contract_required_for_native": rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE,
            "hit_stream_handoff_contract": rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
            "hit_stream_handoff": handoff_metadata,
            "v2_5_partner_continuation": describe_raydb_v2_5_partner_continuation(mode),
            "v2_4_phase_timing": rt.v2_4_phase_timing_metadata(
                {
                    "query_preparation": workload_built - started,
                    "scene_build": float(hit_phase_timing.get("prepare_build", 0.0)),
                    "rt_traversal": float(hit_phase_timing.get("traversal", 0.0)),
                    "transfer": handoff_done - handoff_started,
                    "partner_continuation": continuation_done - continuation_started,
                    "materialization": rows_done - continuation_done,
                },
                promoted_performance_path=False,
                same_phase_contract_as_basis=True,
                source=f"raydb_style.paper_rt_device_hit_stream_triton.{backend}.{mode}",
            ),
            "native_symbol": hit_stream.get("native_symbol"),
            "native_rt_core_lowering_path_present": True,
            "native_rt_core_lowering_ready": False,
            "native_device_hit_stream_columns_ready": bool(
                handoff_metadata["native_device_hit_stream_columns_ready"]
            ),
            "rt_core_accelerated": bool(hit_stream.get("rt_core_accelerated", False)),
            "embree_same_contract_baseline": backend == "embree",
            "rt_core_claim_authorized": False,
            "true_zero_copy_authorized": False,
            "scan_fields": list(workload["scan_fields"]),
            "group_keys": list(workload["group_keys"]),
            "triangle_count": _packed_or_sequence_count(workload["triangles"]),
            "ray_count": _packed_or_sequence_count(workload["rays"]),
            "hit_stream_column_schema": list(rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS),
            "typed_primitive_payload_column_schema": list(rt.GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS),
            "hit_stream_row_count": int(hit_stream.get("row_count", 0)),
            "hit_stream_overflow": bool(hit_stream.get("overflow", False)),
            "hit_event_count_before_dedup": hit_stream.get("hit_event_count_before_dedup"),
            "continuation_execution_path": execution_path,
            "generic_primitive_used": hit_stream.get("primitive"),
            "python_rebuilt_primitive_row_table": False,
            "materializes_host_rows_for_legacy_bridge": bool(
                handoff_metadata["materializes_host_rows_for_bridge"]
            ),
            "engine_boundary": (
                "Native execution owns only generic RT traversal and hit columns. "
                "App code supplies typed primitive payload columns; Triton performs "
                "generic grouped continuation without native RayDB, SQL, table, or "
                "database semantics."
            ),
            "claim_boundary": (
                "This is Goal2685 typed-column handoff evidence. Current local/legacy bridge "
                "may still materialize host hit rows before constructing columns; native "
                "device-column output and pod review are required before zero-copy or speedup wording."
            ),
        },
    }


def require_optix_partner_resident_experimental_backend() -> Any:
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("PyTorch with CUDA is required for optix_partner_resident_experimental") from exc
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for optix_partner_resident_experimental")
    rt.optix_version()
    return torch


def _run_optix_partner_resident_experimental_result_mode(
    *,
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    copies: int = 1,
    repeat: int = 1,
    warmup: int = 0,
) -> dict[str, Any]:
    if mode not in OPTIX_PARTNER_RESIDENT_RESULT_MODES:
        raise ValueError(
            "OptiX partner-resident experimental RayDB-style slice currently supports only "
            "count/sum/min/max/avg_as_sum_count"
        )
    torch = require_optix_partner_resident_experimental_backend()
    record_set = {
        "row_ids": torch.tensor(fixture["row_ids"], dtype=torch.int64, device="cuda"),
        "columns": {
            name: torch.tensor(values, dtype=torch.int64, device="cuda")
            for name, values in fixture["columns"].items()
        },
    }
    prepare_started = time.perf_counter()
    descriptor = rt.prepare_partner_resident_columnar_record_set(record_set, backend="optix")
    prepare_sec = time.perf_counter() - prepare_started
    query = rt.columnar_plan_to_grouped_query(plan)
    group_capacity = _infer_dense_group_capacity(fixture, plan)
    dispatch_query = query
    reduction = mode
    composite_lowering: tuple[str, ...] = ()
    if mode == "avg_as_sum_count":
        decomposed_plans = rt.decompose_columnar_aggregate_plan(plan)
        composite_lowering = tuple(item.aggregate for item in decomposed_plans)
        dispatch_query = rt.columnar_plan_to_grouped_query(decomposed_plans[0])
        reduction = "sum_count"
    query_times: list[float] = []
    dispatch_result: dict[str, Any] | None = None
    for iteration in range(warmup + repeat):
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        query_started = time.perf_counter()
        dispatch_result = rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
            descriptor,
            dispatch_query,
            reduction=reduction,
            allow_experimental_native=True,
            group_capacity=group_capacity,
            semantic_aggregate=mode,
        )
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        query_sec = time.perf_counter() - query_started
        if iteration >= warmup:
            query_times.append(query_sec)
    assert dispatch_result is not None
    query_sec = query_times[-1]
    query_median_sec = float(statistics.median(query_times))
    result_rows = tuple(dispatch_result["rows"])
    dispatch_metadata = dict(dispatch_result["metadata"])
    cpu_rows = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": prepare_sec + query_sec,
        "rows": list(result_rows),
        "matches_cpu_reference": tuple(result_rows) == tuple(cpu_rows),
        "metadata": {
            "contract": "columnar_grouped_aggregate_optix_partner_resident_experimental",
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {
                "prepare_sec": prepare_sec,
                "query_sec": query_sec,
                "query_median_sec": query_median_sec,
                "query_min_sec": float(min(query_times)),
                "query_max_sec": float(max(query_times)),
                "query_repeat": int(repeat),
                "query_warmup": int(warmup),
                "elapsed_sec": prepare_sec + query_median_sec,
            },
            **_fixture_metadata(fixture),
            "lowering_plan": rt.plan_columnar_aggregate_lowering(
                OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND
            ).to_dict(),
            **dispatch_metadata,
            "partner_resident_descriptor": descriptor.to_metadata(),
            "partner_input_constructed_by_fixture": True,
            "composite_lowering": list(composite_lowering),
            "native_avg_abi_added": False,
            "native_abi_added": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "rt_core_accelerated": False,
            "true_zero_copy_authorized": False,
            "claim_boundary": (
                "Experimental OptiX partner-resident count/sum/min/max parity and composite "
                "avg_as_sum_count=sum+count lowering through a generic fused sum_count pass for "
                "the synthetic RayDB-style columnar aggregate contract. This demonstrates "
                "Python+partner+RTDL descriptor execution for CUDA tensors, but it does not "
                "reproduce RayDB, expose SQL/DBMS behavior, authorize true zero-copy wording, "
                "or authorize performance wording."
            ),
        },
    }


def _infer_dense_group_capacity(fixture: dict[str, Any], plan: dict[str, Any]) -> int:
    group_key = plan["group_keys"][0]
    values = tuple(int(value) for value in fixture["columns"][group_key])
    if any(value < 0 for value in values):
        raise ValueError("experimental partner-resident backend requires non-negative dense group keys")
    return max(values) + 1


def _run_native_result_mode(
    *,
    backend: str,
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    prepare_dataset: Any,
    result_modes: tuple[str, ...],
    contract: str,
    rt_core_accelerated: bool,
    copies: int = 1,
) -> dict[str, Any]:
    backend_label = "OptiX" if backend == "optix" else backend.title()
    if mode not in result_modes:
        raise ValueError(f"{backend_label} RayDB-style slice currently supports only count and sum")
    query = rt.columnar_plan_to_grouped_query(plan)
    lowering_plan = rt.plan_columnar_aggregate_lowering(backend).to_dict()
    prepare_started = time.perf_counter()
    dataset = prepare_dataset(
        fixture,
        primary_fields=("ship_year", "discount", "quantity"),
    )
    prepare_sec = time.perf_counter() - prepare_started
    try:
        preparation_metadata = dataset.columnar_preparation_metadata()
        query_started = time.perf_counter()
        result_rows = dataset.grouped_count(query) if mode == "count" else dataset.grouped_sum(query)
        query_sec = time.perf_counter() - query_started
    finally:
        dataset.close()
    cpu_rows = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": prepare_sec + query_sec,
        "rows": list(result_rows),
        "matches_cpu_reference": tuple(result_rows) == tuple(cpu_rows),
        "metadata": {
            "contract": contract,
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {
                "prepare_sec": prepare_sec,
                "query_sec": query_sec,
                "elapsed_sec": prepare_sec + query_sec,
            },
            **_fixture_metadata(fixture),
            "lowering_plan": lowering_plan,
            "uses_existing_compatibility_wrapper": False,
            "materializes_input_rows_for_wrapper": False,
            "direct_columnar_record_set_api": True,
            "columnar_preparation": preparation_metadata,
            "native_abi_added": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "rt_core_accelerated": rt_core_accelerated,
            "claim_boundary": (
                f"{backend_label} parity for count/sum over the synthetic RayDB-style "
                "columnar aggregate contract. This uses existing generic columnar "
                "payload capability through direct record-set preparation; it does not "
                "add native RayDB ABI, reproduce RayDB, or authorize performance wording."
            ),
        },
    }


def run_suite(
    *,
    backend: str = "cpu_python_reference",
    copies: int = 1,
    repeat: int = 1,
    warmup: int = 0,
    fixture_kind: str = "repeated",
    generated_rows: int = DEFAULT_GENERATED_ROW_COUNT,
    generated_groups: int = DEFAULT_GENERATED_GROUP_COUNT,
    generated_revenue_mod: int = DEFAULT_GENERATED_REVENUE_MOD,
) -> dict[str, Any]:
    if backend == "cpu_python_reference":
        modes = CPU_RESULT_MODES
    elif backend == "embree":
        modes = EMBREE_RESULT_MODES
    elif backend == "optix":
        modes = OPTIX_RESULT_MODES
    elif backend == OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND:
        modes = OPTIX_PARTNER_RESIDENT_RESULT_MODES
    elif backend in (
        PAPER_RT_CPU_REFERENCE_BACKEND,
        PAPER_RT_EMBREE_BACKEND,
        PAPER_RT_OPTIX_BACKEND,
        PAPER_RT_EMBREE_HIT_STREAM_TRITON_BACKEND,
        PAPER_RT_OPTIX_HIT_STREAM_TRITON_BACKEND,
        PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND,
    ):
        modes = PAPER_RT_RESULT_MODES
    else:
        raise ValueError(f"unsupported backend: {backend}")
    results = {
        mode: run_result_mode(
            mode,
            backend=backend,
            copies=copies,
            repeat=repeat,
            warmup=warmup,
            fixture_kind=fixture_kind,
            generated_rows=generated_rows,
            generated_groups=generated_groups,
            generated_revenue_mod=generated_revenue_mod,
        )
        for mode in modes
    }
    fixture = make_benchmark_fixture(
        fixture_kind=fixture_kind,
        copies=copies,
        generated_rows=generated_rows,
        generated_groups=generated_groups,
        generated_revenue_mod=generated_revenue_mod,
    )
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend,
        "copies": int(copies),
        "fixture_kind": fixture.get("fixture_kind", fixture_kind),
        "generation": fixture.get("generation", {}),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "row_count": len(fixture["row_ids"]),
        "modes": results,
        "all_match_cpu_reference": all(payload.get("matches_cpu_reference", True) for payload in results.values()),
        "claim_boundary": (
            "CPU-only synthetic RayDB-style fixture for RTDL contract design. "
            "No Embree, OptiX, authors-code, SQL engine, DBMS, or speedup claim."
            if backend == "cpu_python_reference"
            else (
                "Paper-shaped RayDB RT CPU reference: rows are Triangle3D primitives, "
                "queries are +Z rays, and primitive hits are deduplicated before grouped "
                "aggregation. No RT-core or speedup claim yet."
                if backend == PAPER_RT_CPU_REFERENCE_BACKEND
                else (
                    "Paper-shaped RayDB RT native lowering through the generic "
                    f"{GENERIC_RAY_TRIANGLE_GROUPED_REDUCTION_3D_SYMBOL} primitive. "
                    "Same-contract Embree-vs-OptiX evidence is required before performance wording."
                    if backend in (PAPER_RT_EMBREE_BACKEND, PAPER_RT_OPTIX_BACKEND)
                    else (
                        "Paper-shaped RayDB RT hit-stream handoff through generic "
                        f"{rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE} rows "
                        "plus Triton grouped continuation. Same-contract artifacts "
                        "and review are required before performance wording."
                        if backend
                        in (
                            PAPER_RT_EMBREE_HIT_STREAM_TRITON_BACKEND,
                            PAPER_RT_OPTIX_HIT_STREAM_TRITON_BACKEND,
                            PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND,
                        )
                        else (
                            "Experimental OptiX partner-resident count/sum/min/max plus composite avg_as_sum_count "
                            "parity for the synthetic RayDB-style contract. "
                            "No authors-code, SQL engine, DBMS, true zero-copy, or speedup claim."
                            if backend == OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND
                            else f"{'OptiX' if backend == 'optix' else backend.title()} count/sum parity for the synthetic RayDB-style contract. "
                            "No authors-code, SQL engine, DBMS, or speedup claim."
                        )
                    )
                )
            )
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RayDB-style CPU reference benchmark slice.")
    parser.add_argument("--mode", choices=("all", *RESULT_MODES), default="all")
    parser.add_argument("--backend", choices=BACKENDS, default="cpu_python_reference")
    parser.add_argument("--fixture-kind", choices=("repeated", "generated"), default="repeated")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--generated-rows", type=int, default=DEFAULT_GENERATED_ROW_COUNT)
    parser.add_argument("--generated-groups", type=int, default=DEFAULT_GENERATED_GROUP_COUNT)
    parser.add_argument("--generated-revenue-mod", type=int, default=DEFAULT_GENERATED_REVENUE_MOD)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=0)
    args = parser.parse_args(argv)
    payload = (
        run_suite(
            backend=args.backend,
            copies=args.copies,
            repeat=args.repeat,
            warmup=args.warmup,
            fixture_kind=args.fixture_kind,
            generated_rows=args.generated_rows,
            generated_groups=args.generated_groups,
            generated_revenue_mod=args.generated_revenue_mod,
        )
        if args.mode == "all"
        else run_result_mode(
            args.mode,
            backend=args.backend,
            copies=args.copies,
            repeat=args.repeat,
            warmup=args.warmup,
            fixture_kind=args.fixture_kind,
            generated_rows=args.generated_rows,
            generated_groups=args.generated_groups,
            generated_revenue_mod=args.generated_revenue_mod,
        )
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
