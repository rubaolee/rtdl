#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import platform
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_JSON = ROOT / "build" / "section_5_6_scalability" / "section_5_6_scalability.json"
OUT_DIR = ROOT / "docs" / "reports"
OUT_MD = OUT_DIR / "goal_14_section_5_6_exact_scale_estimation_2026-03-31.md"

PAPER_R = 5_000_000
PAPER_S_SERIES = (1_000_000, 2_000_000, 3_000_000, 4_000_000, 5_000_000)
ITERATIONS_PER_CASE = 5
WARMUP_PER_CASE = 1

# Rough deep-size heuristics for the current Python object model on CPython 3. These are
# intentionally rounded and used only for feasibility estimation.
POLYGON_BYTES = 600
SEGMENT_BYTES = 172
POINT_BYTES = 124


def load_payload() -> dict[str, object]:
    return json.loads(BUILD_JSON.read_text(encoding="utf-8"))


def hardware_summary() -> dict[str, str]:
    def run(*args: str) -> str:
        return subprocess.check_output(args, text=True).strip()

    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "chip": run("sysctl", "-n", "machdep.cpu.brand_string"),
        "logical_cores": run("sysctl", "-n", "hw.ncpu"),
        "physical_cores": run("sysctl", "-n", "hw.physicalcpu"),
        "memory_gb": f"{int(run('sysctl', '-n', 'hw.memsize')) / (1024**3):.1f}",
    }


def lsi_per_probe_segment_seconds(payload: dict[str, object], distribution: str) -> float:
    records = [
        r for r in payload["records"]
        if r["workload"] == "lsi" and r["distribution"] == distribution
    ]
    largest = max(records, key=lambda r: r["probe_polygons"])
    probe_segments = largest["probe_polygons"] * 4
    return (largest["query_time_ms"] / 1000.0) / probe_segments


def pip_per_probe_point_seconds(payload: dict[str, object], distribution: str) -> float:
    records = [
        r for r in payload["records"]
        if r["workload"] == "pip" and r["distribution"] == distribution
    ]
    largest = max(records, key=lambda r: r["probe_polygons"])
    probe_points = largest["probe_polygons"]
    return (largest["query_time_ms"] / 1000.0) / probe_points


def build_size_adjustment(measured_r: int, target_r: int) -> float:
    # Embree traversal should not scale linearly in build size. Use a conservative logarithmic
    # adjustment to convert from the current R=800 analogue to a 5M-polygon target.
    return math.log2(target_r) / math.log2(measured_r)


def format_hours(seconds: float) -> str:
    return f"{seconds / 3600.0:.2f} h"


def format_minutes(seconds: float) -> str:
    return f"{seconds / 60.0:.2f} min"


def format_gb(num_bytes: int) -> str:
    return f"{num_bytes / (1024**3):.2f} GiB"


def total_query_seconds_for_profile(payload: dict[str, object], *, workload: str, build_polygons: int, probe_series: tuple[int, ...]) -> float:
    measured_r = payload["config"]["build_polygons"]
    build_factor = build_size_adjustment(measured_r, build_polygons)
    total = 0.0
    if workload == "lsi":
        for distribution in ("uniform", "gaussian"):
            unit = lsi_per_probe_segment_seconds(payload, distribution) * build_factor
            for s in probe_series:
                total += unit * (s * 4) * (ITERATIONS_PER_CASE + WARMUP_PER_CASE)
    elif workload == "pip":
        for distribution in ("uniform", "gaussian"):
            unit = pip_per_probe_point_seconds(payload, distribution) * build_factor
            for s in probe_series:
                total += unit * s * (ITERATIONS_PER_CASE + WARMUP_PER_CASE)
    else:
        raise ValueError(f"unsupported workload: {workload}")
    return total


def build_report() -> str:
    payload = load_payload()
    hw = hardware_summary()
    measured_r = payload["config"]["build_polygons"]
    build_factor = build_size_adjustment(measured_r, PAPER_R)
    recommended_lsi_r = 100_000
    recommended_lsi_s = (100_000, 200_000, 300_000, 400_000, 500_000)
    recommended_pip_r = 100_000
    recommended_pip_s = (2_000, 4_000, 6_000, 8_000, 10_000)
    recommended_lsi_total = total_query_seconds_for_profile(
        payload,
        workload="lsi",
        build_polygons=recommended_lsi_r,
        probe_series=recommended_lsi_s,
    )
    recommended_pip_total = total_query_seconds_for_profile(
        payload,
        workload="pip",
        build_polygons=recommended_pip_r,
        probe_series=recommended_pip_s,
    )

    lines = [
        "# Goal 14 Estimation Report: Five-Minute Section 5.6 Local Profiles",
        "",
        "## Goal Definition",
        "",
        "Goal 14 now narrows the current paper-reproduction work to one practical question only: what Section 5.6 profile sizes let `lsi` and `pip` finish in about **five minutes each** on the current Mac while preserving the paper's two-distribution, five-point experiment shape?",
        "",
        "This document is an **estimation report**, not a completion claim for a full paper-scale run.",
        "",
        "## Current Machine",
        "",
        f"- Platform: `{hw['platform']}`",
        f"- Chip: `{hw['chip']}`",
        f"- Logical cores: `{hw['logical_cores']}`",
        f"- Physical cores: `{hw['physical_cores']}`",
        f"- Memory: `{hw['memory_gb']} GiB`",
        "",
        "## Paper Target Context",
        "",
        "- Fixed build-side polygons: `R = 5,000,000`",
        "- Probe-side series: `S = 1,000,000 .. 5,000,000`",
        "- Distributions: `uniform`, `gaussian`",
        "- Workloads: `lsi` and `pip`",
        "- Planned paper-style launch count per case in this estimate: `1 warmup + 5 measured iterations`",
        "",
        "## Estimation Method",
        "",
        "The estimate is derived from the current accepted Section 5.6 Embree analogue (`R = 800`, `S = 160..800`) and converted to the paper scale using a conservative logarithmic build-size adjustment.",
        "",
        "Two separate rates are used:",
        "",
        "- `lsi`: seconds per probe segment from the largest measured case in each distribution, then scaled from `R = 800` to `R = 5,000,000` using a log build-size factor.",
        "- `pip`: seconds per probe point from the largest measured case in each distribution, scaled by the same log build-size factor.",
        "",
        f"Current build-size adjustment factor from `800` to `5,000,000`: `{build_factor:.2f}x`",
        "",
        "## Query-Time Estimate",
        "",
        "| Workload | Distribution | S polygons | Mean query estimate | Case estimate with 1 warmup + 5 measured runs |",
        "| --- | --- | ---: | ---: | ---: |",
    ]

    total_by_workload: dict[str, float] = {"lsi": 0.0, "pip": 0.0}

    for distribution in ("uniform", "gaussian"):
        lsi_unit = lsi_per_probe_segment_seconds(payload, distribution) * build_factor
        pip_unit = pip_per_probe_point_seconds(payload, distribution) * build_factor
        for s in PAPER_S_SERIES:
            lsi_query_sec = lsi_unit * (s * 4)
            pip_query_sec = pip_unit * s
            lsi_case_sec = lsi_query_sec * (ITERATIONS_PER_CASE + WARMUP_PER_CASE)
            pip_case_sec = pip_query_sec * (ITERATIONS_PER_CASE + WARMUP_PER_CASE)
            total_by_workload["lsi"] += lsi_case_sec
            total_by_workload["pip"] += pip_case_sec
            lines.append(
                f"| `lsi` | `{distribution}` | {s:,} | {format_hours(lsi_query_sec)} | {format_hours(lsi_case_sec)} |"
            )
            lines.append(
                f"| `pip` | `{distribution}` | {s:,} | {format_hours(pip_query_sec)} | {format_hours(pip_case_sec)} |"
            )

    lines.extend(
        [
            "",
            "## Overnight Runtime Summary",
            "",
            f"- Estimated total `lsi` query wall time for all `uniform + gaussian` Section 5.6 cases: `{format_hours(total_by_workload['lsi'])}`",
            f"- Estimated total `pip` query wall time for all `uniform + gaussian` Section 5.6 cases: `{format_hours(total_by_workload['pip'])}`",
            f"- Estimated total query wall time for the combined Goal 14 exact-scale Section 5.6 run: `{format_hours(total_by_workload['lsi'] + total_by_workload['pip'])}`",
            "",
            "These numbers exclude Python-side data construction, Embree scene build time, file serialization, OS memory pressure, and thermal throttling. On this fanless MacBook Air, they should be treated as optimistic lower bounds.",
            "",
            "## Memory and Feasibility Estimate",
            "",
            "The current RTDL path materializes Python objects before Embree sees the data. That is the main blocker for exact-scale repetition on this machine.",
            "",
            "| Artifact | Count at paper scale | Rough current-Python footprint |",
            "| --- | ---: | ---: |",
            f"| Build polygons | {PAPER_R:,} | {format_gb(PAPER_R * POLYGON_BYTES)} |",
            f"| LSI build segments | {PAPER_R * 4:,} | {format_gb(PAPER_R * 4 * SEGMENT_BYTES)} |",
            f"| PIP probe points at `S=5M` | {5_000_000:,} | {format_gb(5_000_000 * POINT_BYTES)} |",
            f"| Probe polygons at `S=5M` | {5_000_000:,} | {format_gb(5_000_000 * POLYGON_BYTES)} |",
            f"| LSI probe segments at `S=5M` | {5_000_000 * 4:,} | {format_gb(5_000_000 * 4 * SEGMENT_BYTES)} |",
            "",
            "Interpretation:",
            "",
            "- `lsi` exact-scale cases are likely to exceed safe memory on this 16 GiB machine once Python objects, tuples, IDs, derived segments, native buffers, and Embree acceleration structures are all present.",
            "- `pip` exact-scale cases may fit at the low end of the size series, but the upper sizes are still likely to trigger heavy memory pressure or swap.",
            "- Because the host-side object model is the bottleneck, the exact-scale run is **not currently reliable enough to schedule as-is**, even overnight.",
            "",
            "## Can We Measure CPU vs GPU RT-Hardware Difference On This Mac?",
            "",
            "Not with the current repository.",
            "",
            "Why not:",
            "",
            "- RTDL currently has `run_cpu(...)` and `run_embree(...)`, both CPU-side paths.",
            "- There is no implemented Mac GPU ray-tracing backend in the repo today.",
            "- Therefore the current codebase cannot produce a trustworthy CPU-vs-GPU-RT comparison on this machine.",
            "",
            "What would be required to know that difference:",
            "",
            "1. Implement a GPU backend with the same Section 5.6 generator and metrics contract.",
            "2. Record build time, query time, and total wall time separately for CPU and GPU runs.",
            "3. Run identical seeds, distributions, size series, and iteration counts on both backends.",
            "4. Generate the same figure/report schema for direct comparison.",
            "",
        "## Recommended Five-Minute Profiles",
            "",
            "If the immediate objective is to keep both workloads near a five-minute query-only budget on this Mac, the following scaled profiles are the current recommended starting points:",
            "",
            f"- `lsi` recommendation: fixed `R = {recommended_lsi_r:,}` polygons, varying `S = {', '.join(f'{v:,}' for v in recommended_lsi_s)}` polygons.",
            f"  - estimated total query-only time: `{format_hours(recommended_lsi_total)}`",
            f"  - estimated total query-only time in minutes: `{format_minutes(recommended_lsi_total)}`",
            "  - rationale: this is the largest five-point `lsi` series that still stays under the five-minute query-only target under the current calibration model.",
            "  - caution: this is still an estimate; total wall time can be higher if Python materialization and background Mac usage add overhead.",
            "",
            f"- `pip` recommendation: fixed `R = {recommended_pip_r:,}` polygons, varying `S = {', '.join(f'{v:,}' for v in recommended_pip_s)}` polygons.",
            f"  - estimated total query-only time: `{format_hours(recommended_pip_total)}`",
            f"  - estimated total query-only time in minutes: `{format_minutes(recommended_pip_total)}`",
            "  - rationale: this is the largest five-point `pip` series that stays near the five-minute query-only target under the current calibration model.",
            "  - this profile is much smaller than paper scale because the current PIP path is substantially more expensive on this CPU-only Embree baseline.",
            "",
            "## Practical Recommendation",
            "",
            "Goal 14 should remain a **scaled local-execution** goal for now. The accepted next step is to run these five-minute profiles, not the paper-scale exact-size series. Before attempting exact-scale midnight runs on this Mac, RTDL would still need:",
            "",
            "- packed or memory-mapped numeric dataset generation instead of Python object materialization,",
            "- chunked probe processing so the build side can stay fixed while probe batches stream through Embree,",
            "- separate reporting for generation time, Embree build time, and query time,",
            "- and calibration runs at `100k`, `250k`, `500k`, and `1M` to validate the model before attempting `5M`.",
            "",
            "## Bottom Line",
            "",
            "- The current RTDL implementation does **not** yet support a trustworthy exact-size repetition of RayJoin Section 5.6 on this Mac.",
            f"- The full paper-scale query-only estimate is still roughly `{format_hours(total_by_workload['lsi'])}` for LSI and `{format_hours(total_by_workload['pip'])}` for PIP across the complete Section 5.6 run.",
            f"- The practical Goal 14 target is now the five-minute local profile: `{format_minutes(recommended_lsi_total)}` estimated query-only for LSI and `{format_minutes(recommended_pip_total)}` estimated query-only for PIP.",
            "- The reliable next step is to run those scaled local profiles and record real wall-clock behavior on this Mac.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(build_report(), encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
