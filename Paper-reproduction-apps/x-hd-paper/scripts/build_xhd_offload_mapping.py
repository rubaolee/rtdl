#!/usr/bin/env python3
"""Build the Goal5282 X-HD author-shaped offload mapping artifact.

This script consumes native v2 telemetry produced by Goal5281 and maps the
generic offload row-count shape to author-shaped X-HD fields.  It deliberately
keeps same-denominator Figure 11 claims false unless the helper says otherwise.
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
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"could not parse JSON: {path}") from exc


def build_offload_mapping_artifact(*, native_artifact: Path, date: str) -> dict[str, Any]:
    payload = _load_json(native_artifact)
    native_memory = payload.get("native_memory_telemetry")
    if not isinstance(native_memory, Mapping):
        raise ValueError("expected native_memory_telemetry in Goal5281 artifact")
    mapping = xhd_memory_accounting.author_offload_mapping_from_native_telemetry(native_memory)
    checks = {
        "source_artifact_matched": bool(payload.get("matched", False)),
        "native_schema_v2": native_memory.get("schema")
        == "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v2",
        "offloading_size_shape_available": bool(
            mapping["denominator_alignment"]["offloading_size_row_count_shape_available"]
        ),
        "rtdl_uint64_bytes_consistent": bool(
            mapping["denominator_alignment"].get(
                "rtdl_queue_bytes_match_expected_uint64_pair_shape", False
            )
        ),
        "figure11_claims_remain_false": not bool(
            mapping["denominator_alignment"]["same_denominator_author_figure11"]
        ),
    }
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5282.author_offload_mapping.v1",
        "goal": "Goal5282",
        "date": date,
        "status": "xhd_bounded_offload_mapping_ready__figure11_same_denominator_not_met",
        "input_native_artifact": str(native_artifact),
        "native_route": payload.get("route"),
        "native_generic_symbol": payload.get("native_generic_symbol"),
        "native_frontier_kind_codes": payload.get("frontier_kind_codes"),
        "native_offload_row_count": payload.get("offload_row_count_from_rows"),
        "author_offload_mapping": mapping,
        "checks": checks,
        "matched": all(checks.values()),
        "decision": {
            "xhd_offloading_size_shape_mapped": True,
            "wl_heavy_peak_author_width_candidate_available": True,
            "same_denominator_author_figure11": False,
            "figure11_reproduced": False,
            "reason": (
                "Goal5281 v2 telemetry provides a generic offload row-count "
                "shape. Goal5282 can map that to author-shaped OffloadingSize "
                "and author-width WL Heavy Peak candidate bytes, but measured "
                "RTDL queue bytes are 64-bit pair bytes and WL is still not the "
                "author in_queue + miss_queue denominator."
            ),
        },
        "claim_boundary": {
            "figure11_reproduced": False,
            "author_memory_parity_claimed": False,
            "same_denominator_author_figure11_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build X-HD author-shaped offload mapping evidence.")
    parser.add_argument("--native-artifact", required=True)
    parser.add_argument("--date", default="2026-07-09")
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    artifact = build_offload_mapping_artifact(
        native_artifact=Path(args.native_artifact),
        date=args.date,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0 if artifact["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
