# Goal5844 GPU execution and repair plan

Status: pre-pod implementation and hostile validation complete. The remaining
work is actual CUDA/OptiX compilation, GPU worker-zero, measurement, and any
measurement-directed optimization. No specific GPU model, R570/R590 branch,
or preinstalled OptiX SDK is required. The pod must expose an NVIDIA Linux GPU
and a driver supported by the frozen OptiX 7.6--9.1 registry. A CUDA development
toolkit is intrinsically required to compile the current native provider; the
runner discovers it, and missing user-space Python/OptiX/PyOptiX dependencies
are agent-owned repair work.

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
4. Create an isolated Python 3.11/3.12 environment and install the fully pinned
   Python dependency closure and clean-built PyOptiX wheel. A missing suitable
   Python uses pinned `uv==0.12.10`, not a mutable installer URL. Missing
   packages or headers are repair work, not a request for another pod.
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

## Single local entry point

After the final pre-pod commit is pushed as the tip of the current branch, the
only host-side entry point is:

```bash
COMMIT=$(git rev-parse HEAD)
PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5844_launch_pod_transaction.py \
  --host POD_HOST --port POD_PORT --user root \
  --identity /Users/rl2025/.ssh/id_ed25519_rtdl_codex \
  --expected-commit "$COMMIT" \
  --local-output /tmp/goal5844-result
```

The launcher refuses a dirty checkout, a non-tip remote commit, reused local
or remote output paths, and a wrong endpoint key. It fetches the exact commit
on the pod, invokes `scripts/goal5844_pod_prepare_and_run.sh`, streams the
result through SSH stdout even when SCP/SFTP is unavailable, verifies the
remote archive SHA256, safely extracts it, and independently recomputes the
downloaded result on the Mac.

The pod-local entry point performs these create-only stages in order:

1. Probe GPU, driver, compute capability, CUDA toolkit, compiler, and Python;
   reject an NVCC that cannot target the observed compute capability.
2. Select the highest compatible frozen OptiX stack solely from driver version.
3. Clone exact PyOptiX and OptiX-header commits into fresh clean checkouts.
4. Build a PyOptiX wheel from a Git archive and bind source, headers, Python,
   CMake, C++, NVCC, Ninja, wheel member, installed extension, and package
   versions in one sealed receipt.
5. Build the exact RTDL DSO and require the native v8 symbol with `nm -D`.
6. Run focused tests and one minimal untimed worker for each arm using
   disposable formal/CUDA/CuPy/Numba/XDG preflight caches.
7. Run the fresh-cache alternating eight-block engineering comparison.
8. Verify every copied payload, worker receipt, raw timing summary, schedule,
   native traversal receipt, PyOptiX binary binding, and aggregate twice: once
   on the pod and once after download.

The compact return archive intentionally excludes the venv, upstream clones,
and disposable caches. Any failed stage produces a separately hashed failure
bundle that the launcher retrieves automatically. The comparison directory
itself preserves all evidence
needed for offline verification: RTDL DSO/build manifest/build log/symbols,
device source, PyOptiX source/header archives/wheel/installed extension/build
logs, every worker JSON/stdout/stderr, `SUMMARY.json`, and the non-self-
referential `EVIDENCE_MANIFEST.json`.

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

## Remaining GPU-only gates

1. Compile and load the new native v8 ABI on the selected real toolchain.
2. Pass both minimal GPU workers and the downloaded-result verifier.
3. Obtain the balanced retained timing rows and respond to the measured largest
   layer if the 1.25x internal engineering target is missed.

No source design, environment orchestration, provenance format, transfer path,
offline verifier, or pre-pod test remains to be invented after an endpoint is
provided.
