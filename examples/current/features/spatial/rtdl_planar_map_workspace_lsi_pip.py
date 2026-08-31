#!/usr/bin/env python3
"""Small planar-map workspace example.

This example shows the app-author shape for combining public RTDL planar-map
primitives:

1. write/load two tiny CDB-like planar maps,
2. prepare one reusable workspace,
3. run LSI pair-id rows,
4. run point-location in both directions,
5. summarize the rows in a small Python or Numba continuation.

It intentionally does not call the bundled RayJoin overlay helper. Polygon
overlay assembly and paper-reproduction formatting belong in application code.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path


LEFT_CDB = """\
1 2 1 2 10 0
0.0 0.0
1.0 1.0
2 2 3 4 20 0
0.0 1.0
1.0 0.0
"""

RIGHT_CDB = """\
1 2 1 2 30 0
0.0 0.5
1.0 0.5
2 2 3 4 40 0
0.5 -0.1
0.5 1.1
"""


def _write_fixture(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


def _pair_row_count(row_view) -> int:
    try:
        return len(row_view)
    finally:
        row_view.close()


def _positive_face_count(rows) -> int:
    face_ids = [int(row.get("face_id", 0)) for row in rows]
    try:
        import numba as nb
        import numpy as np

        @nb.njit(cache=False)
        def count_positive(values):
            total = 0
            for value in values:
                if value != 0:
                    total += 1
            return total

        return int(count_positive(np.asarray(face_ids, dtype=np.int64)))
    except Exception:
        return sum(1 for value in face_ids if value != 0)


def main() -> None:
    import rtdsl as rt

    with tempfile.TemporaryDirectory(prefix="rtdl_workspace_example_") as tmp:
        tmpdir = Path(tmp)
        left = _write_fixture(tmpdir, "left_Point.cdb", LEFT_CDB)
        right = _write_fixture(tmpdir, "right_Point.cdb", RIGHT_CDB)
        cache_dir = tmpdir / "packed_cache"

        try:
            with rt.prepare_planar_map_workspace_2d_optix(
                left,
                right,
                cache_dir=cache_dir,
            ) as workspace:
                lsi_pairs = _pair_row_count(workspace.run_lsi_pair_id_rows())
                left_faces = workspace.run_left_points_in_right()
                right_faces = workspace.run_right_points_in_left()
                result = {
                    "status": "ok",
                    "example": "planar_map_workspace_lsi_pip",
                    "lsi_pair_rows": lsi_pairs,
                    "left_points_in_right_positive_faces": _positive_face_count(left_faces),
                    "right_points_in_left_positive_faces": _positive_face_count(right_faces),
                    "metadata": workspace.metadata(),
                }
        except Exception as exc:
            result = {
                "status": "skipped",
                "reason": str(exc),
                "note": (
                    "This example needs the OptiX native backend. The source "
                    "still demonstrates the public RTDL workspace programming shape."
                ),
            }

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
