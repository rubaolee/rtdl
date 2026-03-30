from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import socket
import textwrap
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .baseline_benchmark import benchmark_workload
from .baseline_runner import load_representative_case
from .baseline_runner import run_baseline_case
from .evaluation_matrix import evaluation_entries

ROOT = Path(__file__).resolve().parents[2]


def generate_evaluation_artifacts(
    *,
    workloads: tuple[str, ...] | None = None,
    iterations: int = 5,
    warmup: int = 1,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    output_root = Path(output_dir or ROOT / "build" / "embree_evaluation")
    output_root.mkdir(parents=True, exist_ok=True)
    payload = run_evaluation(workloads=workloads, iterations=iterations, warmup=warmup)

    json_path = output_root / "embree_evaluation.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    markdown_path = output_root / "embree_evaluation_summary.md"
    markdown_path.write_text(generate_markdown_summary(payload), encoding="utf-8")

    csv_path = output_root / "embree_evaluation_table.csv"
    write_csv_table(payload, csv_path)

    figure_dir = output_root / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    latency_svg = figure_dir / "latency_by_case.svg"
    speedup_svg = figure_dir / "speedup_by_case.svg"
    scaling_svg = figure_dir / "scaling_by_workload.svg"
    latency_svg.write_text(build_latency_svg(payload), encoding="utf-8")
    speedup_svg.write_text(build_speedup_svg(payload), encoding="utf-8")
    scaling_svg.write_text(build_scaling_svg(payload), encoding="utf-8")

    pdf_path = output_root / "embree_evaluation_report.pdf"
    write_pdf_report(payload, pdf_path, (latency_svg, speedup_svg, scaling_svg))

    gap_path = output_root / "embree_gap_analysis.md"
    gap_path.write_text(generate_gap_analysis(payload, (latency_svg, speedup_svg, scaling_svg)), encoding="utf-8")

    return {
        "json": json_path,
        "markdown": markdown_path,
        "csv": csv_path,
        "latency_svg": latency_svg,
        "speedup_svg": speedup_svg,
        "scaling_svg": scaling_svg,
        "pdf": pdf_path,
        "gap_analysis": gap_path,
    }


def run_evaluation(
    *,
    workloads: tuple[str, ...] | None = None,
    iterations: int,
    warmup: int,
) -> dict[str, object]:
    from examples.rtdl_language_reference import county_soil_overlay_reference
    from examples.rtdl_language_reference import county_zip_join_reference
    from examples.rtdl_language_reference import point_in_counties_reference
    from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference

    kernels = {
        "lsi": county_zip_join_reference,
        "pip": point_in_counties_reference,
        "overlay": county_soil_overlay_reference,
        "ray_tri_hitcount": ray_triangle_hitcount_reference,
    }

    records = []
    for entry in evaluation_entries(workloads):
        kernel = kernels[entry.workload]
        parity_payload = run_baseline_case(kernel, entry.dataset, backend="both")
        cpu_case = load_representative_case(entry.workload, entry.dataset)
        cpu_bench = benchmark_workload(
            entry.workload,
            entry.dataset,
            backend="cpu",
            iterations=iterations,
            warmup=warmup,
        )
        embree_bench = benchmark_workload(
            entry.workload,
            entry.dataset,
            backend="embree",
            iterations=iterations,
            warmup=warmup,
        )
        records.append(
            {
                **asdict(entry),
                "parity": parity_payload["parity"],
                "note": parity_payload["note"],
                "input_sizes": {
                    key: len(value)
                    for key, value in cpu_case.inputs.items()
                },
                "cpu": cpu_bench,
                "embree": embree_bench,
                "speedup_vs_cpu": (
                    cpu_bench["mean_sec"] / embree_bench["mean_sec"]
                    if embree_bench["mean_sec"] > 0
                    else 0.0
                ),
            }
        )

    return {
        "suite": "rtdl_embree_evaluation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "iterations": iterations,
        "warmup": warmup,
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "records": records,
    }


def generate_markdown_summary(payload: dict[str, object]) -> str:
    lines = [
        "# RTDL Embree Evaluation Summary",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Iterations: `{payload['iterations']}`",
        f"- Warmup: `{payload['warmup']}`",
        f"- Host: `{payload['host']['platform']}`",
        "",
        "## Evaluation Matrix",
        "",
        "| Case | Workload | Dataset | Category | Parity | CPU Mean (s) | Embree Mean (s) | Speedup |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for record in payload["records"]:
        lines.append(
            f"| `{record['case_id']}` | `{record['workload']}` | `{record['dataset']}` | "
            f"`{record['category']}` | `{record['parity']}` | "
            f"{record['cpu']['mean_sec']:.6f} | {record['embree']['mean_sec']:.6f} | {record['speedup_vs_cpu']:.3f}x |"
        )

    lines.extend(
        [
            "",
            "## Key Findings",
            "",
            *[f"- {line}" for line in _key_findings(payload)],
            "",
            "## Figures",
            "",
            "- `figures/latency_by_case.svg`",
            "- `figures/speedup_by_case.svg`",
            "- `figures/scaling_by_workload.svg`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def generate_gap_analysis(payload: dict[str, object], figures: tuple[Path, Path, Path]) -> str:
    lines = [
        "# Embree Gap Analysis",
        "",
        "This report describes what the current Embree evaluation reproduces and what remains deferred to the NVIDIA/OptiX phase.",
        "",
        "## What Goal 9 Reproduces",
        "",
        "- A frozen workload/dataset evaluation matrix across the current four RTDL workloads.",
        "- Reproducible local benchmark artifacts on top of a real native ray tracing engine (Embree).",
        "- Automatic generation of summary tables and figure files from the benchmark outputs.",
        "- CPU-vs-Embree correctness checks before timing claims for every matrix entry.",
        "",
        "## What Goal 9 Does Not Claim",
        "",
        "- NVIDIA RT-core execution.",
        "- OptiX/CUDA runtime behavior.",
        "- Final RayJoin paper performance parity or direct reproduction of the paper's hardware results.",
        "",
        "## Current Local Limitations",
        "",
        "- The local dataset fixtures are tiny public subsets; larger cases are deterministic derived tiles or synthetic generators.",
        "- The current precision mode is still `float_approx` rather than a robust or exact arithmetic implementation.",
        "- The overlay workload is still evaluated as compositional seed generation rather than a full polygon overlay implementation.",
        "",
        "## Generated Figures",
        "",
    ]
    for figure in figures:
        lines.append(f"- `{figure}`")
    lines.append("")
    lines.extend(f"- {finding}" for finding in _key_findings(payload))
    return "\n".join(lines).rstrip() + "\n"


def write_csv_table(payload: dict[str, object], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "case_id",
                "workload",
                "dataset",
                "category",
                "parity",
                "cpu_mean_sec",
                "embree_mean_sec",
                "speedup_vs_cpu",
                "input_sizes",
            ]
        )
        for record in payload["records"]:
            writer.writerow(
                [
                    record["case_id"],
                    record["workload"],
                    record["dataset"],
                    record["category"],
                    record["parity"],
                    f"{record['cpu']['mean_sec']:.9f}",
                    f"{record['embree']['mean_sec']:.9f}",
                    f"{record['speedup_vs_cpu']:.6f}",
                    json.dumps(record["input_sizes"], sort_keys=True),
                ]
            )


def build_latency_svg(payload: dict[str, object]) -> str:
    items = payload["records"]
    width = 1200
    row_h = 30
    top = 70
    height = top + len(items) * row_h + 70
    max_mean = max(max(record["cpu"]["mean_sec"], record["embree"]["mean_sec"]) for record in items) or 1.0
    chart_x = 380
    chart_w = width - chart_x - 80
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<style>text{font-family:Helvetica,Arial,sans-serif;font-size:12px;} .title{font-size:20px;font-weight:bold;} .small{font-size:11px;fill:#555;} </style>',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="40" y="32" class="title">RTDL Embree Evaluation: CPU vs Embree Latency</text>',
        '<text x="40" y="52" class="small">Mean time per case. This is the Embree CPU baseline, not an NVIDIA/RT-core result.</text>',
    ]
    for tick in range(5):
        value = max_mean * tick / 4
        x = chart_x + chart_w * tick / 4
        parts.append(f'<line x1="{x:.1f}" y1="{top-10}" x2="{x:.1f}" y2="{height-40}" stroke="#ddd" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{height-18}" text-anchor="middle" class="small">{value:.4f}s</text>')
    for idx, record in enumerate(items):
        y = top + idx * row_h
        label = f"{record['workload']} | {record['case_id']}"
        cpu_w = chart_w * record["cpu"]["mean_sec"] / max_mean
        embree_w = chart_w * record["embree"]["mean_sec"] / max_mean
        parts.append(f'<text x="40" y="{y+14}" text-anchor="start">{_svg_escape(label)}</text>')
        parts.append(f'<rect x="{chart_x}" y="{y}" width="{cpu_w:.1f}" height="10" fill="#c96f3d"/>')
        parts.append(f'<rect x="{chart_x}" y="{y+12}" width="{embree_w:.1f}" height="10" fill="#2e7d32"/>')
    parts.append(f'<rect x="{chart_x}" y="{height-55}" width="14" height="10" fill="#c96f3d"/>')
    parts.append(f'<text x="{chart_x+20}" y="{height-46}">CPU reference</text>')
    parts.append(f'<rect x="{chart_x+140}" y="{height-55}" width="14" height="10" fill="#2e7d32"/>')
    parts.append(f'<text x="{chart_x+160}" y="{height-46}">Embree baseline</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def build_speedup_svg(payload: dict[str, object]) -> str:
    items = payload["records"]
    width = 1200
    row_h = 28
    top = 70
    height = top + len(items) * row_h + 70
    max_speedup = max(record["speedup_vs_cpu"] for record in items) or 1.0
    chart_x = 380
    chart_w = width - chart_x - 80
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<style>text{font-family:Helvetica,Arial,sans-serif;font-size:12px;} .title{font-size:20px;font-weight:bold;} .small{font-size:11px;fill:#555;} </style>',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="40" y="32" class="title">RTDL Embree Evaluation: Embree Speedup vs CPU</text>',
        '<text x="40" y="52" class="small">Speedup is computed from mean CPU time divided by mean Embree time.</text>',
    ]
    for tick in range(5):
        value = max_speedup * tick / 4
        x = chart_x + chart_w * tick / 4
        parts.append(f'<line x1="{x:.1f}" y1="{top-10}" x2="{x:.1f}" y2="{height-40}" stroke="#ddd" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{height-18}" text-anchor="middle" class="small">{value:.2f}x</text>')
    for idx, record in enumerate(items):
        y = top + idx * row_h
        label = f"{record['workload']} | {record['case_id']}"
        width_px = chart_w * record["speedup_vs_cpu"] / max_speedup
        color = "#2e7d32" if record["speedup_vs_cpu"] >= 1.0 else "#b71c1c"
        parts.append(f'<text x="40" y="{y+14}" text-anchor="start">{_svg_escape(label)}</text>')
        parts.append(f'<rect x="{chart_x}" y="{y}" width="{width_px:.1f}" height="12" fill="{color}"/>')
        parts.append(f'<text x="{chart_x + width_px + 8:.1f}" y="{y+11}" class="small">{record["speedup_vs_cpu"]:.2f}x</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def build_scaling_svg(payload: dict[str, object]) -> str:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in payload["records"]:
        grouped[record["workload"]].append(record)
    width = 1100
    height = 600
    margin_left = 90
    margin_right = 40
    margin_top = 70
    margin_bottom = 80
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    max_scale = max(record["scale_hint"] for record in payload["records"]) or 1
    max_mean = max(record["embree"]["mean_sec"] for record in payload["records"]) or 1.0
    colors = {
        "lsi": "#1565c0",
        "pip": "#6a1b9a",
        "overlay": "#ef6c00",
        "ray_tri_hitcount": "#2e7d32",
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<style>text{font-family:Helvetica,Arial,sans-serif;font-size:12px;} .title{font-size:20px;font-weight:bold;} .small{font-size:11px;fill:#555;} </style>',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="40" y="32" class="title">RTDL Embree Evaluation: Embree Scaling by Workload</text>',
        '<text x="40" y="52" class="small">Scale hints are workload-specific relative size markers for local Embree evaluation.</text>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#333" stroke-width="1"/>',
        f'<line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" stroke="#333" stroke-width="1"/>',
    ]
    for tick in range(5):
        x = margin_left + plot_w * tick / 4
        scale = max_scale * tick / 4
        parts.append(f'<line x1="{x:.1f}" y1="{margin_top+plot_h}" x2="{x:.1f}" y2="{margin_top+plot_h+6}" stroke="#333" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{height-40}" text-anchor="middle" class="small">{int(scale)}</text>')
    for tick in range(5):
        y = margin_top + plot_h - plot_h * tick / 4
        value = max_mean * tick / 4
        parts.append(f'<line x1="{margin_left-6}" y1="{y:.1f}" x2="{margin_left}" y2="{y:.1f}" stroke="#333" stroke-width="1"/>')
        parts.append(f'<text x="{margin_left-10}" y="{y+4:.1f}" text-anchor="end" class="small">{value:.4f}s</text>')
        parts.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{margin_left+plot_w}" y2="{y:.1f}" stroke="#eee" stroke-width="1"/>')
    legend_y = height - 18
    legend_x = margin_left
    for workload, records in grouped.items():
        records.sort(key=lambda item: item["scale_hint"])
        points = []
        for record in records:
            x = margin_left + plot_w * record["scale_hint"] / max_scale
            y = margin_top + plot_h - plot_h * record["embree"]["mean_sec"] / max_mean
            points.append((x, y, record))
        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in points)
        color = colors[workload]
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{polyline}"/>')
        for x, y, record in points:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
            parts.append(f'<text x="{x+5:.1f}" y="{y-6:.1f}" class="small">{_svg_escape(record["case_id"])}</text>')
        parts.append(f'<rect x="{legend_x}" y="{legend_y-10}" width="14" height="10" fill="{color}"/>')
        parts.append(f'<text x="{legend_x+20}" y="{legend_y-1}">{_svg_escape(workload)}</text>')
        legend_x += 170
    parts.append("</svg>")
    return "\n".join(parts)


def write_pdf_report(payload: dict[str, object], output_path: Path, figures: tuple[Path, Path, Path]) -> None:
    lines = [
        "RTDL Embree Evaluation Report",
        "",
        f"Generated: {payload['generated_at']}",
        f"Iterations: {payload['iterations']}",
        f"Warmup: {payload['warmup']}",
        f"Host: {payload['host']['platform']}",
        "",
        "This report summarizes the pre-GPU Embree evaluation for the current RTDL workload surface.",
        "It is an Embree CPU baseline report, not an NVIDIA/RT-core result.",
        "",
        "Evaluation Matrix",
        "",
    ]
    for record in payload["records"]:
        lines.append(
            f"- {record['case_id']}: workload={record['workload']}, category={record['category']}, "
            f"parity={record['parity']}, cpu={record['cpu']['mean_sec']:.6f}s, "
            f"embree={record['embree']['mean_sec']:.6f}s, speedup={record['speedup_vs_cpu']:.2f}x"
        )
    lines.extend(
        [
            "",
            "Key Findings",
            "",
            *[f"- {finding}" for finding in _key_findings(payload)],
            "",
            "Generated Figures",
            "",
        ]
    )
    for figure in figures:
        lines.append(f"- {figure}")
    lines.extend(
        [
            "",
            "Limitations",
            "",
            "- Precision remains float_approx.",
            "- Dataset breadth is based on local fixtures, deterministic tiling, and synthetic generators.",
            "- Final OptiX/RT-core evaluation remains future work.",
        ]
    )
    pdf_bytes = _simple_pdf_from_lines(lines)
    output_path.write_bytes(pdf_bytes)


def _key_findings(payload: dict[str, object]) -> list[str]:
    records = payload["records"]
    parity_failures = [record["case_id"] for record in records if not record["parity"]]
    fastest = min(records, key=lambda record: record["embree"]["mean_sec"])
    slowest = max(records, key=lambda record: record["embree"]["mean_sec"])
    best_speedup = max(records, key=lambda record: record["speedup_vs_cpu"])
    findings = [
        f"All evaluation cases passed CPU-vs-Embree parity checks." if not parity_failures else f"Parity failures: {', '.join(parity_failures)}.",
        f"Fastest Embree case: {fastest['case_id']} at {fastest['embree']['mean_sec']:.6f}s mean.",
        f"Slowest Embree case: {slowest['case_id']} at {slowest['embree']['mean_sec']:.6f}s mean.",
        f"Best Embree speedup vs CPU: {best_speedup['case_id']} at {best_speedup['speedup_vs_cpu']:.2f}x.",
    ]
    workload_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        workload_groups[record["workload"]].append(record)
    for workload, group in workload_groups.items():
        derived = [record for record in group if record["category"] in {"derived", "synthetic"}]
        if derived:
            slowest_local = max(derived, key=lambda record: record["embree"]["mean_sec"])
            findings.append(
                f"{workload} largest evaluated local case: {slowest_local['case_id']} ({slowest_local['embree']['mean_sec']:.6f}s Embree mean)."
            )
    return findings


def _simple_pdf_from_lines(lines: list[str]) -> bytes:
    page_width = 612
    page_height = 792
    left = 54
    top = 748
    line_height = 14
    usable_lines = 46

    wrapped_lines = []
    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue
        wrapped = textwrap.wrap(line, width=92, break_long_words=False, break_on_hyphens=False)
        wrapped_lines.extend(wrapped or [""])

    pages = []
    for index in range(0, len(wrapped_lines), usable_lines):
        pages.append(wrapped_lines[index:index + usable_lines])

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + idx * 2} 0 R" for idx in range(len(pages)))
    objects.append(f"<< /Type /Pages /Count {len(pages)} /Kids [{kids}] >>".encode("ascii"))
    font_object_number = 3 + len(pages) * 2

    for page_index, page_lines in enumerate(pages):
        page_obj = 3 + page_index * 2
        content_obj = page_obj + 1
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {font_object_number} 0 R >> >> /Contents {content_obj} 0 R >>".encode("ascii")
        )
        stream_lines = [
            "BT",
            "/F1 11 Tf",
            f"{left} {top} Td",
            f"{line_height} TL",
        ]
        for line in page_lines:
            escaped = _pdf_escape(line)
            stream_lines.append(f"({escaped}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines).encode("latin-1")
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream")

    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


def _svg_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RTDL Embree evaluation and generate report artifacts.")
    parser.add_argument("--workload", action="append", choices=("lsi", "pip", "overlay", "ray_tri_hitcount"))
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--output-dir", default=str(ROOT / "build" / "embree_evaluation"))
    args = parser.parse_args(argv)

    artifacts = generate_evaluation_artifacts(
        workloads=tuple(args.workload) if args.workload else None,
        iterations=args.iterations,
        warmup=args.warmup,
        output_dir=args.output_dir,
    )
    for name, path in artifacts.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
