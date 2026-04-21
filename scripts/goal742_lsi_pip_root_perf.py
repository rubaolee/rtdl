#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_zip_join_reference


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_polygons_positive_hits():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(
            exact=False,
            boundary_mode="inclusive",
            result_mode="positive_hits",
        ),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


def _fnv64_from_pairs(pairs: list[tuple[int, int]]) -> str:
    value = 1469598103934665603
    for left_id, right_id in sorted(pairs):
        for raw in (left_id, right_id):
            for shift in range(0, 32, 8):
                value ^= (raw >> shift) & 0xFF
                value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016x}"


def _hash_rows(rows, left_field: str, right_field: str) -> tuple[int, str]:
    pairs = [
        (int(row[left_field]), int(row[right_field]))
        for row in rows
        if row.get("contains", 1) == 1
    ]
    return len(pairs), _fnv64_from_pairs(pairs)


def _hash_raw_rows(rows, left_field: str, right_field: str) -> tuple[int, str]:
    try:
        pairs = [
            (int(getattr(rows.rows_ptr[index], left_field)), int(getattr(rows.rows_ptr[index], right_field)))
            for index in range(rows.row_count)
            if not hasattr(rows.rows_ptr[index], "contains") or int(rows.rows_ptr[index].contains) == 1
        ]
        return len(pairs), _fnv64_from_pairs(pairs)
    finally:
        rows.close()


def _time_call(fn):
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


def _median(samples: list[float]) -> float:
    return statistics.median(samples) if samples else 0.0


def build_lsi_sparse(count: int) -> dict[str, tuple[rt.Segment, ...]]:
    cols = max(1, int(count ** 0.5))
    left: list[rt.Segment] = []
    right: list[rt.Segment] = []
    for index in range(count):
        gx = index % cols
        gy = index // cols
        x = float(gx) * 3.0
        y = float(gy) * 3.0
        right.append(rt.Segment(index + 1, x + 0.5, y, x + 0.5, y + 1.0))
        left.append(rt.Segment(index + 1, x, y + 0.5, x + 1.0, y + 0.5))
    return {"left": tuple(left), "right": tuple(right)}


def build_lsi_dense(build_count: int, probe_count: int) -> dict[str, tuple[rt.Segment, ...]]:
    left = [
        rt.Segment(index + 1, 0.0, float(index) * 0.25, float(build_count) * 0.25, float(index) * 0.25)
        for index in range(probe_count)
    ]
    right = [
        rt.Segment(index + 1, float(index) * 0.25, 0.0, float(index) * 0.25, float(probe_count) * 0.25)
        for index in range(build_count)
    ]
    return {"left": tuple(left), "right": tuple(right)}


def build_pip_positive(polygons_count: int, point_count: int) -> dict[str, tuple[object, ...]]:
    side = max(1, int(polygons_count ** 0.5))
    polygons: list[rt.Polygon] = []
    for index in range(polygons_count):
        gx = index % side
        gy = index // side
        x0 = float(gx) * 2.0
        y0 = float(gy) * 2.0
        polygons.append(
            rt.Polygon(
                index + 1,
                ((x0, y0), (x0 + 1.0, y0), (x0 + 1.0, y0 + 1.0), (x0, y0 + 1.0)),
            )
        )
    points: list[rt.Point] = []
    for index in range(point_count):
        polygon = polygons[index % len(polygons)]
        x0, y0 = polygon.vertices[0]
        points.append(rt.Point(index + 1, x0 + 0.5, y0 + 0.5))
    return {"points": tuple(points), "polygons": tuple(polygons)}


def _case_specs(scale: str) -> list[dict[str, object]]:
    if scale == "quick":
        return [
            {"name": "lsi_sparse", "kernel": county_zip_join_reference, "inputs": build_lsi_sparse(384), "fields": ("left_id", "right_id")},
            {"name": "lsi_dense", "kernel": county_zip_join_reference, "inputs": build_lsi_dense(96, 96), "fields": ("left_id", "right_id")},
            {"name": "pip_positive", "kernel": point_in_polygons_positive_hits, "inputs": build_pip_positive(384, 768), "fields": ("point_id", "polygon_id")},
        ]
    return [
        {"name": "lsi_sparse", "kernel": county_zip_join_reference, "inputs": build_lsi_sparse(5000), "fields": ("left_id", "right_id")},
        {"name": "lsi_dense", "kernel": county_zip_join_reference, "inputs": build_lsi_dense(350, 350), "fields": ("left_id", "right_id")},
        {"name": "pip_positive", "kernel": point_in_polygons_positive_hits, "inputs": build_pip_positive(5000, 10000), "fields": ("point_id", "polygon_id")},
    ]


def run_case(spec: dict[str, object], repeats: int) -> dict[str, object]:
    kernel = spec["kernel"]
    inputs = spec["inputs"]
    left_field, right_field = spec["fields"]

    cpu_rows, cpu_sec = _time_call(lambda: rt.run_cpu_python_reference(kernel, **inputs))
    cpu_count, cpu_hash = _hash_rows(cpu_rows, left_field, right_field)

    rt.configure_embree(threads=1)
    one_rows, one_sec = _time_call(lambda: rt.run_embree(kernel, **inputs))
    one_count, one_hash = _hash_rows(one_rows, left_field, right_field)

    rt.configure_embree(threads="auto")
    auto_rows, auto_sec = _time_call(lambda: rt.run_embree(kernel, **inputs))
    auto_count, auto_hash = _hash_rows(auto_rows, left_field, right_field)

    prepared = rt.prepare_embree(kernel).bind(**inputs)
    raw_times: list[float] = []
    raw_counts: list[int] = []
    raw_hashes: list[str] = []
    for _ in range(repeats):
        raw_rows, raw_sec = _time_call(prepared.run_raw)
        raw_count, raw_hash = _hash_raw_rows(raw_rows, left_field, right_field)
        raw_times.append(raw_sec)
        raw_counts.append(raw_count)
        raw_hashes.append(raw_hash)

    return {
        "name": spec["name"],
        "inputs": {key: len(value) for key, value in inputs.items()},
        "row_count": cpu_count,
        "cpu_reference_sec": cpu_sec,
        "embree_1_thread_sec": one_sec,
        "embree_auto_thread_sec": auto_sec,
        "embree_prepared_raw_sec_median": _median(raw_times),
        "embree_auto_speedup_vs_cpu": cpu_sec / auto_sec if auto_sec > 0 else None,
        "embree_auto_speedup_vs_1_thread": one_sec / auto_sec if auto_sec > 0 else None,
        "prepared_raw_speedup_vs_dict_auto": auto_sec / _median(raw_times) if _median(raw_times) > 0 else None,
        "parity": {
            "one_thread": one_count == cpu_count and one_hash == cpu_hash,
            "auto_thread": auto_count == cpu_count and auto_hash == cpu_hash,
            "prepared_raw": all(count == cpu_count for count in raw_counts) and all(row_hash == cpu_hash for row_hash in raw_hashes),
            "hash": cpu_hash,
        },
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 742: LSI/PIP Root Workload Refresh",
        "",
        "## Scope",
        "",
        "This report gives VIP treatment to RTDL's original root workloads: line-segment intersection (`lsi`) and point-in-polygon (`pip`). It separates standalone primitive behavior from later composed polygon apps.",
        "",
        f"- host: `{payload['host']}`",
        f"- platform: `{payload['platform']}`",
        f"- scale: `{payload['scale']}`",
        f"- repeats: `{payload['repeats']}`",
        f"- Embree thread config: `{payload['embree_thread_config']}`",
        "",
        "## Results",
        "",
        "| Case | Inputs | Rows | CPU ref s | Embree 1T s | Embree auto s | Prepared raw median s | Auto vs CPU | Auto vs 1T | Raw vs dict | Parity |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for case in payload["cases"]:
        inputs = ", ".join(f"{key}={value}" for key, value in case["inputs"].items())
        parity = all(case["parity"][key] for key in ("one_thread", "auto_thread", "prepared_raw"))
        lines.append(
            "| {name} | {inputs} | {rows} | {cpu:.6f} | {one:.6f} | {auto:.6f} | {raw:.6f} | {cpu_speed:.2f}x | {thread_speed:.2f}x | {raw_speed:.2f}x | {parity} |".format(
                name=case["name"],
                inputs=inputs,
                rows=case["row_count"],
                cpu=case["cpu_reference_sec"],
                one=case["embree_1_thread_sec"],
                auto=case["embree_auto_thread_sec"],
                raw=case["embree_prepared_raw_sec_median"],
                cpu_speed=case["embree_auto_speedup_vs_cpu"] or 0.0,
                thread_speed=case["embree_auto_speedup_vs_1_thread"] or 0.0,
                raw_speed=case["prepared_raw_speedup_vs_dict_auto"] or 0.0,
                parity=parity,
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `lsi_sparse` is the traversal-friendly root case: many build segments, each probe expected to emit a small number of rows.",
            "- `lsi_dense` is intentionally output-heavy. If this case is slower, the bottleneck is row emission/materialization, not absence of ray traversal.",
            "- `pip_positive` is the historical positive-hit PIP shape: Embree performs native BVH/point-query candidate discovery and emits only accepted containment rows.",
            "- Prepared raw mode measures the low-overhead native result path before Python dict materialization.",
            "",
            "## Boundaries",
            "",
            "- This is an Embree CPU ray-tracing/root-workload closure, not an NVIDIA RT-core claim.",
            "- LSI/PIP remain float-approximate RTDL primitives; exact GIS semantics still require external exact validation when users need it.",
            "- Composed polygon applications should cite these root workloads when they use LSI/PIP for candidate discovery.",
            "",
            "## Independent Review Status",
            "",
            "- Gemini Flash review was requested on 2026-04-21, but the service returned repeated model-capacity 429 responses. The local evidence above is therefore Codex-verified only until a later external review retry succeeds.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal742 standalone LSI/PIP root-workload correctness and performance harness.")
    parser.add_argument("--scale", choices=("quick", "standard"), default="standard")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs" / "reports" / "goal742_lsi_pip_root_perf_macos_2026-04-21.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs" / "reports" / "goal742_lsi_pip_root_workload_refresh_2026-04-21.md")
    args = parser.parse_args()

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": platform.node(),
        "platform": platform.platform(),
        "scale": args.scale,
        "repeats": args.repeats,
        "cases": [],
    }
    rt.configure_embree(threads="auto")
    payload["embree_thread_config"] = rt.embree_thread_config().__dict__

    for spec in _case_specs(args.scale):
        payload["cases"].append(run_case(spec, args.repeats))

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
