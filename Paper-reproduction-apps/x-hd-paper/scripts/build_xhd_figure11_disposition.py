#!/usr/bin/env python3
"""Build the Goal5283 Figure 11 disposition artifact.

The output intentionally separates three things:

* author Figure 11 memory log extraction;
* RTDL bounded / shape-only memory evidence;
* the claim decision.

It does not compute author-vs-RTDL memory ratios.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"could not parse JSON: {path}") from exc


def _author_summary(author_matrix: Mapping[str, Any]) -> dict[str, Any]:
    datasets = author_matrix.get("datasets")
    if not isinstance(datasets, Mapping):
        raise ValueError("expected author Figure 11 matrix with datasets")
    summary: dict[str, Any] = {}
    for name, dataset in datasets.items():
        if not isinstance(dataset, Mapping):
            continue
        summary[str(name)] = {
            "row_count": dataset.get("row_count"),
            "xhd_mean_total_memory_mb": (
                dataset.get("mean_total_memory_mb", {}).get("X-HD")
                if isinstance(dataset.get("mean_total_memory_mb"), Mapping)
                else None
            ),
            "xhd_mean_breakdown_mb": dataset.get("xhd_mean_breakdown_mb"),
        }
    return summary


def build_figure11_disposition(
    *,
    author_matrix_path: Path,
    rtdl_matrix_path: Path,
    offload_mapping_path: Path,
    date: str,
) -> dict[str, Any]:
    author_matrix = _load_json(author_matrix_path)
    rtdl_matrix = _load_json(rtdl_matrix_path)
    offload_mapping = _load_json(offload_mapping_path)
    mapping = offload_mapping["author_offload_mapping"]
    fields = mapping["author_shaped_fields"]
    denominator = mapping["denominator_alignment"]
    claim_boundary = {
        "figure11_reproduced": False,
        "author_memory_parity_claimed": False,
        "same_denominator_author_figure11_claimed": False,
        "memory_ratio_claimed": False,
        "full_paper_reproduction_claimed": False,
    }
    shape_only = {
        "label": "Goal5282 shape-only offload candidate",
        "source_artifact": str(offload_mapping_path),
        "paper_dataset_identity": False,
        "same_denominator_author_figure11": False,
        "figure11_row": False,
        "author_shaped_fields": {
            "OffloadingSize": fields["OffloadingSize"],
            "WL": fields["WL"],
            "WL Heavy Peak": fields["WL Heavy Peak"],
        },
        "rtdl_measured_fields": mapping["rtdl_measured_fields"],
        "why_not_figure11_row": [
            "The source is a generic tiny native telemetry probe, not a Figure 11 paper input.",
            "RTDL measured queue bytes use 64-bit id pairs; author WL Heavy Peak uses uint32 id pairs.",
            "RTDL WL remains unaligned because native in_queue_capacity is attempted frontier hits, not author in_queue + miss_queue.",
            "No author-vs-RTDL Figure 11 memory ratio has a same-denominator basis.",
        ],
    }
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5283.figure11_disposition.v1",
        "goal": "Goal5283",
        "date": date,
        "status": "figure11_closed_denominator_not_aligned_after_native_mapping",
        "inputs": {
            "author_matrix": str(author_matrix_path),
            "rtdl_bounded_memory_matrix": str(rtdl_matrix_path),
            "offload_mapping": str(offload_mapping_path),
        },
        "author_figure11_reference": {
            "schema": author_matrix.get("schema"),
            "status": author_matrix.get("status"),
            "datasets": _author_summary(author_matrix),
        },
        "rtdl_current_memory_matrix": {
            "schema": rtdl_matrix.get("schema"),
            "status": rtdl_matrix.get("status"),
            "row_count": rtdl_matrix.get("row_count"),
            "coverage": rtdl_matrix.get("coverage"),
            "claim_boundary": rtdl_matrix.get("claim_boundary"),
        },
        "shape_only_candidate": shape_only,
        "decision": {
            "offloading_size_shape_mapped": bool(
                denominator["offloading_size_row_count_shape_available"]
            ),
            "wl_heavy_peak_author_width_candidate_available": True,
            "same_byte_denominator_author_figure11": bool(
                denominator["same_byte_denominator_author_figure11"]
            ),
            "same_denominator_author_figure11": False,
            "figure11_reproduced": False,
            "close_current_figure11_line": True,
            "next_if_reopened": (
                "Implement a denominator-aligned generic native worklist that uses "
                "author-compatible queue id width and an author-like in_queue + "
                "miss_queue denominator, or obtain external review accepting a "
                "different memory question."
            ),
        },
        "remaining_gaps": [
            "exact Figure 11 paper input identity is not available in the current POD",
            "RTDL measured queue bytes are not author uint32 queue bytes",
            "RTDL WL is not author in_queue + miss_queue",
            "the shape-only candidate is not a paper Figure 11 row",
        ],
        "claim_boundary": claim_boundary,
        "matched": (
            bool(denominator["offloading_size_row_count_shape_available"])
            and not bool(denominator["same_denominator_author_figure11"])
            and all(value is False for value in claim_boundary.values())
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build X-HD Figure 11 disposition artifact.")
    parser.add_argument("--author-matrix", required=True)
    parser.add_argument("--rtdl-matrix", required=True)
    parser.add_argument("--offload-mapping", required=True)
    parser.add_argument("--date", default="2026-07-09")
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    artifact = build_figure11_disposition(
        author_matrix_path=Path(args.author_matrix),
        rtdl_matrix_path=Path(args.rtdl_matrix),
        offload_mapping_path=Path(args.offload_mapping),
        date=args.date,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0 if artifact["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
