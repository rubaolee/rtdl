"""Untimed, zero-worker target/project-closure preflight for Goal5814."""

from __future__ import annotations

import argparse
from pathlib import Path

from .measurement_protocol import (
    canonical_document,
    file_record,
    owner_directive_receipt_path,
    validate_authority_window,
    validate_execution_request,
    validate_live_target,
    validate_owner_directive_receipt,
    validate_preaction,
    validate_project_closure,
    validate_target_manifest,
)


def run_preflight(
        *, root: Path, preaction_path: Path, target_manifest_path: Path,
        execution_request_path: Path, project_closure_path: Path,
        output_path: Path) -> dict[str, object]:
    output = Path(output_path).absolute()
    if output.exists():
        raise RuntimeError("Goal5814 preflight output already exists")
    root = Path(root).resolve(strict=True)
    preaction = Path(preaction_path).resolve(strict=True)
    target_path = Path(target_manifest_path).resolve(strict=True)
    request_path = Path(execution_request_path).resolve(strict=True)
    closure_path = Path(project_closure_path).resolve(strict=True)
    owner_receipt_path = owner_directive_receipt_path(root=root)
    validate_preaction(preaction)
    validate_owner_directive_receipt(owner_receipt_path, root=root)
    target = validate_target_manifest(
        target_path, root=root, rehash=True, rehash_wheels=True)
    execution_request = validate_execution_request(
        request_path, preaction_path=preaction,
        target_manifest_path=target_path, target_manifest=target,
        owner_receipt_path=owner_receipt_path)
    project_closure = validate_project_closure(
        closure_path, preaction_path=preaction,
        target_manifest_path=target_path,
        execution_request_path=request_path,
        target_manifest=target, execution_request=execution_request,
        owner_receipt_path=owner_receipt_path)
    validate_authority_window(project_closure)
    control_paths = {
        "owner_directive_receipt": owner_receipt_path,
        "preaction": preaction,
        "target_manifest": target_path,
        "execution_request": request_path,
        "project_closure": closure_path,
    }
    control_records = {
        name: file_record(path) for name, path in control_paths.items()}
    observation = validate_live_target(target)
    if {name: file_record(path) for name, path in control_paths.items()} \
            != control_records:
        raise RuntimeError(
            "Goal5814 preflight control-plane bytes changed during live probe")
    result: dict[str, object] = {
        "schema": "rtdl.goal5814.particle_measurement_worker_zero_preflight.v2",
        "status": (
            "PASS__PROJECT_CLOSURE_BOUND__FORMAL_WORKER_ZERO_NOT_STARTED"),
        "owner_directive_receipt_file": file_record(owner_receipt_path),
        "preaction_file": file_record(preaction),
        "target_manifest_file": file_record(target_path),
        "execution_request_file": file_record(request_path),
        "project_closure_file": file_record(closure_path),
        "control_plane_records": control_records,
        "target_observation": observation,
        "target_kat_result_file": target["files"]["target_kat_result"],
        "pyoptix_extension_file": target["files"]["pyoptix_extension"],
        "timed": False,
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(canonical_document(result))
    return result


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--preaction", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--execution-request", type=Path, required=True)
    parser.add_argument("--project-closure", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    result = run_preflight(
        root=args.root,
        preaction_path=args.preaction,
        target_manifest_path=args.target_manifest,
        execution_request_path=args.execution_request,
        project_closure_path=args.project_closure,
        output_path=args.output,
    )
    print(canonical_document(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
