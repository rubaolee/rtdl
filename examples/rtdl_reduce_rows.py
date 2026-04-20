from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


def run_demo() -> dict[str, object]:
    edge_hit_rows = (
        {"pose_id": 100, "link_id": 1, "ray_id": 10, "any_hit": 0},
        {"pose_id": 100, "link_id": 2, "ray_id": 11, "any_hit": 1},
        {"pose_id": 200, "link_id": 1, "ray_id": 12, "any_hit": 0},
        {"pose_id": 200, "link_id": 2, "ray_id": 13, "any_hit": 0},
    )
    neighbor_rows = (
        {"point_id": 1, "neighbor_id": 2, "distance": 0.5},
        {"point_id": 1, "neighbor_id": 3, "distance": 0.75},
        {"point_id": 2, "neighbor_id": 1, "distance": 0.5},
    )

    return {
        "app": "reduce_rows_demo",
        "boundary": "reduce_rows is a Python standard-library helper over emitted rows; it is not a native RT backend reduction.",
        "pose_collision_flags": rt.reduce_rows(
            edge_hit_rows,
            group_by="pose_id",
            op="any",
            value="any_hit",
            output_field="pose_blocked",
        ),
        "neighbor_counts": rt.reduce_rows(
            neighbor_rows,
            group_by="point_id",
            op="count",
            output_field="neighbor_count",
        ),
        "hausdorff_style_distance": rt.reduce_rows(
            neighbor_rows,
            op="max",
            value="distance",
            output_field="max_nearest_distance",
        ),
    }


def main() -> None:
    print(json.dumps(run_demo(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
