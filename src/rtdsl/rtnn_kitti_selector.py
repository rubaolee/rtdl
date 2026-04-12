from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .rtnn_duplicate_audit import find_exact_cross_package_matches
from .rtnn_kitti import KittiFrameRecord
from .rtnn_kitti import load_kitti_bounded_points_from_manifest
from .rtnn_kitti import write_kitti_bounded_package_manifest


@dataclass(frozen=True)
class KittiDuplicateFreePair:
    query_start_index: int
    search_start_index: int
    query_record: KittiFrameRecord
    search_record: KittiFrameRecord
    query_point_count: int
    search_point_count: int
    duplicate_match_count: int
    notes: str


def find_duplicate_free_kitti_pair(
    *,
    source_root: str | Path,
    candidate_records: tuple[KittiFrameRecord, ...],
    query_start_index: int,
    max_search_offset: int,
    max_points_per_frame: int,
    max_total_points: int,
    work_dir: str | Path,
) -> KittiDuplicateFreePair:
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    if query_start_index < 0:
        raise ValueError("query_start_index must be non-negative")
    if max_search_offset <= 0:
        raise ValueError("max_search_offset must be positive")
    if query_start_index >= len(candidate_records):
        raise ValueError("query_start_index is outside the available KITTI frame range")

    query_record = candidate_records[query_start_index]
    for offset in range(1, max_search_offset + 1):
        search_start_index = query_start_index + offset
        if search_start_index >= len(candidate_records):
            break
        search_record = candidate_records[search_start_index]
        query_manifest = work_dir / f"query_{query_start_index}.json"
        search_manifest = work_dir / f"search_{search_start_index}.json"
        write_kitti_bounded_package_manifest(
            query_manifest,
            source_root=source_root,
            max_frames=1,
            start_index=query_start_index,
            max_points_per_frame=max_points_per_frame,
            max_total_points=max_total_points,
        )
        write_kitti_bounded_package_manifest(
            search_manifest,
            source_root=source_root,
            max_frames=1,
            start_index=search_start_index,
            max_points_per_frame=max_points_per_frame,
            max_total_points=max_total_points,
        )
        query_points = load_kitti_bounded_points_from_manifest(query_manifest).points
        search_points = load_kitti_bounded_points_from_manifest(search_manifest).points
        duplicates = find_exact_cross_package_matches(query_points, search_points)
        if not duplicates:
            return KittiDuplicateFreePair(
                query_start_index=query_start_index,
                search_start_index=search_start_index,
                query_record=query_record,
                search_record=search_record,
                query_point_count=len(query_points),
                search_point_count=len(search_points),
                duplicate_match_count=0,
                notes="Found a duplicate-free bounded KITTI pair for strict cuNSearch comparison.",
            )

    raise RuntimeError(
        "No duplicate-free KITTI frame pair was found within the requested search window."
    )
