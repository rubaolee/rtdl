# Goal2119: Clean Pod Rerun and OptiX Compiler Audit

Date: 2026-05-16

Status: clean rerun completed; OptiX RT evidence remains blocked on this pod.

## Purpose

This goal resumed the interrupted Hausdorff/OptiX pod work from Goal2117 and
re-ran it from a clean pod checkout. The immediate question was whether the
previous `OptiX module compile error: Internal compiler error` was caused by a
half-applied RTDL patch, a dirty pod checkout, a missing install step, or a
broader pod/toolchain problem.

## Pod And Checkout

User pod command:

```text
ssh root@213.173.102.150 -p 36295 -i ~/.ssh/id_ed25519
```

Codex used the project key:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\id_ed25519_rtdl_codex
```

Observed pod:

| Field | Value |
| --- | --- |
| Host | `c54d2d041030` |
| GPU | NVIDIA RTX 2000 Ada Generation |
| Driver | `565.57.01` |
| CUDA | `/usr/local/cuda-12.8` |
| Clean repo head | `8072665a` |
| OptiX SDK tried | `v8.0.0`, then `v8.1.0` |
| Built library | `/root/work/rtdl/build/librtdl_optix.so` |

Clean setup steps:

1. `git fetch origin main`
2. `git reset --hard origin/main`
3. `rm -rf build`
4. Copy only the four experimental files for the rerun:
   `src/native/optix/rtdl_optix_core.cpp`,
   `src/native/optix/rtdl_optix_workloads.cpp`,
   `tests/goal2110_hausdorff_exact_rt_nearest_witness_test.py`,
   `tests/goal695_optix_fixed_radius_summary_test.py`
5. Normalize copied CRLF line endings on the pod.
6. Rebuild with `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8`.

The clean rebuild succeeded.

## Experimental Native Variants Tried

The interrupted version had already tried lazy count-pipeline construction and
moving nearest-witness from any-hit to closest-hit. This clean rerun continued
with a narrower compiler-stress reduction:

| Variant | Purpose | Result |
| --- | --- | --- |
| Ray-origin query coordinates | Avoid fetching query points through a payload index in intersection/hit code. | Build succeeded; module compile still ICE. |
| Lower payload counts | Count path from 3 payloads to 1; nearest path from 4 to 3. | Build succeeded; module compile still ICE. |
| No any-hit/closest-hit for fixed-radius point modules | Intersection program updates payload directly, removing hit programs from the fixed-radius modules. | Build succeeded; module compile still ICE. |
| Env-controlled `RTDL_OPTIX_MODULE_OPT_LEVEL=0` | Allow forcing OptiX module optimization level 0. | Build succeeded; known-good OptiX control still ICE. |

These source edits are diagnostic. They do not authorize a performance or RT-core
claim by themselves.

## Clean Rerun Results

| Probe | Artifact | Result |
| --- | --- | --- |
| Focused Python/static tests | n/a | `tests.goal2110_...` and `tests.goal695_...` passed on pod. |
| Hausdorff RT nearest witness, 512 x 512 | `docs/reports/goal2119_clean_rt_nearest_rayorigin_512.json` | Failed with OptiX module compiler ICE. |
| Hausdorff RT threshold search, 512 x 512 | `docs/reports/goal2119_clean_rt_threshold_rayorigin_512.json` | Failed with OptiX module compiler ICE. |
| Known-good RTDL OptiX ray/triangle any-hit control | n/a | Also failed with the same OptiX module compiler ICE. |
| CUDA/CuPy HD positive control, 4096 x 4096 | `docs/reports/goal2119_clean_cuda_positive_control_4096.json` | Passed; RTDL v2 user CUDA matched CuPy exact reference. |

Positive CUDA control:

| Method | Seconds | Exact Match |
| --- | ---: | --- |
| `cupy_rawkernel` | `0.003644183` | yes |
| `rtdl_v2_user_cuda` | `0.003642023` | yes |

The CUDA/CuPy path is healthy on this pod. The failure is specific to OptiX
custom module compilation.

## Environment Repairs Tried

| Repair | Outcome |
| --- | --- |
| OptiX SDK `v8.0.0` | Build succeeds; custom module compile ICE remains. |
| OptiX SDK `v8.1.0` | Build succeeds; custom module compile ICE remains. |
| `RTDL_OPTIX_PTX_COMPILER=nvcc` | ICE remains. |
| NVRTC PTX path | ICE remains. |
| `RTDL_OPTIX_PTX_ARCH=compute_89` | ICE remains. |
| `RTDL_OPTIX_PTX_ARCH=compute_75` | ICE remains. |
| `RTDL_OPTIX_MODULE_OPT_LEVEL=0` | ICE remains. |
| Cleared `/var/tmp/OptixCache_root` | ICE remains. |
| Extracted clean `libnvoptix.so.565.57.01` overlay from matching NVIDIA deb | ICE remains. |
| Attempted `apt-get install libgeos-dev pkg-config` | Blocked by NVIDIA package bind-mount state; not relevant to OptiX-only control. |

The package repair issue is the known container pattern where NVIDIA driver
files are bind-mounted and `dpkg` cannot make backup hard links:

```text
unable to make backup link ... Invalid cross-device link
```

That explains why oracle/GEOS comparison tests could not be repaired through
normal apt, but it does not explain the OptiX-only control failure. The
OptiX-only ray/triangle control bypassed oracle/GEOS and still hit the compiler
ICE.

## Interpretation

The previous statement "the Hausdorff fixed-radius module is blocked by an
OptiX compiler ICE" was too narrow. The clean rerun shows this pod cannot
compile even RTDL's existing ray/triangle custom OptiX module. Therefore:

- this pod is usable for CUDA/CuPy v2 user-path evidence;
- this pod is not usable for RTDL OptiX RT-core evidence;
- the current failure is an environment/toolchain blocker, not a Hausdorff
  algorithm result and not a proof that the RTDL native code is impossible;
- no RT-core Hausdorff claim is authorized from this pod.

## Next Step

Use a different clean NVIDIA pod for OptiX custom-primitive evidence, preferably
with one of these known-good profiles:

| Preferred field | Value |
| --- | --- |
| Driver | `570.x` or newer if available, otherwise a clean `565.x` image without half-configured NVIDIA packages |
| CUDA | CUDA 12.x, with `nvcc` available |
| OptiX SDK | `v8.1.0` for `565.x+`; try `v8.0.0` only if `v8.1.0` fails |
| First control | run RTDL `goal637` OptiX-only ray/triangle any-hit control before HD |

If the next pod passes the OptiX-only control, continue HD RT work there. If it
fails the same way, stop HD-specific work and produce a minimal NVIDIA OptiX
custom-primitive repro from RTDL's ray/triangle control.

## Verdict

- Clean rerun: `accept`.
- CUDA/CuPy HD positive control: `accept`.
- OptiX RT-core HD evidence on this pod: `needs-new-pod`.
- RT-core Hausdorff speedup claim: `needs-more-evidence`.
