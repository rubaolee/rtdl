# Goal5844 GPU execution and repair plan

Status: ready for an arbitrary single-NVIDIA-GPU pod. No specific GPU model,
driver branch, CUDA image, or preinstalled OptiX SDK is required from the
owner. Environment repair is agent-owned.

## Fixed comparison

- Task: the exact Goal5843 16,384-triangle, 16,384-query weighted all-hit
  checked-U64 scalar task.
- RTDL arm: ordinary public generic family route using native v8 integrated
  audit and compact traversal receipt.
- Comparison arm: NVIDIA `otk-pyoptix` commit
  `3144f224c0fd18733925faf3d8fb82c7376b8dcf`, rebuilt against the same selected
  OptiX headers as RTDL.
- Regime: prepared steady execution, scalar output only, validation outside
  registered intervals, separate fresh process per arm/block.
- Schedule: eight alternating two-arm blocks, 16 warmups and 128 retained
  samples per worker by default.
- Internal target: median within-block RTDL/PyOptiX ratio at most 1.25x.
- Claim status: engineering-only, regardless of result.

## Agent-owned pod sequence

1. Probe `nvidia-smi`, OS, Python, host compiler, CUDA roots, NVCC, NVRTC,
   libdevice, and driver-visible OptiX runtime.
2. Fetch the exact pushed Goal5844 commit into a clean checkout. Never run the
   benchmark from copied dirty source.
3. Select the highest mutually usable OptiX header API, beginning with 9.1 and
   falling back to 9.0 or another source-compatible API if runtime negotiation
   fails. Build pinned PyOptiX and RTDL against the same selected headers.
4. Create an isolated Python 3.12 environment and install pinned NumPy, Numba,
   llvmlite, CuPy/CUDA bindings, build tools, and the clean-built PyOptiX wheel.
   Missing packages or headers are repair work, not a request for another pod.
5. Build the current RTDL DSO with
   `scripts/goal5838_build_selected_sphere_optix_provider.py`, binding exact
   commit, GPU compute capability, CUDA/NVRTC files, headers, and build log.
6. Verify with `nm -D` that
   `rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v8` is exported.
7. Run Goal5844 tests on the pod, then run one untimed worker-zero for each arm.
   Reject wrong output, missing traversal, wrong generation, wrong v8 boundary,
   or receipt-validation failure before timing.
8. Run `scripts/goal5844_run_gpu_engineering_comparison.py` with cache and
   output roots outside the clean checkout.
9. Preserve `SUMMARY.json`, every worker JSON, stdout/stderr, native build
   manifest/log, package freeze, hardware identity, exact Git commit, and
   selected SDK/CUDA identities.
10. Copy evidence back, independently revalidate it on the Mac, and write the
    measured phase diagnosis.

## Performance decision tree

- Ratio <= 1.25x: mark the internal engineering target met, retain all rows,
  and request deferred external review before any manuscript use.
- Ratio > 1.25x: retain the adverse result and compare public, provider-owner,
  direct-native-v8, and explicit-forensic medians. Optimize only the largest
  measured remaining layer.
- Provider close to PyOptiX but public slow: reduce non-frozen protocol/generic
  envelope construction without dropping validation.
- Native v8 itself slow: profile integrated audit bookkeeping and host/device
  synchronization; do not blame Python.
- Provider slow but native close: profile compact receipt hashing and Python
  result construction.
- Both arms unstable: rerun only after recording GPU utilization/clock state;
  never discard a completed adverse block selectively.

## Current external dependency

The last supplied endpoint `194.68.245.56:22160` timed out on 2026-09-04.
Local implementation and review continue, but fresh GPU build and timing need
one reachable NVIDIA pod endpoint.
