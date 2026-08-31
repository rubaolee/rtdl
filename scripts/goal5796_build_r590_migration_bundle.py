#!/usr/bin/env python3
"""Build a deterministic Goal5796 R590+ non-timed migration bundle."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "history" / "internal_docs" / "goal5796_r590_non_timed_migration_bundle_20260823.tar.gz"
BASE = ROOT / "history" / "internal_docs" / "goal5791_portable_source_v26_20260820.tar.gz"
PUBLIC = ROOT / ".tmp_goal5795_public_smoke_20260823_v4" / "goal5795_public_source.tar.gz"

OVERLAYS = (
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
)

MATCHED = tuple(
    str(path.relative_to(ROOT)).replace("\\", "/")
    for path in sorted((ROOT / "experiments" / "goal5796_matched").iterdir())
    if path.is_file()
)

RUNNER = r'''#!/usr/bin/env bash
set -euo pipefail

bundle_root="$(cd "$(dirname "$0")" && pwd)"
run_root="${1:-/root/goal5796_r590_non_timed_run}"

driver_version="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n 1)"
driver_branch="${driver_version%%.*}"
printf 'driver_version=%s\n' "$driver_version"
if [ "$driver_branch" -lt 590 ]; then
  printf 'BLOCKED_CURRENT_PYOPTIX_9_1_REQUIRES_R590_OR_LATER\n' >&2
  exit 42
fi
if [ -e "$run_root" ]; then
  printf 'create-only run root already exists: %s\n' "$run_root" >&2
  exit 43
fi
for command in git cmake ninja g++ python3 nvidia-smi; do
  command -v "$command" >/dev/null || { printf 'missing command: %s\n' "$command" >&2; exit 44; }
done
cuda_root="/usr/local/cuda"
test -f "$cuda_root/include/cuda.h" || { echo 'missing CUDA headers' >&2; exit 45; }

(cd "$bundle_root" && sha256sum -c SHA256SUMS)
mkdir -p "$run_root/source" "$run_root/upstream" "$run_root/results"
tar -xzf "$bundle_root/payload/goal5791_base_source.tar.gz" -C "$run_root/source"
tar -xzf "$bundle_root/payload/goal5795_public_source.tar.gz" -C "$run_root/source"
cp -a "$bundle_root/overlay/." "$run_root/source/"

git init -q "$run_root/upstream/otk-pyoptix"
git -C "$run_root/upstream/otk-pyoptix" remote add origin https://github.com/NVIDIA/otk-pyoptix.git
git -C "$run_root/upstream/otk-pyoptix" fetch -q --depth 1 origin 3144f224c0fd18733925faf3d8fb82c7376b8dcf
git -C "$run_root/upstream/otk-pyoptix" checkout -q --detach FETCH_HEAD
test "$(git -C "$run_root/upstream/otk-pyoptix" rev-parse HEAD)" = 3144f224c0fd18733925faf3d8fb82c7376b8dcf

git init -q "$run_root/upstream/optix-dev"
git -C "$run_root/upstream/optix-dev" remote add origin https://github.com/NVIDIA/optix-dev.git
git -C "$run_root/upstream/optix-dev" fetch -q --depth 1 origin f1f6dd803f3159992d248178f6e09421c6eb8b6d
git -C "$run_root/upstream/optix-dev" checkout -q --detach FETCH_HEAD
test "$(git -C "$run_root/upstream/optix-dev" rev-parse HEAD)" = f1f6dd803f3159992d248178f6e09421c6eb8b6d

python3 -m venv --copies "$run_root/venv"
. "$run_root/venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install \
  scikit-build-core==1.0.3 pybind11==3.1.0 ninja==1.13.0 \
  numpy==2.4.4 Pillow==10.2.0 numba==0.65.1 \
  cuda-pathfinder==1.6.1 cuda-bindings==12.9.7 cuda-python==12.9.7 \
  cupy-cuda12x==14.0.1
export PYOPTIX_CMAKE_ARGS="-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=$run_root/upstream/optix-dev"
python -m pip install --no-build-isolation --no-deps "$run_root/upstream/otk-pyoptix"
python -m pip install --no-deps -e "$run_root/source"
python -c 'import optix; print("pyoptix_version", optix.version())'

make -C "$run_root/source" build-optix \
  OPTIX_PREFIX="$run_root/upstream/optix-dev" \
  CUDA_PREFIX="$cuda_root" OPTIX_CUDA_ARCH=sm_89
native="$run_root/source/build/librtdl_optix.so"
test -s "$native"

matched="$run_root/source/experiments/goal5796_matched"
spec_sha="$(sha256sum "$matched/semantic_spec.json" | awk '{print $1}')"
test "$spec_sha" = 88bc8468c78302ed18cb3176e70a6c1dea65bc8306bf5e747bc18dea1e3fac4b

bash "$matched/build_direct.sh" \
  "$run_root/upstream/optix-dev/include" "$cuda_root/include" "$matched/direct_optix"
"$matched/direct_optix" "$matched/matched_device.cu" \
  "$run_root/upstream/optix-dev/include" "$cuda_root/include" "$spec_sha" \
  > "$run_root/results/DIRECT_RESULT.json"
python "$matched/independent_oracle.py" --spec "$matched/semantic_spec.json" \
  --result "$run_root/results/DIRECT_RESULT.json" > "$run_root/results/DIRECT_ORACLE.json"

python "$matched/pyoptix_baseline.py" \
  --spec "$matched/semantic_spec.json" --device-source "$matched/matched_device.cu" \
  --optix-include "$run_root/upstream/optix-dev/include" --cuda-include "$cuda_root/include" \
  --output "$run_root/results/PYOPTIX_RESULT.json"
python "$matched/independent_oracle.py" --spec "$matched/semantic_spec.json" \
  --result "$run_root/results/PYOPTIX_RESULT.json" > "$run_root/results/PYOPTIX_ORACLE.json"

PYTHONPATH="$run_root/source/src" python "$matched/rtdl_baseline.py" \
  --spec "$matched/semantic_spec.json" --native "$native" \
  --optix-include "$run_root/upstream/optix-dev/include" --cuda-include "$cuda_root/include" \
  --optix-sdk 9.1.0 --compute-capability 8.9 \
  --proof "$matched/independent_oracle.py" --output "$run_root/results/RTDL_RESULT.json"
python "$matched/independent_oracle.py" --spec "$matched/semantic_spec.json" \
  --result "$run_root/results/RTDL_RESULT.json" > "$run_root/results/RTDL_ORACLE.json"

python - "$run_root" <<'PY'
import hashlib, json, pathlib, platform, subprocess, sys
root = pathlib.Path(sys.argv[1])
results = root / "results"
arms = {}
for name in ("DIRECT_RESULT.json", "PYOPTIX_RESULT.json", "RTDL_RESULT.json"):
    path = results / name
    value = json.loads(path.read_bytes())
    if value["status"] != "PASS": raise SystemExit(f"{name} not PASS")
    if value["registered_performance_timing_count"] != 0: raise SystemExit("timing count nonzero")
    arms[name] = {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
outputs = [json.loads((results / name).read_bytes())["outputs"] for name in arms]
if not (outputs[0] == outputs[1] == outputs[2]): raise SystemExit("A/B/D outputs differ")
receipt = {
  "schema": "rtdl.goal5796.r590_non_timed_transaction.v1", "status": "PASS",
  "hostname": platform.node(),
  "gpu": subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap", "--format=csv,noheader"], check=True, text=True, capture_output=True).stdout.strip(),
  "arms": arms, "all_three_outputs_exact_and_identical": True,
  "registered_performance_timing_count": 0, "performance_claimed": False,
}
(results / "TRANSACTION_RESULT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
print(json.dumps(receipt, indent=2, sort_keys=True))
PY
'''


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    payloads: dict[str, bytes] = {
        "payload/goal5791_base_source.tar.gz": BASE.read_bytes(),
        "payload/goal5795_public_source.tar.gz": PUBLIC.read_bytes(),
    }
    for relative in OVERLAYS:
        payloads[f"overlay/{relative}"] = (ROOT / relative).read_bytes()
    for relative in MATCHED:
        payloads[f"overlay/{relative}"] = (ROOT / relative).read_bytes()
    payloads["RUN_NON_TIMED.sh"] = RUNNER.encode("utf-8")

    manifest = {
        "schema": "rtdl.goal5796.r590_non_timed_migration_bundle.v1",
        "status": "FROZEN",
        "required_driver_branch_minimum": 590,
        "current_pyoptix_commit": "3144f224c0fd18733925faf3d8fb82c7376b8dcf",
        "current_pyoptix_distribution_version": "9.1.0",
        "optix_dev_commit": "f1f6dd803f3159992d248178f6e09421c6eb8b6d",
        "formal_timing_authorized": False,
        "registered_performance_timing_count": 0,
        "payloads": {
            name: {"bytes": len(data), "sha256": digest(data)}
            for name, data in sorted(payloads.items())
        },
    }
    payloads["MANIFEST.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    payloads["SHA256SUMS"] = "".join(
        f"{digest(data)}  {name}\n" for name, data in sorted(payloads.items())
        if name != "SHA256SUMS"
    ).encode("utf-8")

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(payloads.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if name == "RUN_NON_TIMED.sh" else 0o644
            archive.addfile(info, io.BytesIO(data))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            compressed.write(buffer.getvalue())
    print(json.dumps({
        "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "bytes": OUTPUT.stat().st_size,
        "sha256": digest(OUTPUT.read_bytes()),
        "payload_count": len(payloads),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
