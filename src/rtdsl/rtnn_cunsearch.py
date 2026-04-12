from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CuNSearchAdapterConfig:
    binary_path: str
    source_root: str | None
    build_dir: str | None
    current_status: str
    notes: str


@dataclass(frozen=True)
class CuNSearchInvocationPlan:
    binary_path: str
    request_format: str
    workload: str
    target_dimension: str
    radius: float
    k_max: int
    notes: str


def resolve_cunsearch_binary(binary_path: str | Path | None = None) -> Path | None:
    candidate = binary_path or os.environ.get("RTDL_CUNSEARCH_BIN")
    if not candidate:
        return None
    resolved = Path(candidate).expanduser()
    if not resolved.is_absolute():
        resolved = Path.cwd() / resolved
    resolved = resolved.resolve()
    if not resolved.exists():
        return None
    if not resolved.is_file():
        return None
    return resolved


def cunsearch_available(binary_path: str | Path | None = None) -> bool:
    return resolve_cunsearch_binary(binary_path) is not None


def cunsearch_adapter_config(binary_path: str | Path | None = None) -> CuNSearchAdapterConfig:
    resolved = resolve_cunsearch_binary(binary_path)
    source_root = os.environ.get("RTDL_CUNSEARCH_SOURCE_ROOT")
    build_dir = os.environ.get("RTDL_CUNSEARCH_BUILD_DIR")
    if resolved is None:
        return CuNSearchAdapterConfig(
            binary_path="",
            source_root=source_root,
            build_dir=build_dir,
            current_status="planned",
            notes=(
                "cuNSearch is not configured locally; set RTDL_CUNSEARCH_BIN on the Linux host "
                "after a reproducible build is available."
            ),
        )
    return CuNSearchAdapterConfig(
        binary_path=str(resolved),
        source_root=source_root,
        build_dir=build_dir,
        current_status="binary_resolved",
        notes="Binary path is configured, but full adapter execution remains a later goal.",
    )


def plan_cunsearch_fixed_radius_neighbors(
    *,
    radius: float,
    k_max: int,
    binary_path: str | Path | None = None,
) -> CuNSearchInvocationPlan:
    resolved = resolve_cunsearch_binary(binary_path)
    if resolved is None:
        raise RuntimeError(
            "cuNSearch adapter is not online yet; set RTDL_CUNSEARCH_BIN to a built cuNSearch binary "
            "on the Linux validation host before running the first external adapter goal."
        )
    return CuNSearchInvocationPlan(
        binary_path=str(resolved),
        request_format="json_request_v1",
        workload="fixed_radius_neighbors",
        target_dimension="3d",
        radius=radius,
        k_max=k_max,
        notes=(
            "This is an invocation-plan skeleton only. It freezes the request contract without "
            "claiming the cuNSearch execution path is online."
        ),
    )


def _point_record(point) -> dict[str, float | int]:
    return {
        "id": int(point.id),
        "x": float(point.x),
        "y": float(point.y),
        "z": float(point.z),
    }


def write_cunsearch_fixed_radius_request(
    destination: str | Path,
    query_points,
    search_points,
    *,
    radius: float,
    k_max: int,
    binary_path: str | Path | None = None,
) -> Path:
    plan = plan_cunsearch_fixed_radius_neighbors(
        radius=radius,
        k_max=k_max,
        binary_path=binary_path,
    )
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "adapter": "cunsearch",
        "request_format": plan.request_format,
        "workload": plan.workload,
        "target_dimension": plan.target_dimension,
        "binary_path": plan.binary_path,
        "radius": radius,
        "k_max": k_max,
        "query_points": [_point_record(point) for point in query_points],
        "search_points": [_point_record(point) for point in search_points],
    }
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
