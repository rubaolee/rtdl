#!/usr/bin/env python3
"""Create-only controller for the exact Goal5776 real-scale matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess

from goal5776_real_scale_formal_contract import (
    FORMAL_WORKER_TIMEOUT_SECONDS,
    contract_document,
    contract_sha256,
    schedule,
    statistical_rows,
)


def _run_worker(
    command: list[str], *, worker_environment: dict[str, str], worker_index: int,
) -> None:
    process = subprocess.Popen(
        command, env=worker_environment, start_new_session=True)
    try:
        returncode = process.wait(timeout=FORMAL_WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait()
        raise RuntimeError(
            f"Goal5776 worker {worker_index} exceeded the frozen "
            f"{FORMAL_WORKER_TIMEOUT_SECONDS}-second limit terminally"
        ) from exc
    if returncode != 0:
        raise RuntimeError(f"Goal5776 worker {worker_index} failed terminally")


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


def _preserve_python_entrypoint(value: object) -> Path:
    """Make the configured interpreter absolute without dereferencing a venv.

    A virtual-environment ``bin/python`` is normally a symlink to the system
    executable.  ``Path.resolve()`` therefore discards the environment whose
    site-packages were admitted during prepare.  The formal controller must
    launch the exact configured entrypoint spelling after verifying its bytes.
    """
    return Path(os.path.abspath(str(value)))


def _validate_worker_python_environment(
    runtime: dict[str, object], worker_environment: dict[str, str],
) -> str:
    """Prove the exact worker entrypoint can import the admitted partners.

    This check runs before the output root and before worker zero.  It prevents
    a controller path rewrite from turning an admitted venv into a package-less
    system interpreter.
    """
    python = str(_preserve_python_entrypoint(runtime["python_executable"]))
    probe = subprocess.run([
        python, "-c",
        "import json,os,platform,sys,numba,numpy,cupy,scipy;"
        "print(json.dumps({'python_executable':os.path.abspath(sys.executable),"
        "'python_version':platform.python_version(),"
        "'numba_version':numba.__version__,'numpy_version':numpy.__version__,"
        "'cupy_version':cupy.__version__,'scipy_version':scipy.__version__},"
        "sort_keys=True))",
    ], env=worker_environment, text=True, capture_output=True, check=True,
       timeout=60)
    observed = json.loads(probe.stdout)
    expected = {
        "python_executable": python,
        "python_version": runtime["python_version"],
        "numba_version": runtime["numba_version"],
        "numpy_version": runtime["numpy_version"],
        "cupy_version": runtime["cupy_version"],
        "scipy_version": runtime["scipy_version"],
    }
    if observed != expected:
        raise PermissionError("Goal5776 worker Python environment drifted")
    return python


def _validate_authority(
    authority: dict[str, object], runtime: dict[str, object],
    *, runtime_sha256: str,
) -> None:
    body = dict(authority)
    claimed = body.pop("authority_sha256", None)
    if claimed != _digest(body):
        raise PermissionError("Goal5776 owner authority digest mismatch")
    expected = {
        "schema", "bundle_sha256", "execution_source_sha256",
        "data_archive_sha256", "rtdbscan_evidence_sha256",
        "native_library_sha256",
        "target_identity_sha256", "prepared_identity_sha256", "plan_sha256",
        "formal_identity_sha256", "leaf_cache_manifest_sha256",
        "runtime_budget_sha256", "owner_confirmed_conservative_budget_seconds",
        "expected_value_statement_sha256",
        "formal_contract_sha256", "runtime_sha256", "expected_worker_count",
        "expected_independent_row_count", "owner_authorized_exactly_once",
        "repair_retry_resume_replacement_allowed", "authority_sha256",
    }
    if set(authority) != expected or (
        authority["schema"] != "rtdl.goal5776.owner_formal_authority.v2"
        or authority["owner_authorized_exactly_once"] is not True
        or authority["repair_retry_resume_replacement_allowed"] is not False
        or type(authority["owner_confirmed_conservative_budget_seconds"])
            not in (int, float)
        or float(authority["owner_confirmed_conservative_budget_seconds"])
        != float(runtime.get("conservative_budget_seconds", 0.0))
        or int(authority["expected_worker_count"]) != len(schedule())
        or int(authority["expected_independent_row_count"])
        != len(statistical_rows())
        or authority["formal_contract_sha256"] != contract_sha256()
    ):
        raise PermissionError("Goal5776 exact formal authority is absent")
    for key in (
        "bundle_sha256", "execution_source_sha256", "data_archive_sha256",
        "rtdbscan_evidence_sha256", "native_library_sha256",
        "target_identity_sha256",
        "prepared_identity_sha256", "plan_sha256", "formal_identity_sha256",
        "leaf_cache_manifest_sha256", "formal_contract_sha256",
        "runtime_budget_sha256",
        "expected_value_statement_sha256",
    ):
        if authority[key] != runtime.get(key):
            raise PermissionError(f"Goal5776 authority/runtime mismatch: {key}")
    if authority["runtime_sha256"] != runtime_sha256:
        raise PermissionError("Goal5776 authority/runtime byte mismatch")


def _validate_plan(plan_path: Path, runtime: dict[str, object]) -> dict[str, object]:
    if not plan_path.is_file() or _sha(plan_path) != runtime.get("plan_sha256"):
        raise PermissionError("Goal5776 exact plan bytes are absent")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    expected = {
        "schema": "rtdl.goal5776.real_scale_plan.v1",
        "bundle_sha256": runtime.get("bundle_sha256"),
        "data_archive_sha256": runtime.get("data_archive_sha256"),
        "prepared_identity_sha256": runtime.get("prepared_identity_sha256"),
        "target_identity_sha256": runtime.get("target_identity_sha256"),
        "formal_identity_sha256": runtime.get("formal_identity_sha256"),
        "runtime_budget_sha256": runtime.get("runtime_budget_sha256"),
        "expected_value_statement_sha256": runtime.get(
            "expected_value_statement_sha256"),
        "conservative_budget_seconds": runtime.get("conservative_budget_seconds"),
        "formal_worker_count": len(schedule()),
        "independent_row_count": len(statistical_rows()),
        "v3_required_or_executed": False,
        "formal_worker_executed": False,
        "registered_formal_timing_created": False,
        "formal_requires_second_exact_owner_authority": True,
    }
    for key, value in expected.items():
        if plan.get(key) != value:
            raise PermissionError(f"Goal5776 plan/runtime mismatch: {key}")
    source = Path(str(runtime.get("source_root", ""))).resolve()
    formal_sources = plan.get("formal_sources")
    if not isinstance(formal_sources, dict):
        raise PermissionError("Goal5776 plan lacks formal source identities")
    for name, expected_sha in formal_sources.items():
        path = source / "scripts" / str(name)
        if not path.is_file() or _sha(path) != expected_sha:
            raise PermissionError(f"Goal5776 formal source drift: {name}")
    return plan


def _zero_writable_tree(root: Path) -> bool:
    if root.is_symlink() or not root.is_dir():
        return False
    return all(
        not path.is_symlink() and (path.stat().st_mode & 0o222) == 0
        for path in (root, *root.rglob("*"))
    )


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


def _validate_prepared_bytes(runtime: dict[str, object]) -> None:
    execution_source = Path(str(runtime.get("execution_source_path", ""))).resolve()
    data_archive = Path(str(runtime.get("data_archive_path", ""))).resolve()
    evidence = Path(str(runtime.get("rtdbscan_evidence_path", ""))).resolve()
    budget = Path(str(runtime.get("runtime_budget_path", ""))).resolve()
    if not execution_source.is_file() \
            or _sha(execution_source) != runtime.get("execution_source_sha256"):
        raise PermissionError("Goal5776 execution-source bytes drifted")
    if not data_archive.is_file() \
            or _sha(data_archive) != runtime.get("data_archive_sha256"):
        raise PermissionError("Goal5776 data-archive bytes drifted")
    data_manifest = Path(str(runtime.get("data_manifest_path", ""))).resolve()
    if not data_manifest.is_file() \
            or _sha(data_manifest) != runtime.get("data_manifest_sha256"):
        raise PermissionError("Goal5776 data-manifest bytes drifted")
    if not evidence.is_file() \
            or _sha(evidence) != runtime.get("rtdbscan_evidence_sha256") \
            or evidence.stat().st_mode & 0o222:
        raise PermissionError("Goal5776 fixed-radius evidence is not sealed")
    if not budget.is_file() \
            or _sha(budget) != runtime.get("runtime_budget_sha256") \
            or budget.stat().st_mode & 0o222:
        raise PermissionError("Goal5776 runtime budget is not sealed")
    python = _preserve_python_entrypoint(runtime.get("python_executable", ""))
    if not python.is_file() \
            or _sha(python) != runtime.get("python_executable_sha256"):
        raise PermissionError("Goal5776 frozen Python executable drifted")
    for key in (
        "source_root", "data_root", "leaf_cache_root", "target_functional_root",
    ):
        if not _zero_writable_tree(Path(str(runtime.get(key, ""))).resolve()):
            raise PermissionError(f"Goal5776 prepared tree is not sealed: {key}")
    source = Path(str(runtime.get("source_root", ""))).resolve()
    if _tree_digest(source) != runtime.get("source_tree_sha256"):
        raise PermissionError("Goal5776 prepared source tree digest drifted")
    manifest = json.loads(data_manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.real_scale_data_manifest.v1":
        raise PermissionError("Goal5776 data manifest schema drifted")
    data_root = Path(str(runtime.get("data_root", ""))).resolve()
    expected = {str(row["path"])[5:]: row for row in manifest.get("files", [])
                if str(row.get("path", "")).startswith("DATA/")}
    actual = {
        path.relative_to(data_root).as_posix(): path
        for path in data_root.rglob("*") if path.is_file()
    }
    if set(actual) != set(expected):
        raise PermissionError("Goal5776 extracted data membership drifted")
    for name, path in actual.items():
        row = expected[name]
        if path.stat().st_size != int(row["size_bytes"]) \
                or _sha(path) != row["sha256"]:
            raise PermissionError(f"Goal5776 extracted data bytes drifted: {name}")


def run(
    *, runtime_path: Path, plan_path: Path,
    authorization_path: Path, output_root: Path,
) -> Path:
    if output_root.exists():
        raise FileExistsError(output_root)
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    _validate_plan(plan_path, runtime)
    _validate_prepared_bytes(runtime)
    authority = json.loads(authorization_path.read_text(encoding="utf-8"))
    _validate_authority(authority, runtime, runtime_sha256=_sha(runtime_path))
    frozen_environment = runtime.get("formal_worker_environment")
    if not isinstance(frozen_environment, dict):
        raise PermissionError("Goal5776 runtime lacks worker environment")
    worker_environment = dict(os.environ)
    worker_environment.update({
        str(key): str(value) for key, value in frozen_environment.items()
        if isinstance(value, str) and value
    })
    worker_python = _validate_worker_python_environment(
        runtime, worker_environment)
    rows = schedule()
    output_root.mkdir(parents=False)
    worker_root = output_root / "workers"
    worker_root.mkdir()
    contract_path = output_root / "FORMAL_CONTRACT.json"
    schedule_path = output_root / "SCHEDULE.json"
    contract_path.write_text(
        json.dumps(contract_document(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    schedule_path.write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    worker = Path(__file__).with_name("goal5776_real_scale_formal_worker.py")
    for item in rows:
        destination = worker_root / f'{int(item["worker_index"]):04d}.json'
        command = [
            worker_python, str(worker), "--runtime", str(runtime_path),
            "--worker-index", str(item["worker_index"]),
            "--output", str(destination),
        ]
        _run_worker(
            command, worker_environment=worker_environment,
            worker_index=int(item["worker_index"]),
        )
    receipt = {
        "schema": "rtdl.goal5776.real_scale_formal_controller_receipt.v1",
        "worker_count": len(rows),
        "independent_row_count": len(statistical_rows()),
        "formal_contract_sha256": contract_sha256(),
        "frozen_contract_file_sha256": _sha(contract_path),
        "schedule_sha256": _sha(schedule_path),
        "runtime_sha256": _sha(runtime_path),
        "plan_sha256": _sha(plan_path),
        "authorization_sha256": _sha(authorization_path),
        "runtime_budget_sha256": runtime["runtime_budget_sha256"],
        "owner_confirmed_conservative_budget_seconds": authority[
            "owner_confirmed_conservative_budget_seconds"],
        "retry_resume_replacement_row_drop_relabel_used": False,
    }
    receipt_path = output_root / "CONTROLLER_RECEIPT.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    print(run(
        runtime_path=args.runtime.resolve(),
        plan_path=args.plan.resolve(),
        authorization_path=args.authorization.resolve(),
        output_root=args.output_root.resolve(),
    ))


if __name__ == "__main__":
    main()
