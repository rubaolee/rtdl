#!/usr/bin/env python3
"""Probe whether a pod is ready to run current RTDL NVIDIA/OptiX packets."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

def _optix_prefix_candidates() -> tuple[Path, ...]:
    raw_candidates = [
        Path(os.environ["OPTIX_PREFIX"]) if os.environ.get("OPTIX_PREFIX") else None,
        Path("/root/vendor/optix-sdk"),
        Path("/root/vendor/optix-dev"),
        Path("/workspace/vendor/optix-sdk"),
        Path("/workspace/vendor/optix-dev"),
        Path("/workspace/vendor/optix-dev-8.0.0"),
        Path.home() / "vendor" / "optix-dev",
    ]
    candidates: list[Path] = []
    seen: set[str] = set()
    for candidate in raw_candidates:
        if candidate is None:
            continue
        normalized = str(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(candidate)
    return tuple(candidates)


def _run(command: list[str], *, timeout: int = 10) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "ok": completed.returncode == 0,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "ok": False,
        }


def _module_status(module: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(module)
    return {"module": module, "available": spec is not None}


def _file_status(path: Path) -> dict[str, Any]:
    return {"path": str(path), "exists": path.exists()}


def _optix_prefix_status() -> dict[str, Any]:
    candidates = _optix_prefix_candidates()
    checked = []
    selected: str | None = None
    for prefix in candidates:
        header = prefix / "include" / "optix.h"
        checked.append(_file_status(header))
        if header.exists() and selected is None:
            selected = str(prefix)
    return {
        "selected_prefix": selected,
        "checked_headers": tuple(checked),
        "available": selected is not None,
    }


def _native_library_status() -> dict[str, Any]:
    env_path = os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB")
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            ROOT / "build" / "librtdl_optix.so",
            ROOT / "build" / "rtdl_optix.dll",
            ROOT / "build" / "librtdl_optix.dylib",
        ]
    )
    checked = tuple(_file_status(path) for path in candidates)
    selected = next((item["path"] for item in checked if item["exists"]), None)
    return {"selected_library": selected, "checked_libraries": checked, "available": selected is not None}


def _build_command(optix_prefix: str | None) -> str:
    prefix = optix_prefix or "$OPTIX_PREFIX"
    cuda_prefix = os.environ.get("RTDL_CUDA_PREFIX") or os.environ.get("CUDA_HOME") or "/usr/local/cuda"
    return f"make build-optix OPTIX_PREFIX={prefix} CUDA_PREFIX={cuda_prefix}"


def probe() -> dict[str, Any]:
    nvidia_smi_path = shutil.which("nvidia-smi")
    nvcc_path = shutil.which("nvcc")
    make_path = shutil.which("make")
    gpp_path = shutil.which("g++") or shutil.which("c++")
    optix = _optix_prefix_status()
    library = _native_library_status()

    checks = {
        "nvidia_smi": {
            "path": nvidia_smi_path,
            "available": nvidia_smi_path is not None,
            "probe": _run(["nvidia-smi"], timeout=20) if nvidia_smi_path else None,
        },
        "nvcc": {
            "path": nvcc_path,
            "available": nvcc_path is not None,
            "probe": _run(["nvcc", "--version"], timeout=10) if nvcc_path else None,
        },
        "make": {"path": make_path, "available": make_path is not None},
        "cxx": {"path": gpp_path, "available": gpp_path is not None},
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "modules": {
            "numpy": _module_status("numpy"),
            "cupy": _module_status("cupy"),
            "numba": _module_status("numba"),
        },
        "optix_headers": optix,
        "rtdl_optix_library": library,
    }

    blockers = []
    for key in ("nvidia_smi", "nvcc", "make", "cxx"):
        if not checks[key]["available"]:
            blockers.append(f"{key} unavailable")
    if not optix["available"]:
        blockers.append("OptiX headers unavailable")
    if not checks["modules"]["numpy"]["available"]:
        blockers.append("numpy unavailable")
    warnings = []
    if not checks["modules"]["cupy"]["available"]:
        warnings.append("cupy unavailable: partner comparison rows will fail")
    if not checks["modules"]["numba"]["available"]:
        warnings.append("numba unavailable: Numba continuation rows will fail")
    if not library["available"]:
        warnings.append("librtdl_optix unavailable: run the build command before hardware packets")

    return {
        "tool": "rtdl_pod_bootstrap_probe",
        "repo": str(ROOT),
        "status": "ready" if not blockers and library["available"] else "not_ready",
        "checks": checks,
        "blockers": tuple(blockers),
        "warnings": tuple(warnings),
        "recommended_build_command": _build_command(optix["selected_prefix"]),
        "recommended_validation_command": (
            "PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so "
            "python scripts/rtdl_v2_10_pod_validation_bundle.py "
            "--run-front-door --run-scale-profile "
            "--output-dir docs/reports/v2_10_pod_validation_bundle_pod"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
    }


def _print_text(payload: dict[str, Any]) -> None:
    print("RTDL Pod Bootstrap Probe")
    print(f"repo: {payload['repo']}")
    print(f"status: {payload['status']}")
    checks = payload["checks"]
    for name in ("nvidia_smi", "nvcc", "make", "cxx"):
        value = checks[name]
        status = "PASS" if value["available"] else "WARN"
        print(f"[{status}] {name}: {value.get('path') or 'not found'}")
    print(f"[{'PASS' if checks['optix_headers']['available'] else 'WARN'}] optix headers: {checks['optix_headers']['selected_prefix'] or 'not found'}")
    print(f"[{'PASS' if checks['rtdl_optix_library']['available'] else 'WARN'}] librtdl_optix: {checks['rtdl_optix_library']['selected_library'] or 'not found'}")
    for name, value in checks["modules"].items():
        print(f"[{'PASS' if value['available'] else 'WARN'}] python module {name}")
    if payload["blockers"]:
        print("blockers:")
        for item in payload["blockers"]:
            print(f"- {item}")
    if payload["warnings"]:
        print("warnings:")
        for item in payload["warnings"]:
            print(f"- {item}")
    print("build:")
    print(payload["recommended_build_command"])
    print("validate:")
    print(payload["recommended_validation_command"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--strict", action="store_true", help="return nonzero if not ready")
    args = parser.parse_args(argv)

    payload = probe()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_text(payload)
    return 1 if args.strict and payload["status"] != "ready" else 0


if __name__ == "__main__":
    raise SystemExit(main())
