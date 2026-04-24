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
        recommended_status = "ready_for_review"
        blocker = "none"
        next_step = (
            "Run a bounded RTX road-hazard compact-output review against the same native segment/polygon foundation, "
            "without claiming whole-app speedup."
        )
    elif segment_status == "blocked_by_gate_failure":
        recommended_status = "blocked_by_segment_polygon_gate_failure"
        blocker = "segment_polygon_native_gate_failure"
        next_step = (
            "Resolve Goal807/864 segment/polygon parity or PostGIS failures before any road-hazard RT promotion work."
        )
    else:
        recommended_status = "needs_segment_polygon_real_optix_artifact"
        blocker = "segment_polygon_real_optix_artifact_missing"
        next_step = (
            "Collect the real OptiX/RTX segment-polygon gate artifact first; road hazard cannot be promoted ahead of its core hit-count primitive."
        )

    return {
        "goal": "Goal865 road hazard review packet",
        "date": "2026-04-23",
        "app": "road_hazard_screening",
        "source_segment_polygon_packet": str(DEFAULT_SEGMENT_PACKET),
        "segment_polygon_recommended_status": segment_status,
        "road_hazard_recommended_status": recommended_status,
        "blocker": blocker,
        "next_step": next_step,
        "allowed_claim_today": "no RTX road-hazard speedup claim today",
        "claim_scope_after_promotion": (
            "bounded compact road-hazard outputs only, and only after the segment/polygon native gate reaches review-ready status"
        ),
        "boundary": (
            "This packet does not promote road_hazard_screening into an active RTX claim set. "
            "It only makes the dependency on the segment/polygon native gate explicit."
        ),
    }


def to_markdown(packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Goal865 Road Hazard Review Packet",
            "",
            f"- app: `{packet['app']}`",
            f"- segment/polygon status: `{packet['segment_polygon_recommended_status']}`",
            f"- road-hazard status: `{packet['road_hazard_recommended_status']}`",
            f"- blocker: `{packet['blocker']}`",
            f"- allowed claim today: {packet['allowed_claim_today']}",
            "",
            "## Next Step",
            "",
            packet["next_step"],
            "",
            "## Boundary",
            "",
            packet["boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a review packet for road_hazard_screening from the segment/polygon review state.")
    parser.add_argument("--segment-packet-json", type=Path, default=DEFAULT_SEGMENT_PACKET)
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs" / "reports" / "goal865_road_hazard_review_packet_2026-04-23.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs" / "reports" / "goal865_road_hazard_review_packet_2026-04-23.md")
    args = parser.parse_args(argv)

    packet = build_packet(_load_json(args.segment_packet_json))
    packet["source_segment_polygon_packet"] = str(args.segment_packet_json)
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md), "road_hazard_recommended_status": packet["road_hazard_recommended_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
