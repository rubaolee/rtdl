#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEGMENT_PACKET = ROOT / "docs" / "reports" / "goal864_segment_polygon_gate_review_packet_2026-04-23.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_packet(segment_packet: dict[str, Any]) -> dict[str, Any]:
    segment_status = str(segment_packet["recommended_status"])
    if segment_status == "ready_for_review":
        compact_status = "ready_for_review"
        compact_blocker = "none"
        compact_next = (
            "Review compact segment_flags/segment_counts only, using the native hit-count foundation and keeping pair-row output excluded."
        )
    elif segment_status == "blocked_by_gate_failure":
        compact_status = "blocked_by_segment_polygon_gate_failure"
        compact_blocker = "segment_polygon_gate_failure"
        compact_next = (
            "Resolve the upstream Goal807/864 segment-polygon gate failure before compact anyhit promotion work."
        )
    else:
        compact_status = "needs_segment_polygon_real_optix_artifact"
        compact_blocker = "segment_polygon_real_optix_artifact_missing"
        compact_next = (
            "Collect the real OptiX/RTX segment-polygon gate artifact first; compact anyhit modes cannot outrun the underlying native hit-count primitive."
        )

    return {
        "goal": "Goal866 segment_polygon_anyhit_rows review packet",
        "date": "2026-04-23",
        "app": "segment_polygon_anyhit_rows",
        "source_segment_polygon_packet": str(DEFAULT_SEGMENT_PACKET),
        "source_segment_polygon_status": segment_status,
        "compact_modes": {
            "segment_flags": {
                "recommended_status": compact_status,
                "blocker": compact_blocker,
                "next_step": compact_next,
                "claim_scope_after_promotion": "compact any-hit flags only; not pair-row output",
            },
            "segment_counts": {
                "recommended_status": compact_status,
                "blocker": compact_blocker,
                "next_step": compact_next,
                "claim_scope_after_promotion": "compact any-hit counts only; not pair-row output",
            },
        },
        "rows_mode": {
            "recommended_status": "needs_native_pair_row_emitter",
            "blocker": "native_pair_row_emitter_missing",
            "next_step": "Implement a true native OptiX any-hit row emitter before any row-output RT claim review.",
            "allowed_claim_today": "no RTX pair-row speedup claim today",
        },
        "boundary": (
            "This packet does not promote segment_polygon_anyhit_rows into an active RTX claim set. "
            "Compact modes may only inherit native readiness through the segment-polygon hit-count gate; rows mode remains blocked by missing native pair-row output."
        ),
    }


def to_markdown(packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Goal866 Segment Polygon Anyhit Review Packet",
            "",
            f"- app: `{packet['app']}`",
            f"- source segment/polygon status: `{packet['source_segment_polygon_status']}`",
            "",
            "## Compact Modes",
            "",
            f"- `segment_flags`: `{packet['compact_modes']['segment_flags']['recommended_status']}`",
            f"- `segment_counts`: `{packet['compact_modes']['segment_counts']['recommended_status']}`",
            f"- blocker: `{packet['compact_modes']['segment_counts']['blocker']}`",
            "",
            "## Rows Mode",
            "",
            f"- `rows`: `{packet['rows_mode']['recommended_status']}`",
            f"- blocker: `{packet['rows_mode']['blocker']}`",
            f"- allowed claim today: {packet['rows_mode']['allowed_claim_today']}",
            "",
            "## Boundary",
            "",
            packet["boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a review packet for segment_polygon_anyhit_rows from the Goal864 segment/polygon state.")
    parser.add_argument("--segment-packet-json", type=Path, default=DEFAULT_SEGMENT_PACKET)
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs" / "reports" / "goal866_segment_polygon_anyhit_review_packet_2026-04-23.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs" / "reports" / "goal866_segment_polygon_anyhit_review_packet_2026-04-23.md")
    args = parser.parse_args(argv)

    packet = build_packet(_load_json(args.segment_packet_json))
    packet["source_segment_polygon_packet"] = str(args.segment_packet_json)
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md), "rows_status": packet["rows_mode"]["recommended_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
