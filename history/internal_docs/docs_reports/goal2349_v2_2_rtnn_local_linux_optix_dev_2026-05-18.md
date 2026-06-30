# Goal2349 - RTNN v2.2 Local Linux OptiX Development Pass

Date: 2026-05-18

Status: local development pass complete; pod performance evidence still required.

## Purpose

This pass uses the local Linux machine as an OptiX build and smoke-test platform while the RTX pod is being prepared. It is deliberately not a performance-evidence pass: the local GPU is a GTX 1070, which can catch CUDA/OptiX integration failures but is not accepted RT-core hardware for RTDL v2.2 claims.

## Environment

| Item | Value |
| --- | --- |
| Host | `lx1` / `192.168.1.20` |
| Checkout | `/home/lestat/work/rtdl_goal2346_linux_check` |
| RTDL commit | `e733685a` |
| Local checkout status | Clean except local `scratch/` artifacts |
| GPU | `NVIDIA GeForce GTX 1070` |
| Driver | `580.126.09` |
| CUDA | `nvcc` 12.0.140 |
| CMake | 3.28.3 |
| Host compiler used for RTNN | `g++-12` 12.4.0 |
| OptiX SDK for RTDL | `/home/lestat/vendor/optix-dev` |

## RTDL OptiX Smoke Result

The clean local checkout built RTDL's OptiX runtime:

```bash
CUDA_HOME=/usr PATH=/usr/bin:$PATH \
LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/local/cuda/lib64:$LD_LIBRARY_PATH \
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev CUDA_PREFIX=/usr
```

The resulting library was present at `build/librtdl_optix.so`, and a direct runtime probe returned:

```text
optix_version() == (9, 0, 0)
```

The current RTDL 2D fixed-radius smoke row was also run with:

```bash
RTDL_OPTIX_LIBRARY=/home/lestat/work/rtdl_goal2346_linux_check/build/librtdl_optix.so \
PYTHONPATH=src:. \
python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtdl-current-2d-smoke \
  --point-file scratch/goal2349_ppp_2d_512.txt \
  --radius 0.05 \
  --threshold 1 \
  --row-label local_linux_gtx1070_2d_smoke \
  --json-out scratch/goal2349_rtdl_current_2d_smoke.json
```

Result: `ok=true`, `elapsed_sec=0.5893395352177322`, `query_count=512`, `search_count=512`, `row_count=512`.

This row only verifies that RTDL's current OptiX smoke path still loads and executes on the local host. It is not a paper-equivalent RTNN row and is not accepted RT-core performance evidence.

## External RTNN Build Result

The external RTNN repository (`https://github.com/horizon-research/rtnn`) was cloned into the disposable local scratch path:

```text
/home/lestat/work/rtdl_goal2346_linux_check/scratch/rtnn_goal2346
```

The default build failed first because CUDA 12.0 rejects GCC 13 as a host compiler. Reconfiguring with GCC 12 fixed that toolchain gate:

```bash
cd /home/lestat/work/rtdl_goal2346_linux_check/scratch/rtnn_goal2346/src
rm -rf build_gcc12
mkdir build_gcc12
cd build_gcc12
CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 \
cmake -DKNN=5 -DCUDA_HOST_COMPILER=/usr/bin/g++-12 ..
make -j4
```

CUDA 12 then exposed three compatibility issues in RTNN's older source. These were patched only in the disposable external checkout:

| File | Local patch |
| --- | --- |
| `src/optixNSearch/thrust_helper.cu` | Added `#include <thrust/count.h>`, `#include <thrust/unique.h>`, and `#include <thrust/tuple.h>`. |
| `src/optixNSearch/sort.cpp` | Added `#include <thrust/host_vector.h>`. |
| `src/optixNSearch/geometry.cu` | Replaced legacy NVRTC intrinsics `uint_as_float` / `float_as_uint` with CUDA spellings `__uint_as_float` / `__float_as_uint`. |

After those local patches, the RTNN executable built successfully:

```text
[100%] Built target optixNSearch
```

## External RTNN Smoke Result

A deterministic 3D synthetic RTNN-format point cloud was generated:

```bash
python3 scripts/goal2348_rtnn_v2_2_external_runner.py generate \
  --point-file scratch/goal2349_ppp_3d_1024.txt \
  --point-count 1024 \
  --dimension 3 \
  --seed 2350 \
  --json-out scratch/goal2349_ppp_3d_1024_generate.json
```

Then the external RTNN radius-search smoke ran successfully:

```bash
LD_LIBRARY_PATH=/home/lestat/work/rtdl_goal2346_linux_check/scratch/rtnn_goal2346/src/build_gcc12/lib:$LD_LIBRARY_PATH \
python3 scripts/goal2348_rtnn_v2_2_external_runner.py run-rtnn \
  --rtnn-binary /home/lestat/work/rtdl_goal2346_linux_check/scratch/rtnn_goal2346/src/build_gcc12/bin/optixNSearch \
  --rtnn-cwd /home/lestat/work/rtdl_goal2346_linux_check/scratch/rtnn_goal2346/src/build_gcc12 \
  --rtnn-library-dir /home/lestat/work/rtdl_goal2346_linux_check/scratch/rtnn_goal2346/src/build_gcc12/lib \
  --point-file /home/lestat/work/rtdl_goal2346_linux_check/scratch/goal2349_ppp_3d_1024.txt \
  --search-mode radius \
  --radius 0.05 \
  --k-max 16 \
  --device 0 \
  --timeout-sec 60 \
  --row-label local_linux_gtx1070_rtnn_radius_smoke_after_intrinsic_patch \
  --json-out scratch/goal2349_rtnn_radius_smoke_after_intrinsic_patch.json
```

Result summary:

| Field | Value |
| --- | --- |
| RTNN return code | `0` |
| Wall elapsed | `0.9436607311945409` seconds |
| GPU reported by RTNN | `NVIDIA GeForce GTX 1070` |
| `time create pipeline` | `446.184 ms` |
| `time sort and/or partition queries` | `93.5842 ms` |
| `time initial traversal` | `0.058877 ms` |
| `time search compute` | `0.050558 ms` |
| `time result copy D2H` | `0.892054 ms` |
| `time total search time` | `95.5021 ms` |

This smoke confirms that the RTNN external baseline can be made runnable with this host's CUDA 12 toolchain. It does not authorize RTDL speedup claims, broad RT-core claims, or paper-reproduction claims.

## Pod-Ready Next Steps

1. Reuse the Goal2348 runner on an RTX pod against the same RTDL commit.
2. Build RTDL OptiX with the pod's OptiX SDK and record `librtdl_optix.so` provenance.
3. Build external RTNN with GCC/CUDA-compatible settings; apply the same CUDA 12 source compatibility patches with `python3 scripts/goal2348_rtnn_v2_2_external_runner.py patch-rtnn-cuda12 --rtnn-root ...` if needed.
4. Run matched synthetic and paper-style RTNN rows for radius and KNN, with RTDL current behavior recorded separately from any new v2.2 primitive work.
5. Only after same-hardware rows exist, decide which RTNN ideas should become app-agnostic RTDL v2.2 primitives.

## Claim Boundary

Local Linux is a dev platform here, not release evidence. The accepted future evidence must come from an RTX pod or equivalent RT-core GPU with matched RTDL and RTNN rows. The current status is: build and smoke path de-risked; performance comparison and primitive-design validation still pending.
