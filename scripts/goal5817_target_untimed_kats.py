#!/usr/bin/env python3
"""Run all six untimed Goal5817 arm/task KATs before formal worker zero."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from experiments.goal5802_premeasurement.workload import RELATION_TASK, TRIANGLE_TASK
from experiments.goal5805_successor.protocol import validate_target_manifest
from experiments.goal5817_three_arm.formal_python_worker import _adapter
from experiments.goal5817_three_arm.protocol import (
    digest, file_record, validate_freeze,
)


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Goal5817 JSON root differs: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.write_bytes(
        json.dumps(value, indent=2, allow_nan=False, sort_keys=True).encode("utf-8")
        + b"\n")


def _run_python_kat(
        arm: str, task: str, target_path: Path, output_path: Path) -> None:
    """Run one arm/task in its own process, matching formal isolation."""

    target = _read(target_path.resolve(strict=True))
    validate_target_manifest(target, rehash=True)
    adapter = _adapter(arm, task, target)
    adapter.load()
    adapter.prepare()
    execute = adapter.measurement_execution_callable()
    receipts = []
    result = None
    for _ in range(2):
        result = execute()
        receipts.append(adapter.measurement_lifecycle_receipt(result))
    if result is None:
        raise RuntimeError("Goal5817 Python KAT produced no result")
    evidence = adapter.finalize_measurement_evidence(result)
    adapter.close()
    _write(output_path, {
        "schema": "rtdl.goal5817.python_untimed_kat.v1",
        "status": "PASS__UNTIMED_EXACT__ZERO_FORMAL_TIMINGS",
        "arm": arm,
        "task": task,
        "execution_count": 2,
        "lifecycle_receipts": receipts,
        "final_evidence": evidence,
        "clock_read_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--freeze", type=Path)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--child-python-arm", choices=("PYOPTIX", "RTDL"))
    parser.add_argument("--child-python-task", choices=("relation", "triangle"))
    parser.add_argument("--child-output", type=Path)
    args = parser.parse_args()
    if args.child_python_arm is not None:
        if args.child_python_task is None or args.child_output is None:
            raise RuntimeError("Goal5817 Python KAT child arguments are incomplete")
        _run_python_kat(
            args.child_python_arm, args.child_python_task,
            args.target_manifest, args.child_output)
        print(json.dumps({
            "arm": args.child_python_arm,
            "task": args.child_python_task,
            "status": "PASS__UNTIMED_EXACT__ZERO_FORMAL_TIMINGS",
        }, sort_keys=True))
        return 0
    if args.root is None or args.freeze is None or args.direct_binary is None \
            or args.output_directory is None:
        raise RuntimeError("Goal5817 parent KAT arguments are incomplete")
    root = args.root.resolve(strict=True)
    freeze_path = args.freeze.resolve(strict=True)
    target_path = args.target_manifest.resolve(strict=True)
    direct_binary = args.direct_binary.resolve(strict=True)
    output = args.output_directory.absolute()
    if output.exists():
        raise RuntimeError("Goal5817 untimed KAT output already exists")
    freeze = _read(freeze_path)
    target = _read(target_path)
    validate_freeze(freeze, rehash=True, root=root)
    validate_target_manifest(target, rehash=True)
    output.mkdir(parents=True)
    rows = []
    for arm in ("PYOPTIX", "RTDL"):
        for task in ("relation", "triangle"):
            path = output / f"{arm.lower()}_{task}.json"
            command = [
                sys.executable, str(Path(__file__).resolve()),
                "--target-manifest", str(target_path),
                "--child-python-arm", arm,
                "--child-python-task", task,
                "--child-output", str(path),
            ]
            child_environment = dict(os.environ)
            child_environment["PYTHONPATH"] = os.pathsep.join((
                str(root), str((root / "src").resolve(strict=True))))
            completed = subprocess.run(
                command, cwd=root, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=False,
                env=child_environment)
            (output / f"{arm.lower()}_{task}.stdout.bin").write_bytes(
                completed.stdout)
            (output / f"{arm.lower()}_{task}.stderr.bin").write_bytes(
                completed.stderr)
            if completed.returncode != 0 or not path.is_file():
                raise RuntimeError(
                    f"Goal5817 isolated Python KAT failed: {arm}/{task}")
            value = _read(path)
            if value.get("status") \
                    != "PASS__UNTIMED_EXACT__ZERO_FORMAL_TIMINGS" \
                    or value.get("arm") != arm or value.get("task") != task \
                    or value.get("clock_read_count") != 0 \
                    or value.get("formal_worker_count") != 0 \
                    or value.get("registered_performance_timing_count") != 0:
                raise RuntimeError(
                    f"Goal5817 isolated Python KAT receipt differs: {arm}/{task}")
            rows.append({"arm": arm, "task": task, "file": file_record(path)})

    files = target["files"]
    for task in ("relation", "triangle"):
        task_id = RELATION_TASK if task == "relation" else TRIANGLE_TASK
        command = [
            str(direct_binary), "--local-untimed-functional",
            "--task", task_id,
            "--ptx", str(files["matched_ptx"]["path"]),
        ]
        if task == "relation":
            command.extend([
                "--compaction-cubin",
                str(files["relation_compaction_cubin"]["path"]),
            ])
        completed = subprocess.run(
            command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False)
        (output / f"direct_{task}.stderr.bin").write_bytes(completed.stderr)
        if completed.returncode != 0:
            raise RuntimeError(f"Goal5817 Direct untimed KAT failed: {task}")
        value = json.loads(completed.stdout)
        if value.get("status") != "PASS" \
                or value.get("correctness", {}).get("oracle_exact") is not True \
                or value.get("registered_performance_timing_count") != 0:
            raise RuntimeError(f"Goal5817 Direct untimed KAT differs: {task}")
        path = output / f"direct_{task}.json"
        _write(path, value)
        rows.append({"arm": "DIRECT", "task": task, "file": file_record(path)})

    manifest = {
        "schema": "rtdl.goal5817.target_untimed_kat_manifest.v1",
        "status": "PASS__ALL_SIX_ARM_TASK_KATS__FORMAL_WORKER_ZERO",
        "freeze_file": file_record(freeze_path),
        "target_manifest_file": file_record(target_path),
        "direct_binary_file": file_record(direct_binary),
        "controlled_python_import_roots": [
            str(root), str((root / "src").resolve(strict=True)),
        ],
        "rows": rows,
        "clock_read_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    manifest["kat_manifest_sha256"] = digest(manifest)
    manifest_path = output / "kat_manifest.json"
    _write(manifest_path, manifest)
    print(json.dumps({
        "status": manifest["status"],
        "kat_manifest_file": file_record(manifest_path),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
