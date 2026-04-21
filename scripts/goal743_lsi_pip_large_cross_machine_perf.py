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
from scripts.goal742_lsi_pip_root_perf import build_lsi_dense
from scripts.goal742_lsi_pip_root_perf import build_lsi_sparse
from scripts.goal742_lsi_pip_root_perf import build_pip_positive
from scripts.goal742_lsi_pip_root_perf import point_in_polygons_positive_hits


def _fnv64_from_pair_iter(pairs) -> str:
    value = 1469598103934665603
    for left_id, right_id in pairs:
        for raw in (left_id, right_id):
            for shift in range(0, 32, 8):
                value ^= (raw >> shift) & 0xFF
                value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016x}"


def _expected_hash(case_name: str, inputs: dict[str, tuple[object, ...]]) -> tuple[int, str]:
    if case_name == "lsi_sparse_large":
        count = len(inputs["left"])
        return count, _fnv64_from_pair_iter((index, index) for index in range(1, count + 1))
    if case_name == "lsi_dense_large":
        left_count = len(inputs["left"])
        right_count = len(inputs["right"])
        return left_count * right_count, _fnv64_from_pair_iter(
            (left_id, right_id)
            for left_id in range(1, left_count + 1)
            for right_id in range(1, right_count + 1)
        )
    if case_name == "pip_positive_large":
        point_count = len(inputs["points"])
        polygon_count = len(inputs["polygons"])
        return point_count, _fnv64_from_pair_iter(
            (point_id, ((point_id - 1) % polygon_count) + 1)
            for point_id in range(1, point_count + 1)
        )
    raise ValueError(f"unknown case {case_name}")


def _hash_dict_rows(rows, left_field: str, right_field: str) -> tuple[int, str]:
    pairs = sorted(
        (int(row[left_field]), int(row[right_field]))
        for row in rows
        if row.get("contains", 1) == 1
    )
    return len(pairs), _fnv64_from_pair_iter(pairs)


def _hash_raw_rows(rows, left_field: str, right_field: str) -> tuple[int, str]:
    try:
        pairs = sorted(
            (int(getattr(rows.rows_ptr[index], left_field)), int(getattr(rows.rows_ptr[index], right_field)))
            for index in range(rows.row_count)
            if not hasattr(rows.rows_ptr[index], "contains") or int(rows.rows_ptr[index].contains) == 1
        )
        return len(pairs), _fnv64_from_pair_iter(pairs)
    finally:
        rows.close()


def _time_call(fn):
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


def _median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def _case_specs(scale: str) -> list[dict[str, object]]:
    if scale == "quick":
        return [
            {
                "name": "lsi_sparse_large",
                "kernel": county_zip_join_reference,
                "inputs": build_lsi_sparse(1_000),
                "fields": ("left_id", "right_id"),
                "workload": "LSI sparse",
                "meaning": "many segment pairs in space, one expected hit per probe",
            },
            {
                "name": "lsi_dense_large",
                "kernel": county_zip_join_reference,
                "inputs": build_lsi_dense(160, 160),
                "fields": ("left_id", "right_id"),
                "workload": "LSI dense",
                "meaning": "all probes intersect all build segments; intentionally row-output-heavy",
            },
            {
                "name": "pip_positive_large",
                "kernel": point_in_polygons_positive_hits,
                "inputs": build_pip_positive(1_000, 2_000),
                "fields": ("point_id", "polygon_id"),
                "workload": "PIP positive",
                "meaning": "many point/polygon containment probes, one expected positive row per point",
            },
        ]
    return [
        {
            "name": "lsi_sparse_large",
            "kernel": county_zip_join_reference,
            "inputs": build_lsi_sparse(100_000),
            "fields": ("left_id", "right_id"),
            "workload": "LSI sparse",
            "meaning": "many segment pairs in space, one expected hit per probe",
        },
        {
            "name": "lsi_dense_large",
            "kernel": county_zip_join_reference,
            "inputs": build_lsi_dense(1_000, 1_000),
            "fields": ("left_id", "right_id"),
            "workload": "LSI dense",
            "meaning": "all probes intersect all build segments; intentionally row-output-heavy",
        },
        {
            "name": "pip_positive_large",
            "kernel": point_in_polygons_positive_hits,
            "inputs": build_pip_positive(100_000, 200_000),
            "fields": ("point_id", "polygon_id"),
            "workload": "PIP positive",
            "meaning": "many point/polygon containment probes, one expected positive row per point",
        },
    ]


def _time_dict_mode(kernel, inputs, *, threads: str | int, repeats: int, left_field: str, right_field: str) -> dict[str, object]:
    rt.configure_embree(threads=threads)
    times: list[float] = []
    counts: list[int] = []
    hashes: list[str] = []
    for _ in range(repeats):
        rows, seconds = _time_call(lambda: rt.run_embree(kernel, **inputs))
        count, digest = _hash_dict_rows(rows, left_field, right_field)
        times.append(seconds)
        counts.append(count)
        hashes.append(digest)
    return {
        "median_sec": _median(times),
        "samples_sec": times,
        "row_counts": counts,
        "hashes": hashes,
    }


def _time_prepared_raw(kernel, inputs, *, repeats: int, left_field: str, right_field: str) -> dict[str, object]:
    rt.configure_embree(threads="auto")
    prepared = rt.prepare_embree(kernel).bind(**inputs)
    times: list[float] = []
    counts: list[int] = []
    hashes: list[str] = []
    for _ in range(repeats):
        rows, seconds = _time_call(prepared.run_raw)
        count, digest = _hash_raw_rows(rows, left_field, right_field)
        times.append(seconds)
        counts.append(count)
        hashes.append(digest)
    return {
        "median_sec": _median(times),
        "samples_sec": times,
        "row_counts": counts,
        "hashes": hashes,
    }


def run_case(spec: dict[str, object], repeats: int) -> dict[str, object]:
    kernel = spec["kernel"]
    inputs = spec["inputs"]
    left_field, right_field = spec["fields"]
    expected_count, expected_hash = _expected_hash(spec["name"], inputs)

    one = _time_dict_mode(kernel, inputs, threads=1, repeats=1, left_field=left_field, right_field=right_field)
    auto = _time_dict_mode(kernel, inputs, threads="auto", repeats=repeats, left_field=left_field, right_field=right_field)
    raw = _time_prepared_raw(kernel, inputs, repeats=repeats, left_field=left_field, right_field=right_field)

    def mode_matches(mode: dict[str, object]) -> bool:
        return all(count == expected_count for count in mode["row_counts"]) and all(digest == expected_hash for digest in mode["hashes"])

    return {
        "name": spec["name"],
        "workload": spec["workload"],
        "meaning": spec["meaning"],
        "inputs": {key: len(value) for key, value in inputs.items()},
        "expected_rows": expected_count,
        "expected_hash": expected_hash,
        "embree_1_thread_dict": one,
        "embree_auto_dict": auto,
        "embree_auto_prepared_raw": raw,
        "auto_speedup_vs_1_thread_dict": one["median_sec"] / auto["median_sec"] if auto["median_sec"] > 0 else None,
        "prepared_raw_speedup_vs_auto_dict": auto["median_sec"] / raw["median_sec"] if raw["median_sec"] > 0 else None,
        "rows_per_sec_auto_dict": expected_count / auto["median_sec"] if auto["median_sec"] > 0 else None,
        "rows_per_sec_prepared_raw": expected_count / raw["median_sec"] if raw["median_sec"] > 0 else None,
        "parity": {
            "one_thread_dict": mode_matches(one),
            "auto_dict": mode_matches(auto),
            "auto_prepared_raw": mode_matches(raw),
        },
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 743: Cross-Machine Large LSI/PIP Embree Performance",
        "",
        "## Purpose",
        "",
        "This report explains how Embree accelerates the RT part of app-shaped spatial workloads built from RTDL's original root primitives: line-segment intersection (`lsi`) and point-in-polygon (`pip`).",
        "",
        "It intentionally separates three costs:",
        "",
        "- RT traversal and native row discovery (`prepared_raw`)",
        "- RT traversal plus Python dict materialization (`auto_dict`)",
        "- single-thread native traversal plus materialization (`1_thread_dict`)",
        "",
        f"- host: `{payload['host']}`",
        f"- platform: `{payload['platform']}`",
        f"- scale: `{payload['scale']}`",
        f"- repeats: `{payload['repeats']}`",
        f"- Embree thread config: `{payload['embree_thread_config']}`",
        "",
        "## Easy Performance Table",
        "",
        "| Workload | Data scale | Rows | 1T dict s | Auto dict s | Prepared raw s | Auto vs 1T | Raw vs dict | Auto rows/s | Raw rows/s | Parity |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for case in payload["cases"]:
        inputs = ", ".join(f"{key}={value}" for key, value in case["inputs"].items())
        parity = all(case["parity"].values())
        lines.append(
            "| {workload} | {inputs} | {rows} | {one:.6f} | {auto:.6f} | {raw:.6f} | {thread:.2f}x | {raw_speed:.2f}x | {auto_rps:,.0f} | {raw_rps:,.0f} | {parity} |".format(
                workload=case["workload"],
                inputs=inputs,
                rows=case["expected_rows"],
                one=case["embree_1_thread_dict"]["median_sec"],
                auto=case["embree_auto_dict"]["median_sec"],
                raw=case["embree_auto_prepared_raw"]["median_sec"],
                thread=case["auto_speedup_vs_1_thread_dict"] or 0.0,
                raw_speed=case["prepared_raw_speedup_vs_auto_dict"] or 0.0,
                auto_rps=case["rows_per_sec_auto_dict"] or 0.0,
                raw_rps=case["rows_per_sec_prepared_raw"] or 0.0,
                parity=parity,
            )
        )
    lines.extend([
        "",
        "## What Each Row Means",
        "",
    ])
    for case in payload["cases"]:
        lines.append(f"- `{case['workload']}`: {case['meaning']}.")
    lines.extend(
        [
            "",
            "## Main Reading",
            "",
            "- If `prepared_raw` is much faster than `auto_dict`, Embree is doing the RT part quickly and Python row materialization is the remaining app-interface cost.",
            "- If `auto_dict` is much faster than `1T dict`, automatic Embree multithreading helps the app-visible path.",
            "- If dense LSI scales poorly, that is expected: every probe emits every build pair, so output volume dominates after traversal.",
            "- PIP positive-hit mode is the preferred app shape because it emits only accepted containment rows instead of a full point/polygon matrix.",
            "",
            "## Boundary",
            "",
            "- This is Embree CPU ray-tracing performance, not NVIDIA RT-core performance.",
            "- Large-scale correctness is checked by deterministic expected row counts and stable hashes; Goal742 separately records CPU-reference parity on smaller scales.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Large cross-machine LSI/PIP Embree benchmark.")
    parser.add_argument("--scale", choices=("quick", "large"), default="large")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, default=None)
    args = parser.parse_args()

    rt.configure_embree(threads="auto")
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": platform.node(),
        "platform": platform.platform(),
        "scale": args.scale,
        "repeats": args.repeats,
        "embree_thread_config": rt.embree_thread_config().__dict__,
        "cases": [],
    }
    for spec in _case_specs(args.scale):
        payload["cases"].append(run_case(spec, args.repeats))

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.output_md is not None:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
