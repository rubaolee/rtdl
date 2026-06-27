from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .reference import Point
from .reference import Polygon
from .reference import Segment
from .runtime import run_cpu
from .embree_runtime import run_embree

ROOT = Path(__file__).resolve().parents[2]


FIXED_BUILD_POLYGONS = 800
PROBE_POLYGON_SERIES = (160, 320, 480, 640, 800)
SCALABILITY_DISTRIBUTIONS = ("uniform", "gaussian")


@dataclass(frozen=True)
class ScalabilityConfig:
    build_polygons: int = FIXED_BUILD_POLYGONS
    probe_series: tuple[int, ...] = PROBE_POLYGON_SERIES
    iterations: int = 3
    warmup: int = 1
    base_seed: int = 17


def generate_section_5_6_artifacts(
    *,
    output_dir: str | Path | None = None,
    config: ScalabilityConfig | None = None,
    publish_docs: bool = True,
) -> dict[str, Path]:
    cfg = config or ScalabilityConfig()
    output_root = Path(output_dir or ROOT / "build" / "section_5_6_scalability")
    output_root.mkdir(parents=True, exist_ok=True)
    figures_dir = output_root / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    payload = run_section_5_6(cfg)

    json_path = output_root / "section_5_6_scalability.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    figure13_svg = figures_dir / "figure13_lsi_scalability.svg"
    figure14_svg = figures_dir / "figure14_pip_scalability.svg"
    figure13_svg.write_text(build_scalability_figure_svg(payload, workload="lsi", title="Figure 13 Analogue: LSI Scalability"), encoding="utf-8")
    figure14_svg.write_text(build_scalability_figure_svg(payload, workload="pip", title="Figure 14 Analogue: PIP Scalability"), encoding="utf-8")

    markdown_path = output_root / "section_5_6_scalability_report.md"
    markdown_path.write_text(generate_markdown_report(payload, figure13_svg, figure14_svg), encoding="utf-8")

    pdf_path = output_root / "section_5_6_scalability_report.pdf"
    pdf_path.write_bytes(_simple_pdf_from_lines(generate_pdf_lines(payload, figure13_svg, figure14_svg)))

    artifacts = {
        "json": json_path,
        "figure13_svg": figure13_svg,
        "figure14_svg": figure14_svg,
        "markdown": markdown_path,
        "pdf": pdf_path,
    }
    if publish_docs:
        published_md = ROOT / "docs" / "reports" / "section_5_6_scalability_report_2026-03-31.md"
        published_pdf = ROOT / "docs" / "reports" / "section_5_6_scalability_report_2026-03-31.pdf"
        published_md.write_text(markdown_path.read_text(encoding="utf-8"), encoding="utf-8")
        published_pdf.write_bytes(pdf_path.read_bytes())
        artifacts["published_markdown"] = published_md
        artifacts["published_pdf"] = published_pdf
    return artifacts


def run_section_5_6(config: ScalabilityConfig) -> dict[str, object]:
    from examples.rtdl_language_reference import county_zip_join_reference
    from examples.rtdl_language_reference import point_in_counties_reference

    lsi_kernel = county_zip_join_reference
    pip_kernel = point_in_counties_reference

    records: list[dict[str, object]] = []
    parity_checks: list[dict[str, object]] = []

    for distribution in SCALABILITY_DISTRIBUTIONS:
        build_polygons = generate_synthetic_polygons(
            count=config.build_polygons,
            distribution=distribution,
            seed=config.base_seed + _distribution_seed_offset(distribution),
        )
        build_segments = polygons_to_segments(build_polygons)

        for probe_polygons_count in config.probe_series:
            probe_polygons = generate_synthetic_polygons(
                count=probe_polygons_count,
                distribution=distribution,
                seed=config.base_seed + 100 + probe_polygons_count + _distribution_seed_offset(distribution),
            )

            probe_segments = polygons_to_segments(probe_polygons)
            probe_points = polygon_probe_points(probe_polygons)

            lsi_rows, lsi_timings = _benchmark_kernel(
                lsi_kernel,
                inputs={"left": probe_segments, "right": build_segments},
                iterations=config.iterations,
                warmup=config.warmup,
            )
            pip_rows, pip_timings = _benchmark_kernel(
                pip_kernel,
                inputs={"points": probe_points, "polygons": build_polygons},
                iterations=config.iterations,
                warmup=config.warmup,
            )

            lsi_intersections = len(lsi_rows)
            pip_probe_points = len(probe_points)

            records.append(
                {
                    "workload": "lsi",
                    "distribution": distribution,
                    "build_polygons": config.build_polygons,
                    "probe_polygons": probe_polygons_count,
                    "query_time_ms": _mean_ms(lsi_timings),
                    "throughput": (
                        lsi_intersections / statistics.mean(lsi_timings)
                        if statistics.mean(lsi_timings) > 0
                        else 0.0
                    ),
                    "throughput_unit": "intersections/s",
                    "result_count": lsi_intersections,
                }
            )
            records.append(
                {
                    "workload": "pip",
                    "distribution": distribution,
                    "build_polygons": config.build_polygons,
                    "probe_polygons": probe_polygons_count,
                    "query_time_ms": _mean_ms(pip_timings),
                    "throughput": (
                        pip_probe_points / statistics.mean(pip_timings)
                        if statistics.mean(pip_timings) > 0
                        else 0.0
                    ),
                    "throughput_unit": "probe-points/s",
                    "result_count": len(pip_rows),
                }
            )

        # Reduced-size correctness checks against CPU on one representative size per distribution.
        parity_probe_polygons = generate_synthetic_polygons(
            count=120,
            distribution=distribution,
            seed=config.base_seed + 999 + _distribution_seed_offset(distribution),
        )
        parity_build_polygons = generate_synthetic_polygons(
            count=160,
            distribution=distribution,
            seed=config.base_seed + 1999 + _distribution_seed_offset(distribution),
        )
        parity_lsi_cpu = run_cpu(
            lsi_kernel,
            left=polygons_to_segments(parity_probe_polygons),
            right=polygons_to_segments(parity_build_polygons),
        )
        parity_lsi_embree = run_embree(
            lsi_kernel,
            left=polygons_to_segments(parity_probe_polygons),
            right=polygons_to_segments(parity_build_polygons),
        )
        parity_pip_cpu = run_cpu(
            pip_kernel,
            points=polygon_probe_points(parity_probe_polygons),
            polygons=parity_build_polygons,
        )
        parity_pip_embree = run_embree(
            pip_kernel,
            points=polygon_probe_points(parity_probe_polygons),
            polygons=parity_build_polygons,
        )
        parity_checks.append(
            {
                "distribution": distribution,
                "lsi_parity": parity_lsi_cpu == parity_lsi_embree,
                "pip_parity": parity_pip_cpu == parity_pip_embree,
                "lsi_probe_polygons": 120,
                "lsi_build_polygons": 160,
                "pip_probe_polygons": 120,
                "pip_build_polygons": 160,
            }
        )

    return {
        "suite": "rtdl_section_5_6_scalability",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "method": "Embree-phase scaled analogue of RayJoin Section 5.6",
        "config": {
            "build_polygons": config.build_polygons,
            "probe_series": list(config.probe_series),
            "iterations": config.iterations,
            "warmup": config.warmup,
            "distributions": list(SCALABILITY_DISTRIBUTIONS),
        },
        "records": records,
        "parity_checks": parity_checks,
    }


def generate_synthetic_polygons(*, count: int, distribution: str, seed: int) -> tuple[Polygon, ...]:
    rng = random.Random(seed)
    polygons: list[Polygon] = []
    for polygon_id in range(count):
        cx, cy = _sample_center(rng, distribution)
        width = rng.uniform(0.8, 2.4)
        height = rng.uniform(0.8, 2.4)
        angle = rng.uniform(0.0, math.tau)
        half_w = width * 0.5
        half_h = height * 0.5
        local = (
            (-half_w, -half_h),
            (half_w, -half_h),
            (half_w, half_h),
            (-half_w, half_h),
        )
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        vertices = []
        for dx, dy in local:
            x = cx + dx * cos_a - dy * sin_a
            y = cy + dx * sin_a + dy * cos_a
            vertices.append((x, y))
        polygons.append(Polygon(id=polygon_id + 1, vertices=tuple(vertices)))
    return tuple(polygons)


def polygons_to_segments(polygons: tuple[Polygon, ...]) -> tuple[Segment, ...]:
    segments: list[Segment] = []
    next_id = 1
    for polygon in polygons:
        wrapped = polygon.vertices + (polygon.vertices[0],)
        for start, end in zip(wrapped, wrapped[1:]):
            segments.append(
                Segment(
                    id=next_id,
                    x0=start[0],
                    y0=start[1],
                    x1=end[0],
                    y1=end[1],
                )
            )
            next_id += 1
    return tuple(segments)


def polygon_probe_points(polygons: tuple[Polygon, ...]) -> tuple[Point, ...]:
    points: list[Point] = []
    for polygon in polygons:
        xs = [vertex[0] for vertex in polygon.vertices]
        ys = [vertex[1] for vertex in polygon.vertices]
        points.append(
            Point(
                id=polygon.id,
                x=sum(xs) / len(xs),
                y=sum(ys) / len(ys),
            )
        )
    return tuple(points)


def build_scalability_figure_svg(payload: dict[str, object], *, workload: str, title: str) -> str:
    records = [record for record in payload["records"] if record["workload"] == workload]
    width = 1200
    height = 820
    margin = 70
    panel_w = 480
    panel_h = 260
    gap_x = 80
    gap_y = 90
    series = {
        distribution: sorted(
            [record for record in records if record["distribution"] == distribution],
            key=lambda item: item["probe_polygons"],
        )
        for distribution in SCALABILITY_DISTRIBUTIONS
    }
    max_time = max(record["query_time_ms"] for record in records) or 1.0
    max_throughput = max(record["throughput"] for record in records) or 1.0
    x_max = max(record["probe_polygons"] for record in records) or 1

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<style>text{font-family:Helvetica,Arial,sans-serif;font-size:12px;} .title{font-size:22px;font-weight:bold;} .subtitle{font-size:12px;fill:#555;} .axis{stroke:#333;stroke-width:1;} .grid{stroke:#ddd;stroke-width:1;} .small{font-size:11px;fill:#444;}</style>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="40" y="34" class="title">{_svg_escape(title)}</text>',
        f'<text x="40" y="54" class="subtitle">Scaled Embree analogue with fixed build side R={payload["config"]["build_polygons"]} polygons and varying probe side S.</text>',
    ]

    panel_specs = [
        ("uniform", "query_time_ms", "(a) Uniform - Query Time", "Query Time (ms)", max_time, "#1565c0"),
        ("gaussian", "query_time_ms", "(b) Gaussian - Query Time", "Query Time (ms)", max_time, "#6a1b9a"),
        ("uniform", "throughput", "(c) Uniform - Throughput", _throughput_label(workload), max_throughput, "#2e7d32"),
        ("gaussian", "throughput", "(d) Gaussian - Throughput", _throughput_label(workload), max_throughput, "#ef6c00"),
    ]

    for index, (distribution, field, panel_title, y_label, y_max, color) in enumerate(panel_specs):
        row = index // 2
        col = index % 2
        x0 = margin + col * (panel_w + gap_x)
        y0 = 90 + row * (panel_h + gap_y)
        points = series[distribution]
        _append_panel(parts, points, x0=x0, y0=y0, width=panel_w, height=panel_h, x_max=x_max, y_max=y_max, field=field, title=panel_title, y_label=y_label, color=color)

    parts.append("</svg>")
    return "\n".join(parts)


def generate_markdown_report(payload: dict[str, object], figure13_svg: Path, figure14_svg: Path) -> str:
    lines = [
        "# RTDL Section 5.6 Scalability Analogue Report",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Method: `{payload['method']}`",
        f"- Fixed build-side polygons: `{payload['config']['build_polygons']}`",
        f"- Probe-side series: `{', '.join(str(item) for item in payload['config']['probe_series'])}`",
        f"- Iterations: `{payload['config']['iterations']}`",
        f"- Warmup: `{payload['config']['warmup']}`",
        "",
        "## Support Decision",
        "",
        "The repository did not previously support Section 5.6 as an executable experiment.",
        "It had the workload surface and planning notes, but it lacked:",
        "",
        "- deterministic uniform / gaussian scalability generators,",
        "- a fixed-R / varying-S experiment runner for `lsi` and `pip`,",
        "- Figure 13 / Figure 14 analogue generation, and",
        "- a dedicated report path for the Section 5.6 structure.",
        "",
        "This report is therefore a **revised Embree-phase scaled analogue**, not a claim of the original 5M / 1M..5M GPU experiment.",
        "",
        "## Correctness Gate",
        "",
    ]
    for check in payload["parity_checks"]:
        lines.append(
            f"- `{check['distribution']}` parity sample: `lsi={check['lsi_parity']}`, `pip={check['pip_parity']}` "
            f"on reduced CPU-vs-Embree checks."
        )
    lines.extend(
        [
            "",
            "## Results",
            "",
            "| Workload | Distribution | Probe Polygons | Query Time (ms) | Throughput | Output Rows |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for record in payload["records"]:
        lines.append(
            f"| `{record['workload']}` | `{record['distribution']}` | {record['probe_polygons']} | "
            f"{record['query_time_ms']:.3f} | {record['throughput']:.2f} `{record['throughput_unit']}` | "
            f"{record['result_count']} |"
        )
    lines.extend(
        [
            "",
            "## Generated Figures",
            "",
            f"- `{figure13_svg}`",
            f"- `{figure14_svg}`",
            "",
            "## Interpretation",
            "",
            "- Figure 13 analogue corresponds to `lsi` only.",
            "- Figure 14 analogue corresponds to `pip` only.",
            "- Query-time curves and throughput curves follow the structure of RayJoin Section 5.6.",
            "- For `pip`, throughput is computed from probe-point count per second; the `Output Rows` column is the emitted RTDL row count and therefore reflects the current point/polygon row schema rather than raw point count.",
            "- Scale and hardware are intentionally different from the original paper.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def generate_pdf_lines(payload: dict[str, object], figure13_svg: Path, figure14_svg: Path) -> list[str]:
    lines = [
        "RTDL Section 5.6 Scalability Analogue Report",
        "",
        f"Generated: {payload['generated_at']}",
        f"Method: {payload['method']}",
        f"Fixed build-side polygons: {payload['config']['build_polygons']}",
        f"Probe-side series: {', '.join(str(item) for item in payload['config']['probe_series'])}",
        "",
        "Support decision:",
        "The previous RTDL baseline did not execute Section 5.6 directly. This revision adds a scaled Embree-phase analogue for LSI and PIP.",
        "",
        "Correctness gate:",
    ]
    for check in payload["parity_checks"]:
        lines.append(
            f"- {check['distribution']}: lsi parity={check['lsi_parity']}, pip parity={check['pip_parity']} on reduced CPU-vs-Embree samples."
        )
    lines.extend(
        [
            "",
            "Results snapshot:",
        ]
    )
    for record in payload["records"]:
        lines.append(
            f"- {record['workload']} | {record['distribution']} | probe={record['probe_polygons']} | "
            f"time={record['query_time_ms']:.3f} ms | throughput={record['throughput']:.2f} {record['throughput_unit']} | "
            f"results={record['result_count']}"
        )
    lines.extend(
        [
            "",
            f"Figure 13 analogue SVG: {figure13_svg}",
            f"Figure 14 analogue SVG: {figure14_svg}",
            "",
            "Limitations:",
            "- This is a scaled Embree analogue, not the original 5M / 1M..5M RT-core benchmark.",
            "- Overlay is not part of Section 5.6 and is not included here.",
            "- The final NVIDIA phase is still needed for paper-style RT-core reproduction.",
        ]
    )
    return lines


def _benchmark_kernel(kernel, *, inputs: dict[str, object], iterations: int, warmup: int) -> tuple[tuple[dict[str, object], ...], list[float]]:
    result_rows = ()
    timings: list[float] = []
    for _ in range(warmup):
        run_embree(kernel, **inputs)
    for _ in range(iterations):
        start = time.perf_counter()
        result_rows = run_embree(kernel, **inputs)
        timings.append(time.perf_counter() - start)
    return result_rows, timings


def _sample_center(rng: random.Random, distribution: str) -> tuple[float, float]:
    if distribution == "uniform":
        return rng.uniform(-1000.0, 1000.0), rng.uniform(-1000.0, 1000.0)
    if distribution == "gaussian":
        return rng.gauss(0.0, 250.0), rng.gauss(0.0, 250.0)
    raise ValueError(f"unsupported distribution `{distribution}`")


def _distribution_seed_offset(distribution: str) -> int:
    return 0 if distribution == "uniform" else 10000


def _mean_ms(timings_sec: list[float]) -> float:
    return statistics.mean(timings_sec) * 1000.0 if timings_sec else 0.0


def _throughput_label(workload: str) -> str:
    if workload == "lsi":
        return "Intersections/s"
    return "Probe Points/s"


def _append_panel(
    parts: list[str],
    points: list[dict[str, object]],
    *,
    x0: int,
    y0: int,
    width: int,
    height: int,
    x_max: int,
    y_max: float,
    field: str,
    title: str,
    y_label: str,
    color: str,
) -> None:
    parts.append(f'<rect x="{x0}" y="{y0}" width="{width}" height="{height}" fill="none" stroke="#bbb"/>')
    parts.append(f'<text x="{x0+8}" y="{y0+20}">{_svg_escape(title)}</text>')
    plot_left = x0 + 56
    plot_top = y0 + 30
    plot_width = width - 80
    plot_height = height - 70
    parts.append(f'<line class="axis" x1="{plot_left}" y1="{plot_top+plot_height}" x2="{plot_left+plot_width}" y2="{plot_top+plot_height}"/>')
    parts.append(f'<line class="axis" x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_top+plot_height}"/>')
    parts.append(f'<text x="{plot_left + plot_width / 2:.1f}" y="{y0+height-12}" text-anchor="middle" class="small">Probe-side polygons (S)</text>')
    parts.append(f'<text x="{x0+12}" y="{plot_top + plot_height / 2:.1f}" transform="rotate(-90 {x0+12},{plot_top + plot_height / 2:.1f})" text-anchor="middle" class="small">{_svg_escape(y_label)}</text>')
    for tick in range(5):
        x_value = x_max * (tick + 1) / 5
        x = plot_left + plot_width * x_value / x_max
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{plot_top}" x2="{x:.1f}" y2="{plot_top+plot_height}"/>')
        parts.append(f'<text x="{x:.1f}" y="{plot_top+plot_height+18}" text-anchor="middle" class="small">{int(x_value)}</text>')
    for tick in range(5):
        y_value = y_max * tick / 4
        y = plot_top + plot_height - plot_height * tick / 4
        parts.append(f'<line class="grid" x1="{plot_left}" y1="{y:.1f}" x2="{plot_left+plot_width}" y2="{y:.1f}"/>')
        label = f"{y_value:.1f}" if y_max < 1000 else f"{int(y_value)}"
        parts.append(f'<text x="{plot_left-8}" y="{y+4:.1f}" text-anchor="end" class="small">{label}</text>')
    polyline = []
    for point in points:
        x = plot_left + plot_width * point["probe_polygons"] / x_max
        y = plot_top + plot_height - plot_height * float(point[field]) / y_max
        polyline.append(f"{x:.1f},{y:.1f}")
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
    parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(polyline)}"/>')


def _svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _simple_pdf_from_lines(lines: list[str]) -> bytes:
    page_width = 612
    page_height = 792
    left = 54
    top = 748
    line_height = 14
    usable_lines = 46

    wrapped_lines: list[str] = []
    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(
            textwrap.wrap(line, width=92, break_long_words=False, break_on_hyphens=False) or [""]
        )

    pages = [wrapped_lines[index:index + usable_lines] for index in range(0, len(wrapped_lines), usable_lines)]

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
            stream_lines.append(f"({_pdf_escape(line)}) Tj")
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


def _pdf_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RTDL Embree analogue of RayJoin Section 5.6 scalability tests.")
    parser.add_argument("--output-dir", default=str(ROOT / "build" / "section_5_6_scalability"))
    parser.add_argument("--build-polygons", type=int, default=FIXED_BUILD_POLYGONS)
    parser.add_argument("--probe-series", default="500,1000,1500,2000,2500")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args(argv)

    cfg = ScalabilityConfig(
        build_polygons=args.build_polygons,
        probe_series=tuple(int(item) for item in args.probe_series.split(",") if item),
        iterations=args.iterations,
        warmup=args.warmup,
    )
    artifacts = generate_section_5_6_artifacts(output_dir=args.output_dir, config=cfg, publish_docs=True)
    print(artifacts["markdown"])
    print(artifacts["pdf"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
