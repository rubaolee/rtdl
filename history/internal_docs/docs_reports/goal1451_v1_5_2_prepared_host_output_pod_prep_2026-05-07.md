# Goal1451 v1.5.2 Prepared Host-Output Pod Prep

## Verdict

Pod work is better prepared. A local Linux OptiX compatibility run now passes,
but the remaining RT-priority evidence still requires a real NVIDIA RT-capable
pod if we want RTX/RT-core wording or performance conclusions.

## Completed

- Added `scripts/goal1450_v1_5_2_prepared_host_output_pod_executor.sh`.
- Added `docs/handoff/goal1450_pod_runbook_2026-05-07.md`.
- Added tests that require the executor/runbook to build OptiX, require both
  Embree and OptiX, record artifacts, and keep claim boundaries closed.
- Validated the new files on Windows and Linux.
- Ran Linux dry runs to confirm the executor writes environment, build, parity,
  and summary artifacts.
- Fixed the executor's `NVCC` default so it falls back to `command -v nvcc`
  when `${CUDA_PREFIX}/bin/nvcc` is absent.

## Dry-Run Finding

The first Linux dry run recorded a controlled `build-optix` failure because the
host had `nvcc` at `/usr/bin/nvcc` while the initial executor default pointed at
`/usr/local/cuda/bin/nvcc`. The executor now chooses `${CUDA_PREFIX}/bin/nvcc`
only when it exists, otherwise it falls back to `command -v nvcc`.

After that fix, the Linux dry run built `librtdl_optix.so` and the required
Embree+OptiX prepared host-output parity package passed on that host. The host
reports a GTX 1070, which is not an NVIDIA RT-core target. Treat that result as
OptiX compatibility/parity evidence only, not RT-core evidence and not a
performance claim.

## Pod Command

```bash
git clone https://github.com/rubaolee/rtdl rtdl_goal1450_pod
cd rtdl_goal1450_pod
bash scripts/goal1450_v1_5_2_prepared_host_output_pod_executor.sh
```

If OptiX headers are custom:

```bash
OPTIX_PREFIX=/path/to/optix-dev CUDA_PREFIX=/usr/local/cuda \
  bash scripts/goal1450_v1_5_2_prepared_host_output_pod_executor.sh
```

## Boundary

This prep work does not authorize true zero-copy wording, public speedup
wording, whole-app claims, stable primitive wording, or release action. The
remaining accepted evidence is required Embree+OptiX prepared host-output parity
with no required backend skips.
