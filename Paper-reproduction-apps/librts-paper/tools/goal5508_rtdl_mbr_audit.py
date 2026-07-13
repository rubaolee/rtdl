from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

REMOTE_ROOT = Path("/workspace/rtdl-goal5481")
ROOT = (
    REMOTE_ROOT
    if (REMOTE_ROOT / "src" / "rtdsl").is_dir()
    else next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "src" / "rtdsl").is_dir()
    )
)
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "librts-paper"))

from run_exact_point_contains_count_gate import load_geometry_mbr_columns


def fnv1a_float32(columns) -> tuple[str, list[list[float]]]:
    values = np.stack(
        (columns.min_x, columns.min_y, columns.max_x, columns.max_y), axis=1
    ).astype("<f4", copy=False)
    digest = 1469598103934665603
    for byte in values.tobytes(order="C"):
        digest = ((digest ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    samples = [
        values[0].tolist(),
        values[len(values) // 2].tolist(),
        values[-1].tolist(),
    ]
    return format(digest, "x"), samples


def main() -> None:
    output = []
    for raw_path in sys.argv[1:]:
        path = Path(raw_path)
        columns = load_geometry_mbr_columns(path)
        digest, samples = fnv1a_float32(columns)
        values = np.stack(
            (columns.min_x, columns.min_y, columns.max_x, columns.max_y), axis=1
        ).astype("<f4", copy=False)
        widths = np.abs(values[:, 2] - values[:, 0])
        heights = np.abs(values[:, 3] - values[:, 1])
        invalid_count = int(
            np.count_nonzero(
                (columns.min_x >= columns.max_x)
                | (columns.min_y >= columns.max_y)
            )
        )
        output.append(
            {
                "path": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "count": len(columns),
                "invalid_non_strict_aabb_count": invalid_count,
                "width_lt_1e_7_count": int(np.count_nonzero(widths < 1.0e-7)),
                "height_lt_1e_7_count": int(np.count_nonzero(heights < 1.0e-7)),
                "width_min": float(widths.min()),
                "height_min": float(heights.min()),
                "float32_mbr_fnv1a": digest,
                "samples": samples,
            }
        )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
