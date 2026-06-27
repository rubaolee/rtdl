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


def format_gb(num_bytes: int) -> str:
    return f"{num_bytes / (1024**3):.2f} GiB"


def build_report() -> str:
    payload = load_payload()
    hw = hardware_summary()
    measured_r = payload["config"]["build_polygons"]
    build_factor = build_size_adjustment(measured_r, PAPER_R)

    lines = [
        "# Goal 14 Estimation Report: Exact-Scale Section 5.6 on the Current Mac",
        "",
        "## Goal Definition",
        "",
        "Goal 14 narrows the current paper-reproduction work to one question only: can RTDL repeat RayJoin Section 5.6 with the **same nominal data sizes** on the current Mac, and if so, what should we expect for runtime and interpretability?",
        "",
        "This document is an **estimation report**, not a completion claim for the exact-scale run.",
        "",
        "## Current Machine",
        "",
        f"- Platform: `{hw['platform']}`",
        f"- Chip: `{hw['chip']}`",
        f"- Logical cores: `{hw['logical_cores']}`",
        f"- Physical cores: `{hw['physical_cores']}`",
        f"- Memory: `{hw['memory_gb']} GiB`",
        "",
        "## Paper Target",
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
            "## Practical Recommendation",
            "",
            "Goal 14 should remain an **estimation and readiness** goal for now. Before attempting exact-scale midnight runs on this Mac, RTDL should first add:",
            "",
            "- packed or memory-mapped numeric dataset generation instead of Python object materialization,",
            "- chunked probe processing so the build side can stay fixed while probe batches stream through Embree,",
            "- separate reporting for generation time, Embree build time, and query time,",
            "- and calibration runs at `100k`, `250k`, `500k`, and `1M` to validate the model before attempting `5M`.",
            "",
            "## Bottom Line",
            "",
            "- The current RTDL implementation does **not** yet support a trustworthy exact-size repetition of RayJoin Section 5.6 on this Mac.",
            f"- If the host-side memory model were removed as a blocker, the query-only estimate is roughly `{format_hours(total_by_workload['lsi'])}` for LSI and `{format_hours(total_by_workload['pip'])}` for PIP across the full paper-style run.",
            "- The reliable next step is not the midnight run itself; it is refactoring the Section 5.6 path so exact-scale inputs can be generated and consumed without Python-object explosion.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(build_report(), encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
