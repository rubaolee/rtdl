from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KittiLinuxReadyReport:
    source_root: str
    exists: bool
    velodyne_dir_count: int
    velodyne_bin_count: int
    sample_velodyne_dirs: tuple[str, ...]
    sample_bin_files: tuple[str, ...]
    current_status: str
    notes: str


def inspect_kitti_linux_source_root(source_root: str | Path) -> KittiLinuxReadyReport:
    root = Path(source_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return KittiLinuxReadyReport(
            source_root=str(root),
            exists=False,
            velodyne_dir_count=0,
            velodyne_bin_count=0,
            sample_velodyne_dirs=(),
            sample_bin_files=(),
            current_status="missing",
            notes="KITTI source root does not exist yet on Linux.",
        )

    velodyne_dirs = sorted(path for path in root.rglob("velodyne") if path.is_dir())
    bin_files = sorted(
        path for path in root.rglob("*.bin") if "velodyne" in path.relative_to(root).parts
    )
    status = "ready" if bin_files else "empty"
    notes = (
        "KITTI source root contains Velodyne binary files and is ready for bounded package preparation."
        if bin_files
        else "KITTI source root exists, but no Velodyne binary files were found yet."
    )
    return KittiLinuxReadyReport(
        source_root=str(root),
        exists=True,
        velodyne_dir_count=len(velodyne_dirs),
        velodyne_bin_count=len(bin_files),
        sample_velodyne_dirs=tuple(path.relative_to(root).as_posix() for path in velodyne_dirs[:5]),
        sample_bin_files=tuple(path.relative_to(root).as_posix() for path in bin_files[:5]),
        current_status=status,
        notes=notes,
    )


def write_kitti_linux_ready_report(
    source_root: str | Path,
    destination: str | Path,
) -> Path:
    report = inspect_kitti_linux_source_root(source_root)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "report_kind": "kitti_linux_ready_report_v1",
        "report": asdict(report),
    }
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
