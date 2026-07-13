from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from collections import Counter
from pathlib import Path


EXPECTED_AE_COMMIT = "d605fe1bd5708cbf3c457a3a9698e0cc7bcdc14b"
EXPECTED_SUBMODULES = {
    "RTSpatial": "7c54c181b1058c87768767998c00e225cc58666e",
    "RayJoin": "2151f56d09cbcfd4edbff259d97ac3123705411b",
    "SpatialQueryBenchmark": "9140ad997519713bb5fdceba639a357afa4609ad",
}
SOURCE_PATHS = (
    "README.md",
    "3_download_datasets.sh",
    "4_run_experiments.sh",
    "5_draw_figures.sh",
    "expr/common.sh",
    "expr/query/query.sh",
    "expr/query/update.sh",
    "expr/query/scalability.sh",
    "expr/query/pip.sh",
    "expr/query/paper_logs.zip",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ("git", "-C", str(root), *args), text=True
    ).strip()


def _submodule_pins(root: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for line in _git(root, "submodule", "status").splitlines():
        match = re.match(r"^[ +-]?([0-9a-f]{40})\s+(\S+)", line.strip())
        if match:
            pins[match.group(2)] = match.group(1)
    return pins


def _paper_log_categories(archive_path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            parts = name.split("/")
            if len(parts) >= 3 and parts[0] == "logs" and name.endswith(".log"):
                counts[parts[1]] += 1
    return counts


def _require_tokens(path: Path, tokens: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise RuntimeError(f"{path} is missing expected tokens: {missing}")


def build_audit(ae_root: Path) -> dict[str, object]:
    ae_root = ae_root.resolve()
    head = _git(ae_root, "rev-parse", "HEAD")
    pins = _submodule_pins(ae_root)
    if head != EXPECTED_AE_COMMIT:
        raise RuntimeError(f"unexpected PPoPPAE commit: {head}")
    if pins != EXPECTED_SUBMODULES:
        raise RuntimeError(f"unexpected PPoPPAE submodule pins: {pins}")
    for relative in SOURCE_PATHS:
        if not (ae_root / relative).is_file():
            raise FileNotFoundError(ae_root / relative)

    _require_tokens(
        ae_root / "expr" / "common.sh",
        (
            "CONTAINS_QUERY_SIZE=100000",
            "INTERSECTS_QUERY_SIZE=10000",
            "RAY_DUP_INTERSECTS_QUERY_SIZE=50000",
            'RANGE_QUERY_INTERSECTS_SELECTIVITIES=("0.0001" "0.001" "0.01")',
            "SYNTHETIC_DATA_SIZES=(10000000 20000000 30000000 40000000 50000000)",
        ),
    )
    _require_tokens(
        ae_root / "5_draw_figures.sh",
        (
            'mv point_query.pdf "$AE_FIGURES_DIR/fig7.pdf"',
            'mv range_contains_query.pdf "$AE_FIGURES_DIR/fig8.pdf"',
            'mv range_intersects_query.pdf "$AE_FIGURES_DIR/fig9.pdf"',
            'mv dup_rays.pdf "$AE_FIGURES_DIR/fig10.pdf"',
            'mv scalability.pdf "$AE_FIGURES_DIR/fig11.pdf"',
            'mv update_all.pdf "$AE_FIGURES_DIR/fig12.pdf"',
            'mv pip_time.pdf "$AE_FIGURES_DIR/fig13.pdf"',
        ),
    )

    categories = _paper_log_categories(ae_root / "expr" / "query" / "paper_logs.zip")
    figure_targets = (
        {
            "paper_figure": 6,
            "paper_question": "point-query performance and query-count scaling",
            "ae_output": "fig7.pdf",
            "author_entrypoint": "expr/query/query.sh",
            "log_prefixes": ("point-contains_queries_",),
            "datasets": "six real datasets; OSMParks query-size sweep",
            "current_rtdl_status": "bounded same-input point count only",
        },
        {
            "paper_figure": 7,
            "paper_question": "range-contains performance and query-count scaling",
            "ae_output": "fig8.pdf",
            "author_entrypoint": "expr/query/query.sh",
            "log_prefixes": ("range-contains_queries_",),
            "datasets": "six real datasets; OSMParks query-size sweep",
            "current_rtdl_status": "bounded same-input range-contains count only",
        },
        {
            "paper_figure": 8,
            "paper_question": "range-intersects performance by selectivity and query count",
            "ae_output": "fig9.pdf",
            "author_entrypoint": "expr/query/query.sh",
            "log_prefixes": ("range-intersects_select_",),
            "datasets": "six real datasets; selectivity 0.01%, 0.1%, 1%",
            "current_rtdl_status": "bounded same-input exact rows only",
        },
        {
            "paper_figure": 9,
            "paper_question": "Ray-Multicast k sweep, prediction, and phase breakdown",
            "ae_output": "fig10.pdf",
            "author_entrypoint": "expr/query/query.sh",
            "log_prefixes": ("ray_duplication_range-intersects_",),
            "datasets": "six real datasets; 50K queries at 0.1% selectivity",
            "current_rtdl_status": "source/reference audit complete; native spike no-go and reverted",
        },
        {
            "paper_figure": 10,
            "paper_question": "build cost, mutation throughput, and update sensitivity",
            "ae_output": "fig12.pdf",
            "author_entrypoint": "expr/query/update.sh",
            "log_prefixes": ("insertion_batch_", "deletion_batch_", "point-contains_update_"),
            "datasets": "real datasets plus 50M synthetic insertion/deletion workloads",
            "current_rtdl_status": "bounded mutation semantics and sparse-refit speedup only",
        },
        {
            "paper_figure": 11,
            "paper_question": "10M-50M uniform/Gaussian scalability",
            "ae_output": "fig11.pdf",
            "author_entrypoint": "expr/query/scalability.sh",
            "log_prefixes": ("scalability_",),
            "datasets": "generated 10M-50M uniform and Gaussian rectangles",
            "current_rtdl_status": "not reproduced",
        },
        {
            "paper_figure": 12,
            "paper_question": "100K point-in-polygon application performance",
            "ae_output": "fig13.pdf",
            "author_entrypoint": "expr/query/pip.sh",
            "log_prefixes": ("pip_queries_100000",),
            "datasets": "USCounty, USCensus, USWater, EUParks",
            "current_rtdl_status": "one Level-B representative same-input relation gate",
        },
    )
    for target in figure_targets:
        target["paper_logs_present"] = any(
            category.startswith(prefix)
            for category in categories
            for prefix in target["log_prefixes"]
        )

    dataset_script = (ae_root / "3_download_datasets.sh").read_text(encoding="utf-8")
    archive_specs = []
    for name, checksum in re.findall(r'"(polygons|queries|synthetic)"\s+\\\n\s+"([0-9a-f]{32})"', dataset_script):
        archive_specs.append({"name": name, "md5": checksum})
    exact_inputs_present = (ae_root / ".datasets").exists()
    source_hashes = {
        relative: _sha256(ae_root / relative) for relative in SOURCE_PATHS
    }
    log_count = sum(categories.values())
    all_targets_have_logs = all(bool(target["paper_logs_present"]) for target in figure_targets)
    return {
        "schema": "rtdl.paper_reproduction.librts.full_target_availability.v1",
        "status": "paper_targets_and_author_logs_available__exact_inputs_not_acquired",
        "provenance": {
            "paper": "LibRTS: A Spatial Indexing Library by Ray Tracing, PPoPP 2025",
            "paper_doi": "10.1145/3710848.3710850",
            "ae_repository": "https://github.com/RTSpatial/PPoPPAE",
            "ae_commit": head,
            "submodule_pins": pins,
            "source_sha256": source_hashes,
        },
        "author_evidence": {
            "paper_log_count": log_count,
            "paper_log_category_count": len(categories),
            "paper_log_categories": dict(sorted(categories.items())),
            "all_paper_figure_targets_have_author_logs": all_targets_have_logs,
            "logs_are_author_reference_evidence_not_rtdl_reproduction": True,
        },
        "dataset_acquisition": {
            "script": "3_download_datasets.sh",
            "archives": archive_specs,
            "exact_inputs_present_in_audit_checkout": exact_inputs_present,
            "direct_sharepoint_head_probe_status": [401, 401, 401],
            "direct_head_probe_is_not_author_downloader_execution": True,
            "large_zenodo_archive_downloaded": False,
            "large_zenodo_archive_published_size": "23.1 GB",
        },
        "numbering_warning": {
            "paper_to_ae_output": {
                "6": "fig7.pdf",
                "7": "fig8.pdf",
                "8": "fig9.pdf",
                "9": "fig10.pdf",
                "10": "fig12.pdf",
                "11": "fig11.pdf",
                "12": "fig13.pdf",
            },
            "mechanical_numeric_matching_is_valid": False,
        },
        "figure_targets": list(figure_targets),
        "decision": {
            "full_paper_reproduction_complete": False,
            "paper_target_matrix_complete": True,
            "author_paper_logs_available": all_targets_have_logs,
            "exact_paper_inputs_available": exact_inputs_present,
            "next_goal": "extract_author_log_denominators_before_any_large_dataset_download",
            "pod_required_next": False,
        },
        "claim_boundary": {
            "paper_figures_reproduced": False,
            "author_logs_treated_as_rtdl_results": False,
            "exact_dataset_identity_claimed": False,
            "author_performance_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ae-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_audit(args.ae_root)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
