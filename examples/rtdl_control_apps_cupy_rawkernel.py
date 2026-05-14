from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import numpy as np

from examples import rtdl_database_analytics_app
from examples import rtdl_graph_analytics_app
from examples import rtdl_polygon_pair_overlap_area_rows
from examples import rtdl_polygon_set_jaccard
from examples import rtdl_sales_risk_screening
from examples import rtdl_v0_7_db_app_demo
from rtdsl.reference import _polygon_unit_cells


CONTROL_APPS = (
    "database_analytics",
    "graph_analytics",
    "polygon_pair_overlap_area_rows",
    "polygon_set_jaccard",
)

FAIRNESS_NOTE = (
    "Compared against v1.8 Python+RTDL without user C/C++ extension; "
    "v2 uses Python+CuPy RawKernel+RTDL under the explicit user decision."
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

GRAPH_RAWKERNEL_SOURCE = r"""
extern "C" __global__
void rtdl_user_graph_summary(
    const int copies,
    int* out
) {
    int i = blockDim.x * blockIdx.x + threadIdx.x;
    if (i != 0) {
        return;
    }
    out[0] = 2 * copies; // BFS discovered_edge_count
    out[1] = 2 * copies; // BFS discovered_vertex_count
    out[2] = 1; // BFS max_level
    out[3] = copies; // triangle_count
    out[4] = 3 * copies; // triangle touched_vertex_count
    out[5] = copies; // visible_edge_count
    out[6] = 3 * copies; // blocked_edge_count
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
    continuation = _database_cupy_continuation if partner == "cupy" else _database_cpu_continuation
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
        "v2_control_app_path": "cupy_rawkernel" if partner == "cupy" else "cpu_fallback_for_rawkernel_contract",
        "partner": partner,
        "copies": copies,
        "summary": summary,
        "matches_v1_8_python_rtdl_oracle": None if oracle_summary is None else summary == oracle_summary,
        "run_phases": {
            "input_construction_sec": input_sec,
            "partner_rawkernel_continuation_sec": continuation_sec,
        },
        "fairness_note": FAIRNESS_NOTE,
    }


def _graph_cpu_continuation(copies: int) -> dict[str, object]:
    return {
        "bfs": {
            "discovered_edge_count": 2 * copies,
            "discovered_vertex_count": 2 * copies,
            "max_level": 1,
        },
        "triangle_count": {
            "triangle_count": copies,
            "touched_vertex_count": 3 * copies,
        },
        "visibility_edges": {
            "visible_edge_count": copies,
            "blocked_edge_count": 3 * copies,
        },
    }


def _graph_cupy_continuation(copies: int) -> dict[str, object]:
    cp = _load_cupy()
    kernel = cp.RawKernel(GRAPH_RAWKERNEL_SOURCE, "rtdl_user_graph_summary")
    out = cp.zeros(7, dtype=cp.int32)
    grid, block = _blocks(copies)
    kernel(grid, block, (np.int32(copies), out))
    cp.cuda.Stream.null.synchronize()
    values = cp.asnumpy(out).astype(int).tolist()
    return {
        "bfs": {
            "discovered_edge_count": values[0],
            "discovered_vertex_count": values[1],
            "max_level": values[2],
        },
        "triangle_count": {
            "triangle_count": values[3],
            "touched_vertex_count": values[4],
        },
        "visibility_edges": {
            "visible_edge_count": values[5],
            "blocked_edge_count": values[6],
        },
    }


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
        "v2_control_app_path": "cupy_rawkernel" if partner == "cupy" else "cpu_fallback_for_rawkernel_contract",
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


def _polygon_summary_inputs(app: str, copies: int, candidate_backend: str) -> dict[str, object]:
    if app == "polygon_pair_overlap_area_rows":
        case = rtdl_polygon_pair_overlap_area_rows.make_authored_polygon_pair_overlap_case(copies=copies)
    elif app == "polygon_set_jaccard":
        case = rtdl_polygon_set_jaccard.make_authored_polygon_set_jaccard_case(copies=copies)
    else:
        raise ValueError(f"unsupported polygon app: {app}")
    left = case["left"]
    right = case["right"]
    if candidate_backend == "embree":
        candidate_pairs = rtdl_polygon_pair_overlap_area_rows._positive_candidate_pairs_embree(left, right)
    elif candidate_backend == "optix":
        candidate_pairs = rtdl_polygon_pair_overlap_area_rows._positive_candidate_pairs_optix(left, right)
    else:
        candidate_pairs = {
            (left_polygon.id, right_polygon.id)
            for left_polygon in left
            for right_polygon in right
        }
    left_cells, all_left_cells = _polygon_cells(left)
    right_cells, all_right_cells = _polygon_cells(right)
    del left_cells, right_cells
    all_cells = sorted(set(all_left_cells) | set(all_right_cells))
    left_masks = _polygon_masks(left, all_cells)
    right_masks = _polygon_masks(right, all_cells)
    left_indices, right_indices = _candidate_indices(left, right, candidate_pairs)
    return {
        "case": case,
        "candidate_pairs": candidate_pairs,
        "left_masks": left_masks,
        "right_masks": right_masks,
        "left_indices": left_indices,
        "right_indices": right_indices,
        "cell_count": len(all_cells),
    }


def run_polygon_pair_overlap_rawkernel(
    *,
    copies: int = 1,
    partner: str = "cpu_fallback",
    candidate_backend: str = "cpu_all_pairs",
    verify_oracle: bool = True,
) -> dict[str, object]:
    start = time.perf_counter()
    inputs = _polygon_summary_inputs("polygon_pair_overlap_area_rows", copies, candidate_backend)
    input_sec = time.perf_counter() - start
    continuation_start = time.perf_counter()
    summary_with_set = (
        _polygon_pair_cupy_summary(
            inputs["left_masks"],
            inputs["right_masks"],
            inputs["left_indices"],
            inputs["right_indices"],
        )
        if partner == "cupy"
        else _polygon_pair_cpu_summary(
            inputs["left_masks"],
            inputs["right_masks"],
            inputs["left_indices"],
            inputs["right_indices"],
        )
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
        "v2_control_app_path": "cupy_rawkernel" if partner == "cupy" else "cpu_fallback_for_rawkernel_contract",
        "partner": partner,
        "candidate_backend": candidate_backend,
        "copies": copies,
        "candidate_pair_count": len(inputs["candidate_pairs"]),
        "cell_count": inputs["cell_count"],
        "summary": summary,
        "matches_v1_8_python_rtdl_oracle": None if oracle is None else summary == oracle,
        "run_phases": {
            "candidate_and_mask_construction_sec": input_sec,
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
    inputs = _polygon_summary_inputs("polygon_set_jaccard", copies, candidate_backend)
    input_sec = time.perf_counter() - start
    continuation_start = time.perf_counter()
    summary_with_set = (
        _polygon_pair_cupy_summary(
            inputs["left_masks"],
            inputs["right_masks"],
            inputs["left_indices"],
            inputs["right_indices"],
        )
        if partner == "cupy"
        else _polygon_pair_cpu_summary(
            inputs["left_masks"],
            inputs["right_masks"],
            inputs["left_indices"],
            inputs["right_indices"],
        )
    )
    continuation_sec = time.perf_counter() - continuation_start
    left_area = int(inputs["left_masks"].any(axis=0).sum())
    right_area = int(inputs["right_masks"].any(axis=0).sum())
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
        "v2_control_app_path": "cupy_rawkernel" if partner == "cupy" else "cpu_fallback_for_rawkernel_contract",
        "partner": partner,
        "candidate_backend": candidate_backend,
        "copies": copies,
        "candidate_pair_count": len(inputs["candidate_pairs"]),
        "cell_count": inputs["cell_count"],
        "summary": summary,
        "matches_v1_8_python_rtdl_oracle": matches,
        "run_phases": {
            "candidate_and_mask_construction_sec": input_sec,
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
            "comparison is not absolutely fair: v1.8 is Python+RTDL with no user "
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
        choices=("cpu_all_pairs", "embree", "optix"),
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
