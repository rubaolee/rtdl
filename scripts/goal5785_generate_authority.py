#!/usr/bin/env python3
"""Generate fail-closed Goal5785 prepare/formal authority files on target."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import tarfile


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


def _write_create_only(path: Path, payload: dict[str, object]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _outer_json(bundle: Path, name: str) -> dict[str, object]:
    with tarfile.open(bundle, "r:gz") as archive:
        handle = archive.extractfile(name)
        if handle is None:
            raise RuntimeError(f"Goal5785 bundle omitted {name}")
        return json.load(handle)


def prepare_body(
    *, bundle_sha256: str, source_sha256: str, data_sha256: str,
    expectation_sha256: str, gpu: tuple[str, str, str, str], cc: str,
    python_identity: dict[str, str], authorized: bool,
) -> dict[str, object]:
    return {
        "schema": "rtdl.goal5776.owner_create_only_prepare_authority.v2",
        "bundle_sha256": bundle_sha256,
        "source_archive_sha256": source_sha256,
        "data_archive_sha256": data_sha256,
        "expected_value_statement_sha256": expectation_sha256,
        "required_gpu_name": gpu[0],
        "required_gpu_uuid": gpu[1],
        "required_driver_version": gpu[2],
        "required_compute_capability": cc,
        "required_cuda_toolkit": "12.8",
        "required_optix_sdk": "9.0.0",
        "required_python_executable_sha256": python_identity["python_executable_sha256"],
        "required_python_version": python_identity["python"],
        "required_numba_version": python_identity["numba"],
        "required_numpy_version": python_identity["numpy"],
        "required_cupy_version": python_identity["cupy"],
        "required_scipy_version": python_identity["scipy"],
        "owner_authorized_create_only_prepare": authorized,
        "formal_worker_allowed": False,
        "registered_formal_timing_allowed": False,
    }


def formal_body(runtime: dict[str, object], runtime_sha256: str, *, authorized: bool) -> dict[str, object]:
    keys = (
        "bundle_sha256", "execution_source_sha256", "data_archive_sha256",
        "rtdbscan_evidence_sha256", "native_library_sha256",
        "target_identity_sha256", "prepared_identity_sha256", "plan_sha256",
        "formal_identity_sha256", "leaf_cache_manifest_sha256",
        "runtime_budget_sha256", "expected_value_statement_sha256",
        "formal_contract_sha256",
    )
    missing = [key for key in keys if key not in runtime]
    if missing:
        raise RuntimeError(f"Goal5785 runtime omitted formal identity fields: {missing}")
    result = {key: runtime[key] for key in keys}
    result.update({
        "schema": "rtdl.goal5776.owner_formal_authority.v2",
        "runtime_sha256": runtime_sha256,
        "owner_confirmed_conservative_budget_seconds": runtime["conservative_budget_seconds"],
        "expected_worker_count": 464,
        "expected_independent_row_count": 34,
        "owner_authorized_exactly_once": authorized,
        "repair_retry_resume_replacement_allowed": False,
    })
    return result


def _authorize(body: dict[str, object]) -> dict[str, object]:
    result = dict(body)
    result["authority_sha256"] = _digest(body)
    return result


def command_prepare(args: argparse.Namespace) -> None:
    bundle = args.bundle.resolve()
    data = args.data_bundle.resolve()
    python = args.python.resolve()
    manifest = _outer_json(bundle, "PORTABLE_MANIFEST.json")
    if manifest.get("run_goal_id") != 5785 \
            or manifest.get("formal_worker_count") != 464 \
            or manifest.get("independent_comparison_row_count") != 34:
        raise RuntimeError("Goal5785 exact bundle manifest is absent")
    nvidia = subprocess.run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ], text=True, capture_output=True, check=True, timeout=30)
    lines = [line.strip() for line in nvidia.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("Goal5785 requires exactly one visible GPU")
    gpu = tuple(part.strip() for part in lines[0].split(","))
    if len(gpu) != 4 or gpu[3].replace(".", "") != args.cc:
        raise RuntimeError("Goal5785 target compute capability mismatch")
    version = subprocess.run([
        str(python), "-c",
        "import json,platform,numba,numpy,cupy,scipy; print(json.dumps({"
        "'python':platform.python_version(),'numba':numba.__version__,"
        "'numpy':numpy.__version__,'cupy':cupy.__version__,"
        "'scipy':scipy.__version__},sort_keys=True))",
    ], text=True, capture_output=True, check=True, timeout=60)
    python_identity = {**json.loads(version.stdout), "python_executable_sha256": _sha(python)}
    body = prepare_body(
        bundle_sha256=_sha(bundle),
        source_sha256=str(manifest["source_archive_sha256"]),
        data_sha256=_sha(data),
        expectation_sha256=str(manifest["expected_value_statement_sha256"]),
        gpu=gpu, cc=args.cc, python_identity=python_identity,
        authorized=args.owner_authorized,
    )
    payload = _authorize(body)
    _write_create_only(args.output, payload)
    print(json.dumps({
        "output": str(args.output), "authority_sha256": payload["authority_sha256"],
        "owner_authorized": args.owner_authorized, "gpu": gpu,
        "python_identity": python_identity,
    }, sort_keys=True))


def command_formal(args: argparse.Namespace) -> None:
    runtime_path = args.runtime.resolve()
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    body = formal_body(runtime, _sha(runtime_path), authorized=args.owner_authorized)
    payload = _authorize(body)
    _write_create_only(args.output, payload)
    print(json.dumps({
        "output": str(args.output), "authority_sha256": payload["authority_sha256"],
        "owner_authorized": args.owner_authorized,
    }, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--bundle", type=Path, required=True)
    prepare.add_argument("--data-bundle", type=Path, required=True)
    prepare.add_argument("--python", type=Path, required=True)
    prepare.add_argument("--cc", choices=("89",), required=True)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--owner-authorized", action="store_true")
    prepare.set_defaults(run=command_prepare)
    formal = subparsers.add_parser("formal")
    formal.add_argument("--runtime", type=Path, required=True)
    formal.add_argument("--output", type=Path, required=True)
    formal.add_argument("--owner-authorized", action="store_true")
    formal.set_defaults(run=command_formal)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
