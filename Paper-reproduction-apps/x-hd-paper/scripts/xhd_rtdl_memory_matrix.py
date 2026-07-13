#!/usr/bin/env python3
"""Build status-bearing RTDL memory matrix rows from hd_exec-compatible JSON.

This app-owned helper intentionally keeps every memory field status-bearing.
It is not the author's Figure 11 script, and it does not compute author-vs-RTDL
memory ratios.  Its job is to collect the RTDL-side evidence in a shape that can
be reviewed before any Figure 11 reproduction claim is attempted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent

import xhd_memory_accounting


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exercised by CLI behavior
        raise ValueError(f"could not parse JSON artifact: {path}") from exc


def _field_summary(fields: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {
        key: {
            "status": value.get("status"),
            "bytes": value.get("bytes"),
            "mb": value.get("mb"),
            "method": value.get("method"),
        }
        for key, value in fields.items()
    }


def _row_from_payload(
    *,
    payload: Mapping[str, Any],
    artifact_path: str,
    row_label: str | None = None,
) -> dict[str, Any]:
    rtdl = payload.get("RTDL")
    if not isinstance(rtdl, Mapping):
        raise ValueError("expected hd_exec-compatible payload with RTDL object")
    accounting = xhd_memory_accounting.rtdl_memory_accounting_from_hd_exec_payload(payload)
    author_fields = accounting.get("author_mapped_fields")
    rtdl_only = accounting.get("rtdl_only_fields")
    if not isinstance(author_fields, Mapping) or not isinstance(rtdl_only, Mapping):
        raise ValueError("expected status-bearing RTDL memory_accounting fields")
    route = rtdl.get("route", {})
    directed = None
    if isinstance(route, Mapping):
        directed = (
            route.get("directed_a_to_b")
            or route.get("cell_mbr_summary", {})
            .get("rtdl_route", {})
            .get("directed_a_to_b")
        )
    directed = directed if isinstance(directed, Mapping) else {}
    native_memory = directed.get("frontier_native_memory_telemetry")
    native_memory = native_memory if isinstance(native_memory, Mapping) else None
    return {
        "row_label": row_label or Path(artifact_path).stem,
        "source_artifact": artifact_path,
        "input1": rtdl.get("input1"),
        "input2": rtdl.get("input2"),
        "point_count_a": int(rtdl.get("point_count_a", accounting.get("point_count_a", 0)) or 0),
        "point_count_b": int(rtdl.get("point_count_b", accounting.get("point_count_b", 0)) or 0),
        "route_label": rtdl.get("route_label", accounting.get("route_label")),
        "hd_result": payload.get("HDResult"),
        "author_mapped_fields": _field_summary(author_fields),
        "rtdl_only_fields": _field_summary(rtdl_only),
        "estimated_author_mapped_bytes_excluding_unavailable": accounting.get(
            "estimated_author_mapped_bytes_excluding_unavailable"
        ),
        "estimated_author_mapped_mb_excluding_unavailable": accounting.get(
            "estimated_author_mapped_mb_excluding_unavailable"
        ),
        "estimated_total_accounted_bytes_excluding_unavailable": accounting.get(
            "estimated_total_accounted_bytes_excluding_unavailable"
        ),
        "estimated_total_accounted_mb_excluding_unavailable": accounting.get(
            "estimated_total_accounted_mb_excluding_unavailable"
        ),
        "native_memory_telemetry_collected": native_memory is not None,
        "native_memory_telemetry_schema": None if native_memory is None else native_memory.get("schema"),
        "frontier_row_count": directed.get("frontier_row_count", accounting.get("frontier_row_count")),
        "frontier_attempted_count": directed.get("frontier_attempted_count"),
        "candidate_distance_evaluations": directed.get("candidate_distance_evaluations"),
        "same_denominator_author_figure11": False,
        "same_denominator_reason": (
            "RTDL status-bearing memory rows are derived from RTDL route metadata/native telemetry. "
            "They do not use the author Figure 11 allocator denominator, paper-exact inputs, "
            "author WL in/miss queue accounting, or author heavy-worklist peak accounting."
        ),
    }


def build_rtdl_memory_matrix(
    rows: Iterable[tuple[Path, str | None]],
    *,
    date: str,
) -> dict[str, Any]:
    matrix_rows = [
        _row_from_payload(payload=_load_json(path), artifact_path=str(path), row_label=label)
        for path, label in rows
    ]
    measured_bvh_rows = sum(
        1
        for row in matrix_rows
        if row["author_mapped_fields"]["BVH"]["status"] == "measured_native_optix_accel_output_buffer"
    )
    unavailable_heavy_rows = sum(
        1
        for row in matrix_rows
        if row["author_mapped_fields"]["WL Heavy Peak"]["bytes"] is None
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.rtdl_memory_matrix.v1",
        "goal": "Goal5276",
        "date": date,
        "status": "rtdl_bounded_memory_matrix_ready__figure11_not_reproduced",
        "row_count": len(matrix_rows),
        "rows": matrix_rows,
        "coverage": {
            "measured_bvh_rows": measured_bvh_rows,
            "wl_heavy_peak_unavailable_rows": unavailable_heavy_rows,
            "all_rows_same_denominator_author_figure11": False,
        },
        "claim_boundary": {
            "figure11_reproduced": False,
            "author_memory_parity_claimed": False,
            "exact_gpu_allocator_measurement_claimed": False,
            "performance_ratio_claimed": False,
            "same_denominator_author_figure11_claimed": False,
        },
        "semantics": (
            "RTDL-side status-bearing memory matrix for bounded/pilot artifacts. "
            "Measured BVH means RTDL native OptiX accel output bytes when available; "
            "estimated fields remain estimates, unavailable fields remain unavailable. "
            "No author Figure 11 ratio is authorized from this matrix."
        ),
    }


def _parse_row_arg(value: str) -> tuple[Path, str | None]:
    if "::" in value:
        path_text, label = value.split("::", 1)
        return Path(path_text), label or None
    return Path(value), None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an RTDL status-bearing memory matrix.")
    parser.add_argument("--input", action="append", required=True, help="JSON path, optionally PATH::row label")
    parser.add_argument("--date", default="2026-07-09")
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    matrix = build_rtdl_memory_matrix([_parse_row_arg(value) for value in args.input], date=args.date)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
