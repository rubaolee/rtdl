from __future__ import annotations

import json
import struct
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path

from .rtnn_kitti import discover_kitti_velodyne_frames
from .rtnn_kitti import resolve_kitti_source_root
from .rtnn_reproduction import rtnn_paper_dataset_targets
from .rtnn_reproduction import RtnnPaperDatasetTarget


@dataclass(frozen=True)
class KittiFramePointCount:
    sequence: str
    frame_id: str
    relative_bin_path: str
    point_count: int


@dataclass(frozen=True)
class KittiRecipeFrame:
    sequence: str
    frame_id: str
    relative_bin_path: str
    source_point_count: int
    take_point_count: int
    cumulative_point_count: int


@dataclass(frozen=True)
class KittiPaperFamilyRecipe:
    target_handle: str
    paper_label: str
    target_point_count: int
    source_root: str
    source_frame_count: int
    source_point_count: int
    start_index: int
    stride: int
    selected_frame_count: int
    selected_point_count: int
    truncated_last_frame: bool
    recipe_status: str
    paper_equivalence_status: str
    exact_recipe_status: str
    selection_rule: str
    frames: tuple[KittiRecipeFrame, ...]
    notes: str


@dataclass(frozen=True)
class KittiRecipeCsvExport:
    path: str
    target_handle: str
    paper_label: str
    point_count: int
    selected_frame_count: int
    source_root: str
    format: str
    recipe_status: str
    paper_equivalence_status: str
    notes: str


def inspect_kitti_frame_point_counts(
    source_root: str | Path | None = None,
) -> tuple[KittiFramePointCount, ...]:
    resolved = resolve_kitti_source_root(source_root)
    if resolved is None:
        raise RuntimeError(
            "KITTI source root is not configured; set RTDL_KITTI_SOURCE_ROOT "
            "or pass source_root before inspecting frame point counts."
        )

    counts: list[KittiFramePointCount] = []
    for record in discover_kitti_velodyne_frames(resolved):
        bin_path = resolved / record.relative_bin_path
        size_bytes = bin_path.stat().st_size
        if size_bytes % 16 != 0:
            raise RuntimeError(
                f"KITTI frame file has invalid size {size_bytes} bytes; expected a multiple of 16: {bin_path}"
            )
        counts.append(
            KittiFramePointCount(
                sequence=record.sequence,
                frame_id=record.frame_id,
                relative_bin_path=record.relative_bin_path,
                point_count=size_bytes // 16,
            )
        )
    return tuple(counts)


def plan_kitti_paper_family_recipe(
    *,
    target_handle: str,
    source_root: str | Path | None = None,
    start_index: int = 0,
    stride: int = 1,
    target_point_count: int | None = None,
) -> KittiPaperFamilyRecipe:
    if start_index < 0:
        raise ValueError("start_index must be non-negative")
    if stride <= 0:
        raise ValueError("stride must be positive")
    if target_point_count is not None and target_point_count <= 0:
        raise ValueError("target_point_count must be positive")

    targets = _rtnn_kitti_targets_by_handle()
    if target_handle not in targets:
        raise ValueError(f"unknown RTNN KITTI paper target handle: {target_handle}")
    target = targets[target_handle]
    resolved = resolve_kitti_source_root(source_root)
    if resolved is None:
        raise RuntimeError(
            "KITTI source root is not configured; set RTDL_KITTI_SOURCE_ROOT "
            "or pass source_root before planning a KITTI recipe."
        )

    desired_count = target.point_count if target_point_count is None else target_point_count
    frame_counts = inspect_kitti_frame_point_counts(resolved)
    selected: list[KittiRecipeFrame] = []
    cumulative = 0
    for frame in frame_counts[start_index::stride]:
        if cumulative >= desired_count:
            break
        remaining = desired_count - cumulative
        take_count = min(frame.point_count, remaining)
        if take_count <= 0:
            continue
        cumulative += take_count
        selected.append(
            KittiRecipeFrame(
                sequence=frame.sequence,
                frame_id=frame.frame_id,
                relative_bin_path=frame.relative_bin_path,
                source_point_count=frame.point_count,
                take_point_count=take_count,
                cumulative_point_count=cumulative,
            )
        )

    truncated_last_frame = bool(selected and selected[-1].take_point_count < selected[-1].source_point_count)
    recipe_status = "bounded_family_recipe_ready" if cumulative == desired_count else "insufficient_source_points"
    if recipe_status == "bounded_family_recipe_ready":
        notes = (
            "This recipe reaches the requested KITTI point count from a deterministic "
            "Velodyne frame order, but it is still a bounded family recipe because the "
            "paper's exact frame ids are not frozen."
        )
    else:
        notes = (
            "The configured KITTI source does not contain enough selected Velodyne "
            "points to reach the requested target point count."
        )

    return KittiPaperFamilyRecipe(
        target_handle=target.handle,
        paper_label=target.paper_label,
        target_point_count=desired_count,
        source_root=str(resolved),
        source_frame_count=len(frame_counts),
        source_point_count=sum(frame.point_count for frame in frame_counts),
        start_index=start_index,
        stride=stride,
        selected_frame_count=len(selected),
        selected_point_count=cumulative,
        truncated_last_frame=truncated_last_frame,
        recipe_status=recipe_status,
        paper_equivalence_status="bounded_family_recipe_not_exact_paper_recipe",
        exact_recipe_status=target.exact_recipe_status,
        selection_rule=(
            "Discover KITTI Velodyne .bin files in stable sequence/frame/path order; "
            "take frames from start_index with the requested stride; preserve source "
            "point order inside each frame; truncate only the final selected frame "
            "when the requested point count is reached."
        ),
        frames=tuple(selected),
        notes=notes,
    )


def write_kitti_paper_family_recipe_manifest(
    destination: str | Path,
    *,
    target_handle: str,
    source_root: str | Path | None = None,
    start_index: int = 0,
    stride: int = 1,
    target_point_count: int | None = None,
) -> Path:
    recipe = plan_kitti_paper_family_recipe(
        target_handle=target_handle,
        source_root=source_root,
        start_index=start_index,
        stride=stride,
        target_point_count=target_point_count,
    )
    payload = {
        "manifest_kind": "kitti_paper_family_recipe_manifest_v1",
        "recipe": asdict(recipe),
        "claim_boundary": {
            "paper_family_dataset": True,
            "exact_paper_recipe": False,
            "same_contract_author_rtdl_bounded_comparison_allowed": (
                recipe.recipe_status == "bounded_family_recipe_ready"
            ),
            "paper_reproduction_wording_allowed": False,
        },
    }
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def write_kitti_paper_family_recipe_csv(
    destination: str | Path,
    *,
    target_handle: str,
    source_root: str | Path | None = None,
    start_index: int = 0,
    stride: int = 1,
    target_point_count: int | None = None,
) -> KittiRecipeCsvExport:
    recipe = plan_kitti_paper_family_recipe(
        target_handle=target_handle,
        source_root=source_root,
        start_index=start_index,
        stride=stride,
        target_point_count=target_point_count,
    )
    if recipe.recipe_status != "bounded_family_recipe_ready":
        raise RuntimeError(
            f"KITTI recipe {target_handle!r} is not ready for CSV export: {recipe.recipe_status}"
        )
    source_root_path = Path(recipe.source_root)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for frame in recipe.frames:
            frame_path = source_root_path / frame.relative_bin_path
            for index, (x, y, z, _intensity) in enumerate(_iter_kitti_frame_xyzi(frame_path)):
                if index >= frame.take_point_count:
                    break
                handle.write(f"{x:.9g},{y:.9g},{z:.9g}\n")
                written += 1

    if written != recipe.selected_point_count:
        raise RuntimeError(
            f"KITTI CSV export wrote {written} points, expected {recipe.selected_point_count}"
        )

    return KittiRecipeCsvExport(
        path=str(destination),
        target_handle=recipe.target_handle,
        paper_label=recipe.paper_label,
        point_count=written,
        selected_frame_count=recipe.selected_frame_count,
        source_root=recipe.source_root,
        format="rtnn_csv_xyz",
        recipe_status=recipe.recipe_status,
        paper_equivalence_status=recipe.paper_equivalence_status,
        notes=(
            "CSV rows preserve source frame order and per-frame point order from the "
            "bounded KITTI family recipe. The file is suitable for same-input RTNN/RTDL "
            "comparison, not exact paper wording."
        ),
    )


def _rtnn_kitti_targets_by_handle() -> dict[str, RtnnPaperDatasetTarget]:
    return {
        target.handle: target
        for target in rtnn_paper_dataset_targets(family_handle="kitti_velodyne_point_sets")
    }


def _iter_kitti_frame_xyzi(bin_path: Path):
    payload = bin_path.read_bytes()
    if len(payload) % 16 != 0:
        raise RuntimeError(
            f"KITTI frame file has invalid size {len(payload)} bytes; expected a multiple of 16: {bin_path}"
        )
    return struct.iter_unpack("<ffff", payload)
