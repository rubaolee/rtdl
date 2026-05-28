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
BACKENDS = (
    "cpu_python_reference",
    "embree",
    "optix",
    OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,
    PAPER_RT_CPU_REFERENCE_BACKEND,
    PAPER_RT_EMBREE_BACKEND,
    PAPER_RT_OPTIX_BACKEND,
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
    partner: str = "cupy",
) -> dict[str, Any]:
    """Build RayDB paper query rays as partner-owned device columns.

    The app still owns RayDB predicate-to-ray-grid semantics. The runtime only
    receives generic 3-D ray columns.
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
    if partner == "torch":
        try:
            import torch
        except ImportError as exc:  # pragma: no cover - pod-only optional dependency
            raise RuntimeError("Torch is required for partner-owned paper RT query ray columns") from exc
        if not torch.cuda.is_available():
            raise RuntimeError("Torch CUDA is required for partner-owned paper RT query ray columns")
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
    raise ValueError("paper RT partner ray columns currently support partner='cupy' or partner='torch'")


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
    elif backend in (PAPER_RT_CPU_REFERENCE_BACKEND, PAPER_RT_EMBREE_BACKEND, PAPER_RT_OPTIX_BACKEND):
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
                "Experimental OptiX partner-resident count/sum/min/max plus composite avg_as_sum_count "
                "parity for the synthetic RayDB-style contract. "
                "No authors-code, SQL engine, DBMS, true zero-copy, or speedup claim."
                if backend == OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND
                else f"{'OptiX' if backend == 'optix' else backend.title()} count/sum parity for the synthetic RayDB-style contract. "
                "No authors-code, SQL engine, DBMS, or speedup claim."
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
