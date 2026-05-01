#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1192 public wording evidence batch packet"
RUNNER = ROOT / "scripts/goal1192_public_wording_evidence_batch_runner.sh"
DEFAULT_JSON = ROOT / "docs/reports/goal1192_public_wording_evidence_batch_packet_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1192_public_wording_evidence_batch_packet_2026-04-30.md"

EXPECTED_OUTPUTS: tuple[str, ...] = (
    "database_compact_summary_embree.json",
    "database_compact_summary_optix.json",
    "graph_visibility_edges_embree.json",
    "graph_visibility_edges_optix.json",
    "road_hazard_native_summary_embree.json",
    "road_hazard_native_summary_optix.json",
    "polygon_pair_candidate_discovery_embree.json",
    "polygon_pair_candidate_discovery_optix.json",
    "polygon_jaccard_safe_chunk_embree.json",
    "polygon_jaccard_safe_chunk_optix.json",
    "hausdorff_threshold_prepared_embree.json",
    "hausdorff_threshold_prepared_optix.json",
)

EXPECTED_APPS: tuple[str, ...] = (
    "database_analytics",
    "graph_analytics",
    "road_hazard_screening",
    "polygon_pair_overlap_area_rows",
    "polygon_set_jaccard",
    "hausdorff_distance",
)


def build_packet() -> dict[str, Any]:
    runner_exists = RUNNER.exists()
    runner_text = RUNNER.read_text(encoding="utf-8") if runner_exists else ""
    missing_outputs = [name for name in EXPECTED_OUTPUTS if name not in runner_text]
    missing_apps = [app for app in EXPECTED_APPS if app not in runner_text]
    blockers = []
    if not runner_exists:
        blockers.append("runner missing")
    if missing_outputs:
        blockers.append(f"runner missing expected outputs: {', '.join(missing_outputs)}")
    if missing_apps:
        blockers.append(f"runner missing expected app names: {', '.join(missing_apps)}")
    if "does not authorize public" not in runner_text:
        blockers.append("runner missing no-public-wording boundary")
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not blockers,
        "runner": str(RUNNER.relative_to(ROOT)),
        "expected_app_count": len(EXPECTED_APPS),
        "expected_output_count": len(EXPECTED_OUTPUTS),
        "expected_apps": list(EXPECTED_APPS),
        "expected_outputs": list(EXPECTED_OUTPUTS),
        "blockers": blockers,
        "pod_preconditions": [
            "RTX-class Linux pod with NVIDIA driver visible through nvidia-smi.",
            "OptiX backend built successfully with make build-optix before invoking the runner.",
            "GEOS/pkg-config installed before Embree/geometry baselines.",
            "Run the full batch once, copy back the tgz and sha256, then run a local intake script.",
        ],
        "run_command": "OUTDIR=docs/reports/goal1192_public_wording_evidence_batch bash scripts/goal1192_public_wording_evidence_batch_runner.sh",
        "boundary": (
            "This packet defines a future six-row evidence batch only. It does not run cloud, "
            "does not authorize release, and does not authorize public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1192 Public Wording Evidence Batch Packet",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        "",
        "## Runner",
        "",
        f"- runner: `{payload['runner']}`",
        f"- expected apps: `{payload['expected_app_count']}`",
        f"- expected outputs: `{payload['expected_output_count']}`",
        "",
        "## Pod Preconditions",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["pod_preconditions"])
    lines.extend(["", "## Run Command", "", f"```bash\n{payload['run_command']}\n```", "", "## Expected Outputs", ""])
    lines.extend(f"- `{name}`" for name in payload["expected_outputs"])
    if payload["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {blocker}" for blocker in payload["blockers"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Goal1192 public wording evidence batch packet.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    payload = build_packet()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "json": str(args.output_json), "md": str(args.output_md)}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
