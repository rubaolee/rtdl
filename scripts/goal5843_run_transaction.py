#!/usr/bin/env python3
"""Execute one no-retry Goal5843 formal transaction."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from experiments.goal5843_post_r1_baseline.runtime import create_json, create_text


ROOT = Path(__file__).resolve().parents[1]


def completed_stage_rows(stage_root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted(stage_root.iterdir()):
        observation_path = path / "observation.json"
        if not observation_path.is_file():
            continue
        observation = json.loads(observation_path.read_text(encoding="utf-8"))
        rows.append(
            {
                "stage": observation["stage"],
                "returncode": observation["returncode"],
                "retry_permitted": observation["retry_permitted"],
            }
        )
    return rows


def write_transaction_status(
    output_root: Path,
    stage_root: Path,
    *,
    status: str,
    failure_stage: str | None,
) -> dict[str, object]:
    stage_rows = completed_stage_rows(stage_root)
    value: dict[str, object] = {
        "schema": "rtdl.goal5843.transaction_status.v1",
        "status": status,
        "stage_count": len(stage_rows),
        "stages": stage_rows,
        "worker_zero_reached": (output_root / "baseline/WORKER_ZERO.json").is_file(),
        "post_worker_zero_retry_used": False,
        "post_worker_zero_retry_permitted": False,
        "all_adverse_rows_retained": failure_stage is None,
        "failure_stage": failure_stage,
    }
    create_json(output_root / "TRANSACTION_STATUS.json", value)
    return value


def run_stage(
    *, name: str, command: list[str], stage_root: Path, environment: dict[str, str]
) -> None:
    directory = stage_root / name
    directory.mkdir(parents=False, exist_ok=False)
    create_json(
        directory / "command.json",
        {"schema": "rtdl.goal5843.transaction_stage_command.v1", "argv": command},
    )
    started = time.perf_counter_ns()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    wall_ns = time.perf_counter_ns() - started
    create_text(directory / "stdout.txt", completed.stdout)
    create_text(directory / "stderr.txt", completed.stderr)
    create_json(
        directory / "observation.json",
        {
            "schema": "rtdl.goal5843.transaction_stage_observation.v1",
            "stage": name,
            "returncode": completed.returncode,
            "process_wall_ns": wall_ns,
            "retry_permitted": False,
        },
    )
    if completed.returncode != 0:
        write_transaction_status(
            stage_root.parent,
            stage_root,
            status="FAIL__FORMAL_TRANSACTION_TERMINATED_WITHOUT_RETRY",
            failure_stage=name,
        )
        raise RuntimeError(f"Goal5843 stage failed without retry: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--owner-authorized", action="store_true")
    args = parser.parse_args()
    if not args.owner_authorized:
        raise RuntimeError("explicit --owner-authorized flag required")
    output_root = args.output_root.absolute()
    output_root.mkdir(parents=True, exist_ok=False)
    stage_root = output_root / "stages"
    stage_root.mkdir()
    cache_root = output_root / "formal_leaf_cache"
    cache_manifest = output_root / "FORMAL_LEAF_CACHE_MANIFEST.json"
    cache_preparation = output_root / "CACHE_PREPARATION.json"
    oracle_witness = output_root / "INDEPENDENT_ORACLE_WITNESS.json"
    authority = output_root / "EXECUTION_AUTHORITY.json"
    bound_artifacts = output_root / "bound_artifacts"
    bound_artifacts_receipt = output_root / "BOUND_ARTIFACTS.json"
    baseline_root = output_root / "baseline"
    recount = output_root / "POD_RECOUNT.json"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "src"), str(ROOT), environment.get("PYTHONPATH", ""))
    )
    for name in (
        "RTDL_V4_FORMAL_LEAF_CACHE",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
    ):
        environment.pop(name, None)
    common = [args.python]
    run_stage(
        name="00_prepare_formal_leaf_cache",
        stage_root=stage_root,
        environment=environment,
        command=common
        + [
            "scripts/goal5843_prepare_formal_leaf_cache.py",
            "--preregistration",
            str(args.preregistration.resolve()),
            "--native",
            str(args.native.resolve()),
            "--optix-include",
            str(args.optix_include.resolve()),
            "--cuda-include",
            str(args.cuda_include.resolve()),
            "--optix-sdk",
            args.optix_sdk,
            "--cache-root",
            str(cache_root),
            "--manifest",
            str(cache_manifest),
            "--output",
            str(cache_preparation),
        ],
    )
    run_stage(
        name="01_build_independent_oracle_witness",
        stage_root=stage_root,
        environment=environment,
        command=common
        + [
            "scripts/goal5843_build_independent_oracle_witness.py",
            "--preregistration",
            str(args.preregistration.resolve()),
            "--output",
            str(oracle_witness),
        ],
    )
    run_stage(
        name="02_bind_execution_authority",
        stage_root=stage_root,
        environment=environment,
        command=common
        + [
            "scripts/goal5843_bind_execution_authority.py",
            "--preregistration",
            str(args.preregistration.resolve()),
            "--native",
            str(args.native.resolve()),
            "--native-build-manifest",
            str(args.native_build_manifest.resolve()),
            "--direct-binary",
            str(args.direct_binary.resolve()),
            "--device-source",
            str(args.device_source.resolve()),
            "--optix-include",
            str(args.optix_include.resolve()),
            "--cuda-include",
            str(args.cuda_include.resolve()),
            "--optix-sdk",
            args.optix_sdk,
            "--cache-root",
            str(cache_root),
            "--cache-manifest",
            str(cache_manifest),
            "--cache-preparation",
            str(cache_preparation),
            "--oracle-witness",
            str(oracle_witness),
            "--pyoptix-distribution",
            args.pyoptix_distribution,
            "--output",
            str(authority),
            "--owner-authorized",
        ],
    )
    run_stage(
        name="03_preserve_bound_artifacts",
        stage_root=stage_root,
        environment=environment,
        command=common
        + [
            "scripts/goal5843_preserve_bound_artifacts.py",
            "--preregistration",
            str(args.preregistration.resolve()),
            "--execution-authority",
            str(authority),
            "--destination-root",
            str(bound_artifacts),
            "--output",
            str(bound_artifacts_receipt),
        ],
    )
    run_stage(
        name="04_formal_worker_zero_and_baseline",
        stage_root=stage_root,
        environment=environment,
        command=common
        + [
            "-m",
            "experiments.goal5843_post_r1_baseline.controller",
            "--preregistration",
            str(args.preregistration.resolve()),
            "--execution-authority",
            str(authority),
            "--output-root",
            str(baseline_root),
            "--python",
            args.python,
            "--native",
            str(args.native.resolve()),
            "--direct-binary",
            str(args.direct_binary.resolve()),
            "--device-source",
            str(args.device_source.resolve()),
            "--optix-include",
            str(args.optix_include.resolve()),
            "--cuda-include",
            str(args.cuda_include.resolve()),
            "--optix-sdk",
            args.optix_sdk,
        ],
    )
    run_stage(
        name="05_independent_pod_recount",
        stage_root=stage_root,
        environment=environment,
        command=common
        + [
            "scripts/goal5843_independent_recount.py",
            "--preregistration",
            str(args.preregistration.resolve()),
            "--execution-authority",
            str(authority),
            "--baseline-root",
            str(baseline_root),
            "--output",
            str(recount),
        ],
    )
    status = write_transaction_status(
        output_root,
        stage_root,
        status="PASS__FORMAL_TRANSACTION_AND_POD_RECOUNT_COMPLETE",
        failure_stage=None,
    )
    print(json.dumps(status, sort_keys=True))


if __name__ == "__main__":
    main()
