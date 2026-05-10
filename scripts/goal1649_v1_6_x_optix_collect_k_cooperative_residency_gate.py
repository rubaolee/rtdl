#!/usr/bin/env python3
"""Check whether full-level cooperative collect-k fusion can be resident.

This is a design gate, not performance evidence. It uses recorded capability
artifacts to reject cooperative-grid shapes that cannot fit the CUDA cooperative
launch residency requirement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPABILITY = ROOT / "docs/reports/goal1647_pod_a4500_cooperative_capability_2026-05-10.json"
DEFAULT_JSON = ROOT / "docs/reports/goal1649_v1_6_x_optix_collect_k_cooperative_residency_gate_2026-05-10.json"
DEFAULT_MD = ROOT / "docs/reports/goal1649_v1_6_x_optix_collect_k_cooperative_residency_gate_2026-05-10.md"


def build_gate(
    *,
    capability_path: Path,
    candidate_count: int,
    tile_size: int,
    threads_per_block: int,
    max_threads_per_sm: int,
    max_blocks_per_sm: int,
) -> dict[str, Any]:
    capability = json.loads(capability_path.read_text(encoding="utf-8"))
    cap = capability["capability"]
    sm_count = int(cap["multiprocessor_count"])
    max_resident_blocks = sm_count * max_blocks_per_sm
    max_resident_threads = sm_count * max_threads_per_sm

    levels: list[dict[str, Any]] = []
    current_segments = (candidate_count + tile_size - 1) // tile_size
    segment_capacity = tile_size
    level_index = 0
    while current_segments > 1:
        pair_count = current_segments // 2
        has_carry = (current_segments % 2) != 0
        output_capacity = segment_capacity * 2
        blocks_per_pair = (output_capacity + threads_per_block - 1) // threads_per_block
        required_blocks = pair_count * blocks_per_pair
        required_threads = required_blocks * threads_per_block
        levels.append(
            {
                "level": level_index,
                "input_segments": current_segments,
                "pair_count": pair_count,
                "has_carry": has_carry,
                "segment_capacity": segment_capacity,
                "output_capacity": output_capacity,
                "blocks_per_pair": blocks_per_pair,
                "required_blocks": required_blocks,
                "required_threads": required_threads,
                "fits_block_bound": required_blocks <= max_resident_blocks,
                "fits_thread_bound": required_threads <= max_resident_threads,
                "fits_conservative_residency_gate": (
                    required_blocks <= max_resident_blocks
                    and required_threads <= max_resident_threads
                ),
            }
        )
        current_segments = pair_count + (1 if has_carry else 0)
        segment_capacity = output_capacity
        level_index += 1

    accepted = all(level["fits_conservative_residency_gate"] for level in levels)
    return {
        "goal": "Goal1649",
        "status": "full_level_cooperative_fusion_rejected_by_residency_gate" if not accepted else "full_level_cooperative_fusion_residency_possible",
        "capability_artifact": str(capability_path),
        "gpu_summary": capability.get("nvidia_smi", "unknown"),
        "candidate_count": candidate_count,
        "tile_size": tile_size,
        "threads_per_block": threads_per_block,
        "multiprocessor_count": sm_count,
        "max_threads_per_sm_assumption": max_threads_per_sm,
        "max_blocks_per_sm_assumption": max_blocks_per_sm,
        "max_resident_blocks_bound": max_resident_blocks,
        "max_resident_threads_bound": max_resident_threads,
        "levels": levels,
        "full_level_cooperative_fusion_allowed": accepted,
        "performance_evidence_authorized": False,
        "public_speedup_wording_authorized": False,
        "stable_collect_k_promotion_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Goal1649 is a cooperative residency design gate only. It rejects "
            "or permits a candidate grid shape before implementation work. It "
            "is not performance evidence and does not authorize public speedup wording, "
            "stable COLLECT_K_BOUNDED promotion, release tags, or release action."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1649 v1.6.x OptiX Collect-K Cooperative Residency Gate",
        "",
        "## Verdict",
        "",
        f"`{payload['status']}`",
        "",
        "## Scope",
        "",
        f"- GPU summary: `{payload['gpu_summary']}`",
        f"- Capability artifact: `{payload['capability_artifact']}`",
        f"- Candidate count: `{payload['candidate_count']}`",
        f"- Tile size: `{payload['tile_size']}`",
        f"- Threads per block: `{payload['threads_per_block']}`",
        f"- Multiprocessor count: `{payload['multiprocessor_count']}`",
        f"- Conservative max resident blocks bound: `{payload['max_resident_blocks_bound']}`",
        f"- Conservative max resident threads bound: `{payload['max_resident_threads_bound']}`",
        "",
        "## Levels",
        "",
        "| Level | Input segments | Pair count | Output capacity | Blocks/pair | Required blocks | Required threads | Fits gate |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for level in payload["levels"]:
        lines.append(
            "| {level} | {input_segments} | {pair_count} | {output_capacity} | {blocks_per_pair} | "
            "{required_blocks} | {required_threads} | {fits_conservative_residency_gate} |".format(**level)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A full-level cooperative fusion of the existing row-parallel merge shape is rejected when any level requires more blocks or threads than can be resident together. The current A4500 long workload shape requires all level blocks to be globally resident for `grid.sync()`, so this gate prevents spending pod time on an impossible full-level cooperative launch shape.",
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1649 collect-k cooperative residency gate.")
    parser.add_argument("--capability", type=Path, default=DEFAULT_CAPABILITY)
    parser.add_argument("--candidate-count", type=int, default=262144)
    parser.add_argument("--tile-size", type=int, default=2048)
    parser.add_argument("--threads-per-block", type=int, default=256)
    parser.add_argument("--max-threads-per-sm", type=int, default=1536)
    parser.add_argument("--max-blocks-per-sm", type=int, default=16)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_gate(
        capability_path=args.capability,
        candidate_count=args.candidate_count,
        tile_size=args.tile_size,
        threads_per_block=args.threads_per_block,
        max_threads_per_sm=args.max_threads_per_sm,
        max_blocks_per_sm=args.max_blocks_per_sm,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "allowed": payload["full_level_cooperative_fusion_allowed"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
