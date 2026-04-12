from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .baseline_contracts import compare_baseline_rows
from .reference import fixed_radius_neighbors_cpu
from .rtnn_cunsearch import load_cunsearch_fixed_radius_response
from .rtnn_cunsearch import write_cunsearch_fixed_radius_request
from .rtnn_cunsearch_live import run_cunsearch_fixed_radius_request_live
from .rtnn_kitti import load_kitti_bounded_point_package


@dataclass(frozen=True)
class RtnnBoundedComparisonResult:
    workload: str
    query_point_count: int
    search_point_count: int
    reference_row_count: int
    external_row_count: int
    parity_ok: bool
    notes: str


def compare_bounded_fixed_radius_from_packages(
    *,
    query_package_path: str | Path,
    search_package_path: str | Path,
    external_response_path: str | Path,
    radius: float,
    k_max: int,
) -> RtnnBoundedComparisonResult:
    query_package = load_kitti_bounded_point_package(query_package_path)
    search_package = load_kitti_bounded_point_package(search_package_path)
    external_result = load_cunsearch_fixed_radius_response(external_response_path)

    reference_rows = fixed_radius_neighbors_cpu(
        query_package.points,
        search_package.points,
        radius=radius,
        k_max=k_max,
    )
    parity_ok = compare_baseline_rows(
        "fixed_radius_neighbors",
        reference_rows,
        external_result.rows,
    )
    return RtnnBoundedComparisonResult(
        workload="fixed_radius_neighbors",
        query_point_count=len(query_package.points),
        search_point_count=len(search_package.points),
        reference_row_count=len(reference_rows),
        external_row_count=external_result.row_count,
        parity_ok=parity_ok,
        notes=(
            "This is a bounded offline comparison harness. It compares RTDL reference rows "
            "against a parsed external response artifact without claiming live third-party execution."
        ),
    )


def compare_bounded_fixed_radius_live_cunsearch(
    *,
    query_package_path: str | Path,
    search_package_path: str | Path,
    request_path: str | Path,
    response_path: str | Path,
    radius: float,
    k_max: int,
    cunsearch_source_root: str | Path,
    cunsearch_build_root: str | Path,
    nvcc_path: str | Path = "nvcc",
) -> RtnnBoundedComparisonResult:
    query_package = load_kitti_bounded_point_package(query_package_path)
    search_package = load_kitti_bounded_point_package(search_package_path)
    write_cunsearch_fixed_radius_request(
        request_path,
        query_package.points,
        search_package.points,
        radius=radius,
        k_max=k_max,
        binary_path=str(Path(cunsearch_build_root) / "demo" / "Demo"),
    )
    run_cunsearch_fixed_radius_request_live(
        request_path,
        response_path,
        source_root=cunsearch_source_root,
        build_root=cunsearch_build_root,
        nvcc_path=nvcc_path,
    )
    result = compare_bounded_fixed_radius_from_packages(
        query_package_path=query_package_path,
        search_package_path=search_package_path,
        external_response_path=response_path,
        radius=radius,
        k_max=k_max,
    )
    return RtnnBoundedComparisonResult(
        workload=result.workload,
        query_point_count=result.query_point_count,
        search_point_count=result.search_point_count,
        reference_row_count=result.reference_row_count,
        external_row_count=result.external_row_count,
        parity_ok=result.parity_ok,
        notes=(
            "This is a live bounded Linux comparison using a built cuNSearch library and the same "
            "portable RTDL point packages on both sides."
        ),
    )
