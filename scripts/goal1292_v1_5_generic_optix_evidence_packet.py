#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-05"
GOAL = "Goal1292 v1.5 generic OptiX evidence packet"
DEFAULT_JSON = ROOT / "docs/reports/goal1292_v1_5_generic_optix_evidence_packet_2026-05-05.json"
DEFAULT_MD = ROOT / "docs/reports/goal1292_v1_5_generic_optix_evidence_packet_2026-05-05.md"
RESULT_DIR = "docs/reports/goal1292_v1_5_generic_optix_pod_results"


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def build_packet() -> dict[str, Any]:
    primitive_output = f"{RESULT_DIR}/generic_optix_evidence.json"
    graph_output = f"{RESULT_DIR}/graph_visibility_optix_repeats.json"
    env_output = f"{RESULT_DIR}/rtdl_pod_env.json"
    return {
        "goal": GOAL,
        "date": DATE,
        "source_commit": _git_head(),
        "active_backends": ["embree", "optix"],
        "frozen_backends_before_v2_1": ["vulkan", "hiprt", "apple_rt"],
        "result_dir": RESULT_DIR,
        "env_probe": {
            "script": "scripts/rtdl_pod_env_probe.sh",
            "output_json": env_output,
            "required_fields": [
                "os_id",
                "package_manager",
                "cuda_prefix",
                "nvcc",
                "nvcc_exists",
                "optix_prefix",
                "optix_header_exists",
                "nvidia_smi_tail",
            ],
        },
        "commands": {
            "prepare": [
                f"mkdir -p {RESULT_DIR}",
                f"OUTPUT_JSON={env_output} OUTPUT_ENV={RESULT_DIR}/rtdl_pod_env.sh bash scripts/rtdl_pod_env_probe.sh",
                f". {RESULT_DIR}/rtdl_pod_env.sh",
                "make build-optix",
            ],
            "primitive_runner": (
                "PYTHONPATH=src:. python3 scripts/goal1292_v1_5_generic_optix_evidence_runner.py "
                f"--copies 10000 --query-repeats 100 --output {primitive_output}"
            ),
            "graph_wrapper": (
                "PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py "
                "--backend optix --scenario visibility_edges --output-mode summary "
                f"--copies 30000 --visibility-query-repeats 100 > {graph_output}"
            ),
            "local_sanity": (
                "PYTHONPATH=src:. python3 -m unittest "
                "tests.goal1288_v1_5_generic_anyhit_count_test "
                "tests.goal1290_v1_5_generic_prepared_anyhit_count_test "
                "tests.goal1291_v1_5_embree_prepared_parity_status_test"
            ),
        },
        "required_artifacts": [
            env_output,
            primitive_output,
            graph_output,
            f"{RESULT_DIR}/rtdl_pod_env.sh",
        ],
        "success_criteria": [
            "Environment probe is preserved before any failure interpretation.",
            "Primitive runner records CPU oracle rows and OptiX direct ANY_HIT plus COUNT_HITS parity.",
            "Prepared OptiX COUNT_HITS hit_count matches CPU oracle hit_count.",
            "Graph wrapper artifact preserves visibility_query_repeats=100 and run_phases query mean/min/first timings.",
            "If OptiX remains slower than Embree, classify as optix_still_slower_with_reason only when correctness and bottleneck evidence are present.",
        ],
        "known_gap": (
            "Embree prepared-scene parity for generic prepared ANY_HIT plus COUNT_HITS is not implemented yet; "
            "Goal1291 records it as blocked pending a scene/probe split or reviewed fallback."
        ),
        "boundary": (
            "This is an internal v1.5 NVIDIA evidence packet. It does not authorize public release wording, "
            "whole-app speedup claims, or new Vulkan/HIPRT/Apple RT implementation before v2.1."
        ),
        "public_wording_authorized": False,
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1292 v1.5 Generic OptiX Evidence Packet",
        "",
        f"Date: {payload['date']}",
        f"Source commit: `{payload['source_commit']}`",
        f"Result dir: `{payload['result_dir']}`",
        "",
        "## Scope",
        "",
        f"- Active backends: `{', '.join(payload['active_backends'])}`",
        f"- Frozen before v2.1: `{', '.join(payload['frozen_backends_before_v2_1'])}`",
        f"- Public wording authorized: `{payload['public_wording_authorized']}`",
        "",
        "## Pod Commands",
        "",
    ]
    for command in payload["commands"]["prepare"]:
        lines.append(f"```bash\n{command}\n```")
    lines.extend(
        [
            "```bash\n" + payload["commands"]["local_sanity"] + "\n```",
            "```bash\n" + payload["commands"]["primitive_runner"] + "\n```",
            "```bash\n" + payload["commands"]["graph_wrapper"] + "\n```",
            "",
            "## Required Artifacts",
            "",
        ]
    )
    lines.extend(f"- `{artifact}`" for artifact in payload["required_artifacts"])
    lines.extend(["", "## Success Criteria", ""])
    lines.extend(f"- {criterion}" for criterion in payload["success_criteria"])
    lines.extend(["", "## Known Gap", "", payload["known_gap"], "", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write Goal1292 v1.5 generic OptiX evidence packet.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)

    payload = build_packet()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
