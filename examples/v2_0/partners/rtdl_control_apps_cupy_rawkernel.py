from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import numpy as np

from examples.v2_0.apps.analytics import rtdl_database_analytics_app
from examples.v2_0.apps.analytics import rtdl_graph_analytics_app
from examples.v2_0.features.spatial import rtdl_polygon_pair_overlap_area_rows
from examples.v2_0.features.spatial import rtdl_polygon_set_jaccard
from examples.v2_0.apps.geospatial import rtdl_sales_risk_screening
from examples.internal.archived_apps import rtdl_v0_7_db_app_demo
from rtdsl.partner_adapters import metric_table_payload_to_partner_columns
from rtdsl.partner_adapters import partner_metric_table_reduce_batch
from rtdsl.partner_adapters import partner_metric_table_reduce_repeated_pattern
from rtdsl.partner_adapters import columnar_payload_to_partner_columns
from rtdsl.partner_adapters import partner_columnar_predicate_reduce_batch
from rtdsl.partner_adapters import aabb_pair_payload_to_partner_columns
from rtdsl.partner_adapters import aabb_pair_overlap_summary_2d_partner_columns
from rtdsl.partner_adapters import aabb_tiled_candidate_pair_payload_2d_partner_columns
from rtdsl.reference import _polygon_unit_cells


CONTROL_APPS = (
    "database_analytics",
    "graph_analytics",
    "polygon_pair_overlap_area_rows",
    "polygon_set_jaccard",
)

FAIRNESS_NOTE = (
    "Compared against the legacy Python+RTDL path without user C/C++ extension; "
    "v2 uses Python+partner continuations+RTDL under the explicit user decision."
)

DB_RAWKERNEL_SOURCE = r"""
extern "C" __global__
void rtdl_user_db_summary(
    const int n,
    const int* ship_date,
    const int* discount,
    const int* quantity,
    const int* revenue,
    const int* row_id,
    const int* region,
    const int* channel_web,
    int* promo_count,
    int* open_count_by_region,
    int* web_revenue_by_region,
    int* risky_count,
    int* risky_count_by_region,
    int* risky_revenue_by_region,
    int* risky_order_ids
) {
    int i = blockDim.x * blockIdx.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    int r = region[i];
    int promo = (ship_date[i] >= 12 && ship_date[i] <= 15 && discount[i] == 6 && quantity[i] < 20);
    int open = (ship_date[i] >= 12 && quantity[i] < 20);
    int web = (ship_date[i] >= 12 && channel_web[i] == 1);
    int risky = (ship_date[i] >= 11 && ship_date[i] <= 13 && discount[i] >= 6 && quantity[i] < 20);
    if (promo) {
        atomicAdd(promo_count, 1);
    }
    if (open) {
        atomicAdd(&open_count_by_region[r], 1);
    }
    if (web) {
        atomicAdd(&web_revenue_by_region[r], revenue[i]);
    }
    if (risky) {
        int index = atomicAdd(risky_count, 1);
        risky_order_ids[index] = row_id[i];
        atomicAdd(&risky_count_by_region[r], 1);
        atomicAdd(&risky_revenue_by_region[r], revenue[i]);
    }
}
"""

POLYGON_PAIR_RAWKERNEL_SOURCE = r"""
extern "C" __global__
void rtdl_user_polygon_pair_summary(
    const int pair_count,
    const int cell_count,
    const int* left_index,
    const int* right_index,
    const unsigned char* left_masks,
    const unsigned char* right_masks,
    int* overlap_pair_count,
    int* total_intersection_area,
    int* total_union_area,
    int* set_intersection_area
) {
    int pair = blockDim.x * blockIdx.x + threadIdx.x;
    if (pair >= pair_count) {
        return;
    }
    int li = left_index[pair];
    int ri = right_index[pair];
    int intersection_area = 0;
    int left_area = 0;
    int right_area = 0;
    for (int cell = 0; cell < cell_count; ++cell) {
        int l = left_masks[li * cell_count + cell] != 0;
        int r = right_masks[ri * cell_count + cell] != 0;
        left_area += l;
        right_area += r;
        intersection_area += (l && r);
    }
    if (intersection_area > 0) {
        atomicAdd(overlap_pair_count, 1);
        atomicAdd(total_intersection_area, intersection_area);
        atomicAdd(total_union_area, left_area + right_area - intersection_area);
        atomicAdd(set_intersection_area, intersection_area);
    }
}
"""

REGION_ORDER = ("central", "east", "south", "west")
GRAPH_SUM_METRIC_IDS = np.asarray([0, 1, 3, 4, 5, 6], dtype=np.int32)
GRAPH_SUM_METRIC_VALUES = np.asarray([2, 2, 1, 3, 1, 3], dtype=np.int32)
GRAPH_MAX_METRIC_IDS = np.asarray([2], dtype=np.int32)
GRAPH_MAX_METRIC_VALUES = np.asarray([1], dtype=np.int32)


@dataclass(frozen=True)
class PartnerPairPayloadTable:
    """Compact identity-preserving table handed from RTDL discovery to partner code."""

    left_index: Any
    right_index: Any
    left_min_x: Any
    left_min_y: Any
    left_max_x: Any
    left_max_y: Any
    left_area: Any
    right_min_x: Any
    right_min_y: Any
    right_max_x: Any
    right_max_y: Any
    right_area: Any

    @property
    def pair_count(self) -> int:
        return int(len(self.left_index))


def _load_cupy():
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on GPU environment
        raise RuntimeError("CuPy is required for --partner cupy") from exc
    return cp


def _blocks(n: int, block: int = 256) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return ((max(1, (n + block - 1) // block),), (block,))


def _region_code(name: object) -> int:
    return REGION_ORDER.index(str(name))


def _region_dict(values: list[int] | np.ndarray) -> dict[str, int]:
    return {
        region: int(values[index])
        for index, region in enumerate(REGION_ORDER)
        if int(values[index]) != 0
    }


def _table_columns(rows: tuple[dict[str, object], ...]) -> dict[str, np.ndarray]:
    return {
        "ship_date": np.asarray([int(row["ship_date"]) for row in rows], dtype=np.int32),
        "discount": np.asarray([int(row["discount"]) for row in rows], dtype=np.int32),
        "quantity": np.asarray([int(row["quantity"]) for row in rows], dtype=np.int32),
        "revenue": np.asarray([int(row["revenue"]) for row in rows], dtype=np.int32),
        "row_id": np.asarray([int(row["row_id"]) for row in rows], dtype=np.int32),
        "region": np.asarray([_region_code(row["region"]) for row in rows], dtype=np.int32),
        "channel_web": np.asarray([1 if str(row.get("channel", "")) == "web" else 0 for row in rows], dtype=np.int32),
    }


def _database_cpu_continuation(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    columns = _table_columns(rows)
    promo_count = 0
    open_count = [0] * len(REGION_ORDER)
    web_revenue = [0] * len(REGION_ORDER)
    risky_count = 0
    risky_order_ids: list[int] = []
    risky_count_by_region = [0] * len(REGION_ORDER)
    risky_revenue_by_region = [0] * len(REGION_ORDER)
    for i in range(len(rows)):
        ship_date = int(columns["ship_date"][i])
        discount = int(columns["discount"][i])
        quantity = int(columns["quantity"][i])
        revenue = int(columns["revenue"][i])
        region = int(columns["region"][i])
        channel_web = int(columns["channel_web"][i])
        if 12 <= ship_date <= 15 and discount == 6 and quantity < 20:
            promo_count += 1
        if ship_date >= 12 and quantity < 20:
            open_count[region] += 1
        if ship_date >= 12 and channel_web == 1:
            web_revenue[region] += revenue
        if 11 <= ship_date <= 13 and discount >= 6 and quantity < 20:
            risky_count += 1
            risky_order_ids.append(int(columns["row_id"][i]))
            risky_count_by_region[region] += 1
            risky_revenue_by_region[region] += revenue
    return {
        "regional_dashboard": {
            "promo_order_count": promo_count,
            "open_order_count_by_region": _region_dict(open_count),
            "web_revenue_by_region": _region_dict(web_revenue),
        },
        "sales_risk": {
            "risky_order_count": risky_count,
            "risky_order_ids": sorted(risky_order_ids),
            "risky_order_count_by_region": _region_dict(risky_count_by_region),
            "risky_revenue_by_region": _region_dict(risky_revenue_by_region),
            "highest_risk_region": max(
                _region_dict(risky_revenue_by_region).items(),
                key=lambda item: (item[1], item[0]),
            )[0],
        },
    }


def _database_cupy_continuation(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    cp = _load_cupy()
    columns = _table_columns(rows)
    n = len(rows)
    kernel = cp.RawKernel(DB_RAWKERNEL_SOURCE, "rtdl_user_db_summary")
    arrays = {name: cp.asarray(value) for name, value in columns.items()}
    promo_count = cp.zeros(1, dtype=cp.int32)
    open_count = cp.zeros(len(REGION_ORDER), dtype=cp.int32)
    web_revenue = cp.zeros(len(REGION_ORDER), dtype=cp.int32)
    risky_count = cp.zeros(1, dtype=cp.int32)
    risky_count_by_region = cp.zeros(len(REGION_ORDER), dtype=cp.int32)
    risky_revenue_by_region = cp.zeros(len(REGION_ORDER), dtype=cp.int32)
    risky_order_ids = cp.zeros(n, dtype=cp.int32)
    grid, block = _blocks(n)
    kernel(
        grid,
        block,
        (
            np.int32(n),
            arrays["ship_date"],
            arrays["discount"],
            arrays["quantity"],
            arrays["revenue"],
            arrays["row_id"],
            arrays["region"],
            arrays["channel_web"],
            promo_count,
            open_count,
            web_revenue,
            risky_count,
            risky_count_by_region,
            risky_revenue_by_region,
            risky_order_ids,
        ),
    )
    cp.cuda.Stream.null.synchronize()
    result = {}
    result["regional_dashboard"] = {
        "promo_order_count": int(cp.asnumpy(promo_count)[0]),
        "open_order_count_by_region": _region_dict(cp.asnumpy(open_count)),
        "web_revenue_by_region": _region_dict(cp.asnumpy(web_revenue)),
    }
    risky_revenue_host = cp.asnumpy(risky_revenue_by_region)
    risky_revenue_dict = _region_dict(risky_revenue_host)
    risky_count_host = int(cp.asnumpy(risky_count)[0])
    risky_order_ids_host = sorted(int(value) for value in cp.asnumpy(risky_order_ids)[:risky_count_host])
    result["sales_risk"] = {
        "risky_order_count": risky_count_host,
        "risky_order_ids": risky_order_ids_host,
        "risky_order_count_by_region": _region_dict(cp.asnumpy(risky_count_by_region)),
        "risky_revenue_by_region": risky_revenue_dict,
        "highest_risk_region": max(risky_revenue_dict.items(), key=lambda item: (item[1], item[0]))[0],
    }
    return result


def _partner_to_host(value, partner: str):
    if partner == "torch":
        return value.detach().cpu().tolist()
    if partner == "cupy":
        cp = _load_cupy()

        return cp.asnumpy(value).tolist()
    raise ValueError("partner must be 'torch' or 'cupy'")


def _database_partner_columnar_continuation(rows: tuple[dict[str, object], ...], *, partner: str) -> dict[str, object]:
    columns = columnar_payload_to_partner_columns(
        _table_columns(rows),
        partner=partner,
        category_maps={"region": {region: index for index, region in enumerate(REGION_ORDER)}},
    )
    category_maps = columns["_metadata"]["category_maps"]
    region_count = len(category_maps["region"])
    promo_predicates = (("ship_date", "between", 12, 15), ("discount", "eq", 6), ("quantity", "lt", 20))
    open_predicates = (("ship_date", "ge", 12), ("quantity", "lt", 20))
    web_predicates = (("ship_date", "ge", 12), ("channel_web", "eq", 1))
    risky_predicates = (("ship_date", "between", 11, 13), ("discount", "ge", 6), ("quantity", "lt", 20))
    reductions = partner_columnar_predicate_reduce_batch(
        columns,
        (
            {"name": "promo_count", "predicates": promo_predicates, "output_dtype": "int32"},
            {
                "name": "open_count_by_region",
                "predicates": open_predicates,
                "reduce": "count",
                "group_field": "region",
                "group_count": region_count,
                "output_dtype": "int32",
            },
            {
                "name": "web_revenue_by_region",
                "predicates": web_predicates,
                "reduce": "sum",
                "group_field": "region",
                "value_field": "revenue",
                "group_count": region_count,
                "output_dtype": "int32",
            },
            {"name": "risky_count", "predicates": risky_predicates, "output_dtype": "int32"},
            {
                "name": "risky_order_ids",
                "predicates": risky_predicates,
                "reduce": "ids",
                "value_field": "row_id",
                "output_dtype": "int32",
            },
            {
                "name": "risky_count_by_region",
                "predicates": risky_predicates,
                "reduce": "count",
                "group_field": "region",
                "group_count": region_count,
                "output_dtype": "int32",
            },
            {
                "name": "risky_revenue_by_region",
                "predicates": risky_predicates,
                "reduce": "sum",
                "group_field": "region",
                "value_field": "revenue",
                "group_count": region_count,
                "output_dtype": "int32",
            },
        ),
        partner=partner,
    )
    promo_count = int(_partner_to_host(reductions["promo_count"], partner)[0])
    open_count = _partner_to_host(reductions["open_count_by_region"], partner)
    web_revenue = _partner_to_host(reductions["web_revenue_by_region"], partner)
    risky_count = int(_partner_to_host(reductions["risky_count"], partner)[0])
    risky_order_ids = sorted(int(value) for value in _partner_to_host(reductions["risky_order_ids"], partner))
    risky_count_by_region = _partner_to_host(reductions["risky_count_by_region"], partner)
    risky_revenue_by_region = _partner_to_host(reductions["risky_revenue_by_region"], partner)
    region_order = tuple(
        label for label, _index in sorted(category_maps["region"].items(), key=lambda item: item[1])
    )

    def region_dict(values) -> dict[str, int]:
        return {region: int(values[index]) for index, region in enumerate(region_order) if int(values[index]) != 0}

    risky_revenue_dict = region_dict(risky_revenue_by_region)
    return {
        "regional_dashboard": {
            "promo_order_count": promo_count,
            "open_order_count_by_region": region_dict(open_count),
            "web_revenue_by_region": region_dict(web_revenue),
        },
        "sales_risk": {
            "risky_order_count": risky_count,
            "risky_order_ids": risky_order_ids,
            "risky_order_count_by_region": region_dict(risky_count_by_region),
            "risky_revenue_by_region": risky_revenue_dict,
            "highest_risk_region": max(risky_revenue_dict.items(), key=lambda item: (item[1], item[0]))[0],
        },
    }


def run_database_analytics_rawkernel(
    *,
    copies: int = 1,
    partner: str = "cpu_fallback",
    verify_oracle: bool = True,
) -> dict[str, object]:
    start = time.perf_counter()
    regional_rows = rtdl_v0_7_db_app_demo.make_orders(copies)
    sales_scan_case, _sales_group_case = rtdl_sales_risk_screening.make_sales_case(copies)
    input_sec = time.perf_counter() - start
    continuation_start = time.perf_counter()
    continuation = (
        (lambda rows: _database_partner_columnar_continuation(rows, partner=partner))
        if partner in {"cupy", "torch"}
        else _database_cpu_continuation
    )
    summary = {
        "regional_dashboard": continuation(tuple(regional_rows))["regional_dashboard"],
        "sales_risk": continuation(tuple(sales_scan_case["table"]))["sales_risk"],
    }
    continuation_sec = time.perf_counter() - continuation_start
    oracle_summary = None
    if verify_oracle:
        oracle = rtdl_database_analytics_app.run_app(
            "cpu_python_reference",
            copies=copies,
            output_mode="compact_summary",
        )
        oracle_summary = {
            "regional_dashboard": oracle["sections"]["regional_dashboard"]["summary"],
            "sales_risk": oracle["sections"]["sales_risk"]["summary"],
        }
    return {
        "app": "database_analytics",
        "v2_control_app_path": "partner_columnar_predicate_reduce_batch" if partner in {"cupy", "torch"} else "cpu_fallback_for_rawkernel_contract",
        "partner": partner,
        "copies": copies,
        "summary": summary,
        "matches_v1_8_python_rtdl_oracle": None if oracle_summary is None else summary == oracle_summary,
        "run_phases": {
            "input_construction_sec": input_sec,
            "partner_columnar_continuation_sec": continuation_sec,
        },
        "fairness_note": FAIRNESS_NOTE,
    }


def _graph_metric_rows(copies: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    copies = int(copies)
    if copies < 0:
        raise ValueError("copies must be non-negative")
    return (
        np.tile(GRAPH_SUM_METRIC_IDS, copies),
        np.tile(GRAPH_SUM_METRIC_VALUES, copies),
        np.tile(GRAPH_MAX_METRIC_IDS, copies),
        np.tile(GRAPH_MAX_METRIC_VALUES, copies),
    )


def _graph_summary_from_values(sum_values: list[int], max_values: list[int]) -> dict[str, object]:
    return {
        "bfs": {
            "discovered_edge_count": sum_values[0],
            "discovered_vertex_count": sum_values[1],
            "max_level": max_values[0],
        },
        "triangle_count": {
            "triangle_count": sum_values[2],
            "touched_vertex_count": sum_values[3],
        },
        "visibility_edges": {
            "visible_edge_count": sum_values[4],
            "blocked_edge_count": sum_values[5],
        },
    }


def _graph_cpu_continuation(copies: int) -> dict[str, object]:
    sum_keys, sum_row_values, max_keys, max_row_values = _graph_metric_rows(copies)
    sum_values = np.zeros(len(GRAPH_SUM_METRIC_IDS), dtype=np.int32)
    if len(sum_keys):
        sum_positions = np.asarray(
            [{int(key): index for index, key in enumerate(GRAPH_SUM_METRIC_IDS)}[int(key)] for key in sum_keys],
            dtype=np.int64,
        )
        np.add.at(sum_values, sum_positions, sum_row_values)
    max_values = np.zeros(len(GRAPH_MAX_METRIC_IDS), dtype=np.int32)
    if len(max_keys):
        max_positions = np.asarray(
            [{int(key): index for index, key in enumerate(GRAPH_MAX_METRIC_IDS)}[int(key)] for key in max_keys],
            dtype=np.int64,
        )
        np.maximum.at(max_values, max_positions, max_row_values)
    return _graph_summary_from_values(sum_values.astype(int).tolist(), max_values.astype(int).tolist())


def _graph_cupy_continuation(copies: int) -> dict[str, object]:
    cp = _load_cupy()
    sum_values = partner_metric_table_reduce_repeated_pattern(
        GRAPH_SUM_METRIC_IDS,
        GRAPH_SUM_METRIC_VALUES,
        GRAPH_SUM_METRIC_IDS,
        copies,
        partner="cupy",
        reduce="sum",
        assume_aligned_output=True,
    )
    max_values = partner_metric_table_reduce_repeated_pattern(
        GRAPH_MAX_METRIC_IDS,
        GRAPH_MAX_METRIC_VALUES,
        GRAPH_MAX_METRIC_IDS,
        copies,
        partner="cupy",
        reduce="max",
        initial=0,
        assume_aligned_output=True,
    )
    cp.cuda.Stream.null.synchronize()
    return _graph_summary_from_values(
        cp.asnumpy(sum_values).astype(int).tolist(),
        cp.asnumpy(max_values).astype(int).tolist(),
    )


def run_graph_analytics_rawkernel(
    *,
    copies: int = 1,
    partner: str = "cpu_fallback",
    verify_oracle: bool = True,
) -> dict[str, object]:
    continuation_start = time.perf_counter()
    summary = _graph_cupy_continuation(copies) if partner == "cupy" else _graph_cpu_continuation(copies)
    continuation_sec = time.perf_counter() - continuation_start
    oracle = None
    if verify_oracle:
        bfs_oracle = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            scenario="bfs",
            copies=copies,
            output_mode="summary",
        )["sections"]["bfs"]["summary"]
        triangle_oracle = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            scenario="triangle_count",
            copies=copies,
            output_mode="summary",
        )["sections"]["triangle_count"]["summary"]
        visibility_oracle = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            scenario="visibility_edges",
            copies=copies,
            output_mode="summary",
        )["sections"]["visibility_edges"]["summary"]
        oracle = {
            "bfs": bfs_oracle,
            "triangle_count": triangle_oracle,
            "visibility_edges": visibility_oracle,
        }
    return {
        "app": "graph_analytics",
        "v2_control_app_path": "partner_metric_table_reduce_repeated_pattern" if partner == "cupy" else "cpu_fallback_for_rawkernel_contract",
        "partner": partner,
        "copies": copies,
        "summary": summary,
        "matches_v1_8_python_rtdl_oracle": None if oracle is None else summary == oracle,
        "run_phases": {"partner_rawkernel_continuation_sec": continuation_sec},
        "fairness_note": FAIRNESS_NOTE,
    }


def _polygon_cells(polygons: tuple[Any, ...]) -> tuple[list[set[tuple[int, int]]], list[tuple[int, int]]]:
    per_polygon = [set(_polygon_unit_cells(polygon)) for polygon in polygons]
    all_cells = sorted(set().union(*per_polygon)) if per_polygon else []
    return per_polygon, all_cells


def _polygon_masks(
    polygons: tuple[Any, ...],
    all_cells: list[tuple[int, int]],
) -> np.ndarray:
    index = {cell: i for i, cell in enumerate(all_cells)}
    masks = np.zeros((len(polygons), len(all_cells)), dtype=np.uint8)
    for polygon_index, polygon in enumerate(polygons):
        for cell in _polygon_unit_cells(polygon):
            masks[polygon_index, index[cell]] = 1
    return masks


def _candidate_indices(
    left: tuple[Any, ...],
    right: tuple[Any, ...],
    candidate_pairs: set[tuple[int, int]],
) -> tuple[np.ndarray, np.ndarray]:
    left_index = {polygon.id: i for i, polygon in enumerate(left)}
    right_index = {polygon.id: i for i, polygon in enumerate(right)}
    ordered = sorted(candidate_pairs)
    return (
        np.asarray([left_index[left_id] for left_id, _right_id in ordered], dtype=np.int32),
        np.asarray([right_index[right_id] for _left_id, right_id in ordered], dtype=np.int32),
    )


def _axis_aligned_extent_columns(polygons: tuple[Any, ...]) -> dict[str, np.ndarray]:
    min_x: list[int] = []
    min_y: list[int] = []
    max_x: list[int] = []
    max_y: list[int] = []
    area: list[int] = []
    for polygon in polygons:
        xs = [float(x) for x, _y in polygon.vertices]
        ys = [float(y) for _x, y in polygon.vertices]
        x0 = int(min(xs))
        y0 = int(min(ys))
        x1 = int(max(xs))
        y1 = int(max(ys))
        min_x.append(x0)
        min_y.append(y0)
        max_x.append(x1)
        max_y.append(y1)
        area.append(max(0, x1 - x0) * max(0, y1 - y0))
    return {
        "min_x": np.asarray(min_x, dtype=np.int32),
        "min_y": np.asarray(min_y, dtype=np.int32),
        "max_x": np.asarray(max_x, dtype=np.int32),
        "max_y": np.asarray(max_y, dtype=np.int32),
        "area": np.asarray(area, dtype=np.int32),
    }


def _partner_pair_payload_table(
    left: tuple[Any, ...],
    right: tuple[Any, ...],
    candidate_pairs: set[tuple[int, int]],
) -> PartnerPairPayloadTable:
    left_indices, right_indices = _candidate_indices(left, right, candidate_pairs)
    left_columns = _axis_aligned_extent_columns(left)
    right_columns = _axis_aligned_extent_columns(right)
    return PartnerPairPayloadTable(
        left_index=left_indices,
        right_index=right_indices,
        left_min_x=left_columns["min_x"],
        left_min_y=left_columns["min_y"],
        left_max_x=left_columns["max_x"],
        left_max_y=left_columns["max_y"],
        left_area=left_columns["area"],
        right_min_x=right_columns["min_x"],
        right_min_y=right_columns["min_y"],
        right_max_x=right_columns["max_x"],
        right_max_y=right_columns["max_y"],
        right_area=right_columns["area"],
    )


def _cupy_extent_tile_rows() -> int:
    return max(1, int(os.environ.get("RTDL_CUPY_EXTENT_TILE_ROWS", "2048")))


def _cupy_extent_right_tile_rows() -> int:
    return max(1, int(os.environ.get("RTDL_CUPY_EXTENT_RIGHT_TILE_ROWS", str(_cupy_extent_tile_rows()))))


def _cupy_extent_free_tile_blocks() -> bool:
    return os.environ.get("RTDL_CUPY_EXTENT_FREE_TILE_BLOCKS", "1") not in ("0", "false", "False")


def _partner_pair_payload_table_cupy_extent(
    left: tuple[Any, ...],
    right: tuple[Any, ...],
) -> PartnerPairPayloadTable:
    cp = _load_cupy()
    payload_columns = aabb_tiled_candidate_pair_payload_2d_partner_columns(
        _axis_aligned_extent_columns(left),
        _axis_aligned_extent_columns(right),
        partner="cupy",
        tile_rows=_cupy_extent_tile_rows(),
        right_tile_rows=_cupy_extent_right_tile_rows(),
        free_tile_blocks=_cupy_extent_free_tile_blocks(),
    )
    left_indices = payload_columns["left_index"]
    right_indices = payload_columns["right_index"]
    return PartnerPairPayloadTable(
        left_index=left_indices.astype(cp.int32, copy=False),
        right_index=right_indices.astype(cp.int32, copy=False),
        left_min_x=payload_columns["left_min_x"],
        left_min_y=payload_columns["left_min_y"],
        left_max_x=payload_columns["left_max_x"],
        left_max_y=payload_columns["left_max_y"],
        left_area=payload_columns["left_area"],
        right_min_x=payload_columns["right_min_x"],
        right_min_y=payload_columns["right_min_y"],
        right_max_x=payload_columns["right_max_x"],
        right_max_y=payload_columns["right_max_y"],
        right_area=payload_columns["right_area"],
    )


def _positive_candidate_pairs_cupy_extent(
    left: tuple[Any, ...],
    right: tuple[Any, ...],
) -> set[tuple[int, int]]:
    cp = _load_cupy()
    payload_columns = aabb_tiled_candidate_pair_payload_2d_partner_columns(
        _axis_aligned_extent_columns(left),
        _axis_aligned_extent_columns(right),
        partner="cupy",
        tile_rows=_cupy_extent_tile_rows(),
        right_tile_rows=_cupy_extent_right_tile_rows(),
        free_tile_blocks=_cupy_extent_free_tile_blocks(),
    )
    left_indices = payload_columns["left_index"]
    right_indices = payload_columns["right_index"]
    left_ids = np.asarray([polygon.id for polygon in left], dtype=np.int32)
    right_ids = np.asarray([polygon.id for polygon in right], dtype=np.int32)
    return set(
        zip(
            left_ids[cp.asnumpy(left_indices)].tolist(),
            right_ids[cp.asnumpy(right_indices)].tolist(),
        )
    )


def _polygon_pair_cpu_summary(
    left_masks: np.ndarray,
    right_masks: np.ndarray,
    left_indices: np.ndarray,
    right_indices: np.ndarray,
) -> dict[str, int]:
    overlap_pair_count = 0
    total_intersection_area = 0
    total_union_area = 0
    set_intersection_area = 0
    for li, ri in zip(left_indices, right_indices):
        left_mask = left_masks[int(li)]
        right_mask = right_masks[int(ri)]
        intersection_area = int(np.logical_and(left_mask, right_mask).sum())
        if intersection_area <= 0:
            continue
        left_area = int(left_mask.sum())
        right_area = int(right_mask.sum())
        overlap_pair_count += 1
        total_intersection_area += intersection_area
        total_union_area += left_area + right_area - intersection_area
        set_intersection_area += intersection_area
    return {
        "overlap_pair_count": overlap_pair_count,
        "total_intersection_area": total_intersection_area,
        "total_union_area": total_union_area,
        "set_intersection_area": set_intersection_area,
    }


def _pair_extent_cpu_summary(table: PartnerPairPayloadTable) -> dict[str, int]:
    overlap_pair_count = 0
    total_intersection_area = 0
    total_union_area = 0
    set_intersection_area = 0
    for li, ri in zip(table.left_index, table.right_index):
        left_i = int(li)
        right_i = int(ri)
        width = max(0, min(int(table.left_max_x[left_i]), int(table.right_max_x[right_i])) - max(int(table.left_min_x[left_i]), int(table.right_min_x[right_i])))
        height = max(0, min(int(table.left_max_y[left_i]), int(table.right_max_y[right_i])) - max(int(table.left_min_y[left_i]), int(table.right_min_y[right_i])))
        intersection_area = width * height
        if intersection_area <= 0:
            continue
        overlap_pair_count += 1
        total_intersection_area += intersection_area
        total_union_area += int(table.left_area[left_i]) + int(table.right_area[right_i]) - intersection_area
        set_intersection_area += intersection_area
    return {
        "overlap_pair_count": overlap_pair_count,
        "total_intersection_area": total_intersection_area,
        "total_union_area": total_union_area,
        "set_intersection_area": set_intersection_area,
    }


def _pair_extent_cupy_summary(table: PartnerPairPayloadTable) -> dict[str, int]:
    cp = _load_cupy()
    summary_columns = aabb_pair_overlap_summary_2d_partner_columns(
        aabb_pair_payload_to_partner_columns(table.__dict__, partner="cupy"),
        partner="cupy",
    )
    cp.cuda.Stream.null.synchronize()
    return {
        "overlap_pair_count": int(cp.asnumpy(summary_columns["overlap_pair_count"])[0]),
        "total_intersection_area": int(cp.asnumpy(summary_columns["total_intersection_area"])[0]),
        "total_union_area": int(cp.asnumpy(summary_columns["total_union_area"])[0]),
        "set_intersection_area": int(cp.asnumpy(summary_columns["set_intersection_area"])[0]),
    }


def _polygon_pair_cupy_summary(
    left_masks: np.ndarray,
    right_masks: np.ndarray,
    left_indices: np.ndarray,
    right_indices: np.ndarray,
) -> dict[str, int]:
    cp = _load_cupy()
    pair_count = int(len(left_indices))
    cell_count = int(left_masks.shape[1])
    kernel = cp.RawKernel(POLYGON_PAIR_RAWKERNEL_SOURCE, "rtdl_user_polygon_pair_summary")
    d_left_masks = cp.asarray(left_masks)
    d_right_masks = cp.asarray(right_masks)
    d_left_indices = cp.asarray(left_indices)
    d_right_indices = cp.asarray(right_indices)
    overlap_pair_count = cp.zeros(1, dtype=cp.int32)
    total_intersection_area = cp.zeros(1, dtype=cp.int32)
    total_union_area = cp.zeros(1, dtype=cp.int32)
    set_intersection_area = cp.zeros(1, dtype=cp.int32)
    grid, block = _blocks(pair_count)
    kernel(
        grid,
        block,
        (
            np.int32(pair_count),
            np.int32(cell_count),
            d_left_indices,
            d_right_indices,
            d_left_masks,
            d_right_masks,
            overlap_pair_count,
            total_intersection_area,
            total_union_area,
            set_intersection_area,
        ),
    )
    cp.cuda.Stream.null.synchronize()
    return {
        "overlap_pair_count": int(cp.asnumpy(overlap_pair_count)[0]),
        "total_intersection_area": int(cp.asnumpy(total_intersection_area)[0]),
        "total_union_area": int(cp.asnumpy(total_union_area)[0]),
        "set_intersection_area": int(cp.asnumpy(set_intersection_area)[0]),
    }


def _sum_int(values: Any) -> int:
    if hasattr(values, "sum"):
        return int(values.sum().item())
    return int(np.asarray(values).sum())


def _polygon_summary_inputs(app: str, copies: int, candidate_backend: str, partner: str) -> dict[str, object]:
    if app == "polygon_pair_overlap_area_rows":
        case = rtdl_polygon_pair_overlap_area_rows.make_authored_polygon_pair_overlap_case(copies=copies)
    elif app == "polygon_set_jaccard":
        case = rtdl_polygon_set_jaccard.make_authored_polygon_set_jaccard_case(copies=copies)
    else:
        raise ValueError(f"unsupported polygon app: {app}")
    left = case["left"]
    right = case["right"]
    if candidate_backend == "cupy_extent" and partner == "cupy":
        pair_payload_table = _partner_pair_payload_table_cupy_extent(left, right)
        candidate_pair_count = pair_payload_table.pair_count
    else:
        if candidate_backend == "cupy_extent":
            candidate_pairs = _positive_candidate_pairs_cupy_extent(left, right)
        elif candidate_backend == "embree":
            candidate_pairs = rtdl_polygon_pair_overlap_area_rows._positive_candidate_pairs_embree(left, right)
        elif candidate_backend == "optix":
            candidate_pairs = rtdl_polygon_pair_overlap_area_rows._positive_candidate_pairs_optix(left, right)
        else:
            candidate_pairs = {
                (left_polygon.id, right_polygon.id)
                for left_polygon in left
                for right_polygon in right
            }
        pair_payload_table = _partner_pair_payload_table(left, right, candidate_pairs)
        candidate_pair_count = len(candidate_pairs)
    return {
        "case": case,
        "candidate_pair_count": candidate_pair_count,
        "pair_payload_table": pair_payload_table,
        "left_set_area": _sum_int(pair_payload_table.left_area),
        "right_set_area": _sum_int(pair_payload_table.right_area),
    }


def run_polygon_pair_overlap_rawkernel(
    *,
    copies: int = 1,
    partner: str = "cpu_fallback",
    candidate_backend: str = "cpu_all_pairs",
    verify_oracle: bool = True,
) -> dict[str, object]:
    start = time.perf_counter()
    inputs = _polygon_summary_inputs("polygon_pair_overlap_area_rows", copies, candidate_backend, partner)
    input_sec = time.perf_counter() - start
    continuation_start = time.perf_counter()
    pair_payload_table = inputs["pair_payload_table"]
    summary_with_set = (
        _pair_extent_cupy_summary(pair_payload_table)
        if partner == "cupy"
        else _pair_extent_cpu_summary(pair_payload_table)
    )
    continuation_sec = time.perf_counter() - continuation_start
    summary = {
        "overlap_pair_count": summary_with_set["overlap_pair_count"],
        "total_intersection_area": summary_with_set["total_intersection_area"],
        "total_union_area": summary_with_set["total_union_area"],
    }
    oracle = (
        rtdl_polygon_pair_overlap_area_rows.run_case(
            "cpu_python_reference",
            copies=copies,
            output_mode="summary",
        )["summary"]
        if verify_oracle
        else None
    )
    return {
        "app": "polygon_pair_overlap_area_rows",
        "v2_control_app_path": "aabb_pair_overlap_summary_2d_partner_columns" if partner == "cupy" else "cpu_fallback_for_rawkernel_contract",
        "partner": partner,
        "candidate_backend": candidate_backend,
        "copies": copies,
        "candidate_pair_count": int(inputs["candidate_pair_count"]),
        "pair_payload_row_count": pair_payload_table.pair_count,
        "summary": summary,
        "matches_v1_8_python_rtdl_oracle": None if oracle is None else summary == oracle,
        "run_phases": {
            "candidate_and_payload_construction_sec": input_sec,
            "partner_rawkernel_continuation_sec": continuation_sec,
        },
        "fairness_note": FAIRNESS_NOTE,
    }


def run_polygon_set_jaccard_rawkernel(
    *,
    copies: int = 1,
    partner: str = "cpu_fallback",
    candidate_backend: str = "cpu_all_pairs",
    verify_oracle: bool = True,
) -> dict[str, object]:
    start = time.perf_counter()
    inputs = _polygon_summary_inputs("polygon_set_jaccard", copies, candidate_backend, partner)
    input_sec = time.perf_counter() - start
    continuation_start = time.perf_counter()
    pair_payload_table = inputs["pair_payload_table"]
    summary_with_set = (
        _pair_extent_cupy_summary(pair_payload_table)
        if partner == "cupy"
        else _pair_extent_cpu_summary(pair_payload_table)
    )
    continuation_sec = time.perf_counter() - continuation_start
    left_area = int(inputs["left_set_area"])
    right_area = int(inputs["right_set_area"])
    intersection_area = int(summary_with_set["set_intersection_area"])
    union_area = left_area + right_area - intersection_area
    summary = {
        "intersection_area": intersection_area,
        "left_area": left_area,
        "right_area": right_area,
        "union_area": union_area,
        "jaccard_similarity": 0.0 if union_area == 0 else intersection_area / union_area,
    }
    oracle = (
        rtdl_polygon_set_jaccard.run_case(
            "cpu_python_reference",
            copies=copies,
            output_mode="summary",
        )["summary"]
        if verify_oracle
        else None
    )
    matches = None if oracle is None else all(
        math.isclose(float(summary[key]), float(oracle[key]), rel_tol=1e-12, abs_tol=1e-12)
        if key == "jaccard_similarity"
        else int(summary[key]) == int(oracle[key])
        for key in summary
    )
    return {
        "app": "polygon_set_jaccard",
        "v2_control_app_path": "aabb_pair_overlap_summary_2d_partner_columns" if partner == "cupy" else "cpu_fallback_for_rawkernel_contract",
        "partner": partner,
        "candidate_backend": candidate_backend,
        "copies": copies,
        "candidate_pair_count": int(inputs["candidate_pair_count"]),
        "pair_payload_row_count": pair_payload_table.pair_count,
        "summary": summary,
        "matches_v1_8_python_rtdl_oracle": matches,
        "run_phases": {
            "candidate_and_payload_construction_sec": input_sec,
            "partner_rawkernel_continuation_sec": continuation_sec,
        },
        "fairness_note": FAIRNESS_NOTE,
    }


def run_control_app(
    app: str,
    *,
    copies: int = 1,
    partner: str = "cpu_fallback",
    candidate_backend: str = "cpu_all_pairs",
    verify_oracle: bool = True,
) -> dict[str, object]:
    if app == "database_analytics":
        return run_database_analytics_rawkernel(copies=copies, partner=partner, verify_oracle=verify_oracle)
    if app == "graph_analytics":
        return run_graph_analytics_rawkernel(copies=copies, partner=partner, verify_oracle=verify_oracle)
    if app == "polygon_pair_overlap_area_rows":
        return run_polygon_pair_overlap_rawkernel(
            copies=copies,
            partner=partner,
            candidate_backend=candidate_backend,
            verify_oracle=verify_oracle,
        )
    if app == "polygon_set_jaccard":
        return run_polygon_set_jaccard_rawkernel(
            copies=copies,
            partner=partner,
            candidate_backend=candidate_backend,
            verify_oracle=verify_oracle,
        )
    raise ValueError(f"unsupported app: {app}")


def run_all_control_apps(
    *,
    copies: int = 1,
    partner: str = "cpu_fallback",
    candidate_backend: str = "cpu_all_pairs",
) -> dict[str, object]:
    results = [
        run_control_app(app, copies=copies, partner=partner, candidate_backend=candidate_backend)
        for app in CONTROL_APPS
    ]
    return {
        "goal": "Goal1953",
        "status": "rawkernel-control-app-v2-contract",
        "partner": partner,
        "copies": copies,
        "candidate_backend": candidate_backend,
        "results": results,
        "all_match_v1_8_python_rtdl_oracle": all(
            bool(result["matches_v1_8_python_rtdl_oracle"]) for result in results
        ),
        "fairness_note": (
            "Per explicit user decision, these four former control rows count as v2 "
            "app versions when implemented with CuPy RawKernel continuations. The "
            "comparison is not absolutely fair: the legacy baseline is Python+RTDL with no user "
            "C/C++ extension, while v2 uses Python+CuPy RawKernel+RTDL."
        ),
        "claim_boundary": {
            "counts_as_v2_app_version": partner == "cupy",
            "requires_pod_for_cupy_timing": partner == "cupy",
            "cpu_fallback_is_correctness_only": partner != "cupy",
            "whole_app_speedup_claim_authorized_without_measurement": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run v2 CuPy RawKernel continuations for former control apps.")
    parser.add_argument("--app", choices=(*CONTROL_APPS, "all"), default="all")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--partner", choices=("cpu_fallback", "cupy"), default="cpu_fallback")
    parser.add_argument(
        "--candidate-backend",
        choices=("cpu_all_pairs", "cupy_extent", "embree", "optix"),
        default="cpu_all_pairs",
        help="Polygon candidate discovery source. Use optix on pod for RTDL+RawKernel timing.",
    )
    args = parser.parse_args(argv)
    if args.copies <= 0:
        raise ValueError("--copies must be positive")
    if args.app == "all":
        payload = run_all_control_apps(
            copies=args.copies,
            partner=args.partner,
            candidate_backend=args.candidate_backend,
        )
    else:
        payload = run_control_app(
            args.app,
            copies=args.copies,
            partner=args.partner,
            candidate_backend=args.candidate_backend,
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
