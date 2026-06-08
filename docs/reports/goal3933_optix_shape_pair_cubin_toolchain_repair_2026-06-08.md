# Goal3933 OptiX Shape-Pair CUBIN Toolchain Repair

Date: 2026-06-08

## Purpose

Goal3933 fixes the RTX 4000 Ada pod blocker found while running the Goal3927
combined RayJoin + RTDBSCAN queue.

The pod had driver `550.127.05` and CUDA `12.8` installed. That combination can
compile PTX newer than the driver can load through `cuModuleLoadData`, producing
the familiar `unsupported toolchain` failure. Installing an isolated CUDA 12.4
NVRTC/Numba stack fixed Numba and several direct PTX helpers, but the
shape-pair active-count helper still had to fall back to the system CUDA 12.8
compiler.

## Native Repair

The shape-pair active-count helper is a direct CUDA driver module, not an OptiX
program module. It does not need PTX. The fix is therefore to compile this helper
to CUBIN:

```cpp
std::string cubin = compile_to_cubin(
    kShapePairRelationActiveCountDeviceKernelSrc,
    "shape_pair_relation_active_count_device_kernel.cu");
CU_CHECK(cuModuleLoadData(&g_shape_pair_relation_active_count_device.module, cubin.data()));
```

This keeps the helper generic and app-agnostic. It changes only the direct CUDA
module compilation format for the existing generic active-count continuation.

The closed-shape / shape-pair OptiX program strings also no longer include host
`<math.h>` for the early RayJoin path. They use tiny device-local helpers for
absolute value and clamping, avoiding an Ubuntu 24.04 glibc math-header failure
when NVRTC diagnostics are forced.

## Pod Evidence

Artifacts are stored under:

`docs/reports/goal3933_optix_shape_pair_cubin_toolchain_repair_pod_2026-06-08/`

Pod summary:

- GPU: NVIDIA RTX 4000 Ada Generation, driver `550.127.05`.
- Source commit: `edc90516`.
- Source label: `edc90516+goal3933_cubin_sourcefix`.
- Source dirty scope: `src/native/optix/rtdl_optix_core.cpp` and
  `src/native/optix/rtdl_optix_workloads.cpp`.
- Goal3927 queue status: `pass`.
- Goal3931 evaluator status: `accept_with_boundary`.

RayJoin representative hot-path results:

| Contract | RTDL/OptiX hot median | Numba hot median | RTDL/OptiX vs Numba | Recommended route |
| --- | ---: | ---: | ---: | --- |
| PIP one-shot | 0.001772400 s | 0.000435885 s | 0.246x | Numba scalar count |
| LSI scalar count | 0.000087105 s | 0.023101557 s | 265.216x | RTDL OptiX prepared segment-pair count |
| Overlay active count | 0.000186067 s | 0.039556962 s | 212.595x | RTDL OptiX prepared shape-pair active count |
| PIP repeated requests | 0.145269 ms/request at 100 requests | N/A | 1.252x vs single RTDL request | RTDL OptiX prepared batch executor |

RTDBSCAN queue results:

| Mode | Elapsed |
| --- | ---: |
| Unblocked grouped stream | 0.090492 s |
| Blocked grouped stream | 0.394047 s |

Goal3931 recommends `blocked_candidate_slower_keep_unblocked_default`.

## Boundaries

This is internal engineering evidence, not a release packet. It does not
authorize release wording, public speedup claims, whole-app speedup claims, broad
RT-core claims, automatic partner selection, true zero-copy claims, or paper
reproduction claims.

The RayJoin evaluator warnings are accepted boundaries:

- PIP one-shot lacks loaded-case reuse and nested timing because it is a separate
  one-shot route.
- RTDBSCAN blocked mode is slower than unblocked mode and must not be promoted.

## Validation

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3933_optix_shape_pair_cubin_toolchain_repair_test tests.goal3927_repo_native_combined_pod_perf_queue_test tests.goal3931_combined_pod_perf_manifest_intake_evaluator_test
```

Pod:

```bash
python3 scripts/goal3927_combined_pod_perf_queue.py \
  --output-dir /root/goal3933_combined_pod_artifacts_sourcefix_cubin \
  --rayjoin-data-dir /root/rtdl/data/rayjoin_public_cdb \
  --rtdl-optix-library /root/goal3933_runtime.Phh4Zo/repo/build/librtdl_optix.so \
  --source-commit-label edc90516+goal3933_cubin_sourcefix

python3 scripts/goal3931_evaluate_combined_pod_perf_manifest.py \
  /root/goal3933_combined_pod_artifacts_sourcefix_cubin/summary_manifest.json \
  --output /root/goal3933_combined_pod_artifacts_sourcefix_cubin/goal3931_evaluation.json
```

Expected: queue `pass`; evaluator `accept_with_boundary`.
