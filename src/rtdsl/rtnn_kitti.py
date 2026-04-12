from __future__ import annotations

import json
import os
import struct
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path

from .reference import Point3D


@dataclass(frozen=True)
class KittiSourceConfig:
    source_root: str
    current_status: str
    notes: str


@dataclass(frozen=True)
class KittiFrameRecord:
    sequence: str
    frame_id: str
    relative_bin_path: str


@dataclass(frozen=True)
class KittiBoundedPointPackage:
    points: tuple[Point3D, ...]
    selected_frame_count: int
    selected_point_count: int
    max_points_per_frame: int
    max_total_points: int


def resolve_kitti_source_root(source_root: str | Path | None = None) -> Path | None:
    candidate = source_root or os.environ.get("RTDL_KITTI_SOURCE_ROOT")
    if not candidate:
        return None
    resolved = Path(candidate).expanduser()
    if not resolved.is_absolute():
        resolved = Path.cwd() / resolved
    resolved = resolved.resolve()
    if not resolved.exists() or not resolved.is_dir():
        return None
    return resolved


def kitti_source_config(source_root: str | Path | None = None) -> KittiSourceConfig:
    resolved = resolve_kitti_source_root(source_root)
    if resolved is None:
        return KittiSourceConfig(
            source_root="",
            current_status="planned",
            notes=(
                "KITTI source root is not configured; set RTDL_KITTI_SOURCE_ROOT on the Linux "
                "host before building the first bounded local package."
            ),
        )
    return KittiSourceConfig(
        source_root=str(resolved),
        current_status="source_root_resolved",
        notes="KITTI source root is configured for bounded local package preparation.",
    )


def discover_kitti_velodyne_frames(source_root: str | Path | None = None) -> tuple[KittiFrameRecord, ...]:
    resolved = resolve_kitti_source_root(source_root)
    if resolved is None:
        raise RuntimeError(
            "KITTI source root is not configured; set RTDL_KITTI_SOURCE_ROOT before "
            "discovering bounded KITTI frames."
        )

    records: list[KittiFrameRecord] = []
    for bin_path in sorted(resolved.rglob("*.bin")):
        parts = bin_path.relative_to(resolved).parts
        if "velodyne" not in parts:
            continue
        velodyne_index = parts.index("velodyne")
        sequence = parts[velodyne_index - 1] if velodyne_index >= 1 else "unknown_sequence"
        frame_id = Path(parts[-1]).stem
        records.append(
            KittiFrameRecord(
                sequence=sequence,
                frame_id=frame_id,
                relative_bin_path=bin_path.relative_to(resolved).as_posix(),
            )
        )
    records.sort(key=lambda record: (record.sequence, record.frame_id, record.relative_bin_path))
    return tuple(records)


def select_kitti_bounded_frames(
    *,
    source_root: str | Path | None = None,
    max_frames: int,
    stride: int = 1,
) -> tuple[KittiFrameRecord, ...]:
    if max_frames <= 0:
        raise ValueError("max_frames must be positive")
    if stride <= 0:
        raise ValueError("stride must be positive")

    records = discover_kitti_velodyne_frames(source_root)
    selected = records[::stride][:max_frames]
    return tuple(selected)


def write_kitti_bounded_package_manifest(
    destination: str | Path,
    *,
    source_root: str | Path | None = None,
    max_frames: int,
    stride: int = 1,
    max_points_per_frame: int = 4096,
    max_total_points: int = 65536,
) -> Path:
    if max_points_per_frame <= 0:
        raise ValueError("max_points_per_frame must be positive")
    if max_total_points <= 0:
        raise ValueError("max_total_points must be positive")
    resolved = resolve_kitti_source_root(source_root)
    if resolved is None:
        raise RuntimeError(
            "KITTI source root is not configured; set RTDL_KITTI_SOURCE_ROOT before "
            "writing a bounded KITTI package manifest."
        )
    selected = select_kitti_bounded_frames(
        source_root=resolved,
        max_frames=max_frames,
        stride=stride,
    )
    payload = {
        "manifest_kind": "kitti_bounded_package_manifest_v1",
        "source_root": str(resolved),
        "max_frames": max_frames,
        "stride": stride,
        "max_points_per_frame": max_points_per_frame,
        "max_total_points": max_total_points,
        "bounded_point_rule": (
            "Within each selected frame, keep the first max_points_per_frame points in source order; "
            "then concatenate frames in manifest order and truncate once max_total_points is reached."
        ),
        "selected_frame_count": len(selected),
        "frames": [asdict(record) for record in selected],
    }
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def load_kitti_bounded_points_from_manifest(
    manifest_path: str | Path,
    *,
    point_id_start: int = 1,
) -> KittiBoundedPointPackage:
    if point_id_start <= 0:
        raise ValueError("point_id_start must be positive")
    manifest_path = Path(manifest_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("manifest_kind") != "kitti_bounded_package_manifest_v1":
        raise ValueError("unsupported KITTI bounded package manifest kind")

    source_root = Path(payload["source_root"])
    max_points_per_frame = int(payload["max_points_per_frame"])
    max_total_points = int(payload["max_total_points"])
    records = tuple(KittiFrameRecord(**record) for record in payload["frames"])

    points: list[Point3D] = []
    next_point_id = point_id_start
    for record in records:
        frame_points = _read_kitti_frame_points(source_root / record.relative_bin_path)
        for x, y, z in frame_points[:max_points_per_frame]:
            if len(points) >= max_total_points:
                return KittiBoundedPointPackage(
                    points=tuple(points),
                    selected_frame_count=len(records),
                    selected_point_count=len(points),
                    max_points_per_frame=max_points_per_frame,
                    max_total_points=max_total_points,
                )
            points.append(Point3D(id=next_point_id, x=x, y=y, z=z))
            next_point_id += 1

    return KittiBoundedPointPackage(
        points=tuple(points),
        selected_frame_count=len(records),
        selected_point_count=len(points),
        max_points_per_frame=max_points_per_frame,
        max_total_points=max_total_points,
    )


def write_kitti_bounded_point_package(
    destination: str | Path,
    manifest_path: str | Path,
    *,
    point_id_start: int = 1,
) -> Path:
    package = load_kitti_bounded_points_from_manifest(
        manifest_path,
        point_id_start=point_id_start,
    )
    payload = {
        "package_kind": "kitti_bounded_point_package_v1",
        "selected_frame_count": package.selected_frame_count,
        "selected_point_count": package.selected_point_count,
        "max_points_per_frame": package.max_points_per_frame,
        "max_total_points": package.max_total_points,
        "point_id_start": point_id_start,
        "points": [
            {
                "id": point.id,
                "x": point.x,
                "y": point.y,
                "z": point.z,
            }
            for point in package.points
        ],
    }
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def load_kitti_bounded_point_package(package_path: str | Path) -> KittiBoundedPointPackage:
    package_path = Path(package_path)
    payload = json.loads(package_path.read_text(encoding="utf-8"))
    if payload.get("package_kind") != "kitti_bounded_point_package_v1":
        raise ValueError("unsupported KITTI bounded point package kind")
    points = tuple(
        Point3D(
            id=int(point["id"]),
            x=float(point["x"]),
            y=float(point["y"]),
            z=float(point["z"]),
        )
        for point in payload["points"]
    )
    return KittiBoundedPointPackage(
        points=points,
        selected_frame_count=int(payload["selected_frame_count"]),
        selected_point_count=int(payload["selected_point_count"]),
        max_points_per_frame=int(payload["max_points_per_frame"]),
        max_total_points=int(payload["max_total_points"]),
    )


def _read_kitti_frame_points(bin_path: Path) -> tuple[tuple[float, float, float], ...]:
    if not bin_path.exists():
        raise RuntimeError(f"KITTI frame file is missing: {bin_path}")
    payload = bin_path.read_bytes()
    if len(payload) % 16 != 0:
        raise RuntimeError(
            f"KITTI frame file has invalid size {len(payload)} bytes; expected a multiple of 16."
        )

    points = []
    for x, y, z, _intensity in struct.iter_unpack("<ffff", payload):
        points.append((x, y, z))
    return tuple(points)
