from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
import json
import os
import urllib.request
import xml.etree.ElementTree as ET

from .reference import Polygon


@dataclass(frozen=True)
class PublicPathologyDataset:
    key: str
    title: str
    source_url: str
    access_kind: str
    annotation_format: str
    asset_kind: str
    size_bytes: int | None
    use_for_jaccard: str
    notes: str


NUINSSEG = PublicPathologyDataset(
    key="nuinsseg",
    title="NuInsSeg",
    source_url="https://zenodo.org/api/records/10518968/files/NuInsSeg.zip/content",
    access_kind="direct_http",
    annotation_format="labeled_png_masks_and_imagej_roi_zip",
    asset_kind="full_dataset_zip",
    size_bytes=1627427342,
    use_for_jaccard="preferred_later_public_mask_source",
    notes=(
        "Public Zenodo distribution with raw patches, masks, and ROI files. "
        "Best semantic fit for the current unit-cell Jaccard line, but practical conversion "
        "needs a mask-image decoder that is not yet part of the repo."
    ),
)


MONUSEG = PublicPathologyDataset(
    key="monuseg",
    title="MoNuSeg 2018 Training Data",
    source_url="https://drive.google.com/file/d/1ZgqFJomqQGNnsx7w7QBzQQMVA16lbVCA/view?usp=sharing",
    access_kind="public_google_drive",
    annotation_format="xml_polygon_annotations",
    asset_kind="challenge_training_zip",
    size_bytes=None,
    use_for_jaccard="parser_landed_now_for_public_polygon_annotations",
    notes=(
        "Public challenge data page exposes training/testing downloads. "
        "XML polygon annotations are easier to integrate immediately without adding image dependencies."
    ),
)


PUBLIC_PATHOLOGY_DATASETS = {
    dataset.key: dataset
    for dataset in (
        NUINSSEG,
        MONUSEG,
    )
}


def public_pathology_datasets() -> tuple[PublicPathologyDataset, ...]:
    return tuple(PUBLIC_PATHOLOGY_DATASETS.values())


def write_public_pathology_manifest(output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "datasets": [asdict(dataset) for dataset in public_pathology_datasets()],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def download_nuinsseg_zip(destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(NUINSSEG.source_url) as response, path.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return path


def parse_monuseg_xml_annotations(xml_text: str) -> tuple[Polygon, ...]:
    root = ET.fromstring(xml_text)
    polygons: list[Polygon] = []
    next_id = 1
    for region in root.findall(".//Region"):
        vertices = []
        for vertex in region.findall(".//Vertex"):
            x_value = vertex.attrib.get("X")
            y_value = vertex.attrib.get("Y")
            if x_value is None or y_value is None:
                continue
            vertices.append((float(x_value), float(y_value)))
        if len(vertices) < 3:
            continue
        region_id = region.attrib.get("Id")
        polygon_id = int(region_id) if region_id and region_id.isdigit() else next_id
        polygons.append(Polygon(id=polygon_id, vertices=tuple(vertices)))
        next_id = max(next_id + 1, polygon_id + 1)
    return tuple(polygons)


def load_monuseg_xml_annotations(path: str | Path) -> tuple[Polygon, ...]:
    xml_path = Path(path)
    return parse_monuseg_xml_annotations(xml_path.read_text(encoding="utf-8"))


def render_goal139_markdown() -> str:
    lines = [
        "# Goal 139 Public Pathology Data Acquisition and Conversion",
        "",
        "## Public datasets",
        "",
        "| key | title | annotation_format | access_kind | use_for_jaccard |",
        "| --- | --- | --- | --- | --- |",
    ]
    for dataset in public_pathology_datasets():
        lines.append(
            f"| `{dataset.key}` | `{dataset.title}` | `{dataset.annotation_format}` | `{dataset.access_kind}` | `{dataset.use_for_jaccard}` |"
        )
    lines.extend(
        [
            "",
            "## Current closure",
            "",
            "- NuInsSeg recorded as the preferred future public mask source for the unit-cell Jaccard line.",
            "- MoNuSeg XML polygon parsing landed now as the first public-data conversion surface.",
            "- No claim is made yet that public pathology data is already closed for Goal 138 semantics.",
            "",
        ]
    )
    return "\n".join(lines)


def write_goal139_artifacts(output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    manifest_path = write_public_pathology_manifest(output_path / "manifest.json")
    markdown_path = output_path / "summary.md"
    markdown_path.write_text(render_goal139_markdown(), encoding="utf-8")
    return {"manifest": manifest_path, "markdown": markdown_path}


def monuseg_drive_file_id() -> str:
    return "1ZgqFJomqQGNnsx7w7QBzQQMVA16lbVCA"


def direct_download_allowed(dataset_key: str) -> bool:
    dataset = PUBLIC_PATHOLOGY_DATASETS[dataset_key]
    return dataset.access_kind == "direct_http"


def describe_download_boundary(dataset_key: str) -> str:
    dataset = PUBLIC_PATHOLOGY_DATASETS[dataset_key]
    if dataset.key == "nuinsseg":
        size_gib = dataset.size_bytes / float(1024 ** 3) if dataset.size_bytes else 0.0
        return (
            f"{dataset.title} is directly downloadable over HTTP, but the archive is about "
            f"{size_gib:.2f} GiB and is not pulled automatically in routine tests."
        )
    return (
        f"{dataset.title} is public, but current acquisition is documented as an external "
        "download step rather than a built-in direct HTTP pull."
    )
