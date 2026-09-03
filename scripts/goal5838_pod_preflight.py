#!/usr/bin/env python3
"""Audit a pod before the frozen Goal5838 GPU exam.

This script performs no native build and no GPU launch.  A failed check is a
repairable environment/readiness result, never a scientific Goal5838 failure.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from scripts.goal5838_build_selected_sphere_optix_provider import (
    OPTIX_RUNTIME_ABI_PROBE_SOURCE as _OPTIX_RUNTIME_ABI_PROBE_SOURCE,
)
from scripts.goal5838_build_selected_sphere_optix_provider import (
    probe_optix_runtime_abi,
)

OPTIX_RUNTIME_ABI_PROBE_SOURCE = _OPTIX_RUNTIME_ABI_PROBE_SOURCE

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "0f5c9d4297f73e412732e5a8ab133423fe4cfd21"
KNOWN_OPTIX_DEV_RELEASES = {
    "7.7.0": "7b5c4e8608b8b4b601729f6240fc3fd53cb36d23",
    "8.0.0": "f60c1e44f18426f426a2ed948f28515b3cf67b8a",
    "8.1.0": "50021ea0af6d41609a97777ceebbdf1e1d34efe7",
    "9.0.0": "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd",
    "9.1.0": "f1f6dd803f3159992d248178f6e09421c6eb8b6d",
}
EXPECTED_PACKAGE_VERSIONS = {"numba": "0.65.1", "numpy": "2.4.4"}
FOCUSED_TEST_MODULES = (
    "tests.goal5838_preregistration_test",
    "tests.goal5838_generic_family_lifecycle_test",
    "tests.goal5838_core_seal_and_selection_test",
    "tests.goal5838_family_route_migration_test",
    "tests.goal5838_selected_sphere_any_hit_count_test",
    "tests.goal5838_pod_preflight_test",
)
OPTIX_HEADERS = (
    "optix.h",
    "optix_device.h",
    "optix_function_table_definition.h",
    "optix_stack_size.h",
    "optix_stubs.h",
)
CUDA_HEADERS = ("cuda.h", "cuda_runtime.h", "nvrtc.h")
RESULT_DOMAIN = "rtdl.goal5838.pod_preflight.v1"
PASS_STATUS = (
    "PASS__GOAL5838_POD_READY_FOR_FROZEN_GPU_EXAM"
    "__NO_GPU_EXECUTION_CLAIM"
)
REPAIR_STATUS = (
    "REPAIR_REQUIRED__GOAL5838_POD_ENVIRONMENT_NOT_READY"
    "__NOT_SCIENTIFIC_FAILURE"
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_full_commit(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("--expected-commit must be a full lowercase commit id")
    return value


def _parse_driver_major(value: str) -> int:
    match = re.fullmatch(r"([0-9]+)(?:\.[0-9]+)+", value.strip())
    if match is None:
        raise ValueError(f"invalid NVIDIA driver version: {value!r}")
    return int(match.group(1))


def _parse_compute_capability(value: str) -> tuple[int, int]:
    match = re.fullmatch(
        r"([1-9][0-9]?)\.((?:0|[1-9][0-9]?))", value.strip()
    )
    if match is None:
        raise ValueError(f"invalid compute capability: {value!r}")
    major, minor = (int(part) for part in match.groups())
    if major == 0:
        raise ValueError(f"invalid compute capability: {value!r}")
    return major, minor


def _parse_gpu_rows(output: str) -> list[dict[str, str]]:
    fields = ("name", "uuid", "driver_version", "compute_capability")
    result = []
    for raw_row in output.splitlines():
        if not raw_row.strip():
            continue
        values = tuple(part.strip() for part in raw_row.split(","))
        if len(values) != len(fields) or any(not value for value in values):
            raise ValueError(f"unexpected nvidia-smi row: {raw_row!r}")
        row = dict(zip(fields, values, strict=True))
        _parse_driver_major(row["driver_version"])
        _parse_compute_capability(row["compute_capability"])
        result.append(row)
    return result


def _parse_optix_version(path: Path) -> int:
    match = re.search(
        r"^\s*#\s*define\s+OPTIX_VERSION\s+([0-9]+)\s*$",
        path.read_text(encoding="utf-8", errors="strict"),
        re.MULTILINE,
    )
    if match is None:
        raise ValueError(f"OPTIX_VERSION is absent from {path}")
    return int(match.group(1))


def _optix_sdk_number(value: str) -> int:
    match = re.fullmatch(
        (
            r"([1-9][0-9]?)\.((?:0|[1-9][0-9]?))\."
            r"((?:0|[1-9][0-9]?))"
        ),
        value,
    )
    if match is None:
        raise ValueError(f"invalid OptiX SDK version: {value!r}")
    major, minor, patch = (int(part) for part in match.groups())
    if major == 0 or minor >= 100 or patch >= 100:
        raise ValueError(f"invalid OptiX SDK version: {value!r}")
    return major * 10000 + minor * 100 + patch


def _capture(
    command: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return {
            "command": command,
            "command_display": shlex.join(command),
            "returncode": completed.returncode,
            "output_tail": completed.stdout[-12000:],
        }
    except OSError as exc:
        return {
            "command": command,
            "command_display": shlex.join(command),
            "returncode": -1,
            "output_tail": f"{type(exc).__name__}: {exc}",
        }


def _check(
    rows: list[dict[str, object]],
    name: str,
    passed: bool,
    *,
    requirement: str,
    observed: object,
    repair: str,
    required: bool = True,
) -> None:
    rows.append(
        {
            "name": name,
            "required": required,
            "passed": bool(passed),
            "requirement": requirement,
            "observed": observed,
            "repair": "" if passed else repair,
        }
    )


def _external_path(path: Path, *, root: Path = ROOT) -> Path:
    result = path.expanduser().resolve()
    repository = root.resolve()
    if result == repository or repository in result.parents:
        raise ValueError(f"preflight/evidence path must be outside Git tree: {result}")
    return result


def _write_json_exclusive(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            raise FileExistsError(path) from None
    finally:
        temporary.unlink(missing_ok=True)


def _discover_host_compiler(requested: Path | None) -> Path | None:
    if requested is not None:
        candidate = requested.expanduser().resolve()
        return candidate if candidate.is_file() and os.access(candidate, os.X_OK) else None
    for name in ("g++-13", "g++-12", "g++-11", "g++"):
        candidate = shutil.which(name)
        if candidate is not None:
            return Path(candidate).resolve()
    return None


def _header_inventory(
    include: Path, names: tuple[str, ...]
) -> list[dict[str, object]]:
    rows = []
    for name in names:
        path = include / name
        if path.is_file():
            rows.append(
                {
                    "name": name,
                    "path": str(path.resolve()),
                    "bytes": path.stat().st_size,
                    "sha256": _file_sha256(path),
                }
            )
    return rows


def _artifact_paths(directory: Path) -> dict[str, Path]:
    return {
        "native": directory / "librtdl_optix_goal5838.so",
        "native_build_manifest": directory / "goal5838_native_build.json",
        "native_build_log": directory / "goal5838_native_build.log",
        "gpu_exam": directory / "goal5838_gpu_exam.json",
        "verification": directory / "goal5838_gpu_exam_verification.json",
    }


def _require_distinct_receipt(
    output: Path, artifacts: dict[str, Path]
) -> None:
    if output in artifacts.values():
        raise ValueError("preflight receipt must differ from generated artifacts")


def _command_plan(
    *,
    python: Path,
    cuda_prefix: Path,
    optix_prefix: Path,
    host_compiler: Path,
    optix_sdk: str,
    compute_capability: str,
    expected_commit: str,
    artifacts: dict[str, Path],
) -> dict[str, dict[str, object]]:
    prefix = [
        "env",
        "CUDA_VISIBLE_DEVICES=0",
        "PYTHONPATH=src:.",
        str(python),
    ]
    build = [
        *prefix,
        "scripts/goal5838_build_selected_sphere_optix_provider.py",
        "--cuda-prefix",
        str(cuda_prefix),
        "--optix-prefix",
        str(optix_prefix),
        "--expected-optix-sdk",
        optix_sdk,
        "--compute-capability",
        compute_capability,
        "--host-compiler",
        str(host_compiler),
        "--expected-commit",
        expected_commit,
        "--output",
        str(artifacts["native"]),
        "--manifest",
        str(artifacts["native_build_manifest"]),
        "--log",
        str(artifacts["native_build_log"]),
    ]
    run = [
        *prefix,
        "scripts/goal5838_run_selected_sphere_gpu_exam.py",
        "--native",
        str(artifacts["native"]),
        "--native-build-manifest",
        str(artifacts["native_build_manifest"]),
        "--optix-include",
        str(optix_prefix / "include"),
        "--cuda-include",
        str(cuda_prefix / "include"),
        "--optix-sdk",
        optix_sdk,
        "--compute-capability",
        compute_capability,
        "--expected-commit",
        expected_commit,
        "--output",
        str(artifacts["gpu_exam"]),
    ]
    verify = [
        str(python),
        "scripts/goal5838_verify_selected_sphere_gpu_exam.py",
        "--artifact",
        str(artifacts["gpu_exam"]),
        "--native",
        str(artifacts["native"]),
        "--output",
        str(artifacts["verification"]),
    ]
    return {
        name: {"argv": command, "display": shlex.join(command)}
        for name, command in (("build", build), ("run", run), ("verify", verify))
    }


def _git_probe(*arguments: str) -> dict[str, object]:
    return _capture(["git", *arguments])


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def run_preflight(args: argparse.Namespace) -> dict[str, object]:
    expected_commit = _require_full_commit(args.expected_commit)
    expected_optix_version = _optix_sdk_number(args.expected_optix_sdk)
    output = _external_path(args.output)
    artifact_dir = _external_path(args.artifact_dir)
    if output.exists():
        raise FileExistsError(output)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifacts = _artifact_paths(artifact_dir)
    _require_distinct_receipt(output, artifacts)

    checks: list[dict[str, object]] = []
    probes: dict[str, object] = {}

    head_probe = _git_probe("rev-parse", "HEAD")
    head = str(head_probe["output_tail"]).strip()
    probes["git_head"] = head_probe
    _check(
        checks,
        "exact_expected_commit",
        head_probe["returncode"] == 0 and head == expected_commit,
        requirement=expected_commit,
        observed=head,
        repair="fetch and checkout the exact pushed Goal5838 commit",
    )

    status_probe = _git_probe("status", "--porcelain=v1", "--untracked-files=all")
    dirty = str(status_probe["output_tail"]).strip()
    probes["git_status"] = status_probe
    _check(
        checks,
        "clean_worktree",
        status_probe["returncode"] == 0 and not dirty,
        requirement="no tracked or untracked changes",
        observed=dirty,
        repair="use a fresh checkout; do not discard unreviewed work",
    )

    baseline_probe = _git_probe("cat-file", "-e", f"{BASELINE_COMMIT}^{{commit}}")
    probes["baseline_commit"] = baseline_probe
    _check(
        checks,
        "preregistered_baseline_object_present",
        baseline_probe["returncode"] == 0,
        requirement=BASELINE_COMMIT,
        observed=baseline_probe["returncode"],
        repair=f"git fetch --depth=1 origin {BASELINE_COMMIT}",
    )

    python_path = Path(os.path.abspath(sys.executable))
    _check(
        checks,
        "python_3_12",
        sys.version_info[:2] == (3, 12),
        requirement="Python 3.12.x",
        observed=platform.python_version(),
        repair="create and activate a Python 3.12 environment",
    )
    package_versions = {
        name: _package_version(name) for name in EXPECTED_PACKAGE_VERSIONS
    }
    for name, expected in EXPECTED_PACKAGE_VERSIONS.items():
        _check(
            checks,
            f"python_package_{name}",
            package_versions[name] == expected,
            requirement=expected,
            observed=package_versions[name],
            repair=f"install {name}=={expected} into {python_path}",
        )

    nvidia_smi = shutil.which("nvidia-smi")
    gpu_probe = (
        _capture(
            [
                nvidia_smi,
                "--id=0",
                "--query-gpu=name,uuid,driver_version,compute_cap",
                "--format=csv,noheader,nounits",
            ]
        )
        if nvidia_smi is not None
        else {
            "command": ["nvidia-smi"],
            "command_display": "nvidia-smi",
            "returncode": -1,
            "output_tail": "nvidia-smi not found",
        }
    )
    probes["gpu_identity"] = gpu_probe
    try:
        gpu_rows = (
            _parse_gpu_rows(str(gpu_probe["output_tail"]))
            if gpu_probe["returncode"] == 0
            else []
        )
    except ValueError as exc:
        gpu_rows = []
        probes["gpu_parse_error"] = str(exc)
    _check(
        checks,
        "selected_nvidia_gpu_zero",
        len(gpu_rows) == 1,
        requirement="nvidia-smi GPU index 0 resolves to exactly one GPU",
        observed=gpu_rows,
        repair="repair NVIDIA container visibility; multiple GPUs are allowed",
    )
    gpu = gpu_rows[0] if len(gpu_rows) == 1 else None
    compute_capability = None if gpu is None else gpu["compute_capability"]
    requested_capability = args.compute_capability
    capability_matches = compute_capability is not None and (
        requested_capability is None or compute_capability == requested_capability
    )
    _check(
        checks,
        "compute_capability_identified",
        capability_matches,
        requirement=(
            "a parseable visible-GPU capability"
            if requested_capability is None
            else requested_capability
        ),
        observed=compute_capability,
        repair="query the visible GPU and pass its exact compute capability",
    )

    cuda_prefix = args.cuda_prefix.expanduser().resolve()
    optix_prefix = args.optix_prefix.expanduser().resolve()
    nvcc = cuda_prefix / "bin" / "nvcc"
    cuda_include = cuda_prefix / "include"
    optix_include = optix_prefix / "include"
    _check(
        checks,
        "nvcc_executable",
        nvcc.is_file() and os.access(nvcc, os.X_OK),
        requirement=str(nvcc),
        observed=nvcc.exists(),
        repair="install a CUDA toolkit compatible with the visible GPU",
    )
    if nvcc.is_file() and os.access(nvcc, os.X_OK):
        probes["nvcc_version"] = _capture([str(nvcc), "--version"])
        _check(
            checks,
            "nvcc_version_probe",
            probes["nvcc_version"]["returncode"] == 0,
            requirement="nvcc --version succeeds",
            observed=probes["nvcc_version"],
            repair="repair the CUDA toolkit installation",
        )

    missing_cuda_headers = [
        name for name in CUDA_HEADERS if not (cuda_include / name).is_file()
    ]
    _check(
        checks,
        "cuda_build_headers",
        not missing_cuda_headers,
        requirement=list(CUDA_HEADERS),
        observed={"include": str(cuda_include), "missing": missing_cuda_headers},
        repair="point --cuda-prefix at a complete CUDA toolkit",
    )
    cuda_library_dirs = tuple(
        path
        for path in (
            cuda_prefix / "lib64",
            cuda_prefix / "targets/x86_64-linux/lib",
        )
        if path.is_dir()
    )
    nvrtc_libraries = [
        str(path)
        for directory in cuda_library_dirs
        for path in sorted(directory.glob("libnvrtc.so*"))
        if path.is_file()
    ]
    _check(
        checks,
        "nvrtc_link_library",
        bool(nvrtc_libraries),
        requirement="libnvrtc.so in the selected CUDA toolkit",
        observed=nvrtc_libraries,
        repair="install the CUDA NVRTC runtime/development library",
    )

    missing_optix_headers = [
        name for name in OPTIX_HEADERS if not (optix_include / name).is_file()
    ]
    _check(
        checks,
        "optix_build_headers",
        not missing_optix_headers,
        requirement=list(OPTIX_HEADERS),
        observed={"include": str(optix_include), "missing": missing_optix_headers},
        repair=(
            "acquire a complete OptiX header set compatible with this pod, "
            "then pass its exact version"
        ),
    )
    optix_h = optix_include / "optix.h"
    try:
        optix_version = _parse_optix_version(optix_h) if optix_h.is_file() else None
    except ValueError as exc:
        optix_version = None
        probes["optix_version_parse_error"] = str(exc)
    _check(
        checks,
        "optix_header_version",
        optix_version == expected_optix_version,
        requirement=expected_optix_version,
        observed=optix_version,
        repair=(
            "make --expected-optix-sdk match the selected headers, or select "
            "another exact SDK candidate"
        ),
    )
    optix_header_inventory = _header_inventory(optix_include, OPTIX_HEADERS)
    cuda_header_inventory = _header_inventory(cuda_include, CUDA_HEADERS)
    optix_git_probe = (
        _capture(["git", "-C", str(optix_prefix), "rev-parse", "HEAD"])
        if (optix_prefix / ".git").exists()
        else None
    )
    probes["optix_git_head"] = optix_git_probe
    if optix_git_probe is not None:
        optix_git_head = str(optix_git_probe["output_tail"]).strip()
        known_commit = KNOWN_OPTIX_DEV_RELEASES.get(args.expected_optix_sdk)
        _check(
            checks,
            "known_optix_dev_commit",
            known_commit is None
            or (
                optix_git_probe["returncode"] == 0
                and optix_git_head == known_commit
            ),
            requirement=(
                "exact header hashes"
                if known_commit is None
                else known_commit
            ),
            observed=optix_git_head,
            repair="checkout the recorded exact optix-dev release commit",
            required=False,
        )
    else:
        _check(
            checks,
            "known_optix_dev_commit",
            True,
            requirement="Git identity when available; otherwise exact header hashes",
            observed="non-Git SDK/header distribution",
            repair="",
            required=False,
        )

    host_compiler = _discover_host_compiler(args.host_compiler)
    _check(
        checks,
        "host_compiler",
        host_compiler is not None,
        requirement="an executable g++-13/g++-12/g++-11/g++",
        observed=None if host_compiler is None else str(host_compiler),
        repair="install g++ and pass --host-compiler if discovery is ambiguous",
    )
    abi_probe = None
    if (
        host_compiler is not None
        and not missing_optix_headers
        and not missing_cuda_headers
    ):
        abi_probe = probe_optix_runtime_abi(
            host_compiler, optix_include, cuda_include
        )
    probes["optix_runtime_abi"] = abi_probe
    _check(
        checks,
        "optix_runtime_abi",
        abi_probe is not None and abi_probe["passed"] is True,
        requirement=(
            "a zero-launch optixInit() probe succeeds for the exact selected "
            "headers and host driver"
        ),
        observed=abi_probe,
        repair=(
            "select another compatible OptiX SDK/header release and rerun; "
            "do not classify an ABI mismatch as scientific failure"
        ),
    )
    required_tools = {name: shutil.which(name) for name in ("nm", "ldd")}
    for name, path in required_tools.items():
        _check(
            checks,
            f"tool_{name}",
            path is not None,
            requirement=name,
            observed=path,
            repair=f"install the package that provides {name}",
        )

    python_env = dict(os.environ)
    python_env["PYTHONPATH"] = "src:."
    gate_commands = {
        "freeze": [
            str(python_path),
            "scripts/goal5838_freeze_generic_core.py",
            "--verify-stored",
        ],
        "selection": [
            str(python_path),
            "scripts/goal5838_select_challenge.py",
            "--verify-stored",
        ],
        "focused_tests": [
            str(python_path),
            "-m",
            "unittest",
            *FOCUSED_TEST_MODULES,
        ],
    }
    for name, command in gate_commands.items():
        probe = _capture(command, env=python_env)
        probes[f"gate_{name}"] = probe
        _check(
            checks,
            f"local_gate_{name}",
            probe["returncode"] == 0,
            requirement=f"{name} gate exits zero",
            observed=probe,
            repair=f"diagnose and repair the mutable Goal5838 {name} gate",
        )

    for name, path in artifacts.items():
        _check(
            checks,
            f"fresh_artifact_path_{name}",
            not path.exists(),
            requirement=f"nonexistent exclusive output {path}",
            observed=path.exists(),
            repair="choose a fresh external artifact directory",
        )

    required_failures = [
        str(row["name"])
        for row in checks
        if row["required"] and not row["passed"]
    ]
    ready = not required_failures
    command_plan = None
    if compute_capability is not None and host_compiler is not None:
        command_plan = _command_plan(
            python=python_path,
            cuda_prefix=cuda_prefix,
            optix_prefix=optix_prefix,
            host_compiler=host_compiler,
            optix_sdk=args.expected_optix_sdk,
            compute_capability=compute_capability,
            expected_commit=expected_commit,
            artifacts=artifacts,
        )
    result = {
        "schema": RESULT_DOMAIN,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "status": PASS_STATUS if ready else REPAIR_STATUS,
        "ready_for_gpu_exam": ready,
        "scientific_failure_claimed": False,
        "gpu_execution_performed": False,
        "performance_claim_authorized": False,
        "expected_commit": expected_commit,
        "baseline_commit": BASELINE_COMMIT,
        "expected_optix_sdk": args.expected_optix_sdk,
        "expected_optix_version": expected_optix_version,
        "python": {
            "executable": str(python_path),
            "version": platform.python_version(),
            "packages": package_versions,
        },
        "gpu": gpu,
        "paths": {
            "repository": str(ROOT),
            "cuda_prefix": str(cuda_prefix),
            "optix_prefix": str(optix_prefix),
            "optix_header_inventory": optix_header_inventory,
            "cuda_header_inventory": cuda_header_inventory,
            "artifact_dir": str(artifact_dir),
            "artifacts": {name: str(path) for name, path in artifacts.items()},
        },
        "checks": checks,
        "repair_required_checks": required_failures,
        "probes": probes,
        "command_plan": command_plan,
        "boundary": (
            "This receipt establishes pod readiness only. A non-ready result is "
            "repairable engineering, not scientific failure. A ready result is "
            "not a native build, GPU execution, performance result, Paper App, "
            "external review, consensus, or Goal5838 completion claim."
        ),
        "result_sha256": "",
    }
    result["result_sha256"] = _digest(result)
    _write_json_exclusive(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cuda-prefix", type=Path, required=True)
    parser.add_argument("--optix-prefix", type=Path, required=True)
    parser.add_argument("--expected-optix-sdk", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--compute-capability")
    parser.add_argument("--host-compiler", type=Path)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_preflight(args)
    print(
        json.dumps(
            {
                "status": result["status"],
                "ready_for_gpu_exam": result["ready_for_gpu_exam"],
                "repair_required_checks": result["repair_required_checks"],
                "result_sha256": result["result_sha256"],
            },
            sort_keys=True,
        )
    )
    plan = result["command_plan"]
    if result["ready_for_gpu_exam"] and isinstance(plan, dict):
        for name in ("build", "run", "verify"):
            print(f"{name}: {plan[name]['display']}")
    print(f"output={args.output.expanduser().resolve()}")
    return 0 if result["ready_for_gpu_exam"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
