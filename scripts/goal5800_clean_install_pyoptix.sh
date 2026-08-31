#!/usr/bin/env bash
# Install the clean-built PyOptiX wheel and pinned runtime dependencies into a
# fresh venv. This transaction executes no workload and records no timing.

set -euo pipefail

if [[ "$#" -ne 3 ]]; then
  echo "usage: $0 BASE_PYTHON PYOPTIX_WHEEL OUTPUT_ROOT" >&2
  exit 2
fi

BASE_PYTHON="$1"
PYOPTIX_WHEEL="$2"
OUTPUT_ROOT="$3"
EXPECTED_EXTENSION_SHA256="2e546d0daa497511c878dfd97c93266689ba4a3de1f563d4732137ac23ba0a36"

if [[ -e "$OUTPUT_ROOT" ]]; then
  echo "refusing to reuse output root: $OUTPUT_ROOT" >&2
  exit 3
fi
if [[ ! -x "$BASE_PYTHON" || ! -f "$PYOPTIX_WHEEL" ]]; then
  echo "missing base Python or clean-built wheel" >&2
  exit 4
fi

mkdir -p "$OUTPUT_ROOT/logs"
# The Home Linux image intentionally lacks the Debian python3.12-venv package
# and the account has no passwordless sudo. Bootstrap a pinned user-space
# virtualenv implementation instead of mutating the host Python installation.
"$BASE_PYTHON" -m pip install \
  --target "$OUTPUT_ROOT/virtualenv_bootstrap" \
  --report "$OUTPUT_ROOT/virtualenv_bootstrap_install_report.json" \
  "virtualenv==20.35.4" \
  > "$OUTPUT_ROOT/logs/virtualenv_bootstrap_stdout.txt" \
  2> "$OUTPUT_ROOT/logs/virtualenv_bootstrap_stderr.txt"
PYTHONPATH="$OUTPUT_ROOT/virtualenv_bootstrap" \
  "$BASE_PYTHON" -m virtualenv --no-download "$OUTPUT_ROOT/venv" \
  > "$OUTPUT_ROOT/logs/virtualenv_create_stdout.txt" \
  2> "$OUTPUT_ROOT/logs/virtualenv_create_stderr.txt"
PYTHON="$OUTPUT_ROOT/venv/bin/python"

INSTALL_COMMAND=(
  "$PYTHON" -m pip install
  --report "$OUTPUT_ROOT/install_report.json"
  "$PYOPTIX_WHEEL"
  "numpy==2.4.4"
  "cupy-cuda12x==14.0.1"
  "cuda-python==12.9.7"
  "cuda-bindings==12.9.7"
  "cuda-pathfinder==1.6.1"
)
printf '%q ' "${INSTALL_COMMAND[@]}" > "$OUTPUT_ROOT/logs/install_command.shell"
printf '\n' >> "$OUTPUT_ROOT/logs/install_command.shell"
set +e
"${INSTALL_COMMAND[@]}" \
  > >(tee "$OUTPUT_ROOT/logs/install_stdout.txt") \
  2> >(tee "$OUTPUT_ROOT/logs/install_stderr.txt" >&2)
INSTALL_EXIT_CODE=$?
set -e
printf '%s\n' "$INSTALL_EXIT_CODE" > "$OUTPUT_ROOT/logs/install_exit_code.txt"
if [[ "$INSTALL_EXIT_CODE" -ne 0 ]]; then
  echo "clean PyOptiX environment installation failed" >&2
  exit "$INSTALL_EXIT_CODE"
fi

"$PYTHON" - "$OUTPUT_ROOT" "$PYOPTIX_WHEEL" \
  "$EXPECTED_EXTENSION_SHA256" <<'PY'
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

out = Path(sys.argv[1]).resolve()
wheel = Path(sys.argv[2]).resolve()
expected_extension_sha = sys.argv[3]

import cupy as cp
import numpy as np
import optix

extension_module = sys.modules.get("optix._optix")
if extension_module is None or not getattr(extension_module, "__file__", None):
    raise RuntimeError("optix._optix is not loaded")
extension = Path(extension_module.__file__).resolve()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


extension_sha = sha256(extension)
if extension_sha != expected_extension_sha:
    raise RuntimeError(
        f"clean-installed extension identity mismatch: {extension_sha}")
if tuple(int(value) for value in optix.version()) != (9, 0, 0):
    raise RuntimeError(f"unexpected compatibility API: {optix.version()}")

distributions = {}
for query in (
        "pyoptix", "numpy", "cupy-cuda12x", "cuda-python",
        "cuda-bindings", "cuda-pathfinder"):
    distribution = importlib.metadata.distribution(query)
    distributions[query] = {
        "canonical_name": distribution.metadata["Name"],
        "version": distribution.version,
    }

completed = subprocess.run(
    [str(out / "venv/bin/python"), "-m", "pip", "freeze", "--all"],
    check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
)
(out / "pip_freeze.txt").write_text(completed.stdout, encoding="utf-8")

receipt = {
    "schema": "rtdl.goal5800.pyoptix_clean_install_receipt.v1",
    "status": "PASS__FRESH_VENV__CLEAN_BUILT_EXTENSION_LOADED__UNTIMED",
    "transaction_kind": "installation_and_import_not_performance",
    "registered_performance_timing_count": 0,
    "python": {
        "executable": str(Path(sys.executable).resolve()),
        "version": platform.python_version(),
    },
    "wheel": {
        "path": str(wheel),
        "bytes": wheel.stat().st_size,
        "sha256": sha256(wheel),
    },
    "loaded_optix_package_initializer": {
        "path": str(Path(optix.__file__).resolve()),
        "bytes": Path(optix.__file__).stat().st_size,
        "sha256": sha256(Path(optix.__file__)),
    },
    "loaded_optix_extension": {
        "module": "optix._optix",
        "path": str(extension),
        "bytes": extension.stat().st_size,
        "sha256": extension_sha,
    },
    "optix_api_version": ".".join(map(str, optix.version())),
    "cupy_device_name": cp.cuda.runtime.getDeviceProperties(0)["name"].decode(),
    "numpy_version": np.__version__,
    "distributions": distributions,
    "install_report": {
        "path": "install_report.json",
        "bytes": (out / "install_report.json").stat().st_size,
        "sha256": sha256(out / "install_report.json"),
    },
    "virtualenv_bootstrap_install_report": {
        "path": "virtualenv_bootstrap_install_report.json",
        "bytes": (out / "virtualenv_bootstrap_install_report.json").stat().st_size,
        "sha256": sha256(out / "virtualenv_bootstrap_install_report.json"),
    },
    "pip_freeze": {
        "path": "pip_freeze.txt",
        "bytes": (out / "pip_freeze.txt").stat().st_size,
        "sha256": sha256(out / "pip_freeze.txt"),
    },
}
(out / "clean_install_receipt.json").write_bytes(
    json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n"
)
print(json.dumps({
    "status": receipt["status"],
    "extension_sha256": extension_sha,
    "receipt_sha256": sha256(out / "clean_install_receipt.json"),
}, sort_keys=True))
PY
