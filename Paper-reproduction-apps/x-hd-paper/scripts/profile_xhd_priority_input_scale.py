#!/usr/bin/env python3
"""Profile a bridged X-HD priority input without materializing pairwise rows.

This is a planning/provenance tool for Goal5179. It reads full PLY candidates
streamingly, records geometry/grid statistics, and estimates the scale of a
naive pairwise route. It does not run the X-HD route and does not make a
performance claim.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable


def _parse_grid_shape(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part.strip()) for part in value.replace("x", ",").split(",") if part.strip())
    if len(parts) != 3 or any(part <= 0 for part in parts):
        raise ValueError(f"grid shape must be three positive integers, got: {value!r}")
    return parts


def _read_ply_header(path: Path) -> tuple[dict[str, Any], int]:
    vertex_count: int | None = None
    face_count: int | None = None
    property_names: list[str] = []
    in_vertex_properties = False
    header_lines = 0
    fmt: str | None = None
    with path.open("r", encoding="utf-8", errors="strict") as fh:
        first = fh.readline().strip()
        header_lines += 1
        if first != "ply":
            raise ValueError(f"{path} is not a PLY file")
        for line in fh:
            header_lines += 1
            text = line.strip()
            if text.startswith("format "):
                fmt = text.replace("format ", "", 1)
                if fmt != "ascii 1.0":
                    raise ValueError(f"{path} must be ASCII PLY, got {fmt!r}")
            elif text.startswith("element vertex "):
                vertex_count = int(text.split()[-1])
                in_vertex_properties = True
            elif text.startswith("element face "):
                face_count = int(text.split()[-1])
                in_vertex_properties = False
            elif text.startswith("element "):
                in_vertex_properties = False
            elif in_vertex_properties and text.startswith("property "):
                property_names.append(text.split()[-1])
            elif text == "end_header":
                break
        else:
            raise ValueError(f"{path} header has no end_header")
    if vertex_count is None:
        raise ValueError(f"{path} header has no vertex count")
    missing = [name for name in ("x", "y", "z") if name not in property_names]
    if missing:
        raise ValueError(f"{path} missing coordinate properties: {missing}")
    return (
        {
            "format": fmt,
            "vertex_count": vertex_count,
            "face_count": face_count,
            "property_names": property_names,
            "coordinate_indices": [property_names.index(name) for name in ("x", "y", "z")],
            "header_line_count": header_lines,
        },
        header_lines,
    )


def _iter_ply_vertices(path: Path) -> Iterable[tuple[float, float, float]]:
    header, _ = _read_ply_header(path)
    count = int(header["vertex_count"])
    indices = list(header["coordinate_indices"])
    header_lines = int(header["header_line_count"])
    with path.open("r", encoding="utf-8", errors="strict") as fh:
        for _ in range(header_lines):
            fh.readline()
        for row_index in range(count):
            line = fh.readline()
            if not line:
                raise ValueError(f"{path} ended before {count} vertex rows")
            parts = line.strip().split()
            if len(parts) <= max(indices):
                raise ValueError(f"{path} vertex row {row_index} has too few columns")
            yield (float(parts[indices[0]]), float(parts[indices[1]]), float(parts[indices[2]]))


def _axis_stats(points_path: Path) -> dict[str, Any]:
    header, _ = _read_ply_header(points_path)
    count = int(header["vertex_count"])
    mins = [math.inf, math.inf, math.inf]
    maxs = [-math.inf, -math.inf, -math.inf]
    sums = [0.0, 0.0, 0.0]
    actual = 0
    for point in _iter_ply_vertices(points_path):
        actual += 1
        for axis, value in enumerate(point):
            mins[axis] = min(mins[axis], value)
            maxs[axis] = max(maxs[axis], value)
            sums[axis] += value
    if actual != count:
        raise ValueError(f"{points_path} yielded {actual} vertices, header said {count}")
    extents = [maxs[i] - mins[i] for i in range(3)]
    return {
        "header": {
            "vertex_count": count,
            "face_count": header["face_count"],
            "format": header["format"],
        },
        "mbr": {
            "mins": mins,
            "maxs": maxs,
            "extents": extents,
            "diagonal": math.sqrt(sum(value * value for value in extents)),
            "means": [value / count for value in sums],
        },
    }


def _grid_occupancy(points_path: Path, *, grid_shape: tuple[int, int, int]) -> dict[str, Any]:
    stats = _axis_stats(points_path)
    mins = stats["mbr"]["mins"]
    extents = stats["mbr"]["extents"]
    cells: dict[int, int] = {}
    nx, ny, nz = grid_shape
    for x, y, z in _iter_ply_vertices(points_path):
        coords = (x, y, z)
        index_parts = []
        for axis, n in enumerate(grid_shape):
            if extents[axis] == 0:
                cell = 0
            else:
                cell = int((coords[axis] - mins[axis]) / extents[axis] * n)
                cell = max(0, min(n - 1, cell))
            index_parts.append(cell)
        flat = index_parts[0] * ny * nz + index_parts[1] * nz + index_parts[2]
        cells[flat] = cells.get(flat, 0) + 1
    counts = list(cells.values())
    total_cells = nx * ny * nz
    return {
        "grid_shape": list(grid_shape),
        "total_cells": total_cells,
        "occupied_cells": len(counts),
        "empty_cells": total_cells - len(counts),
        "max_points_per_cell": max(counts) if counts else 0,
        "median_points_per_occupied_cell": statistics.median(counts) if counts else 0,
        "mean_points_per_occupied_cell": (sum(counts) / len(counts)) if counts else 0.0,
        "p95_points_per_occupied_cell": _percentile(counts, 0.95),
        "nonempty_fraction": (len(counts) / total_cells) if total_cells else 0.0,
    }


def _percentile(values: list[int], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    pos = q * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(ordered[lo])
    return float(ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo))


def _pairwise_estimate(count_a: int, count_b: int) -> dict[str, Any]:
    pairs = count_a * count_b
    return {
        "pair_count": pairs,
        "pair_count_scientific": f"{pairs:.6e}",
        "distance_float32_bytes": pairs * 4,
        "distance_float64_bytes": pairs * 8,
        "candidate_row_min_16b_bytes": pairs * 16,
        "candidate_row_24b_bytes": pairs * 24,
        "candidate_row_32b_bytes": pairs * 32,
        "pairwise_exact_route_allowed": False,
        "reason": "Naive pairwise materialization is hundreds of billions of pairs for this target.",
    }


def build_profile(
    *,
    bridge: dict[str, Any],
    grid_shapes: list[tuple[int, int, int]],
) -> dict[str, Any]:
    candidates = bridge["public_same_source_candidates"]
    dragon_path = Path(candidates["dragon.ply"]["path"])
    happy_path = Path(candidates["happy_buddha.ply"]["path"])
    dragon_stats = _axis_stats(dragon_path)
    happy_stats = _axis_stats(happy_path)
    dragon_count = int(dragon_stats["header"]["vertex_count"])
    happy_count = int(happy_stats["header"]["vertex_count"])
    grid_profiles = {
        "dragon.ply": [_grid_occupancy(dragon_path, grid_shape=shape) for shape in grid_shapes],
        "happy_buddha.ply": [_grid_occupancy(happy_path, grid_shape=shape) for shape in grid_shapes],
    }
    return {
        "schema": "rtdl.paper_reproduction.xhd.priority_input_scale_profile.v1",
        "goal": "Goal5179",
        "status": "graphics_dragon_happy_buddha_full_public_candidate_profiled__no_route_run",
        "target": bridge["target"],
        "source_bridge_status": bridge["status"],
        "input_profiles": {
            "dragon.ply": dragon_stats,
            "happy_buddha.ply": happy_stats,
        },
        "grid_occupancy_profiles": grid_profiles,
        "pairwise_estimate": _pairwise_estimate(dragon_count, happy_count),
        "route_feasibility": {
            "do_not_run_naive_pairwise_exact": True,
            "requires_scalable_route": True,
            "candidate_route_components": [
                "author-directed mode from Goal5173",
                "generic grid/cell-MBR construction",
                "nearest-cell-MBR seed",
                "native 3-D cell-MBR frontier",
                "native inline-nearest for inline cells",
                "grouped Numba nearest continuation for offload rows",
            ],
            "next_gate_should_be": "bounded full-public-candidate feasibility gate with fail-closed row capacities and phase counters, not a performance ratio",
        },
        "claim_boundary": {
            "level_b_same_source_candidate_claimed": True,
            "route_run_claimed": False,
            "performance_ratio_claimed": False,
            "figure_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--grid-shapes", default="8,8,8;16,16,16;32,32,32")
    args = parser.parse_args()
    grid_shapes = [_parse_grid_shape(item) for item in args.grid_shapes.split(";") if item.strip()]
    profile = build_profile(bridge=json.loads(args.bridge.read_text()), grid_shapes=grid_shapes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n")
    print(
        "wrote",
        args.output,
        "pair_count=",
        profile["pairwise_estimate"]["pair_count"],
        "route_run=",
        profile["claim_boundary"]["route_run_claimed"],
    )


if __name__ == "__main__":
    main()
