#!/usr/bin/env python3
"""Fresh-process Home controller for the Goal5790-A1 three-arm suite.

This controller is functional-only.  It records no elapsed value, creates no
formal worker, and never interprets a successful process as performance
evidence.  Each case arm is a separate Python process so the product rejection
cannot inherit a compiler, CUDA, native, or OptiX import from either execution
arm.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Mapping, Sequence

from scripts.goal5790_a1_rejected_encoding_cases import (
    CASE_IDS,
    canonical_sha256,
    parse_suite_json,
)


SCHEMA = "rtdl.goal5790_a1.home_controller.v1"
HOME_HOSTNAME = "lx1"
HOME_GPU = "NVIDIA GeForce GTX 1070"
HOME_DRIVER = "580.126.09"
HOME_UUID = "GPU-8e04454e-c177-6e5b-3f43-e676980ecdfa"
HOME_CC = "6.1"
HOME_AUTHORITY_FILE_SHA256 = (
    "bcfd6a99766621d474dc45aa1b8c896df725575fd1131b64471b5d3d75316314")
HOME_AUTHORITY_RECEIPT_SHA256 = (
    "73fc385cabf2ea5b6cff70eb6d0fc31750cda206377015805c2935f02de6bb40")
DEFAULT_HOME_AUTHORITY = (
    Path("history/internal_docs/") /
    "goal5790_frozen_home_machine_authority_20260816.json")
HOME_TOOLCHAIN_FIELDS = (
    "cuda_toolkit_resolved_path", "cuda_nvrtc_resolved_path",
    "cuda_nvrtc_sha256", "cuda_nvrtc_builtins_resolved_path",
    "cuda_nvrtc_builtins_sha256", "cuda_nvrtc_runtime_version",
    "cuda_nvvm_resolved_path", "cuda_nvvm_sha256",
    "cuda_libdevice_resolved_path", "cuda_libdevice_sha256",
    "cuda_nvcc_version", "cuda_host_compiler_path",
    "cuda_host_compiler_version",
)
ARMS = (
    "product_admission_reject",
    "accepted_control",
    "diagnostic_counterfactual",
)
ROOT = Path(__file__).resolve().parents[1]


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _slug(value: str) -> str:
    return value.replace(".", "__").replace("-", "_")


def _load_execution_spec(
    path: Path, *, suite_sha256: str, expected_sha256: str,
) -> dict[str, object]:
    path = path.resolve()
    value = json.loads(path.read_text(encoding="utf-8"))
    body = dict(value)
    claimed = body.pop("execution_spec_sha256", None)
    if claimed != expected_sha256 or canonical_sha256(body) != claimed \
            or value.get("schema") \
                != "rtdl.goal5790_a1.home_execution_spec.v2" \
            or value.get("upstream_suite_sha256") != suite_sha256:
        raise RuntimeError("Goal5790-A1 pre-run execution-spec authority drift")
    rows = value.get("cases")
    if not isinstance(rows, list) or len(rows) != len(CASE_IDS) \
            or tuple(row.get("case_id") for row in rows) != CASE_IDS:
        raise RuntimeError("Goal5790-A1 execution-spec case universe drift")
    _verify_execution_spec_source_members(value)
    return value


def _verify_execution_spec_source_members(
    value: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    """Make frozen source pins an execution gate, not documentation."""

    raw_rows = value.get("pre_run_source_members")
    if not isinstance(raw_rows, list) or not raw_rows:
        raise RuntimeError("Goal5790-A1 execution spec lacks source members")
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_rows):
        if not isinstance(raw, Mapping):
            raise RuntimeError(
                f"Goal5790-A1 source member {index} is not an object")
        logical = raw.get("logical_path")
        expected = raw.get("sha256")
        roles = raw.get("roles")
        if not isinstance(logical, str) or not logical \
                or not isinstance(expected, str) or len(expected) != 64 \
                or not isinstance(roles, list) or not roles \
                or not all(isinstance(role, str) and role for role in roles):
            raise RuntimeError(
                f"Goal5790-A1 source member {index} is malformed")
        relative = Path(logical)
        if relative.is_absolute() or ".." in relative.parts \
                or logical in seen:
            raise RuntimeError(
                f"Goal5790-A1 source member path is unsafe/duplicate: {logical}")
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(
                f"Goal5790-A1 source member escapes repository: {logical}") from exc
        if not path.is_file() or _sha_file(path) != expected:
            raise RuntimeError(
                f"Goal5790-A1 frozen source bytes drifted: {logical}")
        seen.add(logical)
        rows.append(dict(raw))
    return tuple(rows)


def _verify_frozen_home_authority(path: Path) -> dict[str, object]:
    """Rehash the previously qualified Home toolchain, not ambient labels."""

    path = path.resolve()
    if _sha_file(path) != HOME_AUTHORITY_FILE_SHA256:
        raise RuntimeError("Goal5790 frozen Home-authority file bytes drifted")
    value = json.loads(path.read_text(encoding="utf-8"))
    claimed = value.get("receipt_sha256")
    body = dict(value)
    body.pop("receipt_sha256", None)
    if claimed != canonical_sha256(body) \
            or claimed != HOME_AUTHORITY_RECEIPT_SHA256:
        raise RuntimeError("Goal5790 frozen Home-authority receipt drifted")
    expected_identity = {
        "gpu_name": HOME_GPU,
        "driver_version": HOME_DRIVER,
        "gpu_uuid": HOME_UUID,
        "compute_capability": HOME_CC,
        "execution_environment_class": "HOME_PASCAL_FUNCTIONAL_ONLY",
        "modern_rtx_execution_authorized": False,
        "pod_used": False,
    }
    if any(value.get(key) != expected for key, expected in expected_identity.items()):
        raise RuntimeError("Goal5790 frozen Home identity fields drifted")
    toolkit = Path(str(value["cuda_toolkit_resolved_path"]))
    if not toolkit.is_dir() or str(toolkit.resolve()) != str(value[
            "cuda_toolkit_resolved_path"]):
        raise RuntimeError("Goal5790 exact CUDA toolkit root drifted")
    for stem in ("cuda_nvrtc", "cuda_nvrtc_builtins", "cuda_nvvm",
                 "cuda_libdevice"):
        producer = Path(str(value[f"{stem}_resolved_path"]))
        if not producer.is_file() \
                or str(producer.resolve()) != str(value[f"{stem}_resolved_path"]) \
                or _sha_file(producer) != value[f"{stem}_sha256"]:
            raise RuntimeError(f"Goal5790 exact PTX producer drift: {stem}")
    _verify_cuda_host_compiler(value)
    nvcc = toolkit / "bin" / "nvcc"
    nvcc_version = subprocess.run(
        [str(nvcc), "--version"], check=True, text=True,
        capture_output=True).stdout
    if str(value["cuda_nvcc_version"]) not in nvcc_version:
        raise RuntimeError("Goal5790 exact nvcc version drifted")
    return value


def _verify_cuda_host_compiler(
    authority: Mapping[str, object],
) -> Path:
    """Verify the frozen lexical compiler authority without dereferencing it.

    On Home, ``/usr/bin/g++-12`` is an authorized absolute symlink whose target
    is ``/usr/bin/x86_64-linux-gnu-g++-12``.  The symlink spelling controls the
    exact first line printed by ``--version``.  Resolving it before comparison
    therefore rejects the very executable named by the frozen authority.  The
    immutable authority bytes already select the lexical name; admission must
    require that exact absolute name to be a file and execute that name for the
    exact version check, without pretending the dereferenced target string is
    the lexical authority.
    """

    frozen_lexical = str(authority["cuda_host_compiler_path"])
    host_compiler = Path(frozen_lexical)
    if not host_compiler.is_absolute() \
            or str(host_compiler) != frozen_lexical \
            or not host_compiler.is_file():
        raise RuntimeError("Goal5790 exact CUDA host compiler path drifted")
    host_version = subprocess.run(
        [frozen_lexical, "--version"], check=True, text=True,
        capture_output=True).stdout.splitlines()[0].strip()
    if host_version != authority["cuda_host_compiler_version"]:
        raise RuntimeError("Goal5790 exact CUDA host compiler version drifted")
    return host_compiler


def query_exact_home_machine(
    authority: Mapping[str, object],
) -> dict[str, object]:
    line = subprocess.run([
        "nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap",
        "--format=csv,noheader"], check=True, text=True,
        capture_output=True).stdout.strip()
    fields = tuple(item.strip() for item in line.split(","))
    expected = (
        authority["gpu_name"], authority["driver_version"],
        authority["gpu_uuid"], authority["compute_capability"])
    if fields != expected or platform.node() != HOME_HOSTNAME:
        raise RuntimeError(
            f"Goal5790-A1 requires exact Home lx1 authority: "
            f"host={platform.node()!r}, gpu_line={line!r}")
    result: dict[str, object] = {
        "hostname": HOME_HOSTNAME, "gpu": HOME_GPU, "driver": HOME_DRIVER,
        "uuid": HOME_UUID, "compute_capability": HOME_CC,
        "classification": "exact_home_lx1__not_pod",
        "frozen_home_authority_file_sha256": HOME_AUTHORITY_FILE_SHA256,
        "frozen_home_authority_receipt_sha256": authority["receipt_sha256"],
        "home_toolchain_identity_sha256": canonical_sha256({
            field: authority[field] for field in HOME_TOOLCHAIN_FIELDS}),
    }
    result["home_machine_authority_sha256"] = canonical_sha256(result)
    return result


def _load_worker_result(
    path: Path, *, case: Mapping[str, object], arm: str,
    home_machine: Mapping[str, object], execution_spec_sha256: str,
) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "rtdl.goal5790_a1.home_worker.v1" \
            or value.get("status") != "PASS" \
            or value.get("case_id") != case["case_id"] \
            or value.get("case_sha256") != case["case_sha256"] \
            or value.get("arm") != arm \
            or value.get("home_machine") != home_machine \
            or value.get("home_machine_authority_sha256") \
                != home_machine["home_machine_authority_sha256"] \
            or value.get("execution_spec_sha256") != execution_spec_sha256:
        raise RuntimeError(f"worker result identity mismatch: {path}")
    if any(value.get(field) is not False for field in (
            "elapsed_values_recorded",
            "registered_performance_timing_created",
            "performance_claimed", "pod_used", "formal_worker")):
        raise RuntimeError(f"worker exceeded functional scope: {path}")
    cache = value.get("cache_policy")
    if not isinstance(cache, Mapping) \
            or cache.get("formal_leaf_cache_environment_cleared") is not True \
            or cache.get("initially_empty") is not True \
            or cache.get("per_arm_isolated") is not True \
            or cache.get("cache_is_execution_authority") is not False \
            or cache.get("cache_contents_used_as_evidence") is not False:
        raise RuntimeError(f"worker cache governance is incomplete: {path}")
    body = dict(value)
    claimed = body.pop("worker_result_sha256", None)
    if claimed != canonical_sha256(body):
        raise RuntimeError(f"worker result digest mismatch: {path}")
    return value


def build_worker_command(
    *,
    python: str,
    suite: Path,
    output: Path,
    case_id: str,
    arm: str,
    native: Path,
    optix_include: Path,
    cuda_include: Path,
    compute_capability: str,
    optix_sdk: str,
    expected_python: str,
    expected_numba: str,
    expected_numpy: str,
    home_authority_sha256: str,
    home_authority_file: Path,
    home_authority_file_sha256: str,
    execution_spec: Path,
    execution_spec_sha256: str,
) -> list[str]:
    if case_id not in CASE_IDS or arm not in ARMS:
        raise ValueError("unknown Goal5790-A1 worker identity")
    return [
        python, "-m", "scripts.goal5790_a1_home_worker",
        "--suite", str(suite), "--case-id", case_id, "--arm", arm,
        "--output", str(output), "--native", str(native),
        "--optix-include", str(optix_include),
        "--cuda-include", str(cuda_include),
        "--cc", compute_capability, "--optix-sdk", optix_sdk,
        "--expected-python", expected_python,
        "--expected-numba", expected_numba,
        "--expected-numpy", expected_numpy,
        "--home-authority-sha256", home_authority_sha256,
        "--home-authority-file", str(home_authority_file),
        "--home-authority-file-sha256", home_authority_file_sha256,
        "--execution-spec", str(execution_spec),
        "--execution-spec-sha256", execution_spec_sha256,
    ]


def run_controller(
    *,
    suite_path: Path,
    output_root: Path,
    native: Path,
    optix_include: Path,
    cuda_include: Path,
    compute_capability: str,
    optix_sdk: str,
    case_ids: Sequence[str] = CASE_IDS,
    python: str = sys.executable,
    expected_python: str | None = None,
    expected_numba: str | None = None,
    expected_numpy: str | None = None,
    home_machine: Mapping[str, object] | None = None,
    home_authority_path: Path = DEFAULT_HOME_AUTHORITY,
    frozen_home_authority: Mapping[str, object] | None = None,
    execution_spec_path: Path | None = None,
    execution_spec_sha256: str | None = None,
) -> dict[str, object]:
    suite_path = suite_path.resolve()
    native = native.resolve()
    optix_include = optix_include.resolve()
    cuda_include = cuda_include.resolve()
    for path, label in (
        (suite_path, "suite"), (native, "native"),
        (optix_include, "OptiX include"), (cuda_include, "CUDA include"),
    ):
        if not path.exists():
            raise FileNotFoundError(f"{label} path is absent: {path}")
    if output_root.exists():
        raise FileExistsError(output_root)
    if len(set(case_ids)) != len(case_ids) or any(item not in CASE_IDS for item in case_ids):
        raise ValueError("case selection contains unknown or duplicate IDs")

    suite = parse_suite_json(suite_path.read_text(encoding="utf-8"))
    if execution_spec_path is None or execution_spec_sha256 is None:
        raise ValueError("pre-run execution spec path and SHA are required")
    execution_spec_path = execution_spec_path.resolve()
    execution_spec = _load_execution_spec(
        execution_spec_path, suite_sha256=str(suite["suite_sha256"]),
        expected_sha256=execution_spec_sha256)
    by_id = {str(row["case_id"]): row for row in suite["cases"]}
    output_root.mkdir(parents=True)
    raw_root = output_root / "RAW"
    raw_root.mkdir()
    expected_python = expected_python or platform.python_version()
    expected_numba = expected_numba or importlib.metadata.version("numba")
    expected_numpy = expected_numpy or importlib.metadata.version("numpy")
    authority_path = home_authority_path.resolve()
    authority = (
        _verify_frozen_home_authority(authority_path)
        if frozen_home_authority is None else dict(frozen_home_authority))
    if authority.get("receipt_sha256") != HOME_AUTHORITY_RECEIPT_SHA256:
        raise RuntimeError("controller lacks exact frozen Home authority")
    machine = (
        query_exact_home_machine(authority) if home_machine is None
        else dict(home_machine))
    expected_machine = {
        "hostname": HOME_HOSTNAME, "gpu": HOME_GPU, "driver": HOME_DRIVER,
        "uuid": HOME_UUID, "compute_capability": HOME_CC,
        "classification": "exact_home_lx1__not_pod",
        "frozen_home_authority_file_sha256": HOME_AUTHORITY_FILE_SHA256,
        "frozen_home_authority_receipt_sha256": HOME_AUTHORITY_RECEIPT_SHA256,
        "home_toolchain_identity_sha256": canonical_sha256({
            field: authority[field] for field in HOME_TOOLCHAIN_FIELDS}),
    }
    expected_machine["home_machine_authority_sha256"] = canonical_sha256(
        expected_machine)
    if machine != expected_machine or compute_capability != "61":
        raise RuntimeError("controller is not bound to exact Home lx1/CC6.1")

    rows: list[dict[str, object]] = []
    parent_pids: list[int] = []
    for case_id in case_ids:
        case = by_id[case_id]
        arms: dict[str, object] = {}
        for arm in ARMS:
            path = raw_root / f"{_slug(case_id)}__{arm}.json"
            cache_root = output_root / "NON_AUTHORITY_CACHE" / _slug(case_id) / arm
            cupy_cache = cache_root / "cupy"
            numba_cache = cache_root / "numba"
            cupy_cache.mkdir(parents=True)
            numba_cache.mkdir()
            command = build_worker_command(
                python=python, suite=suite_path, output=path,
                case_id=case_id, arm=arm, native=native,
                optix_include=optix_include, cuda_include=cuda_include,
                compute_capability=compute_capability, optix_sdk=optix_sdk,
                expected_python=expected_python,
                expected_numba=expected_numba,
                expected_numpy=expected_numpy,
                home_authority_sha256=str(
                    machine["home_machine_authority_sha256"]),
                home_authority_file=authority_path,
                home_authority_file_sha256=HOME_AUTHORITY_FILE_SHA256,
                execution_spec=execution_spec_path,
                execution_spec_sha256=execution_spec_sha256,
            )
            worker_environment = dict(os.environ)
            for key in tuple(worker_environment):
                if key.startswith("RTDL_V4_FORMAL_LEAF_CACHE"):
                    worker_environment.pop(key)
            worker_environment["CUPY_CACHE_DIR"] = str(cupy_cache.resolve())
            worker_environment["NUMBA_CACHE_DIR"] = str(numba_cache.resolve())
            completed = subprocess.run(
                command, cwd=str(Path(__file__).resolve().parents[1]),
                check=False, text=True, capture_output=True,
                env=worker_environment)
            if completed.returncode != 0:
                raise RuntimeError(
                    f"{case_id}/{arm} failed ({completed.returncode})\n"
                    f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}")
            value = _load_worker_result(
                path, case=case, arm=arm, home_machine=machine,
                execution_spec_sha256=execution_spec_sha256)
            parent_pids.append(int(value["parent_pid"]))
            arms[arm] = value
        if len({int(arms[name]["parent_pid"]) for name in ARMS}) != 3:
            raise RuntimeError(f"{case_id} did not use three fresh parent PIDs")
        rows.append({
            "case_id": case_id,
            "case_sha256": case["case_sha256"],
            "expected_rule_id": case["expected_rule_id"],
            "arms": arms,
        })
    if len(set(parent_pids)) != len(parent_pids):
        raise RuntimeError("one worker PID was reused across suite arms")
    facade_reject_count = sum(
        row["arms"]["product_admission_reject"]["arm_result"].get(
            "production_facade_called") is True
        for row in rows)
    typed_schema_reject_count = sum(
        row["arms"]["product_admission_reject"]["arm_result"].get(
            "product_rejection_gate") == "verify_typed_physical_schema"
        for row in rows)
    expected_typed_schema_rejects = int(CASE_IDS[4] in case_ids)
    if facade_reject_count != len(rows) - expected_typed_schema_rejects \
            or typed_schema_reject_count != expected_typed_schema_rejects:
        raise RuntimeError("Goal5790-A1 rejection-gate partition drifted")

    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PASS",
        "scope": "home_functional_only__zero_registered_timing",
        "suite_sha256": suite["suite_sha256"],
        "suite_file_sha256": _sha_file(suite_path),
        "execution_spec_file_sha256": _sha_file(execution_spec_path),
        "execution_spec_sha256": execution_spec["execution_spec_sha256"],
        "native_library_sha256": _sha_file(native),
        "home_machine": machine,
        "frozen_home_authority_file": authority_path.as_posix(),
        "frozen_home_authority_file_sha256": HOME_AUTHORITY_FILE_SHA256,
        "frozen_home_authority_receipt_sha256": HOME_AUTHORITY_RECEIPT_SHA256,
        "compute_capability": compute_capability,
        "optix_sdk": optix_sdk,
        "case_count": len(rows),
        "arm_count": len(rows) * len(ARMS),
        "fresh_parent_pid_count": len(set(parent_pids)),
        "product_admission_reject_count": len(rows),
        "production_facade_reject_count": facade_reject_count,
        "typed_physical_schema_reject_count": typed_schema_reject_count,
        "product_admission_launch_count": 0,
        "accepted_control_count": len(rows),
        "diagnostic_counterexample_count": len(rows),
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "pod_used": machine["classification"] != "exact_home_lx1__not_pod",
        "formal_worker_count": 0,
        "cache_policy": {
            "formal_leaf_cache_environment_cleared": True,
            "per_arm_cupy_cache": "create_only_isolated_non_authority",
            "per_arm_numba_cache": "create_only_isolated_non_authority",
            "cache_contents_used_as_evidence": False,
        },
        "cases": rows,
    }
    result["result_sha256"] = canonical_sha256(result)
    (output_root / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--cc", choices=("61",), required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument(
        "--home-authority", type=Path, default=DEFAULT_HOME_AUTHORITY)
    parser.add_argument("--execution-spec", required=True, type=Path)
    parser.add_argument("--execution-spec-sha256", required=True)
    parser.add_argument("--case-id", action="append", dest="case_ids")
    args = parser.parse_args()
    result = run_controller(
        suite_path=args.suite, output_root=args.output,
        native=args.native, optix_include=args.optix_include,
        cuda_include=args.cuda_include, compute_capability=args.cc,
        optix_sdk=args.optix_sdk,
        home_authority_path=args.home_authority,
        execution_spec_path=args.execution_spec,
        execution_spec_sha256=args.execution_spec_sha256,
        case_ids=CASE_IDS if args.case_ids is None else tuple(args.case_ids),
    )
    print(json.dumps({
        "status": result["status"], "case_count": result["case_count"],
        "result_sha256": result["result_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
