from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from xhd_input_loader import _parse_wkt_geometry_line


def _parse_indices(text: str) -> list[int]:
    indices: list[int] = []
    for item in text.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        value = int(stripped)
        if value < 0:
            raise ValueError(f"indices must be non-negative, got {value}")
        indices.append(value)
    if not indices:
        raise ValueError("at least one index is required")
    return indices


def inspect_wkt_points_by_index(path: Path, *, n_dims: int, indices: list[int]) -> dict[str, Any]:
    requested = sorted(set(indices))
    remaining = set(requested)
    found: dict[int, dict[str, Any]] = {}
    global_offset = 0
    geometry_rows = 0

    with path.open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            row_points = _parse_wkt_geometry_line(line, n_dims=n_dims)
            if row_points is None:
                continue
            row_count = len(row_points)
            row_start = global_offset
            row_end = global_offset + row_count
            geometry_rows += 1
            for index in list(remaining):
                if row_start <= index < row_end:
                    local_index = index - row_start
                    coord = tuple(float(value) for value in row_points[local_index])
                    coord32 = np.asarray(coord, dtype=np.float32)
                    found[index] = {
                        "index": index,
                        "coordinate_float64": list(coord),
                        "coordinate_float32": [float(value) for value in coord32],
                        "geometry_line_number": line_number,
                        "geometry_row_index": geometry_rows - 1,
                        "local_index_in_geometry": int(local_index),
                        "geometry_point_count": int(row_count),
                    }
                    remaining.remove(index)
            global_offset = row_end
            if not remaining:
                break

    missing = [index for index in requested if index not in found]
    if missing:
        raise IndexError(f"{path} does not contain requested point indices: {missing}; parsed {global_offset} points")

    return {
        "schema": "rtdl.paper_reproduction.xhd.wkt_point_index_inspection.v1",
        "path": str(path),
        "n_dims": n_dims,
        "requested_indices": requested,
        "parsed_point_count_until_last_hit": int(global_offset),
        "geometry_rows_until_last_hit": int(geometry_rows),
        "points": [found[index] for index in requested],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect app-owned X-HD WKT point coordinates by global point index."
    )
    parser.add_argument("--path", required=True, type=Path)
    parser.add_argument("--n-dims", required=True, type=int, choices=(2, 3))
    parser.add_argument("--indices", required=True, help="Comma-separated zero-based global point indices")
    parser.add_argument("--summary", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    result = inspect_wkt_points_by_index(args.path, n_dims=args.n_dims, indices=_parse_indices(args.indices))
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
