"""Create-only, target-bound, no-retry 144-process Goal5814 controller."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Mapping

from .evaluate import (
    CONTROLLER_RESULT_SCHEMA, evaluate_file, validate_worker_measurement,
)
from .formal_worker import validate_worker_result
from .independent_recount import recount_files
from .measurement_protocol import (
    CACHE_RULE,
    EXECUTION_CONCURRENCY_RULE,
    INVALID_ROW_RULE,
    PROJECT_CLOSURE_ENV,
    SCHEDULE_SHA256,
    TOTAL_WORKER_COUNT,
    WORKER_TIMEOUT_SECONDS,
    canonical_document,
    file_record,
    owner_directive_receipt_path,
    schedule,
    schedule_document,
    strict_json_bytes,
    validate_authority_window,
    validate_execution_request,
    validate_live_target,
    validate_owner_directive_receipt,
    validate_preaction,
    validate_project_closure,
    validate_target_manifest,
)


ProcessRunner = Callable[..., Any]
NowProvider = Callable[[], datetime]


class ControllerError(RuntimeError):
    """The formal transaction failed terminally without replacement."""


def _write_create_only(path: Path, value: object) -> None:
    with Path(path).open("xb") as stream:
        stream.write(canonical_document(value))


def _portable_output_record(path: Path, output_root: Path) -> dict[str, object]:
    """Hash one raw output while recording a relocation-safe path."""

    resolved_root = Path(output_root).resolve(strict=True)
    resolved = Path(path).resolve(strict=True)
    try:
        relative = resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ControllerError(
            "Goal5814 raw output escaped the formal output root") from error
    payload = resolved.read_bytes()
    return {
        "path": relative.as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _control_records(paths: Mapping[str, Path]) -> dict[str, dict[str, object]]:
    return {name: file_record(path) for name, path in paths.items()}


def _require_control_records_unchanged(
        paths: Mapping[str, Path],
        expected: Mapping[str, Mapping[str, object]]) -> None:
    observed = _control_records(paths)
    if observed != expected:
        raise ControllerError(
            "Goal5814 pre-worker control-plane bytes changed")


def _bind_project_closure_environment(
        environment: dict[str, str], closure_path: Path) -> None:
    """Bind a worker to the exact closure already cached by its controller."""

    environment[PROJECT_CLOSURE_ENV] = str(
        Path(closure_path).resolve(strict=True))


def _worker_command(
        *, python: str, root: Path, preaction: Path, target: Path,
        execution_request: Path, spec: Any) -> list[str]:
    return [
        python,
        "-m", "experiments.goal5814_particle.formal_worker",
        "--root", str(root),
        "--preaction", str(preaction),
        "--target-manifest", str(target),
        "--execution-request", str(execution_request),
        "--ordinal", str(spec.ordinal),
        "--regime", spec.regime,
        "--block", str(spec.block),
        "--position", str(spec.position),
        "--arm", spec.arm,
        "--worker-id", spec.worker_id,
    ]


def _worker_environment(
        *, root: Path, target: Mapping[str, Any], directory: Path,
        base: Mapping[str, str]) -> tuple[dict[str, str], Path]:
    cache_root = directory / "isolated_caches"
    paths = {
        "home": directory / "home",
        "tmp": directory / "tmp",
        "xdg": cache_root / "xdg",
        "cuda": cache_root / "cuda",
        "cupy": cache_root / "cupy",
        "numba": cache_root / "numba",
        "optix": cache_root / "optix",
    }
    for path in paths.values():
        path.mkdir(parents=True)
    environment = dict(base)
    environment.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONPATH": os.pathsep.join((str(root), str(root / "src"))),
        "HOME": str(paths["home"]),
        "TMP": str(paths["tmp"]),
        "TEMP": str(paths["tmp"]),
        "TMPDIR": str(paths["tmp"]),
        "XDG_CACHE_HOME": str(paths["xdg"]),
        "CUDA_CACHE_PATH": str(paths["cuda"]),
        "CUDA_CACHE_DISABLE": "1",
        "CUPY_CACHE_DIR": str(paths["cupy"]),
        "NUMBA_CACHE_DIR": str(paths["numba"]),
        "OPTIX_CACHE_PATH": str(paths["optix"]),
        "OPTIX_CACHE_ENABLED": "0",
        "OPTIX_CACHE_MAXSIZE": "0",
        "RTDL_DISABLE_CUBIN_CACHE": "1",
        "RTDL_OPTIX_DISABLE_CUBIN_CACHE": "1",
        "CUDA_VISIBLE_DEVICES": target["cuda_visible_devices"],
    })
    for key, target_key in (
            ("LD_LIBRARY_PATH", "ld_library_path"),
            ("LD_PRELOAD", "ld_preload")):
        value = target[target_key]
        if value is None:
            environment.pop(key, None)
        else:
            environment[key] = value
    return environment, cache_root


def _terminal_failure(
        *, output: Path, stage: str, worker_id: str | None,
        detail: str) -> None:
    value = {
        "schema": "rtdl.goal5814.particle_formal_controller_failure.v1",
        "status": "TERMINAL_FAILURE__PRESERVED_AS_MISSING__NO_EVALUATION",
        "stage": stage,
        "worker_id": worker_id,
        "detail": detail,
        "invalid_row_disposition": INVALID_ROW_RULE,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
    }
    _write_create_only(output / "TERMINAL_FAILURE.json", value)


def run_formal_controller(
        *, root: Path, preaction_path: Path, target_manifest_path: Path,
        execution_request_path: Path, project_closure_path: Path,
        output_root: Path,
        process_runner: ProcessRunner = subprocess.run,
        live_target_runner: ProcessRunner = subprocess.run,
        now_provider: NowProvider = lambda: datetime.now(timezone.utc),
        base_environment: Mapping[str, str] | None = None,
        ) -> dict[str, Any]:
    """Run the sole 144-worker transaction; no partial/resume mode exists."""

    output = Path(output_root).absolute()
    # Collision rejection precedes live probes, directory creation, and worker
    # processes.  A prior output can never turn a rerun into retry_count=0.
    if output.exists():
        raise ControllerError("Goal5814 formal output root already exists")
    resolved_root = Path(root).resolve(strict=True)
    preaction = Path(preaction_path).resolve(strict=True)
    target_path = Path(target_manifest_path).resolve(strict=True)
    request_path = Path(execution_request_path).resolve(strict=True)
    closure_path = Path(project_closure_path).resolve(strict=True)
    owner_receipt_path = owner_directive_receipt_path(root=resolved_root)
    validate_preaction(preaction)
    validate_owner_directive_receipt(
        owner_receipt_path, root=resolved_root)
    target_manifest = validate_target_manifest(
        target_path, root=resolved_root, rehash=True)
    execution_request = validate_execution_request(
        request_path, preaction_path=preaction,
        target_manifest_path=target_path, target_manifest=target_manifest,
        owner_receipt_path=owner_receipt_path)
    project_closure = validate_project_closure(
        closure_path, preaction_path=preaction,
        target_manifest_path=target_path,
        execution_request_path=request_path,
        target_manifest=target_manifest,
        execution_request=execution_request,
        owner_receipt_path=owner_receipt_path)
    validate_authority_window(project_closure, now=now_provider())
    control_paths = {
        "owner_directive_receipt": owner_receipt_path,
        "preaction": preaction,
        "target_manifest": target_path,
        "execution_request": request_path,
        "project_closure": closure_path,
    }
    expected_control_records = _control_records(control_paths)
    validate_live_target(target_manifest, run=live_target_runner)
    _require_control_records_unchanged(
        control_paths, expected_control_records)

    output.mkdir(parents=True, exist_ok=False)
    _write_create_only(
        output / "CONTROL_PLANE_RECORDS.json", expected_control_records)
    worker_root = output / "workers"
    worker_root.mkdir()
    workers: list[dict[str, Any]] = []
    observed_pids: set[int] = set()
    environment_base = os.environ if base_environment is None else base_environment
    # Invoke workers through the current venv entry path, not through the
    # resolved base-interpreter inode recorded for binary custody.  Resolving
    # a venv symlink before exec silently drops that venv's site-packages.
    python = sys.executable
    if Path(python).resolve(strict=True) != Path(
            target_manifest["files"]["python_executable"]["path"]):
        raise ControllerError(
            "Goal5814 controller Python differs from target binary custody")
    for spec in schedule():
        try:
            _require_control_records_unchanged(
                control_paths, expected_control_records)
        except BaseException as error:
            _terminal_failure(
                output=output, stage="CONTROL_PLANE_IDENTITY_CHANGED_BEFORE_WORKER",
                worker_id=spec.worker_id,
                detail=f"{type(error).__name__}: {error}")
            raise ControllerError(
                "Goal5814 control-plane bytes changed before a worker") \
                from error
        remaining_seconds = validate_authority_window(
            project_closure, now=now_provider())
        effective_timeout = min(WORKER_TIMEOUT_SECONDS, remaining_seconds)
        directory = worker_root / spec.worker_id
        directory.mkdir()
        environment, cache_root = _worker_environment(
            root=resolved_root, target=target_manifest["target"],
            directory=directory, base=environment_base)
        _bind_project_closure_environment(environment, closure_path)
        command = _worker_command(
            python=python, root=resolved_root, preaction=preaction,
            target=target_path, execution_request=request_path, spec=spec)
        _write_create_only(directory / "command.json", command)
        try:
            completed = process_runner(
                command,
                cwd=resolved_root,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=effective_timeout,
            )
        except BaseException as error:
            _terminal_failure(
                output=output, stage="WORKER_PROCESS_EXCEPTION",
                worker_id=spec.worker_id,
                detail=f"{type(error).__name__}: {error}")
            raise ControllerError(
                f"Goal5814 worker process failed terminally: {spec.worker_id}") \
                from error
        try:
            _require_control_records_unchanged(
                control_paths, expected_control_records)
        except BaseException as error:
            _terminal_failure(
                output=output, stage="CONTROL_PLANE_IDENTITY_CHANGED",
                worker_id=spec.worker_id,
                detail=f"{type(error).__name__}: {error}")
            raise ControllerError(
                "Goal5814 control-plane bytes changed during a worker") \
                from error
        stdout = completed.stdout if isinstance(completed.stdout, bytes) \
            else str(completed.stdout).encode("utf-8")
        stderr = completed.stderr if isinstance(completed.stderr, bytes) \
            else str(completed.stderr).encode("utf-8")
        stdout_path = directory / "stdout.json"
        stderr_path = directory / "stderr.bin"
        with stdout_path.open("xb") as stream:
            stream.write(stdout)
        with stderr_path.open("xb") as stream:
            stream.write(stderr)
        if completed.returncode != 0:
            _terminal_failure(
                output=output, stage="WORKER_NONZERO_EXIT",
                worker_id=spec.worker_id,
                detail=f"exit_code={completed.returncode}")
            raise ControllerError(
                f"Goal5814 worker failed terminally: {spec.worker_id}")
        try:
            result = strict_json_bytes(stdout, label="worker stdout")
            if stdout != canonical_document(result):
                raise ControllerError(
                    "Goal5814 worker stdout is not exact canonical JSON")
            validate_worker_result(result, expected=spec)
            validate_worker_measurement(result, spec.regime)
            if result["preaction_file"] \
                    != expected_control_records["preaction"] \
                    or result["target_manifest_file"] \
                    != expected_control_records["target_manifest"] \
                    or result["execution_request_file"] \
                    != expected_control_records["execution_request"] \
                    or result["project_closure_file"] \
                    != expected_control_records["project_closure"]:
                raise ControllerError(
                    "Goal5814 worker reported a different control plane")
            if result["pid"] == os.getpid() \
                    or result["pid"] in observed_pids \
                    or result["parent_pid"] != os.getpid():
                raise ControllerError(
                    "Goal5814 worker fresh-process PID differs")
            observed_pids.add(result["pid"])
            cache_files = sorted(
                path.relative_to(directory).as_posix()
                for path in cache_root.rglob("*") if path.is_file())
            if cache_files:
                raise ControllerError(
                    "Goal5814 worker populated a forbidden isolated cache")
        except BaseException as error:
            _terminal_failure(
                output=output, stage="WORKER_RECEIPT_VALIDATION",
                worker_id=spec.worker_id,
                detail=f"{type(error).__name__}: {error}")
            raise ControllerError(
                f"Goal5814 worker receipt failed terminally: {spec.worker_id}") \
                from error
        workers.append({
            "ordinal": spec.ordinal,
            "regime": spec.regime,
            "block": spec.block,
            "position": spec.position,
            "arm": spec.arm,
            "worker_id": spec.worker_id,
            "result": result,
            "stdout_file": _portable_output_record(stdout_path, output),
            "stderr_file": _portable_output_record(stderr_path, output),
            "isolated_cache_files_after": cache_files,
        })

    try:
        _require_control_records_unchanged(
            control_paths, expected_control_records)
    except BaseException as error:
        _terminal_failure(
            output=output, stage="CONTROL_PLANE_IDENTITY_CHANGED_AT_END",
            worker_id=None, detail=f"{type(error).__name__}: {error}")
        raise ControllerError(
            "Goal5814 control-plane bytes changed before publication") from error

    controller: dict[str, Any] = {
        "schema": CONTROLLER_RESULT_SCHEMA,
        "status": "COMPLETE__144_FRESH_PROCESSES__NO_RETRY_OR_REPLACEMENT",
        "preaction_file": file_record(preaction),
        "target_manifest_file": file_record(target_path),
        "execution_request_file": file_record(request_path),
        "project_closure_file": file_record(closure_path),
        "schedule_sha256": SCHEDULE_SHA256,
        "schedule": schedule_document(),
        "workers": workers,
        "execution_concurrency": EXECUTION_CONCURRENCY_RULE,
        "invalid_row_disposition": INVALID_ROW_RULE,
        "timed": True,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
        "formal_worker_count": len(workers),
        "unique_worker_pid_count": len(observed_pids),
        "registered_performance_timing_count": sum(
            row["result"]["registered_performance_timing_count"]
            for row in workers),
    }
    controller_path = output / "controller.json"
    _write_create_only(controller_path, controller)
    evaluation = evaluate_file(controller_path, output / "evaluation.json")
    recount = recount_files(
        controller_path, output / "evaluation.json",
        output / "independent_recount.json")
    return {
        "status": controller["status"],
        "formal_worker_count": TOTAL_WORKER_COUNT,
        "registered_performance_timing_count": controller[
            "registered_performance_timing_count"],
        "evaluation_sha256": evaluation["evaluation_sha256"],
        "independent_recount_sha256": recount["recount_sha256"],
        "project_closure_sha256": expected_control_records[
            "project_closure"]["sha256"],
        "cache_rule": CACHE_RULE,
    }


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--preaction", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--execution-request", type=Path, required=True)
    parser.add_argument("--project-closure", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    result = run_formal_controller(
        root=args.root,
        preaction_path=args.preaction,
        target_manifest_path=args.target_manifest,
        execution_request_path=args.execution_request,
        project_closure_path=args.project_closure,
        output_root=args.output_root,
    )
    print(canonical_document(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
