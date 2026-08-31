#!/usr/bin/env python3
"""Build the preregistered Goal5753 held-out application universe.

This script deliberately knows nothing about V4 implementation coverage.  It
derives a stable problem/paper universe from the source bundle of the survey
"Ray Tracing Cores for General-Purpose Computing: A Literature Review" and
then applies only the exclusions frozen below: prior RTDL paper applications
and problem families already used to design V4.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SCHEMA = "rtdl.v4.goal5753.held_out_candidate_universe.v1"
SURVEY_URL = "https://arxiv.org/abs/2603.28771"
SURVEY_SOURCE_URL = "https://export.arxiv.org/e-print/2603.28771"

# This table is the entire admissibility policy.  No entry is classified by
# whether the current V4 implementation is expected to pass it.
PAPER_DISPOSITIONS: dict[str, tuple[bool, str]] = {
    "Kim2025RTPDPD": (True, "new_problem_family__penetration_depth"),
    "Zhang2025RTSpMSpMHR": (True, "new_problem_family__sparse_matrix_multiplication"),
    "Xiao2025ACS": (False, "paper_already_used_by_rtdl_triangle_counting"),
    "Geng2025LibRTSAS": (False, "paper_already_used_by_rtdl_librts"),
    "Nagarajan2025RTBarnesHutAB": (False, "paper_already_used_by_rtdl_rt_barneshut"),
    "Sui2024HardwareAcceleratedRT": (True, "new_problem_family__collision_detection"),
    "Henneberg2024MoreBF": (False, "spatial_index_query_family_already_used_to_design_v4"),
    "Meneses2024RTXRMQ": (True, "new_problem_family__range_minimum_query"),
    "Geng2024RayJoinFA": (False, "paper_already_used_by_rtdl_rayjoin"),
    "Mandarapu2023ArkadeKN": (False, "paper_already_used_by_rtdl_arkade"),
    "Liu2023JUNOOH": (False, "nearest_neighbor_family_already_used_to_design_v4"),
    "Wang2024RTODEO": (False, "nearest_neighbor_outlier_family_already_used_to_design_v4"),
    "Lv2024RTScanES": (False, "database_scan_family_already_used_to_design_v4"),
    "Nagarajan2023RTkNNSUU": (False, "nearest_neighbor_family_already_used_to_design_v4"),
    "zhao2023leveraging": (True, "new_problem_family__particle_simulation"),
    "Henneberg2023RTIndeXEH": (False, "database_index_family_already_used_to_design_v4"),
    "Hashinoki2023ImplementationOR": (True, "new_problem_family__radio_wave_propagation"),
    "Nagarajan2023RTDBSCANAD": (False, "paper_already_used_by_rtdl_rt_dbscan"),
    "Morrical2022AcceleratingUM": (True, "new_problem_family__mesh_point_location"),
    "zhu2022rtnn": (False, "paper_already_used_by_rtdl_rtnn"),
    "Wang2022AnGP": (True, "new_problem_family__particle_tracking"),
    "zellmann2020accelerating": (True, "new_problem_family__force_directed_graph_drawing"),
    "Morrical2019EfficientSS": (True, "new_problem_family__volume_space_skipping"),
    "Petrescu2019GPUSR": (True, "new_problem_family__sparse_ray_traced_segmentation"),
    "Chan2018ParticlemeshCI": (True, "new_problem_family__particle_mesh_coupling"),
    "Liu2025RayTC": (True, "new_problem_family__infrared_radiation_simulation"),
    "Cui2024RTSRTAM": (True, "new_problem_family__particle_transport"),
    "Salmon2019ExploitingHR": (True, "new_problem_family__monte_carlo_particle_transport"),
    "Schwarz2010FastPS": (True, "new_problem_family__voxelization"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_bibtex(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", text):
        kind, key = match.group(1), match.group(2).strip()
        depth = 0
        end = None
        for index in range(match.start(), len(text)):
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = index + 1
                    break
        if end is None:
            raise ValueError(f"unterminated BibTeX entry: {key}")
        body = text[match.end() : end - 1]
        fields: dict[str, str] = {"entry_type": kind}
        for field in ("title", "author", "year", "doi", "url", "journal", "booktitle"):
            fm = re.search(
                rf"(?ims)^\s*{field}\s*=\s*(?:\{{(.*?)\}}|\"(.*?)\")\s*,?\s*$",
                body,
            )
            if fm:
                value = next(group for group in fm.groups() if group is not None)
                fields[field] = re.sub(r"\s+", " ", value).strip()
        entries[key] = fields
    return entries


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def build(prob_csv: Path, bib_path: Path, source_archive: Path) -> dict[str, Any]:
    with prob_csv.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    bibliography = parse_bibtex(bib_path.read_text(encoding="utf-8"))

    source_rows: list[dict[str, Any]] = []
    eligible: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_keys: set[str] = set()

    for source_index, row in enumerate(rows):
        raw_problem = row["Problem"].strip()
        cite = re.fullmatch(r"(.+?)~\\cite\{([^}]+)\}", raw_problem)
        if not cite:
            raise ValueError(f"unparseable survey problem row {source_index}: {raw_problem!r}")
        problem, cite_key = cite.group(1).strip(), cite.group(2).strip()
        if cite_key not in PAPER_DISPOSITIONS:
            raise ValueError(f"unclassified citation key: {cite_key}")
        if cite_key not in bibliography:
            raise ValueError(f"citation missing from bibliography: {cite_key}")
        is_eligible, reason = PAPER_DISPOSITIONS[cite_key]
        candidate_id = f"{cite_key}::{slug(problem)}"
        if candidate_id in seen_ids:
            raise ValueError(f"duplicate candidate id: {candidate_id}")
        seen_ids.add(candidate_id)
        seen_keys.add(cite_key)
        record = {
            "source_index": source_index,
            "candidate_id": candidate_id,
            "problem": problem,
            "citation_key": cite_key,
            "paper": bibliography[cite_key],
            "survey_measurements": {
                "best_speedup": row["Best Speedup"],
                "worst_speedup": row["Worst Speedup"],
                "improves_count": row["Improves?"],
                "average": row["Avg"],
            },
            "eligible": is_eligible,
            "disposition": reason,
        }
        source_rows.append(record)
        if is_eligible:
            eligible.append(record)

    missing_policy = sorted(set(PAPER_DISPOSITIONS) - seen_keys)
    if missing_policy:
        raise ValueError(f"policy keys absent from survey table: {missing_policy}")
    eligible.sort(key=lambda record: record["candidate_id"])

    return {
        "schema": SCHEMA,
        "status": "candidate_universe_frozen_before_external_entropy",
        "source": {
            "survey_title": "Ray Tracing Cores for General-Purpose Computing: A Literature Review",
            "survey_url": SURVEY_URL,
            "survey_source_url": SURVEY_SOURCE_URL,
            "survey_source_archive_sha256": sha256(source_archive),
            "survey_source_archive_bytes": source_archive.stat().st_size,
            "prob_csv_sha256": sha256(prob_csv),
            "sample_bib_sha256": sha256(bib_path),
        },
        "policy": {
            "selection_unit": "survey_problem_row",
            "eligible_if": "listed survey row whose paper and problem family were not used to build the nine V3 apps or design the V4 callback system",
            "not_filtered_by": [
                "expected_v4_expressibility",
                "expected_implementation_effort",
                "expected_performance",
                "availability_of_an_existing_rtdl_primitive",
            ],
            "existing_or_design_seen_families_excluded": True,
            "all_citation_keys_explicitly_classified": True,
        },
        "counts": {
            "survey_rows": len(source_rows),
            "eligible_rows": len(eligible),
            "excluded_rows": len(source_rows) - len(eligible),
        },
        "source_rows": source_rows,
        "eligible_candidates_sorted": eligible,
        "claim_boundary": {
            "application_selected": False,
            "v4_expressibility_claimed": False,
            "performance_claimed": False,
            "paper_result_claimed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prob-csv", type=Path, required=True)
    parser.add_argument("--bib", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.prob_csv, args.bib, args.source_archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
