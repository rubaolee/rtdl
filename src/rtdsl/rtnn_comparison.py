from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Union, Optional

from .baseline_contracts import compare_baseline_rows
from .reference import fixed_radius_neighbors_cpu
from .rtnn_cunsearch import load_cunsearch_fixed_radius_response
from .rtnn_cunsearch import write_cunsearch_fixed_radius_request
from .rtnn_cunsearch_live import run_cunsearch_fixed_radius_request_live
from .rtnn_duplicate_audit import assess_cunsearch_duplicate_point_guard
from .rtnn_kitti import load_kitti_bounded_point_package


@dataclass(frozen=True)
class RtnnBoundedComparisonResult:
    workload: str
    query_point_count: int
    search_point_count: int
    reference_row_count: int
    external_row_count: int
    parity_ok: bool
    distance_abs_tol: float
    distance_rel_tol: float
    notes: str


def compare_bounded_fixed_radius_from_packages(
    *,
    query_package_path: Union[str, Path],
    search_package_path: Union[str, Path],
    external_response_path: Union[str, Path],
    radius: float,
    k_max: int,
    abs_tol: float = 1e-6,
    rel_tol: float = 1e-6,
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
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    )
    return RtnnBoundedComparisonResult(
        workload="fixed_radius_neighbors",
        query_point_count=len(query_package.points),
        search_point_count=len(search_package.points),
        reference_row_count=len(reference_rows),
        external_row_count=external_result.row_count,
        parity_ok=parity_ok,
        distance_abs_tol=abs_tol,
        distance_rel_tol=rel_tol,
        notes=(
            "This is a bounded offline comparison harness. It compares RTDL reference rows "
            "against a parsed external response artifact without claiming live third-party execution."
        ),
    )


def compare_bounded_fixed_radius_live_cunsearch(
    *,
    query_package_path: Union[str, Path],
    search_package_path: Union[str, Path],
    request_path: Union[str, Path],
    response_path: Union[str, Path],
    radius: float,
    k_max: int,
    cunsearch_source_root: Union[str, Path],
    cunsearch_build_root: Union[str, Path],
    nvcc_path: Union[str, Path] = "nvcc",
    abs_tol: float = 1e-6,
    rel_tol: float = 1e-6,
) -> RtnnBoundedComparisonResult:
    query_package = load_kitti_bounded_point_package(query_package_path)
    search_package = load_kitti_bounded_point_package(search_package_path)
    duplicate_guard = assess_cunsearch_duplicate_point_guard(
        query_package.points,
        search_package.points,
    )
    if not duplicate_guard.strict_comparison_allowed:
        first_duplicate = duplicate_guard.first_duplicate
        duplicate_note = ""
        if first_duplicate is not None:
            duplicate_note = (
                f" First duplicate pair: query {first_duplicate.query_id}, "
                f"search {first_duplicate.search_id}."
            )
        return RtnnBoundedComparisonResult(
            workload="fixed_radius_neighbors",
            query_point_count=len(query_package.points),
            search_point_count=len(search_package.points),
            reference_row_count=0,
            external_row_count=0,
            parity_ok=False,
            distance_abs_tol=abs_tol,
            distance_rel_tol=rel_tol,
            notes=(
                "Strict live cuNSearch comparison was blocked because the package contains exact "
                "cross-package duplicate points, which are outside the current validated cuNSearch "
                f"parity contract.{duplicate_note}"
            ),
        )
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
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    )
    return RtnnBoundedComparisonResult(
        workload=result.workload,
        query_point_count=result.query_point_count,
        search_point_count=result.search_point_count,
        reference_row_count=result.reference_row_count,
        external_row_count=result.external_row_count,
        parity_ok=result.parity_ok,
        distance_abs_tol=result.distance_abs_tol,
        distance_rel_tol=result.distance_rel_tol,
        notes=(
            "This is a live bounded Linux comparison using a built cuNSearch library and the same "
            "portable RTDL point packages on both sides."
        ),
    )
