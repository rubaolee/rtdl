#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1086 robot chunked Embree baseline intake"
DEFAULT_INPUT_DIR = "docs/reports/goal1085_robot_chunked_embree_baseline"
EXPECTED_CHUNKS = 180
EXPECTED_CHUNK_POSES = 200_000
EXPECTED_TOTAL_POSES = 36_000_000
EXPECTED_OBSTACLES = 4096


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _chunk_index(path: Path) -> int:
    stem = path.stem
    if not stem.startswith("chunk_"):
        raise ValueError(f"unexpected chunk filename {path.name}")
    return int(stem.removeprefix("chunk_"))


def build_intake(*, input_dir: str | Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    directory = ROOT / input_dir
    paths = sorted(directory.glob("chunk_*.json"), key=_chunk_index) if directory.exists() else []
    chunks = [_load(path) for path in paths]
    present_indices = [_chunk_index(path) for path in paths]
    expected_indices = set(range(EXPECTED_CHUNKS))
    missing_indices = sorted(expected_indices.difference(present_indices))
    unexpected_indices = sorted(set(present_indices).difference(expected_indices))
    ok_chunks = [
        chunk
        for chunk in chunks
        if chunk.get("status") == "ok"
        and chunk.get("correctness_parity") is True
        and chunk.get("source_backend") == "embree"
    ]
    scale_ok_chunks = [
        chunk
        for path, chunk in zip(paths, chunks, strict=True)
        if chunk.get("benchmark_scale", {}).get("pose_count") == EXPECTED_CHUNK_POSES
        and chunk.get("benchmark_scale", {}).get("obstacle_count") == EXPECTED_OBSTACLES
        and chunk.get("benchmark_scale", {}).get("pose_id_start")
        == _chunk_index(path) * EXPECTED_CHUNK_POSES + 1
    ]
    native_query_samples = [
        float(chunk["phase_seconds"]["native_anyhit_query"])
        for chunk in chunks
        if "phase_seconds" in chunk and "native_anyhit_query" in chunk["phase_seconds"]
    ]
    prepare_samples = [
        float(chunk["phase_seconds"]["backend_scene_prepare"])
        for chunk in chunks
        if "phase_seconds" in chunk and "backend_scene_prepare" in chunk["phase_seconds"]
    ]
    total_pose_count = sum(int(chunk.get("benchmark_scale", {}).get("pose_count", 0)) for chunk in chunks)
    complete = (
        len(chunks) == EXPECTED_CHUNKS
        and not missing_indices
        and not unexpected_indices
        and len(ok_chunks) == EXPECTED_CHUNKS
        and len(scale_ok_chunks) == EXPECTED_CHUNKS
        and total_pose_count == EXPECTED_TOTAL_POSES
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "input_dir": str(input_dir),
        "source_artifacts": [
            "docs/reports/goal1085_robot_chunked_embree_baseline_packet_2026-04-29.json",
            "scripts/goal1085_robot_chunked_embree_baseline_runner.sh",
        ],
        "expected": {
            "chunk_count": EXPECTED_CHUNKS,
            "chunk_pose_count": EXPECTED_CHUNK_POSES,
            "total_pose_count": EXPECTED_TOTAL_POSES,
            "obstacle_count": EXPECTED_OBSTACLES,
        },
        "observed": {
            "chunk_count": len(chunks),
            "ok_chunk_count": len(ok_chunks),
            "scale_ok_chunk_count": len(scale_ok_chunks),
            "total_pose_count": total_pose_count,
            "missing_indices": missing_indices,
            "unexpected_indices": unexpected_indices,
        },
        "phase_seconds": {
            "native_anyhit_sum_sec": sum(native_query_samples),
            "native_anyhit_median_chunk_sec": statistics.median(native_query_samples) if native_query_samples else 0.0,
            "backend_scene_prepare_sum_sec": sum(prepare_samples),
            "backend_scene_prepare_median_chunk_sec": statistics.median(prepare_samples) if prepare_samples else 0.0,
        },
        "status": "complete" if complete else "missing_or_invalid_chunks",
        "public_speedup_claim_authorized": False,
        "interpretation": (
            "This intake aggregates chunked same-total-work Embree evidence. Even when complete, it does not by itself "
            "authorize a speedup claim against the 36M single RTX timing artifact because the comparison boundary is "
            "same-total-work, not same-single-launch, and still requires 2+ AI review."
        ),
        "valid": True,
        "boundary": (
            "Goal1086 is an intake/aggregation tool for robot Embree chunk artifacts. It does not run the heavy baseline, "
            "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    observed = payload["observed"]
    phases = payload["phase_seconds"]
    lines = [
        "# Goal1086 Robot Chunked Embree Baseline Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Valid intake report: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Observed",
        "",
        f"- Chunk count: `{observed['chunk_count']}` / `{payload['expected']['chunk_count']}`",
        f"- OK chunks: `{observed['ok_chunk_count']}`",
        f"- Scale-OK chunks: `{observed['scale_ok_chunk_count']}`",
        f"- Total poses represented: `{observed['total_pose_count']}`",
        f"- Missing indices: `{observed['missing_indices'][:20]}`{' ...' if len(observed['missing_indices']) > 20 else ''}",
        "",
        "## Aggregated Phases",
        "",
        f"- Native any-hit sum: `{phases['native_anyhit_sum_sec']}` seconds",
        f"- Native any-hit median chunk: `{phases['native_anyhit_median_chunk_sec']}` seconds",
        f"- Backend scene-prepare sum: `{phases['backend_scene_prepare_sum_sec']}` seconds",
        f"- Backend scene-prepare median chunk: `{phases['backend_scene_prepare_median_chunk_sec']}` seconds",
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate Goal1085 robot chunked Embree baseline artifacts.")
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-json", default="docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.md")
    args = parser.parse_args(argv)
    payload = build_intake(input_dir=args.input_dir)
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "valid": payload["valid"], **payload["observed"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
