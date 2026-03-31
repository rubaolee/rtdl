#!/usr/bin/env python3
from __future__ import annotations

import struct
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "docs" / "reports"
BUILD_DIR = ROOT / "build" / "status_report_assets"
RAYJOIN_DRAW_DIR = Path("/tmp/RayJoin_goal13/expr/draw")
OUT_PDF = REPORTS_DIR / "rtdl_status_report_2026-03-31.pdf"


def esc(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def wrap_bullet(text: str, width: int) -> list[str]:
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

    def add_text_page(
        self,
        title: str,
        sections: list[tuple[str, list[str]]],
        *,
        footer: str | None = None,
    ) -> None:
        width, height = 612, 792
        y = 742
        lines: list[str] = [f"BT /F1 22 Tf 72 {y:.1f} Td ({esc(title)}) Tj ET"]
        y -= 28
        for heading, bullets in sections:
            lines.append(f"BT /F1 13 Tf 72 {y:.1f} Td ({esc(heading)}) Tj ET")
            y -= 18
            for bullet in bullets:
                first = True
                for wrapped in wrap_bullet(bullet, 92):
                    prefix = "• " if first else "  "
                    lines.append(f"BT /F1 10.5 Tf 84 {y:.1f} Td ({esc(prefix + wrapped)}) Tj ET")
                    y -= 14
                    first = False
                y -= 2
            y -= 6
        if footer:
            lines.append(f"BT /F1 9 Tf 72 36 Td ({esc(footer)}) Tj ET")
        content = "\n".join(lines).encode("latin-1", "replace")
        content_id = self.add_obj(stream_obj(content))
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
            for wrapped in textwrap.wrap(line, width=94):
                lines.append(f"BT /F1 10 Tf 72 {caption_y:.1f} Td ({esc(wrapped)}) Tj ET")
                caption_y -= 13
        lines.append(f"q {draw_w:.3f} 0 0 {draw_h:.3f} {x:.3f} {y:.3f} cm /Im1 Do Q")

        content = "\n".join(lines).encode("latin-1", "replace")
        content_id = self.add_obj(stream_obj(content))
        page_id = self.add_obj(page_obj(width, height, content_id, [("Im1", image_id)]))
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


def ensure_asset(pdf_path: Path) -> Path:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    png_path = BUILD_DIR / f"{pdf_path.name}.png"
    jpg_path = BUILD_DIR / f"{pdf_path.name}.jpg"
    if not png_path.exists():
        run_command("qlmanage", "-t", "-s", "1600", "-o", str(BUILD_DIR), str(pdf_path))
    if not jpg_path.exists():
        run_command("sips", "-s", "format", "jpeg", str(png_path), "--out", str(jpg_path))
    return jpg_path


def build_report() -> None:
    figure_lsi = ensure_asset(RAYJOIN_DRAW_DIR / "scal_lsi.pdf")
    figure_pip = ensure_asset(RAYJOIN_DRAW_DIR / "scal_pip.pdf")
    figure_overlay = ensure_asset(RAYJOIN_DRAW_DIR / "ag_varying_enlarge.pdf")
    embree_report = ensure_asset(REPORTS_DIR / "embree_evaluation_report_2026-03-30.pdf")

    pdf = PDFBuilder()
    pdf.add_text_page(
        "RTDL Status Summary (Embree Phase)",
        [
            (
                "Project state",
                [
                    "RTDL is now a real executable prototype: Python-hosted DSL, compiler IR, lowering/codegen, CPU reference runtime, and a working Embree backend on this Mac.",
                    "Current audited precision is float_approx. NVIDIA/OptiX remains the final v0.1 target, but the active baseline is Embree-based execution and evaluation.",
                    "The current working tree also includes preserved Goal 13 paper-reproduction artifacts, Goal 14 Section 5.6 local-profile planning, and the completed Goal 15 native C++ comparison slice.",
                ],
            ),
            (
                "Supported workloads",
                [
                    "Six audited workload families are implemented end to end: lsi, pip, overlay, ray_tri_hitcount, segment_polygon_hitcount, and point_nearest_segment.",
                    "The first four use the BVH-oriented Embree path. The last two are currently audited native_loop local workloads, not BVH-accelerated traversal.",
                    "Queries can run through run_cpu(...) for semantic reference and run_embree(...) for native execution.",
                ],
            ),
            (
                "Reliability process",
                [
                    "Feature and audit rounds are executed with multi-agent review, revision, tests, and archived evidence in history/.",
                    "Goal 12 closed the trust-audit revision under a 2-agent Codex + Gemini rule while Claude was quota-limited.",
                    "Goal 15 added a separate native C++ + Embree versus RTDL + Embree comparison harness for deterministic correctness and host-overhead measurement.",
                ],
            ),
        ],
        footer="Prepared locally on 2026-03-31 from the RTDL working tree and RayJoin reference artifacts.",
    )
    pdf.add_text_page(
        "Embree Baseline and Evaluation Status",
        [
            (
                "Published baseline",
                [
                    "The Embree baseline goal is complete: workload contracts are frozen, CPU-vs-Embree parity is encoded, and the baseline runner / benchmark / summary pipeline is in place.",
                    "The current checked-in evaluation matrix covers 17 cases across authored, fixture, derived, and synthetic datasets.",
                    "All published Embree evaluation cases pass parity according to the checked-in 2026-03-30 evaluation summary.",
                ],
            ),
            (
                "Key measured signals",
                [
                    "Largest current local speedup appears in the ray_tri_hitcount synthetic-large case at 165.14x Embree vs CPU on this Mac baseline.",
                    "Current evaluated lsi/pip/overlay cases are still much smaller than the full RayJoin paper campaign and should be treated as baseline validation, not paper-equivalent results.",
                    "The evaluation harness already emits tables, CSVs, SVG figures, a PDF report, and can now be cross-checked against a standalone native C++ comparison slice for lsi and pip.",
                ],
            ),
            (
                "Goal 13 paper-reproduction status",
                [
                    "Goal 13 is canceled as superseded by Goal 15, but its preserved artifacts remain valid references for any future GPU-phase paper-reproduction work.",
                    "The dataset provenance document now maps RayJoin paper labels County/Zipcode, Block/Water, and LKAF..LKSA / PKAF..PKSA to explicit dataset families and internal names.",
                    "Completed slices already include the Figure 13 / Figure 14 Embree analogue, while remaining work is the Table 3 analogue, Table 4 analogue, and Figure 15 analogue generators.",
                ],
            ),
        ],
    )
    pdf.add_image_page(
        "Current RTDL Embree Evaluation Snapshot",
        embree_report,
        [
            "This page is the first-page preview of the current RTDL Embree evaluation report generated inside the repository.",
            "It reflects the existing pre-GPU evaluation pipeline: benchmark cases, parity status, figures, and summary output already work locally.",
        ],
    )
    pdf.add_image_page(
        "RayJoin Figure 13 Reference: LSI Scalability",
        figure_lsi,
        [
            "Reference figure from the RayJoin repository. This remains the style target for any future resumed paper-reproduction work on the Embree phase.",
            "RTDL does not yet regenerate this figure; current local work has only frozen the target matrix, dataset provenance, and registry needed to drive that implementation.",
        ],
    )
    pdf.add_image_page(
        "RayJoin Figure 14 Reference: PIP Scalability",
        figure_pip,
        [
            "Reference figure from the RayJoin repository for PIP scalability.",
            "Any future resumed paper-reproduction work should reproduce the structure, not the GPU numbers: fixed-size synthetic series, uniform and gaussian distributions, query time, and throughput analogues.",
        ],
    )
    pdf.add_image_page(
        "RayJoin Figure 15 Reference: Overlay / Varying Enlarge",
        figure_overlay,
        [
            "Reference figure from the RayJoin repository showing overlay-oriented varying-enlarge behavior.",
            "In RTDL, overlay is currently a compositional workload built from lsi and pip seed generation, so the Embree-phase figure will be an analogue and must be labeled honestly.",
        ],
    )
    pdf.add_text_page(
        "What is Done vs What Remains",
        [
            (
                "Done now",
                [
                    "Language, docs, examples, CPU runtime, Embree runtime, benchmark harness, history/audit process, and the Embree evaluation report are all real and usable.",
                    "RayJoin paper dataset naming ambiguities for LKAF/LKAS/LKAU/LKEU/LKNA/LKSA have been resolved from the RayJoin experiment scripts.",
                    "A machine-readable paper target registry already exists locally in src/rtdsl/paper_reproduction.py, and Goal 15 now adds a checked-in native C++ comparison report for deterministic lsi/pip fixtures.",
                ],
            ),
            (
                "Still missing for paper-complete Embree reproduction",
                [
                    "Larger paper-aligned dataset acquisition and conversion, especially County/Zipcode, Block/Water, and continent-scale lakes/parks pairs.",
                    "Automated Table 3 / Table 4 analogue generators and Figure 13 / Figure 14 / Figure 15 analogue generators.",
                    "A final Embree-phase reproduction report that states which paper targets are exact-input, derived-input, fixture-subset, or synthetic-input.",
                ],
            ),
            (
                "Final v0.1 beyond Embree",
                [
                    "The last major step is the real NVIDIA/OptiX backend so RTDL can rerun RayJoin-style workloads on RT cores and regenerate the paper-style benchmark pipeline with RTDL-generated implementations."
                ],
            ),
        ],
        footer="Report file: docs/reports/rtdl_status_report_2026-03-31.pdf",
    )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    pdf.write(OUT_PDF)


if __name__ == "__main__":
    build_report()
    print(OUT_PDF)
