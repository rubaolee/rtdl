from __future__ import annotations

import numpy as np

from rtdsl.rayjoin_overlay import _rows_from_segment_pairs


class _DatasetStub:
    pass


def main() -> int:
    left = _DatasetStub()
    right = _DatasetStub()
    left_id = 172803
    right_id = 23714604
    lx0 = np.zeros(left_id, dtype=np.float64)
    ly0 = np.zeros(left_id, dtype=np.float64)
    lx1 = np.zeros(left_id, dtype=np.float64)
    ly1 = np.zeros(left_id, dtype=np.float64)
    rx0 = np.zeros(right_id, dtype=np.float64)
    ry0 = np.zeros(right_id, dtype=np.float64)
    rx1 = np.zeros(right_id, dtype=np.float64)
    ry1 = np.zeros(right_id, dtype=np.float64)
    li = left_id - 1
    ri = right_id - 1
    lx0[li], ly0[li], lx1[li], ly1[li] = (
        -144.127807,
        64.799108,
        -144.123679,
        64.793277,
    )
    rx0[ri], ry0[ri], rx1[ri], ry1[ri] = (
        -144.1278071,
        64.799108,
        -144.1236789,
        64.793277,
    )
    rows = _rows_from_segment_pairs(
        np.array([[left_id, right_id]], dtype=np.uint32),
        left,
        right,
        left_coords=(lx0, ly0, lx1, ly1),
        right_coords=(rx0, ry0, rx1, ry1),
        scale_bounds=(-179.148909, 179.778465, -14.548692, 71.390482),
    )
    row = rows[0]
    print({name: str(row[name]) for name in rows.dtype.names})
    print(f"{float(row['intersection_point_x']):.6f} {float(row['intersection_point_y']):.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
