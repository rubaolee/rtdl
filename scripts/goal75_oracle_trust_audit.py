#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import rtdsl as rt
from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from scripts.goal50_postgis_ground_truth import (
    connect,
    hash_full_pip_truth,
    hash_tuples,
    load_case_geometry as load_goal50_case_geometry,
    lsi_pairs,
    pip_positive_triplets,
    pip_triplets,
    recreate_schema as recreate_goal50_schema,
    run_postgis_lsi,
    run_postgis_pip,
)
from scripts.goal56_overlay_four_system import (
    hash_tuples as hash_overlay_tuples,
    load_case_geometry as load_goal56_case_geometry,
    overlay_quadruples,
    run_postgis_overlay,
)
from scripts.goal69_pip_positive_hit_performance import point_in_counties_positive_hits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit the Python reference and native C oracle against PostGIS on deterministic mini and small cases."
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--mini-random-seed", type=int, default=7501)
    parser.add_argument("--small-random-seed", type=int, default=7511)
    parser.add_argument("--mini-random-cases", type=int, default=12)
    parser.add_argument("--small-random-cases", type=int, default=12)
    return parser.parse_args()


def rectangle_polygon(polygon_id: int, x: float, y: float, width: float, height: float) -> dict[str, object]:
    return {
        "id": polygon_id,
        "vertices": (
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        ),
    }


def random_segment_case(rng: random.Random, *, left_count: int, right_count: int, coord_scale: float) -> dict[str, object]:
    def make_segments(base_id: int, count: int) -> tuple[dict[str, float | int], ...]:
        rows: list[dict[str, float | int]] = []
        for offset in range(count):
            x0 = rng.uniform(-coord_scale, coord_scale)
            y0 = rng.uniform(-coord_scale, coord_scale)
            x1 = x0 + rng.uniform(-coord_scale / 2.0, coord_scale / 2.0)
            y1 = y0 + rng.uniform(-coord_scale / 2.0, coord_scale / 2.0)
            rows.append({"id": base_id + offset, "x0": x0, "y0": y0, "x1": x1, "y1": y1})
        return tuple(rows)

    return {
        "left": make_segments(1, left_count),
        "right": make_segments(10_000, right_count),
    }


def random_pip_case(rng: random.Random, *, point_count: int, polygon_count: int, coord_scale: float) -> dict[str, object]:
    polygons = []
    for index in range(polygon_count):
        x = rng.uniform(-coord_scale, coord_scale)
        y = rng.uniform(-coord_scale, coord_scale)
        width = rng.uniform(coord_scale / 20.0, coord_scale / 4.0)
        height = rng.uniform(coord_scale / 20.0, coord_scale / 4.0)
        polygons.append(rectangle_polygon(100 + index, x, y, width, height))
    points = []
    for index in range(point_count):
        points.append(
            {
                "id": 1_000 + index,
                "x": rng.uniform(-coord_scale, coord_scale * 1.2),
                "y": rng.uniform(-coord_scale, coord_scale * 1.2),
            }
        )
    return {"points": tuple(points), "polygons": tuple(polygons)}


def random_overlay_case(rng: random.Random, *, left_count: int, right_count: int, coord_scale: float) -> dict[str, object]:
    def make_polygons(base_id: int, count: int) -> tuple[dict[str, object], ...]:
        rows = []
        for offset in range(count):
            x = rng.uniform(-coord_scale, coord_scale)
            y = rng.uniform(-coord_scale, coord_scale)
            width = rng.uniform(coord_scale / 10.0, coord_scale / 3.0)
            height = rng.uniform(coord_scale / 10.0, coord_scale / 3.0)
            rows.append(rectangle_polygon(base_id + offset, x, y, width, height))
        return tuple(rows)

    return {
        "left": make_polygons(1, left_count),
        "right": make_polygons(10_000, right_count),
    }


def mini_handcrafted_lsi_cases() -> tuple[dict[str, object], ...]:
    return (
        {
            "label": "crossing_segments",
            "left": ({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},),
            "right": ({"id": 10, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0},),
        },
        {
            "label": "endpoint_touch",
            "left": ({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 1.0},),
            "right": ({"id": 10, "x0": 1.0, "y0": 1.0, "x1": 2.0, "y1": 0.0},),
        },
        {
            "label": "parallel_disjoint",
            "left": ({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},),
            "right": ({"id": 10, "x0": 0.0, "y0": 1.0, "x1": 1.0, "y1": 1.0},),
        },
    )


def mini_handcrafted_pip_cases() -> tuple[dict[str, object], ...]:
    return (
        {
            "label": "inside_outside_boundary",
            "points": (
                {"id": 1, "x": 0.5, "y": 0.5},
                {"id": 2, "x": 3.0, "y": 3.0},
                {"id": 3, "x": 2.0, "y": 1.0},
            ),
            "polygons": (
                {"id": 10, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))},
            ),
        },
        {
            "label": "repeated_closing_vertex_outside",
            "points": ({"id": 1, "x": 3.0, "y": 3.0},),
            "polygons": (
                {"id": 10, "vertices": ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0), (0.0, 0.0))},
            ),
        },
        {
            "label": "near_collinear_short_edge",
            "points": ({"id": 1, "x": 0.0005, "y": -0.000001},),
            "polygons": (
                {"id": 10, "vertices": ((0.0, 0.0), (0.001, 0.0), (0.001, 1.0), (0.0, 1.0), (0.0, 0.0))},
            ),
        },
    )


def mini_handcrafted_overlay_cases() -> tuple[dict[str, object], ...]:
    return (
        {
            "label": "crossing_rectangles",
            "left": (rectangle_polygon(1, 0.0, 0.0, 2.0, 2.0),),
            "right": (rectangle_polygon(10, 1.0, -1.0, 2.0, 2.0),),
        },
        {
            "label": "containment_seed",
            "left": (rectangle_polygon(1, 0.0, 0.0, 4.0, 4.0),),
            "right": (rectangle_polygon(10, 1.0, 1.0, 1.0, 1.0),),
        },
        {
            "label": "disjoint",
            "left": (rectangle_polygon(1, 0.0, 0.0, 1.0, 1.0),),
            "right": (rectangle_polygon(10, 3.0, 3.0, 1.0, 1.0),),
        },
    )


def build_case_inventory(*, mini_random_seed: int, small_random_seed: int, mini_random_cases: int, small_random_cases: int) -> dict[str, tuple[dict[str, object], ...]]:
    mini_rng = random.Random(mini_random_seed)
    small_rng = random.Random(small_random_seed)

    mini_lsi = list(mini_handcrafted_lsi_cases())
    mini_pip = list(mini_handcrafted_pip_cases())
    mini_overlay = list(mini_handcrafted_overlay_cases())
    for index in range(mini_random_cases):
        case = random_segment_case(mini_rng, left_count=4, right_count=5, coord_scale=10.0)
        case["label"] = f"mini_random_lsi_{index:02d}"
        mini_lsi.append(case)
        case = random_pip_case(mini_rng, point_count=6, polygon_count=4, coord_scale=10.0)
        case["label"] = f"mini_random_pip_{index:02d}"
        mini_pip.append(case)
        case = random_overlay_case(mini_rng, left_count=3, right_count=3, coord_scale=8.0)
        case["label"] = f"mini_random_overlay_{index:02d}"
        mini_overlay.append(case)

    small_lsi = []
    small_pip = []
    small_overlay = []
    for index in range(small_random_cases):
        case = random_segment_case(small_rng, left_count=12, right_count=14, coord_scale=50.0)
        case["label"] = f"small_random_lsi_{index:02d}"
        small_lsi.append(case)
        case = random_pip_case(small_rng, point_count=24, polygon_count=8, coord_scale=50.0)
        case["label"] = f"small_random_pip_{index:02d}"
        small_pip.append(case)
        case = random_overlay_case(small_rng, left_count=6, right_count=6, coord_scale=30.0)
        case["label"] = f"small_random_overlay_{index:02d}"
        small_overlay.append(case)

    return {
        "mini_lsi": tuple(mini_lsi),
        "mini_pip": tuple(mini_pip),
        "mini_overlay": tuple(mini_overlay),
        "small_lsi": tuple(small_lsi),
        "small_pip": tuple(small_pip),
        "small_overlay": tuple(small_overlay),
    }


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def oracle_lsi_hash(rows) -> dict[str, object]:
    return hash_tuples(lsi_pairs(rows), presorted=False)


def oracle_pip_full_hash(*, point_ids: tuple[int, ...], polygon_ids: tuple[int, ...], rows) -> dict[str, object]:
    positives = tuple((triplet[0], triplet[1]) for triplet in pip_positive_triplets(rows))
    return hash_full_pip_truth(point_ids, polygon_ids, positives)


def oracle_pip_positive_hash(rows) -> dict[str, object]:
    return hash_tuples(pip_positive_triplets(rows), presorted=False)


def oracle_overlay_hash(rows) -> dict[str, object]:
    return hash_overlay_tuples(overlay_quadruples(rows), presorted=False)


def evaluate_lsi_case(conn, label: str, left, right, *, check_python: bool, check_native: bool) -> dict[str, object]:
    with conn.cursor() as cur:
        recreate_goal50_schema(cur)
    load_goal50_case_geometry(conn, prefix="oracle", left_segments=left, right_segments=right)
    postgis, postgis_sec = run_postgis_lsi(conn, "oracle")
    payload: dict[str, object] = {"label": label, "postgis": postgis, "postgis_sec": postgis_sec}
    if check_python:
        python_rows, python_sec = time_call(rt.run_cpu_python_reference, county_zip_join_reference, left=left, right=right)
        python_hash = oracle_lsi_hash(python_rows)
        payload["python"] = {"sec": python_sec, **python_hash, "parity_vs_postgis": python_hash == postgis}
    if check_native:
        native_rows, native_sec = time_call(rt.run_cpu, county_zip_join_reference, left=left, right=right)
        native_hash = oracle_lsi_hash(native_rows)
        payload["native"] = {"sec": native_sec, **native_hash, "parity_vs_postgis": native_hash == postgis}
    return payload


def evaluate_pip_case(conn, label: str, points, polygons, *, check_python: bool, check_native: bool) -> dict[str, object]:
    with conn.cursor() as cur:
        recreate_goal50_schema(cur)
    load_goal50_case_geometry(conn, prefix="oracle", points=points, polygons=polygons)
    postgis_hits, postgis_sec = run_postgis_pip(conn, "oracle")
    point_ids = tuple(int(row["id"]) for row in points)
    polygon_ids = tuple(int(row["id"]) for row in polygons)
    postgis_full = hash_full_pip_truth(
        point_ids,
        polygon_ids,
        tuple((point_id, polygon_id) for point_id, polygon_id, _ in postgis_hits["positive_hits"]),
    )
    postgis_positive = hash_tuples(postgis_hits["positive_hits"], presorted=True)
    payload: dict[str, object] = {
        "label": label,
        "postgis_full": postgis_full,
        "postgis_positive": postgis_positive,
        "postgis_sec": postgis_sec,
    }
    if check_python:
        python_full_rows, python_full_sec = time_call(
            rt.run_cpu_python_reference,
            point_in_counties_reference,
            points=points,
            polygons=polygons,
        )
        python_positive_rows, python_positive_sec = time_call(
            rt.run_cpu_python_reference,
            point_in_counties_positive_hits,
            points=points,
            polygons=polygons,
        )
        full_hash = oracle_pip_full_hash(point_ids=point_ids, polygon_ids=polygon_ids, rows=python_full_rows)
        positive_hash = oracle_pip_positive_hash(python_positive_rows)
        payload["python"] = {
            "full_sec": python_full_sec,
            "positive_sec": python_positive_sec,
            "full": {**full_hash, "parity_vs_postgis": full_hash == postgis_full},
            "positive": {**positive_hash, "parity_vs_postgis": positive_hash == postgis_positive},
        }
    if check_native:
        native_full_rows, native_full_sec = time_call(
            rt.run_cpu,
            point_in_counties_reference,
            points=points,
            polygons=polygons,
        )
        native_positive_rows, native_positive_sec = time_call(
            rt.run_cpu,
            point_in_counties_positive_hits,
            points=points,
            polygons=polygons,
        )
        full_hash = oracle_pip_full_hash(point_ids=point_ids, polygon_ids=polygon_ids, rows=native_full_rows)
        positive_hash = oracle_pip_positive_hash(native_positive_rows)
        payload["native"] = {
            "full_sec": native_full_sec,
            "positive_sec": native_positive_sec,
            "full": {**full_hash, "parity_vs_postgis": full_hash == postgis_full},
            "positive": {**positive_hash, "parity_vs_postgis": positive_hash == postgis_positive},
        }
    return payload


def evaluate_overlay_case(conn, label: str, left, right, *, check_python: bool, check_native: bool) -> dict[str, object]:
    load_goal56_case_geometry(conn, left_polygons=left, right_polygons=right)
    postgis, postgis_sec = run_postgis_overlay(conn)
    payload: dict[str, object] = {"label": label, "postgis": postgis, "postgis_sec": postgis_sec}
    if check_python:
        python_rows, python_sec = time_call(rt.run_cpu_python_reference, county_soil_overlay_reference, left=left, right=right)
        python_hash = oracle_overlay_hash(python_rows)
        payload["python"] = {"sec": python_sec, **python_hash, "parity_vs_postgis": python_hash == postgis}
    if check_native:
        native_rows, native_sec = time_call(rt.run_cpu, county_soil_overlay_reference, left=left, right=right)
        native_hash = oracle_overlay_hash(native_rows)
        payload["native"] = {"sec": native_sec, **native_hash, "parity_vs_postgis": native_hash == postgis}
    return payload


def summarize_workload(case_rows: list[dict[str, object]], *, oracle_key: str | None) -> dict[str, object]:
    summary = {"case_count": len(case_rows), "cases": case_rows}
    if oracle_key is None:
        passed = len([row for row in case_rows if row["python"]["parity_vs_postgis"]])
        summary["python_pass_count"] = passed
        summary["python_all_pass"] = passed == len(case_rows)
        return summary
    if oracle_key == "native_lsi":
        passed = len([row for row in case_rows if row["native"]["parity_vs_postgis"]])
        summary["native_pass_count"] = passed
        summary["native_all_pass"] = passed == len(case_rows)
        return summary
    if oracle_key == "native_overlay":
        passed = len([row for row in case_rows if row["native"]["parity_vs_postgis"]])
        summary["native_pass_count"] = passed
        summary["native_all_pass"] = passed == len(case_rows)
        return summary
    if oracle_key == "pip_python":
        full_pass = len([row for row in case_rows if row["python"]["full"]["parity_vs_postgis"]])
        positive_pass = len([row for row in case_rows if row["python"]["positive"]["parity_vs_postgis"]])
        summary["python_full_pass_count"] = full_pass
        summary["python_positive_pass_count"] = positive_pass
        summary["python_all_pass"] = full_pass == len(case_rows) and positive_pass == len(case_rows)
        return summary
    if oracle_key == "pip_native":
        full_pass = len([row for row in case_rows if row["native"]["full"]["parity_vs_postgis"]])
        positive_pass = len([row for row in case_rows if row["native"]["positive"]["parity_vs_postgis"]])
        summary["native_full_pass_count"] = full_pass
        summary["native_positive_pass_count"] = positive_pass
        summary["native_all_pass"] = full_pass == len(case_rows) and positive_pass == len(case_rows)
        return summary
    raise ValueError(f"unknown oracle key: {oracle_key}")


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Goal 75 Oracle Trust Audit",
        "",
        f"Host label: `{summary['host_label']}`",
        f"Database: `{summary['db_name']}`",
        "",
        "- Python reference oracle is audited on deterministic mini cases only",
        "- native C oracle is accepted here on deterministic small cases",
        "- native-oracle mini-case agreement is retained only as supporting evidence, not as the accepted trust boundary",
        "- PostGIS is the external truth source for `lsi`, `pip`, and overlay-seed semantics",
        "",
        "## Result",
        "",
        f"- mini Python all-pass: `{summary['mini_python']['all_pass']}`",
        f"- small native all-pass: `{summary['small_native']['all_pass']}`",
        "",
        "## Mini Python Envelope",
        "",
        f"- `lsi` cases: `{summary['mini_python']['lsi']['case_count']}` pass `{summary['mini_python']['lsi']['python_pass_count']}`",
        f"- `pip` cases: `{summary['mini_python']['pip']['case_count']}` full pass `{summary['mini_python']['pip']['python_full_pass_count']}` positive pass `{summary['mini_python']['pip']['python_positive_pass_count']}`",
        f"- overlay cases: `{summary['mini_python']['overlay']['case_count']}` pass `{summary['mini_python']['overlay']['python_pass_count']}`",
        "",
        "## Small Native Envelope",
        "",
        f"- `lsi` cases: `{summary['small_native']['lsi']['case_count']}` pass `{summary['small_native']['lsi']['native_pass_count']}`",
        f"- `pip` cases: `{summary['small_native']['pip']['case_count']}` full pass `{summary['small_native']['pip']['native_full_pass_count']}` positive pass `{summary['small_native']['pip']['native_positive_pass_count']}`",
        f"- overlay cases: `{summary['small_native']['overlay']['case_count']}` pass `{summary['small_native']['overlay']['native_pass_count']}`",
        "",
    ]
    return "\n".join(lines)


def persist_summary(output_dir: Path, summary: dict[str, object]) -> None:
    (output_dir / "goal75_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal75_summary.md").write_text(render_markdown(summary), encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = build_case_inventory(
        mini_random_seed=args.mini_random_seed,
        small_random_seed=args.small_random_seed,
        mini_random_cases=args.mini_random_cases,
        small_random_cases=args.small_random_cases,
    )
    conn = connect(args.db_name, args.db_user)
    try:
        mini_lsi = [
            evaluate_lsi_case(conn, case["label"], case["left"], case["right"], check_python=True, check_native=True)
            for case in inventory["mini_lsi"]
        ]
        mini_pip = [
            evaluate_pip_case(conn, case["label"], case["points"], case["polygons"], check_python=True, check_native=True)
            for case in inventory["mini_pip"]
        ]
        mini_overlay = [
            evaluate_overlay_case(conn, case["label"], case["left"], case["right"], check_python=True, check_native=True)
            for case in inventory["mini_overlay"]
        ]

        small_lsi = [
            evaluate_lsi_case(conn, case["label"], case["left"], case["right"], check_python=False, check_native=True)
            for case in inventory["small_lsi"]
        ]
        small_pip = [
            evaluate_pip_case(conn, case["label"], case["points"], case["polygons"], check_python=False, check_native=True)
            for case in inventory["small_pip"]
        ]
        small_overlay = [
            evaluate_overlay_case(conn, case["label"], case["left"], case["right"], check_python=False, check_native=True)
            for case in inventory["small_overlay"]
        ]
    finally:
        conn.close()

    summary = {
        "host_label": args.host_label,
        "db_name": args.db_name,
        "mini_python": {
            "lsi": summarize_workload(mini_lsi, oracle_key=None),
            "pip": summarize_workload(mini_pip, oracle_key="pip_python"),
            "overlay": summarize_workload(mini_overlay, oracle_key=None),
        },
        "small_native": {
            "lsi": summarize_workload(small_lsi, oracle_key="native_lsi"),
            "pip": summarize_workload(small_pip, oracle_key="pip_native"),
            "overlay": summarize_workload(small_overlay, oracle_key="native_overlay"),
        },
        "inventory": {
            "mini_random_seed": args.mini_random_seed,
            "small_random_seed": args.small_random_seed,
            "mini_random_cases": args.mini_random_cases,
            "small_random_cases": args.small_random_cases,
        },
    }
    summary["mini_python"]["all_pass"] = (
        summary["mini_python"]["lsi"]["python_all_pass"]
        and summary["mini_python"]["pip"]["python_all_pass"]
        and summary["mini_python"]["overlay"]["python_all_pass"]
    )
    summary["small_native"]["all_pass"] = (
        summary["small_native"]["lsi"]["native_all_pass"]
        and summary["small_native"]["pip"]["native_all_pass"]
        and summary["small_native"]["overlay"]["native_all_pass"]
    )
    persist_summary(output_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
