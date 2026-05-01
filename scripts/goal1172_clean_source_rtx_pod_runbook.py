#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1172 clean-source RTX pod execution runbook"
DEFAULT_JSON = ROOT / "docs/reports/goal1172_clean_source_rtx_pod_runbook_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1172_clean_source_rtx_pod_runbook_2026-04-30.md"


def build_runbook() -> dict[str, Any]:
    steps = [
        {
            "name": "clone_clean_source",
            "purpose": "Start from a clean pushed commit, not a copied dirty local tree.",
            "commands": [
                "git clone https://github.com/rubaolee/rtdl.git rtdl_clean",
                "cd rtdl_clean",
                "git checkout <pushed_commit_for_goal1170>",
                "git status --short",
            ],
        },
        {
            "name": "install_linux_prerequisites",
            "purpose": "Install strict-reference and native-build dependencies before running gates.",
            "commands": [
                "apt-get update",
                "DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential git cmake pkg-config libgeos-dev python3-dev python3-pip cuda-nvrtc-dev-13-0 cuda-cudart-dev-13-0",
            ],
        },
        {
            "name": "prepare_optix_headers",
            "purpose": "Point the build at OptiX headers compatible with the pod driver/CUDA setup.",
            "commands": [
                "mkdir -p /root/vendor",
                "git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-dev.git /root/vendor/optix-dev",
                "export OPTIX_PREFIX=/root/vendor/optix-dev",
                "export CUDA_PREFIX=/usr/local/cuda",
                "export NVCC=/usr/local/cuda/bin/nvcc",
                "export RTDL_OPTIX_PTX_COMPILER=nvcc",
            ],
        },
        {
            "name": "build_native_optix",
            "purpose": "Build the native OptiX backend once before preflight and app rows.",
            "commands": [
                "make build-optix OPTIX_PREFIX=$OPTIX_PREFIX CUDA_PREFIX=$CUDA_PREFIX NVCC=$NVCC 2>&1 | tee docs/reports/goal1170_clean_source_rtx_claim_grade_batch/make_build_optix.log",
            ],
        },
        {
            "name": "preflight",
            "purpose": "Fail fast before any benchmark if source or environment is not claim-grade ready.",
            "commands": [
                "PYTHONPATH=src:. python3 scripts/goal1171_clean_source_rtx_pod_preflight.py --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1171_preflight.json --output-md docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1171_preflight.md",
            ],
        },
        {
            "name": "run_goal1170_batch",
            "purpose": "Run all eight RTX rows in one pod session.",
            "commands": [
                "PYTHONPATH=src:. bash scripts/goal1170_clean_source_rtx_batch_runner.sh 2>&1 | tee docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1170_runner.log",
            ],
        },
        {
            "name": "package_copyback",
            "purpose": "Copy back all logs and JSON artifacts before stopping the pod.",
            "commands": [
                "tar -czf /tmp/goal1170_clean_source_rtx_claim_grade_batch.tgz docs/reports/goal1170_clean_source_rtx_claim_grade_batch",
                "sha256sum /tmp/goal1170_clean_source_rtx_claim_grade_batch.tgz > /tmp/goal1170_clean_source_rtx_claim_grade_batch.tgz.sha256",
            ],
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "steps": steps,
        "valid": True,
        "boundary": (
            "This runbook prepares a future clean-source pod session. It does not run cloud, "
            "does not authorize public wording, and must not be used with a copied dirty tree."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1172 Clean-Source RTX Pod Runbook",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Steps",
        "",
    ]
    for idx, step in enumerate(payload["steps"], start=1):
        lines.extend(
            [
                f"### {idx}. {step['name']}",
                "",
                step["purpose"],
                "",
                "```bash",
                *step["commands"],
                "```",
                "",
            ]
        )
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Goal1172 clean-source RTX pod runbook.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = build_runbook()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "step_count": len(payload["steps"])}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
