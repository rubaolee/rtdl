#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.reference.rtdl_language_reference import point_in_counties_reference
from goal15_compare_embree import build_lsi_dataset
from goal15_compare_embree import build_pip_dataset
from goal15_compare_embree import compile_native
from goal15_compare_embree import _default_embree_prefix
from goal15_compare_embree import _native_runtime_env
from goal15_compare_embree import pair_rows
from goal15_compare_embree import write_points_csv
from goal15_compare_embree import write_polygons_csv
from goal15_compare_embree import write_segments_csv


DEFAULT_FIXTURE_PROFILE = {
    "lsi": {"build": 200, "probe": 120},
    "pip": {"build": 200, "probe": 120},
}

DEFAULT_LARGE_PROFILE = {
    "lsi": {"build": 2000, "probe": 1500},
    "pip": {"build": 2500, "probe": 2000},
}


def _fnv64_from_pairs(pairs: list[tuple[int, int]]) -> str:
    value = 1469598103934665603
    for left_id, right_id in sorted(pairs):
        for raw in (left_id, right_id):
            for shift in range(0, 32, 8):
                value ^= (raw >> shift) & 0xFF
                value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016x}"


def _hash_rows(rows: tuple[dict[str, object], ...], left_field: str, right_field: str) -> str:
    pairs = sorted(
        (int(row[left_field]), int(row[right_field]))
        for row in rows
        if row.get("contains", 1) == 1
    )
    return _fnv64_from_pairs(pairs)


def _time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def _median_repeat(fn, *, repeats: int) -> float:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def _native_summary(
    executable: Path,
    args: list[str],
    timing_out: Path,
    *,
    env: dict[str, str] | None = None,
) -> dict[str, object]:
    timing_out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(executable), *args, "--timing-out", str(timing_out)], check=True, env=env)
    return json.loads(timing_out.read_text(encoding="utf-8"))


def _native_median(
    executable: Path,
    args: list[str],
    timing_dir: Path,
    *,
    repeats: int,
    env: dict[str, str] | None = None,
) -> float:
    timings = []
    for index in range(repeats):
        timing_path = timing_dir / f"timing_{index:02d}.json"
        payload = _native_summary(executable, args, timing_path, env=env)
        timings.append(float(payload["total_sec"]))
    return statistics.median(timings)


def _prepare_mode_medians(kernel, inputs: dict[str, object], *, repeats: int) -> dict[str, float]:
    prepared = rt.prepare_embree(kernel).bind(**inputs)

    def run_raw_once():
        rows = prepared.run_raw()
        rows.close()

    return {
        "dict_sec_median": _median_repeat(lambda: rt.run_embree(kernel, **inputs), repeats=repeats),
        "raw_sec_median": _median_repeat(
            lambda: _close_rows(rt.run_embree(kernel, result_mode="raw", **inputs)),
            repeats=repeats,
        ),
        "prepared_raw_sec_median": _median_repeat(run_raw_once, repeats=repeats),
    }


def _close_rows(rows) -> None:
    rows.close()


def _write_large_inputs(workload: str, inputs: dict[str, object], out_dir: Path) -> tuple[list[str], str, str]:
    if workload == "lsi":
        left_csv = out_dir / "left_segments.csv"
        right_csv = out_dir / "right_segments.csv"
        write_segments_csv(left_csv, inputs["left"])
        write_segments_csv(right_csv, inputs["right"])
        return ["--left", str(left_csv), "--right", str(right_csv)], "left_id", "right_id"
    if workload == "pip":
        points_csv = out_dir / "points.csv"
        polygons_csv = out_dir / "polygons.csv"
        write_points_csv(points_csv, inputs["points"])
        write_polygons_csv(polygons_csv, inputs["polygons"])
        return ["--points", str(points_csv), "--polygons", str(polygons_csv)], "point_id", "polygon_id"
    raise ValueError(f"unsupported Goal 19 workload `{workload}`")


def _fixture_inputs(workload: str, build: int, probe: int) -> tuple[dict[str, object], object, str, str]:
    if workload == "lsi":
        left, right = build_lsi_dataset(build_count=build, probe_count=probe, distribution="uniform")
        return {"left": left, "right": right}, county_zip_join_reference, "left_id", "right_id"
    if workload == "pip":
        points, polygons = build_pip_dataset(build_count=build, probe_count=probe, distribution="uniform")
        return {"points": points, "polygons": polygons}, point_in_counties_reference, "point_id", "polygon_id"
    raise ValueError(f"unsupported Goal 19 workload `{workload}`")


def compare_goal19(
    output_dir: Path | None = None,
    *,
    fixture_profile: dict[str, dict[str, int]] | None = None,
    large_profile: dict[str, dict[str, int]] | None = None,
    fixture_repeats: int = 25,
    large_repeats: int = 20,
) -> dict[str, object]:
    start_total = time.perf_counter()
    out = Path(output_dir or ROOT / "build" / "goal19_compare")
    out.mkdir(parents=True, exist_ok=True)
    system = platform.system()
    native_env = _native_runtime_env(system, _default_embree_prefix(system))

    lsi_exe = compile_native("goal15_lsi_native", "goal15_lsi_native.cpp")
    pip_exe = compile_native("goal15_pip_native", "goal15_pip_native.cpp")
    executables = {"lsi": lsi_exe, "pip": pip_exe}

    fixture_profile = fixture_profile or DEFAULT_FIXTURE_PROFILE
    large_profile = large_profile or DEFAULT_LARGE_PROFILE

    results: dict[str, object] = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fixture_repeats": fixture_repeats,
        "large_repeats": large_repeats,
        "fixture": {},
        "large_profile": {},
    }

    for workload in ("lsi", "pip"):
        fixture_inputs, kernel, left_field, right_field = _fixture_inputs(
            workload,
            fixture_profile[workload]["build"],
            fixture_profile[workload]["probe"],
        )
        fixture_dir = out / "fixture" / workload
        fixture_dir.mkdir(parents=True, exist_ok=True)
        native_args, _, _ = _write_large_inputs(workload, fixture_inputs, fixture_dir)
        native_pairs = fixture_dir / "native_pairs.csv"
        native_payload = _native_summary(
            executables[workload],
            [*native_args, "--pairs-out", str(native_pairs)],
            fixture_dir / "native_timing.json",
            env=native_env,
        )
        native_lines = native_pairs.read_text(encoding="utf-8").splitlines()

        dict_rows = rt.run_embree(kernel, **fixture_inputs)
        raw_rows = rt.run_embree(kernel, result_mode="raw", **fixture_inputs)
        try:
            raw_dict_rows = raw_rows.to_dict_rows()
        finally:
            raw_rows.close()
        prepared_rows = rt.prepare_embree(kernel).bind(**fixture_inputs).run_raw()
        try:
            prepared_dict_rows = prepared_rows.to_dict_rows()
        finally:
            prepared_rows.close()

        modes = _prepare_mode_medians(kernel, fixture_inputs, repeats=fixture_repeats)
        native_median = _native_median(
            executables[workload],
            native_args,
            fixture_dir / "native_timings",
            repeats=fixture_repeats,
            env=native_env,
        )
        dict_hash = _hash_rows(dict_rows, left_field, right_field)
        results["fixture"][workload] = {
            "build": fixture_profile[workload]["build"],
            "probe": fixture_profile[workload]["probe"],
            "row_count": len(dict_rows),
            "dict_matches_native": pair_rows(dict_rows, left_field, right_field) == native_lines,
            "raw_matches_dict": raw_dict_rows == dict_rows,
            "prepared_raw_matches_dict": prepared_dict_rows == dict_rows,
            "dict_pair_hash": dict_hash,
            "native_pair_hash": native_payload["pair_hash"],
            "native_pair_count": native_payload["row_count"],
            "dict_sec_median": modes["dict_sec_median"],
            "raw_sec_median": modes["raw_sec_median"],
            "prepared_raw_sec_median": modes["prepared_raw_sec_median"],
            "native_sec_median": native_median,
            "dict_gap_vs_native": modes["dict_sec_median"] / native_median if native_median > 0 else None,
            "raw_gap_vs_native": modes["raw_sec_median"] / native_median if native_median > 0 else None,
            "prepared_raw_gap_vs_native": modes["prepared_raw_sec_median"] / native_median if native_median > 0 else None,
        }

        large_inputs, kernel, left_field, right_field = _fixture_inputs(
            workload,
            large_profile[workload]["build"],
            large_profile[workload]["probe"],
        )
        large_dir = out / "large_profile" / workload
        large_dir.mkdir(parents=True, exist_ok=True)
        native_args, _, _ = _write_large_inputs(workload, large_inputs, large_dir)
        native_payload = _native_summary(
            executables[workload],
            native_args,
            large_dir / "native_summary.json",
            env=native_env,
        )
        dict_rows = rt.run_embree(kernel, **large_inputs)
        dict_hash = _hash_rows(dict_rows, left_field, right_field)
        modes = _prepare_mode_medians(kernel, large_inputs, repeats=large_repeats)
        native_median = _native_median(
            executables[workload],
            native_args,
            large_dir / "native_timings",
            repeats=large_repeats,
            env=native_env,
        )
        results["large_profile"][workload] = {
            "build": large_profile[workload]["build"],
            "probe": large_profile[workload]["probe"],
            "row_count": len(dict_rows),
            "dict_pair_hash": dict_hash,
            "native_pair_hash": native_payload["pair_hash"],
            "native_pair_count": native_payload["row_count"],
            "dict_matches_native": (dict_hash == native_payload["pair_hash"]),
            "dict_sec_median": modes["dict_sec_median"],
            "raw_sec_median": modes["raw_sec_median"],
            "prepared_raw_sec_median": modes["prepared_raw_sec_median"],
            "native_sec_median": native_median,
            "dict_gap_vs_native": modes["dict_sec_median"] / native_median if native_median > 0 else None,
            "raw_gap_vs_native": modes["raw_sec_median"] / native_median if native_median > 0 else None,
            "prepared_raw_gap_vs_native": modes["prepared_raw_sec_median"] / native_median if native_median > 0 else None,
        }

    results["total_wall_sec"] = time.perf_counter() - start_total
    (out / "goal19_compare.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return results


def format_goal19_report(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 19 Report: RTDL vs Native Embree Performance Comparison",
        "",
        "## Scope",
        "",
        "Goal 19 compares the current RTDL Embree runtime modes against the pure native C++ + Embree executables on matched `lsi` and `pip` workloads.",
        "",
        f"- fixture repeats: `{payload['fixture_repeats']}`",
        f"- larger-profile repeats: `{payload['large_repeats']}`",
        f"- total wall time: `{payload['total_wall_sec'] / 60.0:.2f} min`",
        "",
        "## Deterministic Fixture Comparison",
        "",
    ]
    for workload, stats in payload["fixture"].items():
        lines.extend([
            f"### {workload}",
            "",
            f"- build/probe: `{stats['build']}` / `{stats['probe']}`",
            f"- dict matches native: `{stats['dict_matches_native']}`",
            f"- raw matches dict: `{stats['raw_matches_dict']}`",
            f"- prepared raw matches dict: `{stats['prepared_raw_matches_dict']}`",
            f"- dict median: `{stats['dict_sec_median']:.9f} s`",
            f"- raw median: `{stats['raw_sec_median']:.9f} s`",
            f"- prepared raw median: `{stats['prepared_raw_sec_median']:.9f} s`",
            f"- native median: `{stats['native_sec_median']:.9f} s`",
            f"- dict gap vs native: `{stats['dict_gap_vs_native']:.2f}x`",
            f"- raw gap vs native: `{stats['raw_gap_vs_native']:.2f}x`",
            f"- prepared raw gap vs native: `{stats['prepared_raw_gap_vs_native']:.2f}x`",
            "",
        ])
    lines.extend(["## Larger Profile Comparison", ""])
    for workload, stats in payload["large_profile"].items():
        lines.extend([
            f"### {workload}",
            "",
            f"- build/probe: `{stats['build']}` / `{stats['probe']}`",
            f"- dict matches native: `{stats['dict_matches_native']}`",
            f"- dict median: `{stats['dict_sec_median']:.9f} s`",
            f"- raw median: `{stats['raw_sec_median']:.9f} s`",
            f"- prepared raw median: `{stats['prepared_raw_sec_median']:.9f} s`",
            f"- native median: `{stats['native_sec_median']:.9f} s`",
            f"- dict gap vs native: `{stats['dict_gap_vs_native']:.2f}x`",
            f"- raw gap vs native: `{stats['raw_gap_vs_native']:.2f}x`",
            f"- prepared raw gap vs native: `{stats['prepared_raw_gap_vs_native']:.2f}x`",
            "",
        ])
    lines.extend([
        "## Interpretation",
        "",
        "This report answers the current Embree-phase performance question only for `lsi` and `pip`, because those are the workloads with real native C++ baselines. The larger-profile section uses matched inputs and native summary hashes to ensure correctness before timing claims.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    out = ROOT / "build" / "goal19_compare"
    payload = compare_goal19(out)
    report = format_goal19_report(payload)
    report_path = ROOT / "docs" / "reports" / "goal19_embree_performance_comparison_2026-04-01.md"
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
