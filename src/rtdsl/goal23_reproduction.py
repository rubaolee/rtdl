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
    report_pdf.write_bytes(_simple_pdf_from_lines(_report_pdf_lines(payload, figure13_svg, figure14_svg, figure15_svg)))

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
    lines = [
        "# Goal 23 Embree Reproduction Report",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Boundary: `{payload['goal_boundary']}`",
        f"- Total package wall time: `{payload['total_wall_sec']:.2f} s`",
        "",
        "## Executed Slice",
        "",
        "- Table 3: partial bounded local analogue rows only",
        "- Figure 13: bounded synthetic `lsi` analogue",
        "- Figure 14: bounded synthetic `pip` analogue",
        "- Table 4: bounded overlay-seed analogue",
        "- Figure 15: bounded overlay-seed speedup analogue",
        "",
        "## Missing / Unexecuted Families",
        "",
    ]
    missing_pairs = [
        row for row in payload["table3_rows"]
        if row["execution_status"] != "executed-local-analogue"
    ]
    for row in missing_pairs:
        lines.append(f"- `{row['paper_pair']}` / `{row['workload']}` remains `{row['execution_status']}`: {row['source_note']}")

    lines.extend(
        [
            "",
            "## Table 3 Summary",
            "",
            *[f"- `{row['local_case_id']}`: `{row['paper_pair']}` / `{row['workload']}` / `{row['fidelity']}` / speedup `{row['speedup_vs_cpu']:.2f}x`" for row in payload["table3_rows"] if row["speedup_vs_cpu"] is not None],
            "",
            "## Table 4 Summary",
            "",
            *[f"- `{row['local_case_id']}`: `{row['fidelity']}` / speedup `{row['speedup_vs_cpu']:.2f}x`" for row in payload["table4_rows"]],
            "",
            "## Figure Artifacts",
            "",
            f"- `{figure13_svg}`",
            f"- `{figure14_svg}`",
            f"- `{figure15_svg}`",
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
    width = 900
    height = 420
    left = 220
    top = 70
    bar_h = 36
    gap = 34
    max_speedup = max((row["speedup_vs_cpu"] or 0.0) for row in rows) or 1.0
    chart_w = width - left - 80
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<style>text{font-family:Helvetica,Arial,sans-serif;font-size:12px;} .title{font-size:22px;font-weight:bold;} .axis{stroke:#333;stroke-width:1;}</style>',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="30" y="34" class="title">Figure 15 Bounded Overlay Speedup Analogue</text>',
        '<text x="30" y="54">Embree speedup over CPU for the current overlay-seed local analogue cases.</text>',
        f'<line class="axis" x1="{left}" y1="{top + len(rows) * (bar_h + gap)}" x2="{left + chart_w}" y2="{top + len(rows) * (bar_h + gap)}"/>',
    ]
    for idx, row in enumerate(rows):
        y = top + idx * (bar_h + gap)
        bar_w = chart_w * ((row["speedup_vs_cpu"] or 0.0) / max_speedup)
        parts.append(f'<text x="20" y="{y + 22}">{_svg_escape(row["local_case_id"])}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" fill="#1565c0"/>')
        parts.append(f'<text x="{left + bar_w + 8:.1f}" y="{y + 22}">{row["speedup_vs_cpu"]:.2f}x</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _report_pdf_lines(payload: dict[str, object], figure13_svg: Path, figure14_svg: Path, figure15_svg: Path) -> list[str]:
    lines = [
        "Goal 23 Embree Reproduction Report",
        "",
        f"Generated: {payload['generated_at']}",
        f"Boundary: {payload['goal_boundary']}",
        f"Total package wall time: {payload['total_wall_sec']:.2f} s",
        "",
        "Executed slice:",
        "- Table 3 partial bounded local analogue rows only",
        "- Figure 13 bounded synthetic LSI analogue",
        "- Figure 14 bounded synthetic PIP analogue",
        "- Table 4 bounded overlay-seed analogue",
        "- Figure 15 bounded overlay speedup analogue",
        "",
        "Missing / unexecuted families:",
    ]
    for row in payload["table3_rows"]:
        if row["speedup_vs_cpu"] is None:
            lines.append(f"- {row['paper_pair']} / {row['workload']}: {row['execution_status']} ({row['source_note']})")
    lines.extend(
        [
            "",
            "Executed Table 3 rows:",
        ]
    )
    for row in payload["table3_rows"]:
        if row["speedup_vs_cpu"] is not None:
            lines.append(
                f"- {row['local_case_id']}: {row['paper_pair']} / {row['workload']} / {row['fidelity']} / speedup={row['speedup_vs_cpu']:.2f}x"
            )
    lines.extend(
        [
            "",
            "Overlay rows:",
        ]
    )
    for row in payload["table4_rows"]:
        lines.append(f"- {row['local_case_id']}: speedup={row['speedup_vs_cpu']:.2f}x / {row['fidelity']}")
    lines.extend(
        [
            "",
            f"Figure 13 SVG: {figure13_svg}",
            f"Figure 14 SVG: {figure14_svg}",
            f"Figure 15 SVG: {figure15_svg}",
        ]
    )
    return lines


def _simple_pdf_from_lines(lines: list[str]) -> bytes:
    return _section56_simple_pdf_from_lines(lines)


def _section56_simple_pdf_from_lines(lines: list[str]) -> bytes:
    pages = [lines[index:index + 44] for index in range(0, len(lines), 44)] or [[]]
    objects: list[bytes] = []

    def add_object(payload: bytes) -> int:
        objects.append(payload)
        return len(objects)

    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_ids = []
    content_ids = []

    for page_lines in pages:
        content = ["BT", "/F1 11 Tf"]
        y = 770
        for line in page_lines:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            content.append(f"1 0 0 1 72 {y} Tm ({safe}) Tj")
            y -= 16
        content.append("ET")
        stream = "\n".join(content).encode("utf-8")
        content_id = add_object(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        content_ids.append(content_id)
        page_id = add_object(
            b"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 "
            + str(font_id).encode("ascii")
            + b" 0 R >> >> /Contents "
            + str(content_id).encode("ascii")
            + b" 0 R >>"
        )
        page_ids.append(page_id)

    pages_kids = " ".join(f"{page_id} 0 R" for page_id in page_ids).encode("ascii")
    pages_id = add_object(
        b"<< /Type /Pages /Kids ["
        + pages_kids
        + b"] /Count "
        + str(len(page_ids)).encode("ascii")
        + b" >>"
    )

    for page_id in page_ids:
        page_obj = objects[page_id - 1].replace(b"/Parent 0 0 R", b"/Parent " + str(pages_id).encode("ascii") + b" 0 R")
        objects[page_id - 1] = page_obj

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


def _svg_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
