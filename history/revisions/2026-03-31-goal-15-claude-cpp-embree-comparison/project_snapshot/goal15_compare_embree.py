#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference


def write_segments_csv(path: Path, segments: tuple[rt.Segment, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for segment in segments:
            writer.writerow((segment.id, segment.x0, segment.y0, segment.x1, segment.y1))


def write_points_csv(path: Path, points: tuple[rt.Point, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for point in points:
            writer.writerow((point.id, point.x, point.y))


def write_polygons_csv(path: Path, polygons: tuple[rt.Polygon, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for polygon in polygons:
            row = [polygon.id]
            for x, y in polygon.vertices:
                row.extend((x, y))
            writer.writerow(row)


def compile_native(exe_name: str, source_name: str) -> Path:
    build_dir = ROOT / "build" / "goal15_native"
    build_dir.mkdir(parents=True, exist_ok=True)
    output_path = build_dir / exe_name
    source_path = ROOT / "apps" / source_name
    native_path = ROOT / "src" / "native" / "rtdl_embree.cpp"
    embree_prefix = Path(os.environ.get("RTDL_EMBREE_PREFIX", "/opt/homebrew/opt/embree"))
    cmd = [
        "c++",
        "-std=c++17",
        "-O2",
        "-I",
        str(embree_prefix / "include"),
        str(source_path),
        str(native_path),
        "-L",
        str(embree_prefix / "lib"),
        "-Wl,-rpath," + str(embree_prefix / "lib"),
        "-lembree4",
        "-o",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    return output_path


def pair_rows(rows: tuple[dict[str, object], ...], left_field: str, right_field: str) -> list[str]:
    pairs = sorted((int(row[left_field]), int(row[right_field])) for row in rows if row.get("contains", 1) == 1)
    return [f"{left},{right}" for left, right in pairs]


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def run_native(executable: Path, args: list[str]) -> dict[str, object]:
    subprocess.run([str(executable), *args], check=True)
    return {}


def build_lsi_dataset(build_count: int, probe_count: int, distribution: str):
    del distribution
    left = []
    right = []
    for idx in range(probe_count):
        y = float(idx) * 0.25
        left.append(rt.Segment(id=idx + 1, x0=0.0, y0=y, x1=float(build_count) * 0.25, y1=y))
    for idx in range(build_count):
        x = float(idx) * 0.25
        right.append(rt.Segment(id=idx + 1, x0=x, y0=0.0, x1=x, y1=float(probe_count) * 0.25))
    return tuple(left), tuple(right)


def build_pip_dataset(build_count: int, probe_count: int, distribution: str):
    del distribution
    side = max(1, int(build_count ** 0.5))
    polygons = []
    for idx in range(build_count):
        gx = idx % side
        gy = idx // side
        x0 = gx * 2.0
        y0 = gy * 2.0
        polygons.append(
            rt.Polygon(
                id=idx + 1,
                vertices=((x0, y0), (x0 + 1.0, y0), (x0 + 1.0, y0 + 1.0), (x0, y0 + 1.0)),
            )
        )
    points = []
    for idx in range(probe_count):
        polygon = polygons[idx % len(polygons)]
        x0, y0 = polygon.vertices[0]
        points.append(rt.Point(id=idx + 1, x=x0 + 0.5, y=y0 + 0.5))
    return tuple(points), tuple(polygons)


def compare_goal15(output_dir: Path | None = None) -> dict[str, object]:
    out = Path(output_dir or ROOT / "build" / "goal15_compare")
    out.mkdir(parents=True, exist_ok=True)
    lsi_exe = compile_native("goal15_lsi_native", "goal15_lsi_native.cpp")
    pip_exe = compile_native("goal15_pip_native", "goal15_pip_native.cpp")

    datasets = {
        "lsi": build_lsi_dataset(build_count=200, probe_count=120, distribution="uniform"),
        "pip": build_pip_dataset(build_count=200, probe_count=120, distribution="uniform"),
    }

    results: dict[str, object] = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "workloads": {}}

    # LSI
    left, right = datasets["lsi"]
    lsi_dir = out / "lsi"
    lsi_dir.mkdir(parents=True, exist_ok=True)
    left_csv = lsi_dir / "left_segments.csv"
    right_csv = lsi_dir / "right_segments.csv"
    native_pairs = lsi_dir / "native_pairs.csv"
    native_timing = lsi_dir / "native_timing.json"
    write_segments_csv(left_csv, left)
    write_segments_csv(right_csv, right)
    run_native(lsi_exe, ["--left", str(left_csv), "--right", str(right_csv), "--pairs-out", str(native_pairs), "--timing-out", str(native_timing)])
    cpu_rows, cpu_sec = time_call(rt.run_cpu, county_zip_join_reference, left=left, right=right)
    embree_rows, embree_sec = time_call(rt.run_embree, county_zip_join_reference, left=left, right=right)
    cpu_pairs = pair_rows(cpu_rows, "left_id", "right_id")
    embree_pairs = pair_rows(embree_rows, "left_id", "right_id")
    native_pair_lines = native_pairs.read_text(encoding="utf-8").splitlines()
    results["workloads"]["lsi"] = {
        "cpu_matches_native": cpu_pairs == native_pair_lines,
        "embree_matches_native": embree_pairs == native_pair_lines,
        "cpu_pair_count": len(cpu_pairs),
        "embree_pair_count": len(embree_pairs),
        "native_pair_count": len(native_pair_lines),
        "rtdl_cpu_total_sec": cpu_sec,
        "rtdl_embree_total_sec": embree_sec,
        "native_total_sec": json.loads(native_timing.read_text(encoding="utf-8"))["total_sec"],
    }

    # PIP
    points, polygons = datasets["pip"]
    pip_dir = out / "pip"
    pip_dir.mkdir(parents=True, exist_ok=True)
    points_csv = pip_dir / "points.csv"
    polygons_csv = pip_dir / "polygons.csv"
    native_pairs = pip_dir / "native_pairs.csv"
    native_timing = pip_dir / "native_timing.json"
    write_points_csv(points_csv, points)
    write_polygons_csv(polygons_csv, polygons)
    run_native(pip_exe, ["--points", str(points_csv), "--polygons", str(polygons_csv), "--pairs-out", str(native_pairs), "--timing-out", str(native_timing)])
    cpu_rows, cpu_sec = time_call(rt.run_cpu, point_in_counties_reference, points=points, polygons=polygons)
    embree_rows, embree_sec = time_call(rt.run_embree, point_in_counties_reference, points=points, polygons=polygons)
    cpu_pairs = pair_rows(cpu_rows, "point_id", "polygon_id")
    embree_pairs = pair_rows(embree_rows, "point_id", "polygon_id")
    native_pair_lines = native_pairs.read_text(encoding="utf-8").splitlines()
    results["workloads"]["pip"] = {
        "cpu_matches_native": cpu_pairs == native_pair_lines,
        "embree_matches_native": embree_pairs == native_pair_lines,
        "cpu_pair_count": len(cpu_pairs),
        "embree_pair_count": len(embree_pairs),
        "native_pair_count": len(native_pair_lines),
        "rtdl_cpu_total_sec": cpu_sec,
        "rtdl_embree_total_sec": embree_sec,
        "native_total_sec": json.loads(native_timing.read_text(encoding="utf-8"))["total_sec"],
    }

    report_path = out / "goal15_compare.json"
    report_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return results


def main() -> int:
    payload = compare_goal15()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
