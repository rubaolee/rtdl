#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import struct
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "docs" / "reports"
BUILD_DIR = ROOT / "build" / "paper_report_assets"
EMBREE_EVAL_JSON = ROOT / "build" / "embree_evaluation" / "embree_evaluation.json"
SECTION56_JSON = ROOT / "build" / "section_5_6_scalability" / "section_5_6_scalability.json"
EMBREE_FIGURES = ROOT / "build" / "embree_evaluation" / "figures"
SECTION56_FIGURES = ROOT / "build" / "section_5_6_scalability" / "figures"
RAYJOIN_DRAW_DIR = Path("/tmp/RayJoin_goal13/expr/draw")
OUT_MD = REPORTS_DIR / "rtdl_embree_paper_report_2026-03-31.md"
OUT_PDF = REPORTS_DIR / "rtdl_embree_paper_report_2026-03-31.pdf"


def esc(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def wrap_lines(text: str, width: int) -> list[str]:
    return textwrap.wrap(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]


def stream_obj(data: bytes) -> bytes:
    return b"<< /Length " + str(len(data)).encode() + b" >>\nstream\n" + data + b"\nendstream"


def image_obj_jpeg(data: bytes, width: int, height: int, colorspace: str, bits: int) -> bytes:
    header = (
        f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
        f"/ColorSpace /{colorspace} /BitsPerComponent {bits} "
        f"/Filter /DCTDecode /Length {len(data)} >>\n"
    )
    return header.encode() + b"stream\n" + data + b"\nendstream"


def page_obj(width: int, height: int, content_id: int, images: list[tuple[str, int]]) -> bytes:
    xobjects = ""
    if images:
        refs = " ".join(f"/{name} {obj_id} 0 R" for name, obj_id in images)
        xobjects = f"/XObject << {refs} >> "
    return (
        f"<< /Type /Page /Parent __PAGES__ /MediaBox [0 0 {width} {height}] "
        f"/Resources << /Font << /F1 __FONT__ >> {xobjects}>> "
        f"/Contents {content_id} 0 R >>"
    ).encode()


def jpeg_size(path: Path) -> tuple[int, int, str, int]:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        raise ValueError(f"not a JPEG: {path}")
    i = 2
    while i < len(data):
        while i < len(data) and data[i] == 0xFF:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if i + 2 > len(data):
            break
        seglen = struct.unpack(">H", data[i : i + 2])[0]
        if marker in {
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC5,
            0xC6,
            0xC7,
            0xC9,
            0xCA,
            0xCB,
            0xCD,
            0xCE,
            0xCF,
        }:
            precision = data[i + 2]
            height = struct.unpack(">H", data[i + 3 : i + 5])[0]
            width = struct.unpack(">H", data[i + 5 : i + 7])[0]
            comps = data[i + 7]
            color = "DeviceRGB" if comps >= 3 else "DeviceGray"
            return width, height, color, precision
        i += seglen
    raise ValueError(f"could not parse JPEG size: {path}")


class PDFBuilder:
    def __init__(self) -> None:
        self.objects: list[bytes] = []
        self.pages: list[int] = []

    def add_obj(self, data: bytes) -> int:
        self.objects.append(data)
        return len(self.objects)

    def add_text_page(self, title: str, sections: list[tuple[str, list[str]]], footer: str | None = None) -> None:
        width, height = 612, 792
        y = 742
        lines = [f"BT /F1 22 Tf 72 {y:.1f} Td ({esc(title)}) Tj ET"]
        y -= 30
        for heading, bullets in sections:
            lines.append(f"BT /F1 13 Tf 72 {y:.1f} Td ({esc(heading)}) Tj ET")
            y -= 18
            for bullet in bullets:
                prefix = "• "
                first = True
                for wrapped in wrap_lines(bullet, 90):
                    lines.append(
                        f"BT /F1 10.5 Tf 84 {y:.1f} Td ({esc((prefix if first else '  ') + wrapped)}) Tj ET"
                    )
                    y -= 14
                    first = False
                y -= 2
            y -= 6
        if footer:
            lines.append(f"BT /F1 9 Tf 72 36 Td ({esc(footer)}) Tj ET")
        content_id = self.add_obj(stream_obj("\n".join(lines).encode("latin-1", "replace")))
        page_id = self.add_obj(page_obj(width, height, content_id, []))
        self.pages.append(page_id)

    def add_image_page(self, title: str, image_path: Path, caption_lines: list[str]) -> None:
        width, height = 612, 792
        img_data = image_path.read_bytes()
        img_w, img_h, colorspace, bits = jpeg_size(image_path)
        image_id = self.add_obj(image_obj_jpeg(img_data, img_w, img_h, colorspace, bits))
        available_w = 468
        available_h = 560
        scale = min(available_w / img_w, available_h / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale
        x = (width - draw_w) / 2
        y = 150 + (available_h - draw_h) / 2
        lines = [f"BT /F1 20 Tf 72 744 Td ({esc(title)}) Tj ET"]
        caption_y = 110
        for line in caption_lines:
            for wrapped in wrap_lines(line, 94):
                lines.append(f"BT /F1 10 Tf 72 {caption_y:.1f} Td ({esc(wrapped)}) Tj ET")
                caption_y -= 13
        lines.append(f"q {draw_w:.3f} 0 0 {draw_h:.3f} {x:.3f} {y:.3f} cm /Im1 Do Q")
        content_id = self.add_obj(stream_obj("\n".join(lines).encode("latin-1", "replace")))
        page_id = self.add_obj(page_obj(width, height, content_id, [("Im1", image_id)]))
        self.pages.append(page_id)

    def add_two_image_page(
        self,
        title: str,
        left_label: str,
        left_image: Path,
        right_label: str,
        right_image: Path,
        caption_lines: list[str],
    ) -> None:
        width, height = 612, 792
        left_data = left_image.read_bytes()
        right_data = right_image.read_bytes()
        left_w, left_h, left_cs, left_bits = jpeg_size(left_image)
        right_w, right_h, right_cs, right_bits = jpeg_size(right_image)
        left_id = self.add_obj(image_obj_jpeg(left_data, left_w, left_h, left_cs, left_bits))
        right_id = self.add_obj(image_obj_jpeg(right_data, right_w, right_h, right_cs, right_bits))

        max_w = 216
        max_h = 430
        left_scale = min(max_w / left_w, max_h / left_h)
        right_scale = min(max_w / right_w, max_h / right_h)
        left_draw_w, left_draw_h = left_w * left_scale, left_h * left_scale
        right_draw_w, right_draw_h = right_w * right_scale, right_h * right_scale
        left_x = 52 + (max_w - left_draw_w) / 2
        right_x = 344 + (max_w - right_draw_w) / 2
        img_y = 216 + (max_h - max(left_draw_h, right_draw_h)) / 2

        lines = [f"BT /F1 20 Tf 72 744 Td ({esc(title)}) Tj ET"]
        lines.append(f"BT /F1 11 Tf 100 705 Td ({esc(left_label)}) Tj ET")
        lines.append(f"BT /F1 11 Tf 392 705 Td ({esc(right_label)}) Tj ET")
        caption_y = 124
        for line in caption_lines:
            for wrapped in wrap_lines(line, 94):
                lines.append(f"BT /F1 10 Tf 72 {caption_y:.1f} Td ({esc(wrapped)}) Tj ET")
                caption_y -= 13
        lines.append(f"q {left_draw_w:.3f} 0 0 {left_draw_h:.3f} {left_x:.3f} {img_y:.3f} cm /Im1 Do Q")
        lines.append(f"q {right_draw_w:.3f} 0 0 {right_draw_h:.3f} {right_x:.3f} {img_y:.3f} cm /Im2 Do Q")
        content_id = self.add_obj(stream_obj("\n".join(lines).encode("latin-1", "replace")))
        page_id = self.add_obj(page_obj(width, height, content_id, [("Im1", left_id), ("Im2", right_id)]))
        self.pages.append(page_id)

    def write(self, path: Path) -> None:
        font_id = self.add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        kids = " ".join(f"{page_id} 0 R" for page_id in self.pages)
        pages_id = self.add_obj(f"<< /Type /Pages /Kids [ {kids} ] /Count {len(self.pages)} >>".encode())
        catalog_id = self.add_obj(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())
        final_objects: list[bytes] = []
        for obj in self.objects:
            obj = obj.replace(b"__PAGES__", f"{pages_id} 0 R".encode())
            obj = obj.replace(b"__FONT__", f"{font_id} 0 R".encode())
            final_objects.append(obj)

        offsets: list[int] = []
        blob = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        for index, obj in enumerate(final_objects, start=1):
            offsets.append(len(blob))
            blob.extend(f"{index} 0 obj\n".encode())
            blob.extend(obj)
            blob.extend(b"\nendobj\n")
        xref_offset = len(blob)
        blob.extend(f"xref\n0 {len(final_objects) + 1}\n".encode())
        blob.extend(b"0000000000 65535 f \n")
        for offset in offsets:
            blob.extend(f"{offset:010d} 00000 n \n".encode())
        blob.extend(
            f"trailer\n<< /Size {len(final_objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n".encode()
        )
        path.write_bytes(blob)


def run_command(*args: str) -> None:
    subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def ensure_jpeg(asset: Path) -> Path:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    png_path = BUILD_DIR / f"{asset.name}.png"
    jpg_path = BUILD_DIR / f"{asset.name}.jpg"
    if not png_path.exists():
        run_command("qlmanage", "-t", "-s", "1600", "-o", str(BUILD_DIR), str(asset))
    if not jpg_path.exists():
        run_command("sips", "-s", "format", "jpeg", str(png_path), "--out", str(jpg_path))
    return jpg_path


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def embree_stats(payload: dict[str, object]) -> dict[str, object]:
    records = payload["records"]
    best_speedup = max(records, key=lambda r: r["speedup_vs_cpu"])
    slowest_embree = max(records, key=lambda r: r["embree"]["mean_sec"])
    by_workload: dict[str, list[dict[str, object]]] = {}
    for record in records:
        by_workload.setdefault(record["workload"], []).append(record)
    largest_cases = {}
    for workload, items in by_workload.items():
        largest_cases[workload] = max(items, key=lambda r: sum(r["input_sizes"].values()))
    return {
        "case_count": len(records),
        "all_parity": all(record["parity"] for record in records),
        "best_speedup": best_speedup,
        "slowest_embree": slowest_embree,
        "largest_cases": largest_cases,
    }


def section56_stats(payload: dict[str, object]) -> dict[str, object]:
    records = payload["records"]
    checks = payload["parity_checks"]
    by_key = {(r["workload"], r["distribution"]): [] for r in records}
    for record in records:
        by_key[(record["workload"], record["distribution"])].append(record)
    for items in by_key.values():
        items.sort(key=lambda r: r["probe_polygons"])
    return {
        "all_parity": all(item["lsi_parity"] and item["pip_parity"] for item in checks),
        "lsi_uniform": by_key[("lsi", "uniform")],
        "lsi_gaussian": by_key[("lsi", "gaussian")],
        "pip_uniform": by_key[("pip", "uniform")],
        "pip_gaussian": by_key[("pip", "gaussian")],
    }


def generate_markdown(embree_payload: dict[str, object], section_payload: dict[str, object]) -> str:
    embree = embree_stats(embree_payload)
    sec56 = section56_stats(section_payload)
    best = embree["best_speedup"]
    slowest = embree["slowest_embree"]
    lines = [
        "# RTDL Embree Paper-Style Report",
        "",
        "## Abstract",
        "",
        "This report consolidates the current RTDL Embree-phase evidence into a single paper-style summary. RTDL is a Python-hosted DSL and compiler/runtime stack for non-graphics ray tracing workloads, with RayJoin as the primary target problem. The current audited baseline runs six workload families on a native Embree backend and uses a Python CPU implementation as the semantic reference.",
        "",
        "The report combines three layers of evidence: the frozen Embree baseline evaluation matrix, the current RayJoin paper-reproduction plan and dataset provenance mapping, and the implemented Section 5.6 scalability analogue for `lsi` and `pip`. The resulting artifact is intentionally honest about its scope: it is an Embree-phase reproduction effort, not the final NVIDIA/OptiX v0.1 result.",
        "",
        "## System and Experiment Scope",
        "",
        "- Runtime backends used here: `run_cpu(...)` for semantic reference and `run_embree(...)` for native execution.",
        "- Current audited workloads: `lsi`, `pip`, `overlay`, `ray_tri_hitcount`, `segment_polygon_hitcount`, `point_nearest_segment`.",
        "- Paper-focused reproduction status: Figure 13 and Figure 14 now have implemented scaled analogues; Table 3, Table 4, and Figure 15 remain planned.",
        "- Precision model: `float_approx` only; no robust or exact arithmetic claim is made in this report.",
        "",
        "## Embree Baseline Evaluation",
        "",
        f"- Total benchmark cases: `{embree['case_count']}`.",
        f"- CPU-vs-Embree parity: `{embree['all_parity']}` across the frozen evaluation matrix.",
        f"- Best observed Embree speedup vs CPU: `{best['case_id']}` at `{best['speedup_vs_cpu']:.2f}x`.",
        f"- Slowest Embree case by mean latency: `{slowest['case_id']}` at `{slowest['embree']['mean_sec']:.6f}s`.",
        "",
        "| Workload | Largest Current Case | Embree Mean (s) |",
        "| --- | --- | ---: |",
    ]
    largest_cases = embree["largest_cases"]
    for workload in ("lsi", "pip", "overlay", "ray_tri_hitcount", "segment_polygon_hitcount", "point_nearest_segment"):
        record = largest_cases[workload]
        lines.append(f"| `{workload}` | `{record['case_id']}` | {record['embree']['mean_sec']:.6f} |")
    lines.extend(
        [
            "",
            "## Section 5.6 Support Decision",
            "",
            "The repository did not originally support RayJoin Section 5.6 as an executable experiment. That gap is now closed for an Embree-phase scaled analogue. RTDL implements deterministic synthetic generators, fixed-build-size and varying-probe-size benchmark runners, Figure 13 / Figure 14 analogue generation, and a dedicated reproducible report path.",
            "",
            "This remains a scaled analogue rather than a paper-identical result because the current Embree phase uses:",
            "",
            "- fixed build-side polygons `R = 800`,",
            "- probe-side series `S = 160, 320, 480, 640, 800`,",
            "- distributions `uniform` and `gaussian`,",
            "- local Embree execution instead of NVIDIA RT cores.",
            "",
            f"Correctness gate for the analogue: `{sec56['all_parity']}` on reduced CPU-vs-Embree parity samples.",
            "",
            "## Section 5.6 Quantitative Highlights",
            "",
            "| Series | First Point | Final Point |",
            "| --- | --- | --- |",
        ]
    )
    lines.append(
        f"| `Figure 13 Uniform LSI Throughput` | `{sec56['lsi_uniform'][0]['probe_polygons']} -> {sec56['lsi_uniform'][0]['throughput']:.2f} intersections/s` | `{sec56['lsi_uniform'][-1]['probe_polygons']} -> {sec56['lsi_uniform'][-1]['throughput']:.2f} intersections/s` |"
    )
    lines.append(
        f"| `Figure 13 Gaussian LSI Throughput` | `{sec56['lsi_gaussian'][0]['probe_polygons']} -> {sec56['lsi_gaussian'][0]['throughput']:.2f} intersections/s` | `{sec56['lsi_gaussian'][-1]['probe_polygons']} -> {sec56['lsi_gaussian'][-1]['throughput']:.2f} intersections/s` |"
    )
    lines.append(
        f"| `Figure 14 Uniform PIP Throughput` | `{sec56['pip_uniform'][0]['probe_polygons']} -> {sec56['pip_uniform'][0]['throughput']:.2f} probe-points/s` | `{sec56['pip_uniform'][-1]['probe_polygons']} -> {sec56['pip_uniform'][-1]['throughput']:.2f} probe-points/s` |"
    )
    lines.append(
        f"| `Figure 14 Gaussian PIP Throughput` | `{sec56['pip_gaussian'][0]['probe_polygons']} -> {sec56['pip_gaussian'][0]['throughput']:.2f} probe-points/s` | `{sec56['pip_gaussian'][-1]['probe_polygons']} -> {sec56['pip_gaussian'][-1]['throughput']:.2f} probe-points/s` |"
    )
    lines.extend(
        [
            "",
            "## Figure Coverage",
            "",
            "- Corresponding RayJoin paper figures are included for Figure 13, Figure 14, and Figure 15 when they are available in the local RayJoin working copy.",
            "- RTDL currently provides generated analogues for Figure 13 and Figure 14.",
            "- Figure 15 is included as a paper reference figure only; the matching RTDL overlay-speedup analogue remains open.",
            "",
            "## Limitations and Remaining Work",
            "",
            "- Table 3 and Table 4 paper-scale dataset pairs are still planned rather than reproduced.",
            "- The current `overlay` workload is an overlay-seed analogue, not full polygon overlay materialization.",
            "- The current report uses Embree and local synthetic or derived inputs where the paper used NVIDIA RT cores and larger prepared datasets.",
            "- The final v0.1 target remains the OptiX/NVIDIA phase after this Embree baseline is complete enough.",
            "",
            "## Artifact Pointers",
            "",
            f"- Baseline evaluation summary: `{ROOT / 'docs' / 'reports' / 'embree_evaluation_summary_2026-03-30.md'}`",
            f"- Section 5.6 analogue summary: `{ROOT / 'docs' / 'reports' / 'section_5_6_scalability_report_2026-03-31.md'}`",
            f"- Frozen paper target matrix: `{ROOT / 'docs' / 'rayjoin_paper_reproduction_matrix.md'}`",
            f"- Dataset provenance note: `{ROOT / 'docs' / 'rayjoin_paper_dataset_provenance.md'}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_report() -> None:
    embree_payload = load_json(EMBREE_EVAL_JSON)
    section_payload = load_json(SECTION56_JSON)
    embree = embree_stats(embree_payload)
    sec56 = section56_stats(section_payload)

    OUT_MD.write_text(generate_markdown(embree_payload, section_payload), encoding="utf-8")

    scaling_fig = ensure_jpeg(EMBREE_FIGURES / "scaling_by_workload.svg")
    speedup_fig = ensure_jpeg(EMBREE_FIGURES / "speedup_by_case.svg")
    fig13_local = ensure_jpeg(SECTION56_FIGURES / "figure13_lsi_scalability.svg")
    fig14_local = ensure_jpeg(SECTION56_FIGURES / "figure14_pip_scalability.svg")
    fig13_paper = ensure_jpeg(RAYJOIN_DRAW_DIR / "scal_lsi.pdf")
    fig14_paper = ensure_jpeg(RAYJOIN_DRAW_DIR / "scal_pip.pdf")
    fig15_paper = ensure_jpeg(RAYJOIN_DRAW_DIR / "ag_varying_enlarge.pdf")

    pdf = PDFBuilder()
    pdf.add_text_page(
        "RTDL Embree Paper-Style Report",
        [
            (
                "Abstract",
                [
                    "RTDL is a Python-hosted DSL and compiler/runtime stack for non-graphics ray tracing workloads, with RayJoin as the target problem family. This report consolidates the current Embree-phase evidence into a single paper-style artifact.",
                    "The present system supports six audited workload families, executes them through a Python CPU reference and a native Embree backend, and now includes a scaled Section 5.6 scalability analogue for lsi and pip.",
                    "The resulting report is intentionally scoped as an Embree baseline, not as the final OptiX/NVIDIA v0.1 reproduction.",
                ],
            ),
            (
                "Current contribution",
                [
                    "Executable DSL surface: lsi, pip, overlay, ray_tri_hitcount, segment_polygon_hitcount, and point_nearest_segment.",
                    "Audited local backends: run_cpu(...) for semantic reference and run_embree(...) for native execution.",
                    "Paper-facing status: Figure 13 and Figure 14 analogues are implemented; Table 3, Table 4, and Figure 15 analogue remain open.",
                ],
            ),
        ],
        footer="Generated from checked-in RTDL benchmark and report artifacts on 2026-03-31.",
    )
    pdf.add_text_page(
        "Method and Scope",
        [
            (
                "Runtime and validation contract",
                [
                    "Every benchmarked case in the current baseline is parity-checked between run_cpu(...) and run_embree(...) before timing claims are accepted.",
                    "The current precision model is float_approx only; the report does not claim robust or exact computational geometry.",
                    "The overlay workload remains an overlay-seed analogue rather than full polygon materialization.",
                ],
            ),
            (
                "Paper-reproduction boundary",
                [
                    "Figure 13 and Figure 14 are supported through deterministic synthetic generators and a fixed-R/varying-S Embree experiment runner.",
                    "The current analogue uses R=800 and S=160..800 polygons under uniform and gaussian distributions, rather than the paper's RT-core scale.",
                    "Table 3 and Table 4 still require larger paper-aligned dataset acquisition and conversion, and Figure 15 still lacks a matching RTDL overlay-speedup generator.",
                ],
            ),
        ],
    )
    largest = embree["largest_cases"]
    pdf.add_text_page(
        "Embree Baseline Results",
        [
            (
                "Evaluation matrix",
                [
                    f"Total current benchmark cases: {embree['case_count']} with all parity checks passing = {embree['all_parity']}.",
                    f"Best observed Embree speedup vs CPU: {embree['best_speedup']['case_id']} at {embree['best_speedup']['speedup_vs_cpu']:.2f}x.",
                    f"Slowest Embree case by mean latency: {embree['slowest_embree']['case_id']} at {embree['slowest_embree']['embree']['mean_sec']:.6f}s.",
                ],
            ),
            (
                "Largest currently evaluated cases",
                [
                    f"lsi: {largest['lsi']['case_id']} at {largest['lsi']['embree']['mean_sec']:.6f}s mean.",
                    f"pip: {largest['pip']['case_id']} at {largest['pip']['embree']['mean_sec']:.6f}s mean.",
                    f"overlay: {largest['overlay']['case_id']} at {largest['overlay']['embree']['mean_sec']:.6f}s mean.",
                    f"ray_tri_hitcount: {largest['ray_tri_hitcount']['case_id']} at {largest['ray_tri_hitcount']['embree']['mean_sec']:.6f}s mean.",
                    f"segment_polygon_hitcount: {largest['segment_polygon_hitcount']['case_id']} at {largest['segment_polygon_hitcount']['embree']['mean_sec']:.6f}s mean.",
                    f"point_nearest_segment: {largest['point_nearest_segment']['case_id']} at {largest['point_nearest_segment']['embree']['mean_sec']:.6f}s mean.",
                ],
            ),
        ],
    )
    pdf.add_two_image_page(
        "Baseline Figures",
        "RTDL scaling-by-workload figure",
        scaling_fig,
        "RTDL speedup-by-case figure",
        speedup_fig,
        [
            "These figures come from the frozen Embree baseline evaluation matrix. They summarize the current six-workload local benchmark surface before the paper-specific reproduction steps.",
            "They are not direct RayJoin paper figures, but they provide the current baseline from which the paper-reproduction phase is extending.",
        ],
    )
    pdf.add_two_image_page(
        "Figure 13 Correspondence",
        "RayJoin paper Figure 13 reference",
        fig13_paper,
        "RTDL Embree Figure 13 analogue",
        fig13_local,
        [
            "The left image is the corresponding RayJoin paper scalability figure for LSI. The right image is RTDL's current Embree-phase analogue.",
            "RTDL now supports deterministic uniform and gaussian synthetic LSI scaling runs with query-time and throughput curves, but at a smaller fixed-R/varying-S scale than the paper.",
        ],
    )
    pdf.add_two_image_page(
        "Figure 14 Correspondence",
        "RayJoin paper Figure 14 reference",
        fig14_paper,
        "RTDL Embree Figure 14 analogue",
        fig14_local,
        [
            "The left image is the corresponding RayJoin paper scalability figure for PIP. The right image is RTDL's current Embree-phase analogue.",
            "For PIP, throughput is reported as probe-points per second. The analogue is correctness-gated with CPU-vs-Embree parity on reduced representative samples.",
        ],
    )
    pdf.add_text_page(
        "Section 5.6 Quantitative Highlights",
        [
            (
                "Correctness gate",
                [
                    f"All reduced parity checks for the Section 5.6 analogue passed: {sec56['all_parity']}.",
                ],
            ),
            (
                "Representative throughput trends",
                [
                    f"Uniform LSI throughput: {sec56['lsi_uniform'][0]['probe_polygons']} probe polygons -> {sec56['lsi_uniform'][0]['throughput']:.2f} intersections/s, rising to {sec56['lsi_uniform'][-1]['probe_polygons']} -> {sec56['lsi_uniform'][-1]['throughput']:.2f} intersections/s.",
                    f"Gaussian LSI throughput: {sec56['lsi_gaussian'][1]['probe_polygons']} -> {sec56['lsi_gaussian'][1]['throughput']:.2f} intersections/s, rising to {sec56['lsi_gaussian'][-1]['probe_polygons']} -> {sec56['lsi_gaussian'][-1]['throughput']:.2f} intersections/s.",
                    f"Uniform PIP throughput: {sec56['pip_uniform'][0]['probe_polygons']} -> {sec56['pip_uniform'][0]['throughput']:.2f} probe-points/s, rising to {sec56['pip_uniform'][-1]['probe_polygons']} -> {sec56['pip_uniform'][-1]['throughput']:.2f} probe-points/s.",
                    f"Gaussian PIP throughput: {sec56['pip_gaussian'][0]['probe_polygons']} -> {sec56['pip_gaussian'][0]['throughput']:.2f} probe-points/s, ending at {sec56['pip_gaussian'][-1]['probe_polygons']} -> {sec56['pip_gaussian'][-1]['throughput']:.2f} probe-points/s.",
                ],
            ),
        ],
    )
    pdf.add_image_page(
        "Figure 15 Current Status",
        fig15_paper,
        [
            "This page includes the corresponding RayJoin paper overlay-speedup figure as a reference target.",
            "RTDL does not yet have the matching Figure 15 analogue. Table 4 and Figure 15 remain open because the current overlay path is an overlay-seed analogue and the larger paper-aligned dataset pairs are not all integrated yet.",
        ],
    )
    pdf.add_text_page(
        "Discussion and Next Steps",
        [
            (
                "What this report establishes",
                [
                    "RTDL is now beyond a syntax-only prototype: it has a validated local backend, reproducible benchmark/report generation, and initial paper-structured experiment support on Embree.",
                    "The Section 5.6 slice is implemented and accepted as an Embree-phase analogue, which reduces risk for the later OptiX/NVIDIA phase.",
                ],
            ),
            (
                "What remains for full paper-style reproduction",
                [
                    "Acquire and normalize more of the RayJoin Table 3 and Table 4 dataset pairs into the RTDL pipeline.",
                    "Add larger paper-structured cases to the Embree evaluation matrix with CPU-vs-Embree parity gates.",
                    "Implement the RTDL overlay-speedup analogue needed for Figure 15.",
                    "Carry the same workload and figure pipeline forward to the eventual NVIDIA/OptiX backend.",
                ],
            ),
        ],
        footer=f"Markdown companion: {OUT_MD}",
    )
    pdf.write(OUT_PDF)


if __name__ == "__main__":
    build_report()
