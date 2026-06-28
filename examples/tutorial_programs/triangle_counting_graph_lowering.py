from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    directed_edges = ((1, 2), (1, 3), (2, 3), (2, 4), (3, 4))
    vertex_xy = {
        1: (0.0, 0.0),
        2: (1.0, 0.0),
        3: (0.5, 1.0),
        4: (1.5, 1.0),
    }
    adjacency = {node: set() for edge in directed_edges for node in edge}
    for left, right in directed_edges:
        adjacency[left].add(right)

    two_hop_rows = []
    ray_rows = []
    triangle_rows = tuple(
        {
            "primitive_id": index,
            "edge": (left, right),
            "x0": vertex_xy[left][0],
            "y0": vertex_xy[left][1],
            "x1": vertex_xy[right][0],
            "y1": vertex_xy[right][1],
        }
        for index, (left, right) in enumerate(directed_edges, 1)
    )
    triangle_witness_rows = []
    for src, mids in sorted(adjacency.items()):
        for mid in sorted(mids):
            for dst in sorted(adjacency.get(mid, ())):
                if src >= mid or mid >= dst:
                    continue
                row = {"src": src, "mid": mid, "dst": dst, "ray_id": len(ray_rows) + 1}
                two_hop_rows.append(row)
                ray_rows.append(
                    {
                        "ray_id": row["ray_id"],
                        "src": src,
                        "mid": mid,
                        "dst": dst,
                        "x0": vertex_xy[src][0],
                        "y0": vertex_xy[src][1],
                        "x1": vertex_xy[dst][0],
                        "y1": vertex_xy[dst][1],
                    }
                )
                if dst in adjacency.get(src, set()):
                    primitive = next(item for item in triangle_rows if item["edge"] == (src, dst))
                    triangle_witness_rows.append(
                        {
                            **row,
                            "primitive_id": primitive["primitive_id"],
                            "triangle": (src, mid, dst),
                        }
                    )

    grouped_counts = tuple(
        {
            "source_vertex": src,
            "triangle_count": sum(1 for row in triangle_witness_rows if row["src"] == src),
        }
        for src in sorted(adjacency)
    )
    any_hit_plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    grouped_plan = rtdl_v4.plan_operator_request_v4("grouped_i64", partner="torch")
    payload = {
        "status": "ok",
        "concept": "Triangle counting lowers graph two-hop candidates to witness tests, then reduces witnesses by graph group",
        "manual_data_flow": "directed edges -> graph-derived ray rows + edge primitive rows -> witness tests -> grouped triangle counts",
        "directed_edges": directed_edges,
        "two_hop_rows": tuple(two_hop_rows),
        "ray_rows": tuple(ray_rows),
        "triangle_primitive_rows": triangle_rows,
        "triangle_witness_rows": tuple(triangle_witness_rows),
        "grouped_counts": grouped_counts,
        "v4_surfaces": {
            "hit_test": {"request": "any_hit", "status": any_hit_plan.status, "surface": any_hit_plan.api_surface},
            "count": {"request": "grouped_i64", "status": grouped_plan.status, "surface": grouped_plan.api_surface},
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
