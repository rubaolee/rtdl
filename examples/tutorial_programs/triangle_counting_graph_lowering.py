from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _graph_inputs() -> tuple[tuple[tuple[int, int], ...], dict[int, tuple[float, float]]]:
    directed_edges = ((1, 2), (1, 3), (2, 3), (2, 4), (3, 4))
    vertex_xy = {
        1: (0.0, 0.0),
        2: (1.0, 0.0),
        3: (0.5, 1.0),
        4: (1.5, 1.0),
    }
    return directed_edges, vertex_xy


def _triangle_relation() -> dict[str, object]:
    directed_edges, vertex_xy = _graph_inputs()
    adjacency: dict[int, set[int]] = {node: set() for edge in directed_edges for node in edge}
    for left, right in directed_edges:
        adjacency[left].add(right)

    triangle_primitive_rows = tuple(
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
    two_hop_rows: list[dict[str, int]] = []
    ray_rows: list[dict[str, float | int]] = []
    triangle_witness_rows: list[dict[str, int | tuple[int, int, int]]] = []

    for src, mids in sorted(adjacency.items()):
        for mid in sorted(mids):
            for dst in sorted(adjacency.get(mid, ())):
                if not (src < mid < dst):
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
                    primitive = next(item for item in triangle_primitive_rows if item["edge"] == (src, dst))
                    triangle_witness_rows.append(
                        {
                            **row,
                            "primitive_id": int(primitive["primitive_id"]),
                            "triangle": (src, mid, dst),
                        }
                    )

    grouped_counts = tuple(
        {
            "source_vertex": src,
            "triangle_count": sum(1 for row in triangle_witness_rows if int(row["src"]) == src),
        }
        for src in sorted(adjacency)
    )
    return {
        "directed_edges": directed_edges,
        "two_hop_rows": tuple(two_hop_rows),
        "ray_rows": tuple(ray_rows),
        "triangle_primitive_rows": triangle_primitive_rows,
        "triangle_witness_rows": tuple(triangle_witness_rows),
        "grouped_counts": grouped_counts,
    }


def run_relation_mode() -> dict[str, object]:
    return {
        "tutorial_classification": "core_tutorial_program_relation_first",
        "kernel_programming_method": (
            "Lower graph two-hop rows into rays and edge primitives, emit closing "
            "edge witness rows, then reduce counts per source. The V4 any-hit and "
            "grouped-i64 surfaces execute this relation/continuation pair."
        ),
        "status": "ok",
        "mode": "relation",
        "concept": "triangle counting lowers graph two-hop paths to ray/primitive witness rows, then groups counts",
        "manual_data_flow": "directed edges -> two-hop rows -> ray rows + edge primitive rows -> witness rows -> grouped triangle counts",
        **_triangle_relation(),
    }


def run_visible_mode() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "visible_python_flow",
        "concept": "the two-hop path 1->2->3 is a triangle only if edge 1->3 also exists",
        "two_hop": (1, 2, 3),
        "closing_edge": (1, 3),
        "witness_row": {"src": 1, "mid": 2, "dst": 3, "triangle": (1, 2, 3)},
    }


def run_v4_mode() -> dict[str, object]:
    any_hit_plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    grouped_plan = rtdl_v4.plan_operator_request_v4("primitive_grouped_i64", partner="torch")
    return {
        "status": "ok",
        "mode": "v4",
        "relationship_to_relation": "The relation mode names graph-derived rays, edge primitives, witness rows, and grouped counts. V4 maps the hit test and grouped integer reduction to measured surfaces.",
        "v4_surfaces": {
            "hit_test": {
                "request": "any_hit",
                "partner": "torch",
                "status": any_hit_plan.status,
                "surface": any_hit_plan.api_surface,
            },
            "count": {
                "request": "primitive_grouped_i64",
                "partner": "torch",
                "status": grouped_plan.status,
                "surface": grouped_plan.api_surface,
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Triangle-counting graph lowering tutorial.")
    parser.add_argument("--mode", choices=("relation", "v4", "both", "visible"), default="both")
    args = parser.parse_args(argv)

    payload: dict[str, object] = {
        "status": "ok",
        "concept": "graph triangle counting can be expressed as witness rows plus grouped counts",
    }
    if args.mode in {"relation", "both"}:
        payload["relation_mode"] = run_relation_mode()
    if args.mode in {"v4", "both"}:
        payload["v4_mode"] = run_v4_mode()
    if args.mode == "visible":
        payload["visible_flow"] = run_visible_mode()

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
