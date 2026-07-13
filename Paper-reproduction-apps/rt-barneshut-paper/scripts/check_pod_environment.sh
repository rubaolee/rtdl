#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
RUN_DIR="${APP_DIR}/_runs/pod_preflight"
PYTHON="${PYTHON:-python3}"
detect_optix_root_dir() {
  if [ -n "${OPTIX_ROOT_DIR:-}" ]; then
    printf '%s\n' "${OPTIX_ROOT_DIR}"
    return
  fi
  if [ -n "${OPTIX_PREFIX:-}" ]; then
    printf '%s\n' "${OPTIX_PREFIX}"
    return
  fi
  if [ -n "${OptiX_INSTALL_DIR:-}" ]; then
    printf '%s\n' "${OptiX_INSTALL_DIR}"
    return
  fi
  for candidate in \
    /root/vendor/optix-dev \
    /root/vendor/optix-sdk \
    /workspace/vendor/optix-dev \
    /workspace/vendor/optix-sdk \
    /workspace/vendor/optix-dev-9.0.0 \
    /workspace/vendor/optix-dev-8.1.0 \
    /workspace/vendor/optix-dev-8.0.0 \
    /opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64 \
    /opt/optix; do
    if [ -f "${candidate}/include/optix.h" ]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done
  printf '%s\n' "/opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64"
}

OPTIX_ROOT_DIR="$(detect_optix_root_dir)"

detect_cuda_prefix() {
  if [ -n "${CUDA_PREFIX:-}" ]; then
    printf '%s\n' "${CUDA_PREFIX}"
    return
  fi
  if [ -n "${CUDA_HOME:-}" ] && [ -x "${CUDA_HOME}/bin/nvcc" ]; then
    printf '%s\n' "${CUDA_HOME}"
    return
  fi
  for candidate in /usr/local/cuda /usr/local/cuda-13.0 /usr/local/cuda-12.8 /usr/local/cuda-12.6 /usr/local/cuda-12.5; do
    if [ -x "${candidate}/bin/nvcc" ]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done
  printf '%s\n' "/usr/local/cuda"
}

CUDA_PREFIX="$(detect_cuda_prefix)"

mkdir -p "${RUN_DIR}"

cd "${ROOT_DIR}"

"${PYTHON}" - "${RUN_DIR}/pod_environment_preflight.json" "${OPTIX_ROOT_DIR}" "${CUDA_PREFIX}" <<'PY'
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def run_command(args: list[str]) -> dict[str, object]:
    executable = shutil.which(args[0])
    if executable is None:
        return {
            "available": False,
            "command": args,
            "returncode": None,
            "stdout": "",
            "stderr": f"{args[0]} not found on PATH",
        }
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {
        "available": True,
        "command": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


summary_path = Path(sys.argv[1])
optix_root = Path(sys.argv[2])
cuda_prefix = Path(sys.argv[3])

checks: dict[str, object] = {
    "python": {
        "executable": sys.executable,
        "version": sys.version,
    },
    "commands": {
        "git": run_command(["git", "--version"]),
        "cmake": run_command(["cmake", "--version"]),
        "nvidia_smi": run_command(["nvidia-smi"]),
        "nvcc": run_command([str(cuda_prefix / "bin" / "nvcc"), "--version"]),
    },
    "paths": {
        "optix_root": str(optix_root),
        "optix_header_exists": (optix_root / "include" / "optix.h").exists(),
        "cuda_prefix": str(cuda_prefix),
        "nvcc_exists": (cuda_prefix / "bin" / "nvcc").exists(),
    },
}

torch_payload: dict[str, object] = {"installed": importlib.util.find_spec("torch") is not None}
if torch_payload["installed"]:
    try:
        import torch  # type: ignore

        torch_payload.update(
            {
                "version": getattr(torch, "__version__", None),
                "cuda_available": bool(torch.cuda.is_available()),
                "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
                "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            }
        )
    except Exception as exc:  # pragma: no cover - diagnostic path
        torch_payload.update({"import_error": repr(exc), "cuda_available": False})
checks["torch"] = torch_payload

required = {
    "git": bool(checks["commands"]["git"]["available"] and checks["commands"]["git"]["returncode"] == 0),
    "cmake": bool(checks["commands"]["cmake"]["available"] and checks["commands"]["cmake"]["returncode"] == 0),
    "nvidia_smi": bool(checks["commands"]["nvidia_smi"]["available"] and checks["commands"]["nvidia_smi"]["returncode"] == 0),
    "nvcc": bool(checks["commands"]["nvcc"]["available"] and checks["commands"]["nvcc"]["returncode"] == 0),
    "optix_header": bool(checks["paths"]["optix_header_exists"]),
    "torch_cuda": bool(torch_payload.get("cuda_available", False)),
}

payload = {
    "mode": "rt_barneshut_pod_environment_preflight",
    "ready_for_author_build": all(required[key] for key in ("git", "cmake", "nvidia_smi", "nvcc", "optix_header")),
    "ready_for_rtdl_cuda_gate": all(required[key] for key in ("nvidia_smi", "torch_cuda")),
    "required": required,
    "checks": checks,
    "claim_boundary": (
        "Environment preflight only. Passing this check does not prove RT-BarnesHut "
        "paper reproduction; it only verifies that the POD has the expected build "
        "and CUDA runtime tools."
    ),
}
summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(summary_path)
raise SystemExit(0 if payload["ready_for_author_build"] and payload["ready_for_rtdl_cuda_gate"] else 2)
PY
