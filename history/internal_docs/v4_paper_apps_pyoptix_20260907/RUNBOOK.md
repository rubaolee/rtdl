# GPU runbook: V4 paper apps versus public PyOptiX

This runbook executes the pre-worker-zero first batch. It does not authorize a
performance claim. All paths below except `SOURCE` are outside the Git tree.
Replace only machine paths; do not change workloads, repetitions, ordering, or
analysis after observing a performance result.

## 1. Clean source and fixed environment

Use one clean checkout of the pushed experiment commit and one visible RT GPU.
The commands assume Python 3.12 and CUDA 12.x.

```bash
set -euo pipefail
export SOURCE=/workspace/rtdl-v4-paper-apps-source
export RUN=/workspace/rtdl-v4-paper-apps-run
export DATA_ARCHIVE=/workspace/goal5776_real_scale_data_bundle_20260813.tar.gz
export CUDA_ROOT=/usr/local/cuda
export CUDA_VISIBLE_DEVICES=0
test ! -e "$RUN"
mkdir -p "$RUN"
test -z "$(git -C "$SOURCE" status --porcelain=v1 --untracked-files=all)"
git -C "$SOURCE" rev-parse HEAD
nvidia-smi --query-gpu=name,uuid,compute_cap,driver_version,memory.total \
  --format=csv,noheader,nounits
```

Transfer the exact Goal5776 archive to `DATA_ARCHIVE` without modifying it.
The registered identity is 1,155,932,998 bytes and SHA-256
`f84ed4396dd9e5928bd222f50fca57af2db727a6d994abfc5844a9b1b12981ad`.
The extractor rejects any other archive and validates every member against the
embedded manifest:

```bash
export PYTHONPATH="$SOURCE/src:$SOURCE/scripts:$SOURCE"
python3.12 "$SOURCE/scripts/v4_paper_apps_pyoptix_extract_data.py" \
  --archive "$DATA_ARCHIVE" --output-root "$RUN/data"
```

Create a clean Python 3.12 environment using the already-reviewed Goal5848
dependency set. Preserve the install report because the PyOptiX build receipt
validates it.

```bash
python3.12 -m venv --copies "$RUN/venv"
export PYTHON="$RUN/venv/bin/python"
"$PYTHON" -m pip install --upgrade --no-deps pip==26.2.1
"$PYTHON" -m pip uninstall -y setuptools
"$PYTHON" -m pip install --force-reinstall \
  --report "$RUN/dependency_install_report.json" \
  cmake==3.31.6 wheel==0.45.1 scikit-build-core==1.0.3 \
  pybind11==3.1.0 ninja==1.13.0 packaging==26.3 pathspec==1.1.1 \
  numpy==2.4.4 Pillow==10.2.0 numba==0.65.1 \
  cuda-pathfinder==1.6.1 cuda-bindings==12.9.7 cuda-python==12.9.7 \
  cupy-cuda12x==14.0.1 nvidia-ml-py==13.580.82
export PYTHONPATH="$SOURCE/src:$SOURCE/scripts:$SOURCE"
export LD_LIBRARY_PATH="$CUDA_ROOT/lib64:${LD_LIBRARY_PATH:-}"
```

## 2. Driver-compatible OptiX and pinned public PyOptiX

Select the already-reviewed driver-compatible OptiX header row, then acquire
the exact pinned public NVIDIA PyOptiX source. No GPU model or observed task
performance participates in this selection.

```bash
export DRIVER_VERSION="$(nvidia-smi --query-gpu=driver_version \
  --format=csv,noheader,nounits | sed -n '1p')"
export COMPUTE_CAPABILITY="$(nvidia-smi --query-gpu=compute_cap \
  --format=csv,noheader,nounits | sed -n '1p')"
export SELECTOR="$SOURCE/experiments/goal5798_premeasurement/compatibility.py"
export OPTIX_API="$("$PYTHON" "$SELECTOR" --driver "$DRIVER_VERSION" \
  --field optix_api_version)"
export OPTIX_COMMIT="$("$PYTHON" "$SELECTOR" --driver "$DRIVER_VERSION" \
  --field optix_header_commit)"
export PYOPTIX_COMMIT=3144f224c0fd18733925faf3d8fb82c7376b8dcf
git init -q "$RUN/optix-dev"
git -C "$RUN/optix-dev" remote add origin https://github.com/NVIDIA/optix-dev.git
git -C "$RUN/optix-dev" fetch -q --depth 1 origin "$OPTIX_COMMIT"
git -C "$RUN/optix-dev" checkout -q --detach FETCH_HEAD
git init -q "$RUN/otk-pyoptix"
git -C "$RUN/otk-pyoptix" remote add origin \
  https://github.com/NVIDIA/otk-pyoptix.git
git -C "$RUN/otk-pyoptix" fetch -q --depth 1 origin "$PYOPTIX_COMMIT"
git -C "$RUN/otk-pyoptix" checkout -q --detach FETCH_HEAD
```

Build and install PyOptiX from that clean source. This creates a receipt that
binds source, headers, wheel, loaded extension, tools, and dependencies.

```bash
"$PYTHON" "$SOURCE/scripts/goal5844_build_install_pyoptix.py" \
  --python "$PYTHON" --pyoptix-source "$RUN/otk-pyoptix" \
  --optix-headers "$RUN/optix-dev" --expected-optix-api "$OPTIX_API" \
  --dependency-install-report "$RUN/dependency_install_report.json" \
  --output-root "$RUN/pyoptix-build"
```

Precompile the three public-PyOptiX device programs once before worker zero.
The manifest retains compilation time as a diagnostic and binds the source,
headers, architecture, compiler environment, and PTX bytes. Formal workers do
not invoke NVRTC.

```bash
"$PYTHON" "$SOURCE/scripts/v4_paper_apps_pyoptix_prepare_ptx.py" \
  --optix-include "$RUN/optix-dev/include" \
  --cuda-include "$CUDA_ROOT/include" \
  --compute-capability "$COMPUTE_CAPABILITY" \
  --output-root "$RUN/prebuilt-ptx"
```

## 3. Fresh RTDL native build and local authority

Build the full public V4 OptiX library, not the minimal AOT-only library. The
builder independently rejects source drift, header drift, GPU capability drift,
and missing native symbols.

```bash
mkdir -p "$RUN/native"
"$PYTHON" "$SOURCE/scripts/build_v4_optix_native_snapshot.py" \
  --cuda-prefix "$CUDA_ROOT" --optix-prefix "$RUN/optix-dev" \
  --expected-optix-sdk "$OPTIX_API" \
  --compute-capability "$COMPUTE_CAPABILITY" \
  --host-compiler "$(command -v g++)" \
  --output "$RUN/native/librtdl_optix.so" \
  --manifest "$RUN/native/BUILD_MANIFEST.json" \
  --log "$RUN/native/build.log"
"$PYTHON" "$SOURCE/scripts/v4_paper_apps_pyoptix_local_preflight.py" \
  --output "$RUN/LOCAL_PREFLIGHT.json"
```

`LOCAL_PREFLIGHT.json` must say
`PASS__LOCAL_STATIC_ONLY__GPU_DRY_RUN_REQUIRED`, report 192 formal workers,
and record `working_tree_clean: true`.

Create the single identity-bound config:

```bash
"$PYTHON" "$SOURCE/scripts/v4_paper_apps_pyoptix_make_config.py" \
  --source-root "$SOURCE" --data-root "$RUN/data/DATA" \
  --data-manifest "$RUN/data/DATA_MANIFEST.json" \
  --native-library "$RUN/native/librtdl_optix.so" \
  --native-build-manifest "$RUN/native/BUILD_MANIFEST.json" \
  --pyoptix-build-receipt "$RUN/pyoptix-build/build_receipt.json" \
  --pyoptix-ptx-manifest "$RUN/prebuilt-ptx/PREBUILT_PTX_MANIFEST.json" \
  --optix-include "$RUN/optix-dev/include" \
  --cuda-include "$CUDA_ROOT/include" \
  --compute-capability "$COMPUTE_CAPABILITY" --optix-sdk "$OPTIX_API" \
  --output "$RUN/CONFIG.json"
```

## 4. Untimed parity gate, formal transaction, and recount

The dry run launches eight fresh processes and must pass exact output parity
for all four units. It is not a performance result and does not reach formal
worker zero. It also freezes the exact input-identity object observed by both
arms for each unit; formal workers must reproduce those identities.

```bash
"$PYTHON" "$SOURCE/scripts/v4_paper_apps_pyoptix_controller.py" \
  --mode dry-run --config "$RUN/CONFIG.json" \
  --output-root "$RUN/dry-run" --python "$PYTHON" --timeout-seconds 7200
```

Only after `dry-run/DRY_RUN_SUMMARY.json` says `PASS`, run the fixed 192-worker
transaction. Do not replace failed workers, alter repetitions, or delete any
failure row.

The complete-stage ratio excludes disk input loading. It starts after the
common domain input is loaded and includes implementation imports, preparation,
the first complete execution, required checks, materialization, and close.
Input-load time remains in each worker's diagnostic phases.

```bash
"$PYTHON" "$SOURCE/scripts/v4_paper_apps_pyoptix_controller.py" \
  --mode formal --config "$RUN/CONFIG.json" \
  --dry-run-summary "$RUN/dry-run/DRY_RUN_SUMMARY.json" \
  --output-root "$RUN/formal" --python "$PYTHON" --timeout-seconds 7200
"$PYTHON" "$SOURCE/scripts/v4_paper_apps_pyoptix_recount.py" \
  --formal-summary "$RUN/formal/FORMAL_SUMMARY.json" \
  --output "$RUN/INDEPENDENT_RECOUNT.json"
```

Archive the whole run whether it passes or fails. A failed dry run or formal
transaction is retained adverse evidence; it is not silently retried.

```bash
tar -czf "$RUN.tar.gz" -C "$(dirname "$RUN")" "$(basename "$RUN")"
sha256sum "$RUN.tar.gz" > "$RUN.tar.gz.sha256"
```

No number enters the manuscript until raw workers, controller summary,
independent recount, source/config/build identities, timer boundaries, and
output contracts have been reviewed together.

The formal summary binds each worker by a safe transaction-relative path.
After copying or extracting the complete `$RUN` directory elsewhere, invoke
the recount against the relocated `formal/FORMAL_SUMMARY.json`; the original
pod absolute path is not required.
