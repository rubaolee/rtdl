from __future__ import annotations

import json
import os
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


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
) -> Path:
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
        "selected_frame_count": len(selected),
        "frames": [asdict(record) for record in selected],
    }
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
