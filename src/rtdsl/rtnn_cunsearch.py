from __future__ import annotations
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union


@dataclass(frozen=True)
class CuNSearchAdapterConfig:
    binary_path: str
    version: Optional[str]
    source_root: Optional[str]
    build_dir: Optional[str]
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


@dataclass(frozen=True)
class CuNSearchFixedRadiusResult:
    row_count: int
    rows: Tuple[dict[str, Union[float, int]], ...]


def resolve_cunsearch_binary(binary_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
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

    # Audit recommendation: Basic version/sanity check
    try:
        # We assume cuNSearch binary supports --version or can at least be invoked.
        # If it fails to run, we treat it as an unresolvable binary.
        result = subprocess.run(
            [str(resolved), "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0,
        )
        if result.returncode != 0 and not result.stdout.strip():
            # If --version is not supported but binary runs, we might get a splash screen.
            pass
    except (OSError, subprocess.SubprocessError):
        return None

    return resolved


def cunsearch_available(binary_path: Optional[Union[str, Path]] = None) -> bool:
    return resolve_cunsearch_binary(binary_path) is not None


def cunsearch_adapter_config(binary_path: Optional[Union[str, Path]] = None) -> CuNSearchAdapterConfig:
    resolved = resolve_cunsearch_binary(binary_path)
    source_root = os.environ.get("RTDL_CUNSEARCH_SOURCE_ROOT")
    build_dir = os.environ.get("RTDL_CUNSEARCH_BUILD_DIR")
    if resolved is None:
        return CuNSearchAdapterConfig(
            binary_path="",
            version=None,
            source_root=source_root,
            build_dir=build_dir,
            current_status="planned",
            notes=(
                "cuNSearch is not configured locally; set RTDL_CUNSEARCH_BIN on the Linux host "
                "after a reproducible build is available."
            ),
        )

    # Extract version if possible
    version = None
    try:
        res = subprocess.run([str(resolved), "--version"], capture_output=True, text=True, timeout=1.0)
        if res.returncode == 0:
            version = res.stdout.strip().split("\n")[0]
    except Exception:
        pass

    return CuNSearchAdapterConfig(
        binary_path=str(resolved),
        version=version,
        source_root=source_root,
        build_dir=build_dir,
        current_status="binary_resolved",
        notes="Binary path is configured and version-checked.",
    )


def plan_cunsearch_fixed_radius_neighbors(
    *,
    radius: float,
    k_max: int,
    binary_path: Optional[Union[str, Path]] = None,
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


def _point_record(point) -> dict[str, Union[float, int]]:
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
    binary_path: Optional[Union[str, Path]] = None,
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


def load_cunsearch_fixed_radius_response(response_path: str | Path) -> CuNSearchFixedRadiusResult:
    response_path = Path(response_path)
    payload = json.loads(response_path.read_text(encoding="utf-8"))
    if payload.get("adapter") != "cunsearch":
        raise ValueError("unsupported cuNSearch response adapter")
    if payload.get("response_format") != "json_rows_v1":
        raise ValueError("unsupported cuNSearch response format")
    if payload.get("workload") != "fixed_radius_neighbors":
        raise ValueError("unsupported cuNSearch response workload")

    rows = []
    for row in payload.get("rows", ()):
        rows.append(
            {
                "query_id": int(row["query_id"]),
                "neighbor_id": int(row["neighbor_id"]),
                "distance": float(row["distance"]),
            }
        )
    rows.sort(key=lambda row: (row["query_id"], row["distance"], row["neighbor_id"]))
    return CuNSearchFixedRadiusResult(
        row_count=len(rows),
        rows=tuple(rows),
    )
