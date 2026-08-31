#!/usr/bin/env python3
"""Create-only controller for the exact 128-worker Goal5784 cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess

from goal5784_targeted_formal_contract import (
    FORMAL_WORKER_TIMEOUT_SECONDS, contract_document, contract_sha256,
    schedule, statistical_rows,
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative.startswith("build/") or "/__pycache__/" in f"/{relative}/" \
                or relative.endswith(".pyc"):
            continue
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha(path)))
    return digest.hexdigest()


def _validate_authority(authority: dict[str, object], runtime: dict[str, object],
                        runtime_sha256: str) -> None:
    body = dict(authority)
    claimed = body.pop("authority_sha256", None)
    if claimed != _digest(body):
        raise PermissionError("Goal5784 owner authority digest mismatch")
    expected_fields = {
        "schema", "bundle_sha256", "execution_source_sha256",
        "data_archive_sha256", "native_library_sha256",
        "target_identity_sha256", "prepared_identity_sha256", "plan_sha256",
        "formal_identity_sha256", "leaf_cache_manifest_sha256",
        "expected_value_statement_sha256", "runtime_budget_sha256",
        "preregistration_sha256", "formal_contract_sha256", "runtime_sha256",
        "expected_worker_count",
        "expected_independent_row_count", "owner_authorized_exactly_once",
        "owner_confirmed_formal_budget_seconds",
        "repair_retry_resume_replacement_row_drop_relabel_allowed",
        "authority_sha256",
    }
    if set(authority) != expected_fields or (
        authority.get("schema") != "rtdl.goal5784.owner_formal_authority.v1"
        or authority.get("owner_authorized_exactly_once") is not True
        or authority.get(
            "repair_retry_resume_replacement_row_drop_relabel_allowed") is not False
        or authority.get("expected_worker_count") != len(schedule())
        or authority.get("expected_independent_row_count") != len(statistical_rows())
        or authority.get("formal_contract_sha256") != contract_sha256()
        or authority.get("runtime_sha256") != runtime_sha256
        or authority.get("owner_confirmed_formal_budget_seconds")
            != runtime.get("formal_conservative_budget_seconds")
    ):
        raise PermissionError("Goal5784 exact formal authority is absent")
    for key in (
        "bundle_sha256", "execution_source_sha256", "data_archive_sha256",
        "native_library_sha256", "target_identity_sha256",
        "prepared_identity_sha256", "plan_sha256", "formal_identity_sha256",
        "leaf_cache_manifest_sha256", "expected_value_statement_sha256",
        "runtime_budget_sha256", "preregistration_sha256",
        "formal_contract_sha256",
    ):
        if authority.get(key) != runtime.get(key):
            raise PermissionError(f"Goal5784 authority/runtime mismatch: {key}")


def _validate_plan(plan_path: Path, runtime: dict[str, object]) -> None:
    if not plan_path.is_file() or _sha(plan_path) != runtime.get("plan_sha256"):
        raise PermissionError("Goal5784 plan bytes drifted")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if (
        plan.get("schema") != "rtdl.goal5784.targeted_plan.v1"
        or plan.get("bundle_sha256") != runtime.get("bundle_sha256")
        or plan.get("prepared_identity_sha256")
            != runtime.get("prepared_identity_sha256")
        or plan.get("formal_identity_sha256")
            != runtime.get("formal_identity_sha256")
        or plan.get("formal_contract_sha256") != contract_sha256()
        or plan.get("formal_worker_count") != len(schedule())
        or plan.get("independent_row_count") != len(statistical_rows())
        or plan.get("formal_worker_executed") is not False
        or plan.get("formal_requires_second_exact_owner_authority") is not True
    ):
        raise PermissionError("Goal5784 plan contract mismatch")
    sources = plan.get("formal_sources")
    if not isinstance(sources, dict):
        raise PermissionError("Goal5784 plan omitted formal sources")
    for name, row in sources.items():
        if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
            raise PermissionError(f"Goal5784 malformed source pin: {name}")
        path = Path(str(row["path"])).resolve()
        if not path.is_file() or _sha(path) != row["sha256"]:
            raise PermissionError(f"Goal5784 formal source drift: {name}")


def _validate_prepared(runtime: dict[str, object]) -> None:
    if runtime.get("compute_capability") != [8, 9] \
            or runtime.get("optix_sdk_version") != "9.0.0":
        raise PermissionError("Goal5784 formal target contract is incomplete")
    for key, header in (("optix_include", "optix.h"),
                        ("cuda_include", "cuda.h")):
        include = Path(str(runtime.get(key, ""))).resolve()
        if not include.is_dir() or not (include / header).is_file():
            raise PermissionError(
                f"Goal5784 formal target include is incomplete: {key}")
    for path_key, sha_key in (
        ("execution_source_path", "execution_source_sha256"),
        ("data_archive_path", "data_archive_sha256"),
        ("native_library_path", "native_library_sha256"),
        ("leaf_cache_manifest_path", "leaf_cache_manifest_sha256"),
        ("expected_value_statement_path", "expected_value_statement_sha256"),
        ("runtime_budget_path", "runtime_budget_sha256"),
        ("preregistration_path", "preregistration_sha256"),
    ):
        path = Path(str(runtime.get(path_key, ""))).resolve()
        if not path.is_file() or _sha(path) != runtime.get(sha_key):
            raise PermissionError(f"Goal5784 prepared bytes drifted: {path_key}")
    data_manifest = Path(str(runtime.get("data_manifest_path", ""))).resolve()
    if not data_manifest.is_file() \
            or _sha(data_manifest) != runtime.get("data_manifest_sha256"):
        raise PermissionError("Goal5784 prepared data manifest drifted")
    evidence = Path(str(runtime.get("rtdbscan_evidence_path", ""))).resolve()
    if not evidence.is_file() \
            or _sha(evidence) != runtime.get("rtdbscan_evidence_sha256"):
        raise PermissionError("Goal5784 fixed-radius evidence drifted")
    python = Path(str(runtime.get("python_executable", ""))).resolve()
    if not python.is_file() \
            or _sha(python) != runtime.get("python_executable_sha256"):
        raise PermissionError("Goal5784 Python executable drifted")
    for key in ("source_root", "data_root", "leaf_cache_root",
                "target_functional_root"):
        root = Path(str(runtime.get(key, ""))).resolve()
        if not root.is_dir() or root.is_symlink() or any(
            path.is_symlink() or path.stat().st_mode & 0o222
            for path in (root, *root.rglob("*"))):
            raise PermissionError(f"Goal5784 prepared tree is not sealed: {key}")
    source = Path(str(runtime.get("source_root", ""))).resolve()
    if _tree_digest(source) != runtime.get("source_tree_sha256"):
        raise PermissionError("Goal5784 prepared source tree digest drifted")
    manifest = json.loads(data_manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.real_scale_data_manifest.v1":
        raise PermissionError("Goal5784 data manifest schema drifted")
    data_root = Path(str(runtime.get("data_root", ""))).resolve()
    expected = {str(row["path"])[5:]: row for row in manifest.get("files", [])
                if str(row.get("path", "")).startswith("DATA/")}
    actual = {path.relative_to(data_root).as_posix(): path
              for path in data_root.rglob("*") if path.is_file()}
    if set(actual) != set(expected):
        raise PermissionError("Goal5784 extracted data membership drifted")
    for name, path in actual.items():
        row = expected[name]
        if path.stat().st_size != int(row["size_bytes"]) \
                or _sha(path) != row["sha256"]:
            raise PermissionError(f"Goal5784 extracted data drifted: {name}")


def _run_worker(command: list[str], *, env: dict[str, str], index: int) -> None:
    process = subprocess.Popen(command, env=env, start_new_session=True)
    try:
        returncode = process.wait(timeout=FORMAL_WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait()
        raise RuntimeError(f"Goal5784 worker {index} timed out terminally") from exc
    if returncode != 0:
        raise RuntimeError(f"Goal5784 worker {index} failed terminally")


def run(*, runtime_path: Path, plan_path: Path, authorization_path: Path,
        output_root: Path) -> Path:
    if output_root.exists():
        raise FileExistsError(output_root)
    runtime_sha = _sha(runtime_path)
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    if runtime.get("schema") != "rtdl.goal5776.real_scale_runtime.v1" \
            or runtime.get("run_goal_id") != 5784 \
            or runtime.get("formal_contract_sha256") != contract_sha256():
        raise PermissionError("Goal5784 runtime identity mismatch")
    _validate_plan(plan_path, runtime)
    _validate_prepared(runtime)
    authority = json.loads(authorization_path.read_text(encoding="utf-8"))
    _validate_authority(authority, runtime, runtime_sha)
    frozen_env = runtime.get("formal_worker_environment")
    if not isinstance(frozen_env, dict):
        raise PermissionError("Goal5784 runtime omitted worker environment")
    env = dict(os.environ)
    env.update({str(k): str(v) for k, v in frozen_env.items()
                if isinstance(v, str) and v})
    output_root.mkdir(parents=False)
    worker_root = output_root / "workers"
    worker_root.mkdir()
    (output_root / "FORMAL_CONTRACT.json").write_text(
        json.dumps(contract_document(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    (output_root / "SCHEDULE.json").write_text(
        json.dumps(list(schedule()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    python = str(runtime["python_executable"])
    harness = Path(str(runtime["harness_root"]))
    for worker in schedule():
        index = int(worker["worker_index"])
        output = worker_root / f"worker_{index:04d}.json"
        _run_worker([
            python, str(harness / "goal5784_targeted_worker.py"),
            "--runtime", str(runtime_path), "--worker-index", str(index),
            "--output", str(output),
        ], env=env, index=index)
    _run_worker([
        python, str(harness / "goal5784_targeted_evaluate.py"),
        "--raw-root", str(output_root), "--output",
        str(output_root / "EVALUATION.json"),
    ], env=env, index=len(schedule()))
    _run_worker([
        python, str(harness / "goal5784_targeted_recount.py"),
        "--raw-root", str(output_root), "--output",
        str(output_root / "INDEPENDENT_RECOUNT.json"),
    ], env=env, index=len(schedule()) + 1)
    evaluation = json.loads(
        (output_root / "EVALUATION.json").read_text(encoding="utf-8"))
    recount = json.loads(
        (output_root / "INDEPENDENT_RECOUNT.json").read_text(encoding="utf-8"))
    if evaluation["rows"] != recount["rows"]:
        raise RuntimeError("Goal5784 primary/independent statistics differ")
    receipt = {
        "schema": "rtdl.goal5784.targeted_controller_receipt.v1",
        "worker_count": len(schedule()),
        "independent_row_count": len(statistical_rows()),
        "evaluation_sha256": _sha(output_root / "EVALUATION.json"),
        "independent_recount_sha256": _sha(
            output_root / "INDEPENDENT_RECOUNT.json"),
        "repair_retry_resume_replacement_row_drop_relabel_used": False,
    }
    (output_root / "CONTROLLER_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return output_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(run(runtime_path=args.runtime, plan_path=args.plan,
              authorization_path=args.authorization,
              output_root=args.output_root))


if __name__ == "__main__":
    main()
