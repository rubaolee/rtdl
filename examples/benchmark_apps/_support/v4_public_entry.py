from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import runpy
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())


@dataclass(frozen=True)
class BenchmarkPublicEntry:
    app: str
    idea: str
    relation: str
    operators: tuple[str, ...]
    partners: tuple[str, ...]
    current_entry: str
    full_harness: str


ENTRIES: dict[str, BenchmarkPublicEntry] = {
    "rt_dbscan": BenchmarkPublicEntry(
        app="RTDBSCAN",
        idea="Find radius-neighbor relations and merge dense connected components.",
        relation="fixed-radius point neighborhood",
        operators=("fixed_radius", "component_union"),
        partners=("torch", "numba"),
        current_entry="examples/benchmark_apps/rt_dbscan/v4_app.py",
        full_harness="examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
    ),
    "rtnn": BenchmarkPublicEntry(
        app="RTNN",
        idea="Find nearest witnesses, then summarize or rank candidate neighbors.",
        relation="point-group nearest witness",
        operators=("point_group_nearest", "ranked_summary"),
        partners=("torch", "rtdl_native"),
        current_entry="examples/benchmark_apps/rtnn/v4_app.py",
        full_harness="examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py",
    ),
    "triangle_counting": BenchmarkPublicEntry(
        app="Triangle counting",
        idea="Lower graph structure to RT hit evidence and reduce by group.",
        relation="ray/triangle hit relation over graph-derived geometry",
        operators=("any_hit", "grouped_i64"),
        partners=("torch", "cupy", "numba"),
        current_entry="examples/benchmark_apps/triangle_counting/v4_app.py",
        full_harness="examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
    ),
    "robot_collision": BenchmarkPublicEntry(
        app="Robot collision",
        idea="Ask whether motion segments intersect obstacle primitives.",
        relation="ray/triangle any-hit collision relation",
        operators=("any_hit",),
        partners=("torch", "rtdl_native"),
        current_entry="examples/benchmark_apps/robot_collision/v4_app.py",
        full_harness="examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py",
    ),
    "raydb_style": BenchmarkPublicEntry(
        app="RayDB-style query",
        idea="Build a hit relation, then compute compact aggregate summaries.",
        relation="ray/primitive hit relation",
        operators=("any_hit", "weighted_sum", "grouped_sum"),
        partners=("torch", "cupy"),
        current_entry="examples/benchmark_apps/raydb_style/v4_app.py",
        full_harness="examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py",
    ),
    "librts_spatial_index": BenchmarkPublicEntry(
        app="LibRTS spatial index",
        idea="Use prepared AABB-style indexing for spatial predicates.",
        relation="AABB point/range containment and intersection",
        operators=("aabb_index_query",),
        partners=("rtdl_native",),
        current_entry="examples/benchmark_apps/librts_spatial_index/v4_app.py",
        full_harness="examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
    ),
    "contact_manifold": BenchmarkPublicEntry(
        app="Contact manifold",
        idea="Separate broadphase candidate discovery from closest-hit refinement.",
        relation="candidate-pair contact witness relation",
        operators=("aabb_index_query", "closest_hit_argmin"),
        partners=("rtdl_native", "torch"),
        current_entry="examples/benchmark_apps/contact_manifold/v4_app.py",
        full_harness="examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
    ),
    "spatial_rayjoin": BenchmarkPublicEntry(
        app="Spatial RayJoin",
        idea="Build candidate shape pairs, then refine them with RT predicates.",
        relation="shape-pair spatial join relation",
        operators=("aabb_index_query", "any_hit"),
        partners=("rtdl_native", "torch"),
        current_entry="examples/benchmark_apps/spatial_rayjoin/v4_app.py",
        full_harness="examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
    ),
    "barnes_hut": BenchmarkPublicEntry(
        app="Barnes-Hut",
        idea="Build an aggregate frontier and apply a weighted continuation.",
        relation="body-to-aggregate-frontier relation",
        operators=("aggregate_frontier", "grouped_sum"),
        partners=("rtdl_native", "cupy"),
        current_entry="examples/benchmark_apps/barnes_hut/v4_app.py",
        full_harness="examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
    ),
    "hausdorff_xhd": BenchmarkPublicEntry(
        app="Hausdorff XHD",
        idea="Choose threshold decisions or exact nearest-witness evidence between point sets.",
        relation="point-set threshold or nearest-witness relation",
        operators=("fixed_radius", "point_group_nearest"),
        partners=("torch",),
        current_entry="examples/benchmark_apps/hausdorff_xhd/v4_app.py",
        full_harness="examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
    ),
}


def _payload(entry: BenchmarkPublicEntry) -> dict[str, object]:
    return {
        "app": entry.app,
        "idea": entry.idea,
        "relation": entry.relation,
        "operators": list(entry.operators),
        "partners": list(entry.partners),
        "current_entry": entry.current_entry,
        "learn_more": "tutorials/current/06_benchmark_apps.md",
        "full_harness_policy": (
            "The full harness is available for benchmark reproduction. Start with "
            "this V4 entrypoint when learning or browsing the app."
        ),
    }


def _render(entry: BenchmarkPublicEntry) -> str:
    payload = _payload(entry)
    lines = [
        entry.app,
        f"  idea: {payload['idea']}",
        f"  relation: {payload['relation']}",
        f"  operators: {', '.join(entry.operators)}",
        f"  partners: {', '.join(entry.partners)}",
        f"  current entry: {entry.current_entry}",
        f"  learn more: {payload['learn_more']}",
        "",
        "Run the full benchmark harness only when you need reproduction details:",
        f"  py -3 {entry.current_entry} --run-harness -- --help",
    ]
    return "\n".join(lines)


def _run_harness(entry: BenchmarkPublicEntry, harness_args: list[str]) -> int:
    target = ROOT / entry.full_harness
    args = list(harness_args)
    if args and args[0] == "--":
        args = args[1:]
    sys.argv = [str(target), *args]
    runpy.run_path(str(target), run_name="__main__")
    return 0


def main(app_key: str) -> int:
    entry = ENTRIES[app_key]
    parser = argparse.ArgumentParser(description=f"Current V4 entrypoint for {entry.app}.")
    parser.add_argument("--json", action="store_true", help="Print the entry description as JSON.")
    parser.add_argument(
        "--run-harness",
        action="store_true",
        help="Run the full benchmark harness after this clean V4 entrypoint.",
    )
    parser.add_argument("harness_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.run_harness:
        return _run_harness(entry, args.harness_args)
    if args.json:
        print(json.dumps(_payload(entry), indent=2, sort_keys=True))
    else:
        print(_render(entry))
    return 0
