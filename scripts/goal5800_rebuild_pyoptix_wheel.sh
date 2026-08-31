#!/usr/bin/env bash
# Build the pinned NVIDIA PyOptiX source against the pinned OptiX 9.0 headers.
# This is a create-only, untimed provenance transaction; it is not a benchmark.

set -euo pipefail

if [[ "$#" -ne 4 ]]; then
  echo "usage: $0 PYTHON PYOPTIX_SOURCE OPTIX_HEADER_SOURCE OUTPUT_ROOT" >&2
  exit 2
fi

PYTHON="$1"
PYOPTIX_SOURCE="$2"
OPTIX_HEADER_SOURCE="$3"
OUTPUT_ROOT="$4"

EXPECTED_PYOPTIX_COMMIT="3144f224c0fd18733925faf3d8fb82c7376b8dcf"
EXPECTED_PYOPTIX_TREE="0bf0ec24efb4a43f129aee25dd265aa8149374e3"
EXPECTED_OPTIX_HEADERS_COMMIT="fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd"
EXPECTED_OPTIX_HEADERS_TREE="c30f1b41cb64f6cba6290d7ad82686cc84922267"

if [[ -e "$OUTPUT_ROOT" ]]; then
  echo "refusing to reuse output root: $OUTPUT_ROOT" >&2
  exit 3
fi
if [[ ! -x "$PYTHON" ]]; then
  echo "python is not executable: $PYTHON" >&2
  exit 4
fi

read_git_identity() {
  local repository="$1"
  git -C "$repository" rev-parse HEAD
  git -C "$repository" rev-parse 'HEAD^{tree}'
  git -C "$repository" status --porcelain=v1 --untracked-files=all
}

mapfile -t PYOPTIX_IDENTITY < <(read_git_identity "$PYOPTIX_SOURCE")
mapfile -t OPTIX_HEADER_IDENTITY < <(read_git_identity "$OPTIX_HEADER_SOURCE")
if [[ "${PYOPTIX_IDENTITY[0]}" != "$EXPECTED_PYOPTIX_COMMIT" || \
      "${PYOPTIX_IDENTITY[1]}" != "$EXPECTED_PYOPTIX_TREE" || \
      "${#PYOPTIX_IDENTITY[@]}" -ne 2 ]]; then
  echo "PyOptiX source identity/cleanliness mismatch" >&2
  exit 5
fi
if [[ "${OPTIX_HEADER_IDENTITY[0]}" != "$EXPECTED_OPTIX_HEADERS_COMMIT" || \
      "${OPTIX_HEADER_IDENTITY[1]}" != "$EXPECTED_OPTIX_HEADERS_TREE" || \
      "${#OPTIX_HEADER_IDENTITY[@]}" -ne 2 ]]; then
  echo "OptiX header identity/cleanliness mismatch" >&2
  exit 6
fi
if ! grep -qx '#define OPTIX_VERSION 90000' \
      "$OPTIX_HEADER_SOURCE/include/optix.h"; then
  echo "OptiX header API is not exactly 9.0.0" >&2
  exit 7
fi

mkdir -p "$OUTPUT_ROOT/source" "$OUTPUT_ROOT/wheelhouse" "$OUTPUT_ROOT/logs"
git -C "$PYOPTIX_SOURCE" archive --format=tar HEAD \
  | tar -xf - -C "$OUTPUT_ROOT/source"

export CMAKE_ARGS="-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=$OPTIX_HEADER_SOURCE"
BUILD_COMMAND=(
  "$PYTHON" -m pip wheel
  --no-build-isolation
  --no-deps
  --wheel-dir "$OUTPUT_ROOT/wheelhouse"
  "$OUTPUT_ROOT/source"
)
printf '%q ' "${BUILD_COMMAND[@]}" > "$OUTPUT_ROOT/logs/build_command.shell"
printf '\n' >> "$OUTPUT_ROOT/logs/build_command.shell"

set +e
"${BUILD_COMMAND[@]}" \
  > >(tee "$OUTPUT_ROOT/logs/build_stdout.txt") \
  2> >(tee "$OUTPUT_ROOT/logs/build_stderr.txt" >&2)
BUILD_EXIT_CODE=$?
set -e
printf '%s\n' "$BUILD_EXIT_CODE" > "$OUTPUT_ROOT/logs/build_exit_code.txt"
if [[ "$BUILD_EXIT_CODE" -ne 0 ]]; then
  echo "PyOptiX wheel build failed" >&2
  exit "$BUILD_EXIT_CODE"
fi

mapfile -t WHEELS < <(find "$OUTPUT_ROOT/wheelhouse" -maxdepth 1 -type f \
  -name 'pyoptix-9.1.0-*.whl' -print)
if [[ "${#WHEELS[@]}" -ne 1 ]]; then
  echo "expected exactly one PyOptiX wheel" >&2
  exit 8
fi

"$PYTHON" - "$OUTPUT_ROOT" "$PYOPTIX_SOURCE" "$OPTIX_HEADER_SOURCE" \
  "$PYTHON" "${WHEELS[0]}" <<'PY'
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

out = Path(sys.argv[1]).resolve()
pyoptix = Path(sys.argv[2]).resolve()
headers = Path(sys.argv[3]).resolve()
python = Path(sys.argv[4]).resolve()
wheel = Path(sys.argv[5]).resolve()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        list(args), check=True, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "argv": list(args),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_code": completed.returncode,
    }


with zipfile.ZipFile(wheel) as archive:
    extension_names = sorted(
        name for name in archive.namelist()
        if name.startswith("optix/_optix.") and name.endswith(".so")
    )
    if len(extension_names) != 1:
        raise RuntimeError(f"expected one _optix extension: {extension_names}")
    extension = archive.read(extension_names[0])

source_rows = []
for path in sorted((out / "source").rglob("*")):
    if path.is_file():
        source_rows.append({
            "path": path.relative_to(out / "source").as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

receipt = {
    "schema": "rtdl.goal5800.pyoptix_clean_wheel_build_receipt.v1",
    "status": "PASS__CLEAN_SOURCE_TO_WHEEL_BUILD__UNTIMED",
    "transaction_kind": "build_provenance_not_performance",
    "registered_performance_timing_count": 0,
    "pyoptix_source": {
        "commit": "3144f224c0fd18733925faf3d8fb82c7376b8dcf",
        "tree": "0bf0ec24efb4a43f129aee25dd265aa8149374e3",
        "archive_projection_file_count": len(source_rows),
        "archive_projection_files": source_rows,
    },
    "optix_headers": {
        "commit": "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd",
        "tree": "c30f1b41cb64f6cba6290d7ad82686cc84922267",
        "api_macro": 90000,
        "root": str(headers),
    },
    "build": {
        "python": str(python),
        "python_version": platform.python_version(),
        "cmake_args": f"-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS={headers}",
        "pip": importlib.metadata.version("pip"),
        "scikit_build_core": importlib.metadata.version("scikit-build-core"),
        "pybind11": importlib.metadata.version("pybind11"),
        "ninja": importlib.metadata.version("ninja"),
        "cmake": command("cmake", "--version"),
        "cxx": command("/usr/bin/x86_64-linux-gnu-g++", "--version"),
        "nvcc": command("/usr/bin/nvcc", "--version"),
        "command_file": "logs/build_command.shell",
        "stdout_file": "logs/build_stdout.txt",
        "stderr_file": "logs/build_stderr.txt",
        "exit_code": 0,
    },
    "wheel": {
        "path": wheel.relative_to(out).as_posix(),
        "bytes": wheel.stat().st_size,
        "sha256": sha256(wheel),
        "extension_member": extension_names[0],
        "extension_bytes": len(extension),
        "extension_sha256": hashlib.sha256(extension).hexdigest(),
    },
}
(out / "build_receipt.json").write_bytes(
    json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n"
)
print(json.dumps({
    "status": receipt["status"],
    "wheel": receipt["wheel"],
    "receipt_sha256": sha256(out / "build_receipt.json"),
}, sort_keys=True))
PY
