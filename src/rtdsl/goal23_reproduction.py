from __future__ import annotations

import json
import statistics
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .baseline_benchmark import benchmark_workload
from .baseline_runner import load_representative_case
from .datasets import rayjoin_bounded_plans
from .datasets import rayjoin_public_assets
from .paper_reproduction import dataset_families
from .paper_reproduction import local_profiles
from .paper_reproduction import paper_targets
from .section_5_6_scalability import build_scalability_figure_svg
from .section_5_6_scalability import generate_pdf_lines as _section56_pdf_lines
from .section_5_6_scalability import generate_synthetic_polygons
from .section_5_6_scalability import polygon_probe_points
from .section_5_6_scalability import polygons_to_segments
from .section_5_6_scalability import _distribution_seed_offset
from .embree_runtime import prepare_embree
from .embree_runtime import run_embree
from .runtime import run_cpu

ROOT = Path(__file__).resolve().parents[2]


TABLE3_EXECUTED_CASES = (
    {
        "paper_pair": "County ⊲⊳ Zipcode",
        "workload": "lsi",
        "dataset": "tests/fixtures/rayjoin/br_county_subset.cdb",
        "fidelity": "fixture-subset",
        "local_case_id": "county_fixture_subset_lsi",
        "source_note": "County-side local analogue only; zipcode exact-input not yet acquired.",
    },
    {
        "paper_pair": "County ⊲⊳ Zipcode",
        "workload": "lsi",
        "dataset": "derived/br_county_subset_segments_tiled_x8",
        "fidelity": "derived-input",
        "local_case_id": "county_tiled_x8_lsi",
        "source_note": "Deterministic county fixture enlargement; zipcode exact-input not yet acquired.",
    },
    {
        "paper_pair": "County ⊲⊳ Zipcode",
        "workload": "pip",
        "dataset": "tests/fixtures/rayjoin/br_county_subset.cdb",
        "fidelity": "fixture-subset",
        "local_case_id": "county_fixture_subset_pip",
        "source_note": "County-side local analogue only; zipcode exact-input not yet acquired.",
    },
    {
        "paper_pair": "County ⊲⊳ Zipcode",
        "workload": "pip",
        "dataset": "derived/br_county_subset_polygons_tiled_x8",
        "fidelity": "derived-input",
        "local_case_id": "county_tiled_x8_pip",
        "source_note": "Deterministic county fixture enlargement; zipcode exact-input not yet acquired.",
    },
)

TABLE4_EXECUTED_CASES = (
    {
        "dataset": "tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb",
        "local_case_id": "overlay_fixture_subset",
        "fidelity": "overlay-seed analogue / fixture-subset",
        "source_note": "Current local public sample pair, not a paper-original overlay pair.",
    },
    {
        "dataset": "derived/br_county_soil_polygons_tiled_x8",
        "local_case_id": "overlay_tiled_x8",
        "fidelity": "overlay-seed analogue / derived-input",
        "source_note": "Deterministic enlargement from the current local public sample pair.",
    },
)


def generate_goal23_artifacts(
    *,
    output_dir: str | Path | None = None,
    publish_docs: bool = True,
    config: dict[str, object] | None = None,
) -> dict[str, Path]:
    output_root = Path(output_dir or ROOT / "build" / "goal23_reproduction")
    output_root.mkdir(parents=True, exist_ok=True)
    figures_dir = output_root / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    payload = run_goal23_reproduction(config=config)

    json_path = output_root / "goal23_reproduction.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    table3_md = output_root / "table3_bounded_results.md"
    table4_md = output_root / "table4_overlay_results.md"
    report_md = output_root / "goal23_embree_reproduction_report.md"
    figure13_svg = figures_dir / "figure13_lsi_bounded.svg"
    figure14_svg = figures_dir / "figure14_pip_bounded.svg"
    figure15_svg = figures_dir / "figure15_overlay_speedup_bounded.svg"
    report_pdf = output_root / "goal23_embree_reproduction_report.pdf"

    figure13_svg.write_text(
        build_scalability_figure_svg(payload["figure13"], workload="lsi", title="Figure 13 Bounded Embree Analogue: LSI"),
        encoding="utf-8",
    )
    figure14_svg.write_text(
        build_scalability_figure_svg(payload["figure14"], workload="pip", title="Figure 14 Bounded Embree Analogue: PIP"),
        encoding="utf-8",
    )
    figure15_svg.write_text(_build_overlay_speedup_svg(payload), encoding="utf-8")
    table3_md.write_text(_render_table3(payload), encoding="utf-8")
    table4_md.write_text(_render_table4(payload), encoding="utf-8")
    report_md.write_text(_render_report(payload, figure13_svg, figure14_svg, figure15_svg), encoding="utf-8")
    report_pdf.write_bytes(_build_goal23_paper_pdf(payload))

    artifacts = {
        "json": json_path,
        "table3": table3_md,
        "table4": table4_md,
        "figure13_svg": figure13_svg,
        "figure14_svg": figure14_svg,
        "figure15_svg": figure15_svg,
        "report_markdown": report_md,
        "report_pdf": report_pdf,
    }
    if publish_docs:
        published_md = ROOT / "docs" / "reports" / "goal23_embree_reproduction_report_2026-04-01.md"
        published_pdf = ROOT / "docs" / "reports" / "goal23_embree_reproduction_report_2026-04-01.pdf"
        published_md.write_text(report_md.read_text(encoding="utf-8"), encoding="utf-8")
        published_pdf.write_bytes(report_pdf.read_bytes())
        artifacts["published_markdown"] = published_md
        artifacts["published_pdf"] = published_pdf
    return artifacts


def run_goal23_reproduction(*, config: dict[str, object] | None = None) -> dict[str, object]:
    from examples.rtdl_language_reference import county_soil_overlay_reference
    from examples.rtdl_language_reference import county_zip_join_reference
    from examples.rtdl_language_reference import point_in_counties_reference

    start_total = time.perf_counter()
    cfg = {
        "figure13_build_polygons": 100_000,
        "figure13_probe_series": (100_000, 200_000, 300_000, 400_000, 500_000),
        "figure14_build_polygons": 100_000,
        "figure14_probe_series": (2_000, 4_000, 6_000, 8_000, 10_000),
        "scalability_iterations": 2,
        "scalability_warmup": 1,
        "table_iterations": 3,
        "table_warmup": 1,
    }
    if config:
        cfg.update(config)

    figure13 = _run_bounded_scalability(
        kernel=county_zip_join_reference,
        workload="lsi",
        build_polygons=cfg["figure13_build_polygons"],
        probe_series=tuple(cfg["figure13_probe_series"]),
        distributions=("uniform", "gaussian"),
        iterations=cfg["scalability_iterations"],
        warmup=cfg["scalability_warmup"],
        base_seed=17,
    )
    figure14 = _run_bounded_scalability(
        kernel=point_in_counties_reference,
        workload="pip",
        build_polygons=cfg["figure14_build_polygons"],
        probe_series=tuple(cfg["figure14_probe_series"]),
        distributions=("uniform", "gaussian"),
        iterations=cfg["scalability_iterations"],
        warmup=cfg["scalability_warmup"],
        base_seed=17,
    )

    table3_rows = []
    executed_by_key = {}
    for case in TABLE3_EXECUTED_CASES:
        stats = benchmark_workload(
            case["workload"],
            case["dataset"],
            backend="embree",
            iterations=cfg["table_iterations"],
            warmup=cfg["table_warmup"],
        )
        cpu_stats = benchmark_workload(
            case["workload"],
            case["dataset"],
            backend="cpu",
            iterations=cfg["table_iterations"],
            warmup=cfg["table_warmup"],
        )
        row = {
            **case,
            "execution_status": "executed-local-analogue",
            "embree_mean_sec": stats["mean_sec"],
            "cpu_mean_sec": cpu_stats["mean_sec"],
            "speedup_vs_cpu": (cpu_stats["mean_sec"] / stats["mean_sec"]) if stats["mean_sec"] > 0 else 0.0,
            "note": stats["note"],
        }
        table3_rows.append(row)
        executed_by_key[(case["paper_pair"], case["workload"])] = True

    for target in paper_targets(artifact="table3"):
        key = (target.paper_label, target.workload)
        if key in executed_by_key:
            continue
        family = dataset_families(handle=target.dataset_handle)[0]
        table3_rows.append(
            {
                "paper_pair": target.paper_label,
                "workload": target.workload,
                "dataset": target.dataset_handle,
                "fidelity": "missing/unacquired",
                "local_case_id": "missing",
                "source_note": family.local_plan,
                "execution_status": family.current_status,
                "embree_mean_sec": None,
                "cpu_mean_sec": None,
                "speedup_vs_cpu": None,
                "note": "No bounded local run executed because the required input family is still only source-identified.",
            }
        )

    table4_rows = []
    for case in TABLE4_EXECUTED_CASES:
        embree = benchmark_workload(
            "overlay",
            case["dataset"],
            backend="embree",
            iterations=cfg["table_iterations"],
            warmup=cfg["table_warmup"],
        )
        cpu = benchmark_workload(
            "overlay",
            case["dataset"],
            backend="cpu",
            iterations=cfg["table_iterations"],
            warmup=cfg["table_warmup"],
        )
        table4_rows.append(
            {
                **case,
                "execution_status": "executed-overlay-seed-analogue",
                "embree_mean_sec": embree["mean_sec"],
                "cpu_mean_sec": cpu["mean_sec"],
                "speedup_vs_cpu": (cpu["mean_sec"] / embree["mean_sec"]) if embree["mean_sec"] > 0 else 0.0,
                "note": embree["note"],
            }
        )

    return {
        "suite": "goal23_bounded_embree_reproduction",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "goal_boundary": "bounded-local executable slice only; missing source-identified families remain reported but unexecuted",
        "config": cfg,
        "total_wall_sec": time.perf_counter() - start_total,
        "source_assets": [asdict(asset) for asset in rayjoin_public_assets()],
        "bounded_plans": [asdict(plan) for plan in rayjoin_bounded_plans()],
        "figure13": figure13,
        "figure14": figure14,
        "table3_rows": table3_rows,
        "table4_rows": table4_rows,
    }


def _run_bounded_scalability(
    *,
    kernel,
    workload: str,
    build_polygons: int,
    probe_series: tuple[int, ...],
    distributions: tuple[str, ...],
    iterations: int,
    warmup: int,
    base_seed: int,
) -> dict[str, object]:
    records = []
    parity_checks = []
    prepared = prepare_embree(kernel)

    for distribution in distributions:
        build_polygons_set = generate_synthetic_polygons(
            count=build_polygons,
            distribution=distribution,
            seed=base_seed + _distribution_seed_offset(distribution),
        )
        if workload == "lsi":
            build_input = {"right": polygons_to_segments(build_polygons_set)}
        else:
            build_input = {"polygons": build_polygons_set}

        for probe_count in probe_series:
            probe_polygons = generate_synthetic_polygons(
                count=probe_count,
                distribution=distribution,
                seed=base_seed + 100 + probe_count + _distribution_seed_offset(distribution),
            )
            if workload == "lsi":
                bound_inputs = {
                    "left": polygons_to_segments(probe_polygons),
                    **build_input,
                }
                throughput_unit = "intersections/s"
            else:
                bound_inputs = {
                    "points": polygon_probe_points(probe_polygons),
                    **build_input,
                }
                throughput_unit = "probe-points/s"

            execution = prepared.bind(**bound_inputs)
            for _ in range(warmup):
                rows = execution.run_raw()
                rows.close()

            timings = []
            result_count = 0
            for _ in range(iterations):
                start = time.perf_counter()
                rows = execution.run_raw()
                result_count = len(rows)
                rows.close()
                timings.append(time.perf_counter() - start)

            mean_sec = statistics.mean(timings) if timings else 0.0
            throughput_count = result_count if workload == "lsi" else len(bound_inputs["points"])
            records.append(
                {
                    "workload": workload,
                    "distribution": distribution,
                    "build_polygons": build_polygons,
                    "probe_polygons": probe_count,
                    "query_time_ms": mean_sec * 1000.0,
                    "throughput": (throughput_count / mean_sec) if mean_sec > 0 else 0.0,
                    "throughput_unit": throughput_unit,
                    "result_count": result_count,
                }
            )

        parity_probe_polygons = generate_synthetic_polygons(
            count=120,
            distribution=distribution,
            seed=base_seed + 999 + _distribution_seed_offset(distribution),
        )
        parity_build_polygons = generate_synthetic_polygons(
            count=160,
            distribution=distribution,
            seed=base_seed + 1999 + _distribution_seed_offset(distribution),
        )
        if workload == "lsi":
            cpu_rows = run_cpu(
                kernel,
                left=polygons_to_segments(parity_probe_polygons),
                right=polygons_to_segments(parity_build_polygons),
            )
            embree_rows = run_embree(
                kernel,
                left=polygons_to_segments(parity_probe_polygons),
                right=polygons_to_segments(parity_build_polygons),
            )
        else:
            cpu_rows = run_cpu(
                kernel,
                points=polygon_probe_points(parity_probe_polygons),
                polygons=parity_build_polygons,
            )
            embree_rows = run_embree(
                kernel,
                points=polygon_probe_points(parity_probe_polygons),
                polygons=parity_build_polygons,
            )
        parity_checks.append(
            {
                "distribution": distribution,
                "workload": workload,
                "parity": cpu_rows == embree_rows,
                "probe_polygons": 120,
                "build_polygons": 160,
            }
        )

    return {
        "suite": f"goal23_{workload}_bounded_scalability",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "method": "bounded local Embree analogue using prepared raw execution",
        "config": {
            "build_polygons": build_polygons,
            "probe_series": list(probe_series),
            "iterations": iterations,
            "warmup": warmup,
            "distributions": list(distributions),
            "workloads": [workload],
        },
        "records": records,
        "parity_checks": parity_checks,
    }


def _render_table3(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 23 Table 3 Bounded Results",
        "",
        "Executed rows are bounded local analogues only. Missing families remain explicitly unexecuted.",
        "",
        "| Paper Pair | Workload | Local Case | Fidelity | Execution Status | CPU Mean (s) | Embree Mean (s) | Speedup | Note |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["table3_rows"]:
        cpu = f"{row['cpu_mean_sec']:.6f}" if row["cpu_mean_sec"] is not None else "-"
        embree = f"{row['embree_mean_sec']:.6f}" if row["embree_mean_sec"] is not None else "-"
        speedup = f"{row['speedup_vs_cpu']:.2f}x" if row["speedup_vs_cpu"] is not None else "-"
        lines.append(
            f"| {row['paper_pair']} | `{row['workload']}` | `{row['local_case_id']}` | `{row['fidelity']}` | "
            f"`{row['execution_status']}` | {cpu} | {embree} | {speedup} | {row['source_note']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_table4(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 23 Table 4 Overlay Results",
        "",
        "These rows are bounded local overlay-seed analogues, not full overlay materialization results from the paper datasets.",
        "",
        "| Local Case | Fidelity | Execution Status | CPU Mean (s) | Embree Mean (s) | Speedup | Note |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["table4_rows"]:
        lines.append(
            f"| `{row['local_case_id']}` | `{row['fidelity']}` | `{row['execution_status']}` | "
            f"{row['cpu_mean_sec']:.6f} | {row['embree_mean_sec']:.6f} | {row['speedup_vs_cpu']:.2f}x | {row['source_note']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_report(payload: dict[str, object], figure13_svg: Path, figure14_svg: Path, figure15_svg: Path) -> str:
    executed_rows = [row for row in payload["table3_rows"] if row["speedup_vs_cpu"] is not None]
    missing_rows = [row for row in payload["table3_rows"] if row["speedup_vs_cpu"] is None]
    source_assets = payload["source_assets"]
    bounded_plans = payload["bounded_plans"]
    lines = [
        "# RTDL Embree Reproduction of RayJoin Experiments",
        "",
        f"_Generated: {payload['generated_at']}. Total package wall time: {payload['total_wall_sec']:.2f} s._",
        "",
        "## Abstract",
        "",
        "This report presents the current bounded local reproduction of the RayJoin evaluation structure on top of RTDL's Intel Embree backend.",
        "The purpose is not to claim exact paper-scale equivalence. Instead, the report documents what the current Python-hosted DSL, lowered runtime, and Embree execution engine can already execute on a local Mac while preserving the frozen `5-10 minute` wall-time policy for iterative development.",
        "The executed slice includes bounded analogues for Table 3, Figure 13, Figure 14, Table 4, and Figure 15. Missing dataset families remain explicitly labeled as source-identified and unexecuted.",
        "",
        "## 1. Introduction",
        "",
        "RayJoin evaluates spatial join workloads over ray-tracing style acceleration structures. RTDL is a Python-like DSL and runtime stack that aims to express the same workload family while remaining portable across backends.",
        "In the current pre-NVIDIA phase, the concrete backend is Intel Embree. The work in Goal 23 therefore asks a narrower question: how much of the RayJoin experiment structure can be reproduced honestly on the bounded local Embree path, given current machine limits and incomplete access to the paper's preprocessed datasets?",
        "",
        "## 2. RTDL Language Overview",
        "",
        "RTDL exposes a compact kernel DSL with explicit geometry inputs, candidate traversal, predicate refinement, and emitted row schemas.",
        "A workload such as `lsi` is written as a kernel over segment inputs, lowered into RTDL IR, then executed through a prepared Embree path. The same language surface also supports `pip`, `overlay`, `ray_tri_hitcount`, `segment_polygon_hitcount`, and `point_nearest_segment`.",
        "",
        "## 3. Architecture",
        "",
        "The current execution stack is: Python-like DSL -> `CompiledKernel` -> backend-oriented RayJoin-style plan -> prepared Embree execution -> raw or dictionary result materialization.",
        "For Goal 23, all scalability-style runs use the low-overhead prepared raw execution path so the report reflects the current best local Embree implementation rather than the older dict-heavy runtime path.",
        "",
        "## 4. Datasets and Fidelity Boundary",
        "",
        "RTDL currently mixes three kinds of inputs: checked-in fixture subsets, deterministic derived enlargements, and synthetic generators. The fidelity labels in this report are critical because not all paper-original dataset families are locally executable yet.",
        "",
        "### 4.1 Public Source Registry",
        "",
        "| Asset | Status | Preferred Use |",
        "| --- | --- | --- |",
    ]
    for asset in source_assets:
        lines.append(
            f"| `{asset['asset_id']}` | `{asset['current_status']}` | {asset['preferred_use']} |"
        )
    lines.extend(
        [
            "",
            "### 4.2 Bounded Preparation Policy",
            "",
            "| Dataset Handle | Status | Deterministic Rule |",
            "| --- | --- | --- |",
        ]
    )
    for plan in bounded_plans:
        lines.append(
            f"| `{plan['handle']}` | `{plan['current_status']}` | {plan['deterministic_rule']} |"
        )
    lines.extend(
        [
            "",
            "## 5. Experimental Setup",
            "",
            f"- Goal boundary: `{payload['goal_boundary']}`",
            "- Backend: Intel Embree only; no NVIDIA GPU or OptiX path is used here.",
            "- Runtime mode: prepared raw execution for bounded Figure 13 / Figure 14 analogue runs.",
            f"- Figure 13 profile: fixed `R={payload['config']['figure13_build_polygons']}` polygons, `S={', '.join(str(x) for x in payload['config']['figure13_probe_series'])}`.",
            f"- Figure 14 profile: fixed `R={payload['config']['figure14_build_polygons']}` polygons, `S={', '.join(str(x) for x in payload['config']['figure14_probe_series'])}`.",
            f"- Scalability iterations / warmup: `{payload['config']['scalability_iterations']}` / `{payload['config']['scalability_warmup']}`.",
            f"- Table iterations / warmup: `{payload['config']['table_iterations']}` / `{payload['config']['table_warmup']}`.",
            "",
            "## 6. Results",
            "",
            "### 6.1 Table 3 Executed Rows",
            "",
            "| Paper Pair | Workload | Local Case | Fidelity | CPU Mean (s) | Embree Mean (s) | Speedup |",
            "| --- | --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in executed_rows:
        lines.append(
            f"| {row['paper_pair']} | `{row['workload']}` | `{row['local_case_id']}` | `{row['fidelity']}` | "
            f"{row['cpu_mean_sec']:.6f} | {row['embree_mean_sec']:.6f} | {row['speedup_vs_cpu']:.2f}x |"
        )
    lines.extend(
        [
            "",
            "### 6.2 Missing / Unexecuted Families",
            "",
            "| Paper Pair | Workload | Status | Source Requirement |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in missing_rows:
        lines.append(
            f"| {row['paper_pair']} | `{row['workload']}` | `{row['execution_status']}` | {row['source_note']} |"
        )
    lines.extend(
        [
            "",
            "### 6.3 Table 4 Overlay-Seed Analogue",
            "",
            "| Local Case | Fidelity | CPU Mean (s) | Embree Mean (s) | Speedup |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in payload["table4_rows"]:
        lines.append(
            f"| `{row['local_case_id']}` | `{row['fidelity']}` | {row['cpu_mean_sec']:.6f} | {row['embree_mean_sec']:.6f} | {row['speedup_vs_cpu']:.2f}x |"
        )
    lines.extend(
        [
            "",
            "### 6.4 Embedded Figures",
            "",
            "#### Figure 13: Bounded LSI Analogue",
            "",
            f"![Figure 13 bounded LSI analogue](../../build/goal23_reproduction/figures/{figure13_svg.name})",
            "",
            "#### Figure 14: Bounded PIP Analogue",
            "",
            f"![Figure 14 bounded PIP analogue](../../build/goal23_reproduction/figures/{figure14_svg.name})",
            "",
            "#### Figure 15: Bounded Overlay Speedup Analogue",
            "",
            f"![Figure 15 bounded overlay speedup analogue](../../build/goal23_reproduction/figures/{figure15_svg.name})",
            "",
            "## 7. Discussion",
            "",
            "The executed results show that RTDL can already reproduce a meaningful bounded slice of the RayJoin experiment structure on the local Embree backend.",
            "However, the report is intentionally explicit about the remaining gap: most Table 3 paper-original dataset families are still source-identified rather than fully acquired and converted. In addition, the overlay rows remain an `overlay-seed analogue` rather than a claim of full paper-equivalent polygon overlay execution.",
            "",
            "## 8. Conclusion",
            "",
            "Goal 23 completes the bounded local reproduction package: a paper-style report, embedded figures, explicit tables, dataset provenance, and fidelity labeling.",
            "This report should be read as the current Embree-phase research baseline: reproducible, locally executable, and honest about what is executed, what is scaled, and what remains to be acquired before a fuller RayJoin reproduction can be claimed.",
            "",
            "## Fidelity Labels",
            "",
            "- `fixture-subset`: checked-in tiny public subset",
            "- `derived-input`: deterministic enlargement or bounded reduction from an available source",
            "- `synthetic-input`: deterministic synthetic generator",
            "- `overlay-seed analogue`: current RTDL overlay path, not full polygon materialization",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _build_overlay_speedup_svg(payload: dict[str, object]) -> str:
    rows = payload["table4_rows"]
    width = 980
    height = 440
    left = 250
    top = 96
    bar_h = 34
    gap = 30
    max_speedup = max((row["speedup_vs_cpu"] or 0.0) for row in rows) or 1.0
    chart_w = width - left - 86
    chart_bottom = top + len(rows) * (bar_h + gap)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        (
            '<style>'
            'text{font-family:Helvetica,Arial,sans-serif;font-size:14px;fill:#222;} '
            '.title{font-size:26px;font-weight:bold;} '
            '.subtitle{font-size:14px;fill:#555;} '
            '.axis{stroke:#333;stroke-width:1.4;} '
            '.grid{stroke:#e2e5ea;stroke-width:1;} '
            '.small{font-size:12px;fill:#444;}'
            '</style>'
        ),
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="42" y="42" class="title">Figure 15 Analogue: Overlay-Seed Speedup</text>',
        '<text x="42" y="66" class="subtitle">Embree speedup over the native CPU oracle on the validated local overlay-seed cases.</text>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{chart_bottom}"/>',
        f'<line class="axis" x1="{left}" y1="{chart_bottom}" x2="{left + chart_w}" y2="{chart_bottom}"/>',
    ]
    for tick in range(5):
        x_value = max_speedup * tick / 4
        x = left + chart_w * tick / 4
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{chart_bottom}"/>')
        parts.append(f'<text x="{x:.1f}" y="{chart_bottom+22}" text-anchor="middle" class="small">{x_value:.1f}x</text>')
    parts.append(f'<text x="{left + chart_w/2:.1f}" y="{chart_bottom+44}" text-anchor="middle" class="small">Embree speedup over CPU</text>')
    for idx, row in enumerate(rows):
        y = top + idx * (bar_h + gap)
        bar_w = chart_w * ((row["speedup_vs_cpu"] or 0.0) / max_speedup)
        parts.append(f'<text x="{left-14}" y="{y + 22}" text-anchor="end">{_svg_escape(row["local_case_id"])}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" rx="6" fill="#1565c0"/>')
        parts.append(f'<text x="{left + bar_w + 10:.1f}" y="{y + 22}">{row["speedup_vs_cpu"]:.2f}x</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _report_pdf_lines(payload: dict[str, object], figure13_svg: Path, figure14_svg: Path, figure15_svg: Path) -> list[str]:
    del figure13_svg, figure14_svg, figure15_svg
    return [
        "RTDL Embree Reproduction of RayJoin Experiments",
        f"Generated: {payload['generated_at']}",
        f"Total package wall time: {payload['total_wall_sec']:.2f} s",
    ]


def _simple_pdf_from_lines(lines: list[str]) -> bytes:
    canvas = _PdfCanvas()
    top = 54
    for line in lines:
        if top > 530:
            canvas.new_page()
            top = 54
        top = canvas.paragraph(54, top, 684, line or " ", size=11, leading=16)
    return canvas.to_pdf()


class _PdfCanvas:
    PAGE_W = 792
    PAGE_H = 612

    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.current: list[str] = []
        self.pages.append(self.current)

    def new_page(self) -> None:
        self.current = []
        self.pages.append(self.current)

    def _push(self, command: str) -> None:
        self.current.append(command)

    def _y(self, top: float) -> float:
        return self.PAGE_H - top

    def text(
        self,
        x: float,
        top: float,
        value: str,
        *,
        size: float = 10,
        bold: bool = False,
        color: tuple[float, float, float] = (0.0, 0.0, 0.0),
        align: str = "left",
    ) -> None:
        escaped = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if align != "left":
            width = _estimate_text_width(value, size=size)
            if align == "center":
                x -= width / 2.0
            elif align == "right":
                x -= width
        font = "F2" if bold else "F1"
        self._push(
            f"BT /{font} {size:.2f} Tf {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg "
            f"1 0 0 1 {x:.2f} {self._y(top):.2f} Tm ({escaped}) Tj ET"
        )

    def line(
        self,
        x1: float,
        top1: float,
        x2: float,
        top2: float,
        *,
        color: tuple[float, float, float] = (0.0, 0.0, 0.0),
        width: float = 1.0,
    ) -> None:
        self._push(
            f"q {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} RG {width:.2f} w "
            f"{x1:.2f} {self._y(top1):.2f} m {x2:.2f} {self._y(top2):.2f} l S Q"
        )

    def rect(
        self,
        x: float,
        top: float,
        width: float,
        height: float,
        *,
        stroke: tuple[float, float, float] | None = (0.0, 0.0, 0.0),
        fill: tuple[float, float, float] | None = None,
        line_width: float = 1.0,
    ) -> None:
        pdf_y = self.PAGE_H - top - height
        parts = ["q"]
        if fill is not None:
            parts.append(f"{fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg")
        if stroke is not None:
            parts.append(f"{stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG {line_width:.2f} w")
        operator = "B" if fill is not None and stroke is not None else "f" if fill is not None else "S"
        parts.append(f"{x:.2f} {pdf_y:.2f} {width:.2f} {height:.2f} re {operator} Q")
        self._push(" ".join(parts))

    def polyline(
        self,
        points: list[tuple[float, float]],
        *,
        color: tuple[float, float, float] = (0.0, 0.0, 0.0),
        width: float = 1.2,
    ) -> None:
        if len(points) < 2:
            return
        commands = [
            f"q {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} RG {width:.2f} w",
            f"{points[0][0]:.2f} {self._y(points[0][1]):.2f} m",
        ]
        for x, top in points[1:]:
            commands.append(f"{x:.2f} {self._y(top):.2f} l")
        commands.append("S Q")
        self._push(" ".join(commands))

    def paragraph(
        self,
        x: float,
        top: float,
        width: float,
        text: str,
        *,
        size: float = 10,
        leading: float = 14,
        bold: bool = False,
    ) -> float:
        cursor = top
        for line in _wrap_text(text, width=width, size=size):
            self.text(x, cursor, line, size=size, bold=bold)
            cursor += leading
        return cursor

    def to_pdf(self) -> bytes:
        objects: list[bytes] = []

        def add_object(payload: bytes) -> int:
            objects.append(payload)
            return len(objects)

        font_regular = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font_bold = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        page_ids = []
        for commands in self.pages:
            stream = "\n".join(commands).encode("utf-8")
            content_id = add_object(
                b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
            )
            page_id = add_object(
                b"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 792 612] "
                b"/Resources << /Font << /F1 "
                + str(font_regular).encode("ascii")
                + b" 0 R /F2 "
                + str(font_bold).encode("ascii")
                + b" 0 R >> >> /Contents "
                + str(content_id).encode("ascii")
                + b" 0 R >>"
            )
            page_ids.append(page_id)

        pages_kids = " ".join(f"{page_id} 0 R" for page_id in page_ids).encode("ascii")
        pages_id = add_object(
            b"<< /Type /Pages /Kids [" + pages_kids + b"] /Count " + str(len(page_ids)).encode("ascii") + b" >>"
        )
        for page_id in page_ids:
            objects[page_id - 1] = objects[page_id - 1].replace(
                b"/Parent 0 0 R",
                b"/Parent " + str(pages_id).encode("ascii") + b" 0 R",
            )

        catalog_id = add_object(b"<< /Type /Catalog /Pages " + str(pages_id).encode("ascii") + b" 0 R >>")

        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n".encode("ascii"))
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")
        xref_start = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        pdf.extend(
            b"trailer\n<< /Size "
            + str(len(objects) + 1).encode("ascii")
            + b" /Root "
            + str(catalog_id).encode("ascii")
            + b" 0 R >>\nstartxref\n"
            + str(xref_start).encode("ascii")
            + b"\n%%EOF\n"
        )
        return bytes(pdf)


def _build_goal23_paper_pdf(payload: dict[str, object]) -> bytes:
    canvas = _PdfCanvas()
    _draw_goal23_title_page(canvas, payload)
    canvas.new_page()
    _draw_goal23_architecture_page(canvas)
    canvas.new_page()
    _draw_goal23_dataset_page(canvas, payload)
    canvas.new_page()
    _draw_goal23_table3_page(canvas, payload)
    canvas.new_page()
    _draw_goal23_missing_and_table4_page(canvas, payload)
    canvas.new_page()
    _draw_goal23_scalability_page(canvas, payload["figure13"], title="Figure 13. Bounded LSI Analogue", workload="lsi")
    canvas.new_page()
    _draw_goal23_scalability_page(canvas, payload["figure14"], title="Figure 14. Bounded PIP Analogue", workload="pip")
    canvas.new_page()
    _draw_goal23_overlay_page(canvas, payload)
    return canvas.to_pdf()


def _draw_goal23_title_page(canvas: _PdfCanvas, payload: dict[str, object]) -> None:
    canvas.text(396, 48, "RTDL Embree Reproduction of RayJoin Experiments", size=24, bold=True, align="center")
    canvas.text(396, 76, "Bounded Local Report for Goal 23", size=14, align="center", color=(0.25, 0.25, 0.25))
    canvas.line(54, 98, 738, 98, color=(0.2, 0.2, 0.2), width=1.5)
    top = 126
    top = canvas.paragraph(54, top, 684, "Abstract", size=15, bold=True, leading=18)
    abstract = (
        "This paper-style report summarizes the current bounded local reproduction of the RayJoin evaluation "
        "structure on top of RTDL's Intel Embree backend. The current system does not claim exact paper-scale "
        "equivalence. Instead, it provides a reproducible Embree-phase baseline that executes the currently "
        "supported workload family, reports explicit fidelity labels, and keeps the total local package within "
        "a 5-10 minute development budget."
    )
    top = canvas.paragraph(54, top + 4, 684, abstract, size=11, leading=16)
    top += 12
    intro = (
        "RTDL is a Python-like DSL for ray-join style spatial workloads. Its current execution stack lowers a "
        "kernel through a backend-neutral compiled form and a RayJoin-shaped backend plan, then executes through "
        "prepared Embree kernels with either dictionary or raw-row result materialization. Goal 23 packages the "
        "current bounded reproduction slice into tables and figures corresponding to RayJoin Table 3, Table 4, "
        "Figure 13, Figure 14, and Figure 15."
    )
    top = canvas.paragraph(54, top, 684, intro, size=11, leading=16)
    top += 14
    bullet_y = top
    bullets = [
        f"Generated at {payload['generated_at']}",
        f"Total package wall time: {payload['total_wall_sec']:.2f} s",
        "Backend: Intel Embree only (no GPU path in this report)",
        "Figure 13 and Figure 14 use prepared raw execution with bounded synthetic inputs",
        "Table 3 and Table 4 remain explicit about executed analogues vs missing families",
    ]
    for bullet in bullets:
        canvas.text(66, bullet_y, "•", size=12, bold=True)
        bullet_y = canvas.paragraph(82, bullet_y, 646, bullet, size=11, leading=16)
    canvas.text(738, 586, "1", size=10, align="right", color=(0.4, 0.4, 0.4))


def _draw_goal23_architecture_page(canvas: _PdfCanvas) -> None:
    canvas.text(54, 44, "1. RTDL Language and Architecture", size=18, bold=True)
    top = 74
    paragraph = (
        "RTDL keeps the authoring surface compact: a kernel declares typed geometry inputs, a candidate traversal, "
        "a predicate refinement, and an emitted row schema. The current Embree phase executes these kernels through "
        "prepared low-overhead bindings so the report reflects the best local runtime path rather than the older "
        "Python-dictionary hot path."
    )
    top = canvas.paragraph(54, top, 684, paragraph, size=11, leading=15)
    top += 18
    boxes = [
        ("Python-like DSL", 60),
        ("CompiledKernel", 185),
        ("RayJoin Plan", 310),
        ("Packed Buffers", 435),
        ("Prepared Embree", 560),
        ("Raw Rows / Tables", 685),
    ]
    for label, x in boxes:
        canvas.rect(x, 190, 92, 48, stroke=(0.2, 0.2, 0.2), fill=(0.96, 0.97, 0.99))
        canvas.text(x + 46, 217, label, size=10, bold=True, align="center")
    for (_, x0), (_, x1) in zip(boxes, boxes[1:]):
        canvas.line(x0 + 92, 214, x1, 214, color=(0.15, 0.15, 0.15), width=1.2)
        canvas.line(x1 - 8, 210, x1, 214, color=(0.15, 0.15, 0.15), width=1.2)
        canvas.line(x1 - 8, 218, x1, 214, color=(0.15, 0.15, 0.15), width=1.2)
    top = 284
    canvas.text(54, top, "Execution Notes", size=14, bold=True)
    notes = [
        "The DSL surface currently supports six workloads in the local Embree baseline: lsi, pip, overlay, ray_tri_hitcount, segment_polygon_hitcount, and point_nearest_segment.",
        "Figure 13 and Figure 14 use the prepared raw execution path because it is the only local path shown to stay close to native C/C++ Embree performance in the Goal 19 comparison.",
        "This report therefore describes the current best local execution architecture while keeping the language surface unchanged.",
    ]
    top += 22
    for note in notes:
        canvas.text(66, top, "•", size=12, bold=True)
        top = canvas.paragraph(82, top, 646, note, size=11, leading=15)
    canvas.text(738, 586, "2", size=10, align="right", color=(0.4, 0.4, 0.4))


def _draw_goal23_dataset_page(canvas: _PdfCanvas, payload: dict[str, object]) -> None:
    canvas.text(54, 44, "2. Data Sources and Experimental Setup", size=18, bold=True)
    top = 74
    intro = (
        "Goal 23 mixes executed local analogues with source-identified but unexecuted paper families. This split is "
        "intentional: the report is meant to be honest about what currently runs on the local machine and what still "
        "requires public-source acquisition and conversion."
    )
    top = canvas.paragraph(54, top, 684, intro, size=11, leading=15)
    top += 12
    canvas.text(54, top, "Public Source Registry", size=14, bold=True)
    top += 20
    rows = [[a["asset_id"], a["current_status"], a["preferred_use"]] for a in payload["source_assets"]]
    top = _draw_table(canvas, 54, top, [160, 110, 414], ["Asset", "Status", "Preferred Use"], rows, font_size=9, row_height=24)
    top += 18
    canvas.text(54, top, "Bounded Local Profiles", size=14, bold=True)
    top += 20
    lines = [
        f"Figure 13 (LSI): fixed build side R={payload['config']['figure13_build_polygons']} polygons; probe side S={', '.join(str(v) for v in payload['config']['figure13_probe_series'])}.",
        f"Figure 14 (PIP): fixed build side R={payload['config']['figure14_build_polygons']} polygons; probe side S={', '.join(str(v) for v in payload['config']['figure14_probe_series'])}.",
        "All bounded local comparisons keep the total package near the frozen 5-10 minute target so the reproduction loop remains practical on the current Mac.",
    ]
    for line in lines:
        top = canvas.paragraph(54, top, 684, line, size=11, leading=15)
    canvas.text(738, 586, "3", size=10, align="right", color=(0.4, 0.4, 0.4))


def _draw_goal23_table3_page(canvas: _PdfCanvas, payload: dict[str, object]) -> None:
    canvas.text(54, 44, "3. Table 3: Executed Bounded Local Rows", size=18, bold=True)
    top = 72
    text = (
        "The rows below are the currently executable Table 3 analogues. They are local bounded runs over available "
        "fixture subsets or deterministic enlargements, not exact paper-original dataset pairs."
    )
    top = canvas.paragraph(54, top, 684, text, size=11, leading=15)
    top += 14
    executed = [row for row in payload["table3_rows"] if row["speedup_vs_cpu"] is not None]
    rows = [
        [
            row["paper_pair"],
            row["workload"],
            row["local_case_id"],
            row["fidelity"],
            f"{row['cpu_mean_sec']:.6f}",
            f"{row['embree_mean_sec']:.6f}",
            f"{row['speedup_vs_cpu']:.2f}x",
        ]
        for row in executed
    ]
    top = _draw_table(
        canvas,
        54,
        top,
        [132, 54, 132, 96, 72, 72, 72],
        ["Paper Pair", "Workload", "Local Case", "Fidelity", "CPU (s)", "Embree (s)", "Speedup"],
        rows,
        font_size=8,
        row_height=22,
    )
    top += 20
    canvas.text(54, top, "Missing / Unexecuted Families", size=14, bold=True)
    top += 18
    missing = [row for row in payload["table3_rows"] if row["speedup_vs_cpu"] is None][:7]
    rows = [[row["paper_pair"], row["workload"], row["execution_status"], _truncate(row["source_note"], 74)] for row in missing]
    _draw_table(canvas, 54, top, [178, 58, 86, 362], ["Paper Pair", "Workload", "Status", "Source Requirement"], rows, font_size=8, row_height=22)
    canvas.text(738, 586, "4", size=10, align="right", color=(0.4, 0.4, 0.4))


def _draw_goal23_missing_and_table4_page(canvas: _PdfCanvas, payload: dict[str, object]) -> None:
    canvas.text(54, 44, "4. Remaining Families and Table 4", size=18, bold=True)
    top = 72
    remaining = [row for row in payload["table3_rows"] if row["speedup_vs_cpu"] is None][7:]
    rows = [[row["paper_pair"], row["workload"], row["execution_status"], _truncate(row["source_note"], 72)] for row in remaining]
    top = _draw_table(canvas, 54, top, [178, 58, 86, 362], ["Paper Pair", "Workload", "Status", "Source Requirement"], rows, font_size=8, row_height=22)
    top += 20
    canvas.text(54, top, "Table 4. Overlay-Seed Analogue Rows", size=14, bold=True)
    top += 18
    rows = [
        [
            row["local_case_id"],
            row["fidelity"],
            f"{row['cpu_mean_sec']:.6f}",
            f"{row['embree_mean_sec']:.6f}",
            f"{row['speedup_vs_cpu']:.2f}x",
        ]
        for row in payload["table4_rows"]
    ]
    _draw_table(canvas, 54, top, [170, 260, 76, 76, 76], ["Local Case", "Fidelity", "CPU (s)", "Embree (s)", "Speedup"], rows, font_size=8, row_height=24)
    canvas.text(738, 586, "5", size=10, align="right", color=(0.4, 0.4, 0.4))


def _draw_goal23_scalability_page(canvas: _PdfCanvas, figure_payload: dict[str, object], *, title: str, workload: str) -> None:
    canvas.text(54, 40, title, size=18, bold=True)
    canvas.text(54, 60, f"Fixed build side R={figure_payload['config']['build_polygons']} polygons; prepared raw Embree execution.", size=10, color=(0.35, 0.35, 0.35))
    records = figure_payload["records"]
    _draw_figure_panel(
        canvas,
        x=54,
        top=88,
        width=300,
        height=190,
        records=[r for r in records if r["distribution"] == "uniform"],
        field="query_time_ms",
        title="(a) Uniform - Query Time",
        y_label="Query Time (ms)",
        color=(0.08, 0.40, 0.75),
    )
    _draw_figure_panel(
        canvas,
        x=414,
        top=88,
        width=300,
        height=190,
        records=[r for r in records if r["distribution"] == "gaussian"],
        field="query_time_ms",
        title="(b) Gaussian - Query Time",
        y_label="Query Time (ms)",
        color=(0.42, 0.11, 0.60),
    )
    _draw_figure_panel(
        canvas,
        x=54,
        top=332,
        width=300,
        height=190,
        records=[r for r in records if r["distribution"] == "uniform"],
        field="throughput",
        title="(c) Uniform - Throughput",
        y_label=_throughput_pdf_label(workload),
        color=(0.18, 0.49, 0.20),
    )
    _draw_figure_panel(
        canvas,
        x=414,
        top=332,
        width=300,
        height=190,
        records=[r for r in records if r["distribution"] == "gaussian"],
        field="throughput",
        title="(d) Gaussian - Throughput",
        y_label=_throughput_pdf_label(workload),
        color=(0.94, 0.42, 0.00),
    )
    canvas.text(738, 586, "6" if workload == "lsi" else "7", size=10, align="right", color=(0.4, 0.4, 0.4))


def _draw_goal23_overlay_page(canvas: _PdfCanvas, payload: dict[str, object]) -> None:
    canvas.text(54, 44, "7. Figure 15 and Summary", size=18, bold=True)
    canvas.text(54, 68, "Bounded overlay-seed analogue: Embree speedup over CPU for the currently executable local cases.", size=10, color=(0.35, 0.35, 0.35))
    _draw_overlay_speedup_chart(canvas, 72, 106, 648, 210, payload["table4_rows"])
    top = 352
    canvas.text(54, top, "Discussion", size=14, bold=True)
    top += 20
    paragraphs = [
        "The executed slice shows that RTDL can already reproduce a meaningful bounded subset of the RayJoin evaluation structure on a local Embree backend. Figure 13 and Figure 14 are now first-class generated artefacts rather than planning placeholders.",
        "The main remaining gap is dataset completeness rather than report infrastructure. Most Table 3 paper rows are still source-identified but unexecuted, and Table 4 remains an overlay-seed analogue rather than a full polygon-materialization claim.",
        "This report should therefore be interpreted as the current Embree-phase research baseline: executable, reproducible, bounded, and explicit about fidelity boundaries.",
    ]
    for paragraph in paragraphs:
        top = canvas.paragraph(54, top, 684, paragraph, size=11, leading=15)
        top += 6
    canvas.text(738, 586, "8", size=10, align="right", color=(0.4, 0.4, 0.4))


def _draw_table(
    canvas: _PdfCanvas,
    x: float,
    top: float,
    col_widths: list[float],
    headers: list[str],
    rows: list[list[str]],
    *,
    font_size: float,
    row_height: float,
) -> float:
    total_w = sum(col_widths)
    canvas.rect(x, top, total_w, row_height, stroke=(0.5, 0.5, 0.5), fill=(0.92, 0.94, 0.97), line_width=0.8)
    cursor_x = x
    for header, width in zip(headers, col_widths):
        canvas.text(cursor_x + 4, top + 15, _truncate(header, int(width / 5.5)), size=font_size, bold=True)
        cursor_x += width
    y = top + row_height
    for row in rows:
        canvas.rect(x, y, total_w, row_height, stroke=(0.78, 0.78, 0.78), fill=None, line_width=0.5)
        cursor_x = x
        for value, width in zip(row, col_widths):
            canvas.line(cursor_x, y, cursor_x, y + row_height, color=(0.80, 0.80, 0.80), width=0.4)
            canvas.text(cursor_x + 4, y + 15, _truncate(str(value), int(width / 5.0)), size=font_size)
            cursor_x += width
        canvas.line(x + total_w, y, x + total_w, y + row_height, color=(0.80, 0.80, 0.80), width=0.4)
        y += row_height
    return y


def _draw_figure_panel(
    canvas: _PdfCanvas,
    *,
    x: float,
    top: float,
    width: float,
    height: float,
    records: list[dict[str, object]],
    field: str,
    title: str,
    y_label: str,
    color: tuple[float, float, float],
) -> None:
    plot_left = x + 44
    plot_top = top + 24
    plot_w = width - 62
    plot_h = height - 52
    canvas.rect(x, top, width, height, stroke=(0.75, 0.75, 0.75), fill=None, line_width=0.8)
    canvas.text(x + 8, top + 16, title, size=10, bold=True)
    canvas.line(plot_left, plot_top + plot_h, plot_left + plot_w, plot_top + plot_h, color=(0.2, 0.2, 0.2), width=0.8)
    canvas.line(plot_left, plot_top, plot_left, plot_top + plot_h, color=(0.2, 0.2, 0.2), width=0.8)
    max_x = max(record["probe_polygons"] for record in records) if records else 1
    max_y = max(float(record[field]) for record in records) if records else 1.0
    for step in range(5):
        ratio = step / 4.0
        grid_top = plot_top + plot_h - ratio * plot_h
        canvas.line(plot_left, grid_top, plot_left + plot_w, grid_top, color=(0.88, 0.88, 0.88), width=0.5)
        value = max_y * ratio
        canvas.text(plot_left - 6, grid_top + 4, _format_axis_value(value), size=7, align="right", color=(0.35, 0.35, 0.35))
    points = []
    for record in records:
        x_val = float(record["probe_polygons"])
        y_val = float(record[field])
        px = plot_left + (x_val / max_x) * plot_w
        py = plot_top + plot_h - (y_val / max_y) * plot_h if max_y > 0 else plot_top + plot_h
        points.append((px, py))
        canvas.rect(px - 2.2, py - 2.2, 4.4, 4.4, stroke=None, fill=color)
        canvas.text(px, plot_top + plot_h + 18, str(record["probe_polygons"]), size=7, align="center", color=(0.35, 0.35, 0.35))
    canvas.polyline(points, color=color, width=1.5)
    canvas.text(x + width / 2.0, top + height - 8, "Probe-side polygons (S)", size=7, align="center", color=(0.35, 0.35, 0.35))
    canvas.text(x + 12, top + height / 2.0, y_label, size=7, color=(0.35, 0.35, 0.35))


def _draw_overlay_speedup_chart(canvas: _PdfCanvas, x: float, top: float, width: float, height: float, rows: list[dict[str, object]]) -> None:
    label_w = 200
    chart_left = x + label_w
    chart_w = width - label_w - 30
    bar_h = 28
    gap = 30
    max_speed = max(row["speedup_vs_cpu"] for row in rows) or 1.0
    canvas.rect(x, top, width, height, stroke=(0.75, 0.75, 0.75), fill=None, line_width=0.8)
    canvas.line(chart_left, top + height - 34, chart_left + chart_w, top + height - 34, color=(0.2, 0.2, 0.2), width=0.8)
    for idx, row in enumerate(rows):
        y = top + 36 + idx * (bar_h + gap)
        ratio = row["speedup_vs_cpu"] / max_speed if max_speed > 0 else 0.0
        bar_w = chart_w * ratio
        canvas.text(x + 6, y + 17, row["local_case_id"], size=10)
        canvas.rect(chart_left, y, bar_w, bar_h, stroke=None, fill=(0.08, 0.40, 0.75))
        canvas.text(chart_left + bar_w + 8, y + 17, f"{row['speedup_vs_cpu']:.2f}x", size=10)


def _estimate_text_width(value: str, *, size: float) -> float:
    return len(value) * size * 0.52


def _wrap_text(text: str, *, width: float, size: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if _estimate_text_width(candidate, size=size) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)] + "…"


def _format_axis_value(value: float) -> str:
    if value >= 1000:
        return f"{value:.0f}"
    if value >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def _throughput_pdf_label(workload: str) -> str:
    return "Intersections/s" if workload == "lsi" else "Probe-points/s"


def _svg_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
