#!/usr/bin/env python3
"""Execute one create-only Goal5842 GPU-generation transaction."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validated_python_entrypoint(value: str) -> str:
    """Keep the selected venv launcher instead of resolving its base-Python link."""

    entrypoint = Path(os.path.abspath(value))
    if not entrypoint.is_file() or not os.access(entrypoint, os.X_OK):
        raise RuntimeError(f"Python entrypoint is not executable: {entrypoint}")
    return str(entrypoint)


def create_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(value)


def run_stage(
    name: str,
    command: list[str],
    output_root: Path,
    *,
    worker_zero_reached: bool,
) -> None:
    stage = output_root / "stage_logs" / name
    stage.mkdir(parents=True, exist_ok=False)
    create_text(
        stage / "command.json",
        json.dumps({"argv": command}, indent=2, sort_keys=True) + "\n",
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "src"), str(ROOT), environment.get("PYTHONPATH", ""))
    )
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    create_text(stage / "stdout.txt", completed.stdout)
    create_text(stage / "stderr.txt", completed.stderr)
    create_text(stage / "returncode.txt", f"{completed.returncode}\n")
    if completed.returncode != 0:
        marker = (
            "TRANSACTION_FAILED_NO_RETRY.json"
            if worker_zero_reached
            else "PREFLIGHT_FAILED_REPAIR_ALLOWED.json"
        )
        create_text(
            output_root / marker,
            json.dumps(
                {
                    "failed_stage": name,
                    "returncode": completed.returncode,
                    "worker_zero_reached": worker_zero_reached,
                    "new_transaction_after_repair_permitted": not worker_zero_reached,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        raise RuntimeError(f"Goal5842 transaction stage failed: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--owner-authorized", action="store_true")
    args = parser.parse_args()
    if not args.owner_authorized:
        raise RuntimeError("explicit --owner-authorized is required")
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    python = validated_python_entrypoint(sys.executable)
    prereg = str(args.preregistration.resolve(strict=True))
    native = str(args.native.resolve(strict=True))
    build_manifest = str(args.native_build_manifest.resolve(strict=True))
    direct_binary = str(args.direct_binary.resolve(strict=True))
    device_source = str(args.device_source.resolve(strict=True))
    optix_include = str(args.optix_include.resolve(strict=True))
    cuda_include = str(args.cuda_include.resolve(strict=True))
    authority = output_root / "execution_authority.json"
    witness = output_root / "gpu_identity_witness.json"
    causal_root = output_root / "causal"
    baseline_root = output_root / "baseline"
    recount = output_root / "independent_recount.json"

    common = [
        "--preregistration",
        prereg,
        "--native",
        native,
        "--optix-include",
        optix_include,
        "--cuda-include",
        cuda_include,
        "--optix-sdk",
        args.optix_sdk,
    ]
    run_stage(
        "00_bind_execution_authority",
        [
            python,
            str(ROOT / "scripts/goal5842_bind_execution_authority.py"),
            "--preregistration",
            prereg,
            "--native",
            native,
            "--native-build-manifest",
            build_manifest,
            "--direct-binary",
            direct_binary,
            "--device-source",
            device_source,
            "--optix-include",
            optix_include,
            "--cuda-include",
            cuda_include,
            "--optix-sdk",
            args.optix_sdk,
            "--pyoptix-distribution",
            args.pyoptix_distribution,
            "--output",
            str(authority),
            "--owner-authorized",
        ],
        output_root,
        worker_zero_reached=False,
    )
    authority_value = json.loads(authority.read_text(encoding="utf-8"))
    compute_capability = authority_value["hardware"]["compute_capability"]
    run_stage(
        "01_gpu_identity_witness_no_timing",
        [
            python,
            str(ROOT / "scripts/goal5842_gpu_identity_witness.py"),
            *common,
            "--execution-authority",
            str(authority),
            "--compute-capability",
            compute_capability,
            "--output",
            str(witness),
        ],
        output_root,
        worker_zero_reached=False,
    )
    run_stage(
        "02_causal_admission",
        [
            python,
            "-m",
            "experiments.goal5842_causal_admission.controller",
            "--preregistration",
            prereg,
            "--execution-authority",
            str(authority),
            "--output-root",
            str(causal_root),
            "--python",
            python,
        ],
        output_root,
        worker_zero_reached=True,
    )
    run_stage(
        "03_three_arm_baseline",
        [
            python,
            "-m",
            "experiments.goal5842_causal_admission.baseline_controller",
            *common,
            "--execution-authority",
            str(authority),
            "--output-root",
            str(baseline_root),
            "--python",
            python,
            "--direct-binary",
            direct_binary,
            "--device-source",
            device_source,
        ],
        output_root,
        worker_zero_reached=True,
    )
    run_stage(
        "04_independent_recount",
        [
            python,
            str(ROOT / "scripts/goal5842_independent_recount.py"),
            "--preregistration",
            prereg,
            "--execution-authority",
            str(authority),
            "--identity-witness",
            str(witness),
            "--causal-root",
            str(causal_root),
            "--baseline-root",
            str(baseline_root),
            "--output",
            str(recount),
        ],
        output_root,
        worker_zero_reached=True,
    )
    recount_value = json.loads(recount.read_text(encoding="utf-8"))
    create_text(
        output_root / "TRANSACTION_COMPLETE.json",
        json.dumps(
            {
                "status": "PASS__ONE_GPU_GENERATION_TRANSACTION_COMPLETE",
                "recount_sha256": recount_value["recount_sha256"],
                "architecture_generation": recount_value["architecture_generation"],
                "cross_generation_gate_passed": False,
                "public_performance_claim_authorized": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    print(json.dumps(recount_value, sort_keys=True))


if __name__ == "__main__":
    main()
