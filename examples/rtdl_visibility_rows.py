from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rtdsl as rt


def main() -> None:
    observers = (
        rt.Point(id=1, x=0.0, y=0.0),
        rt.Point(id=2, x=0.0, y=2.0),
    )
    targets = (
        rt.Point(id=10, x=10.0, y=0.0),
        rt.Point(id=11, x=10.0, y=2.0),
    )
    blockers = (
        rt.Triangle(id=100, x0=5.0, y0=-1.0, x1=5.0, y1=1.0, x2=6.0, y2=0.0),
    )

    rows = rt.visibility_rows_cpu(observers, targets, blockers)
    print(
        json.dumps(
            {
                "workload": "visibility_rows",
                "description": "Observer-target pairs become visible=1/0 rows using bounded any-hit internally.",
                "rows": list(rows),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
