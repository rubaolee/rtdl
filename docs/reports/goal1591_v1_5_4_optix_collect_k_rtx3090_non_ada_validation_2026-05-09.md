# Goal 1591: RTX 3090 Non-Ada OptiX Collect-K Validation

## Verdict

RTX 3090 validation completed on a fresh Git checkout at `3fa0bba9c440c54cf26adbf8af6d90df866088e6`. Parity passed for the measured targeted cases. The candidate preset is clearly positive for `candidate_count=65537`, but mixed or slightly negative for `49153` and `65536`, so this non-Ada evidence does not justify promoting the candidate preset or making public speedup claims.

## Environment

- Host: `root@213.192.2.74 -p 40053`
- Checkout: `/root/work/rtdl_rtx3090`
- GPU: `NVIDIA GeForce RTX 3090`
- Driver: `580.126.20`
- Driver CUDA banner: `13.0`
- CUDA toolkit: `/usr/local/cuda-12.4`, `nvcc` release `12.4`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- OptiX library: `/root/work/rtdl_rtx3090/build/librtdl_optix.so`
- Runtime architecture override: `RTDL_OPTIX_PTX_ARCH=compute_86`
- Working runtime library path: `/usr/local/cuda-12.4/lib64`

## Configuration Finding

Putting `/usr/local/cuda-12.4/compat` first in `LD_LIBRARY_PATH` caused the measurement path to fail before timing with `cuInit failed with CUDA driver result 803`. Removing the compat directory fixed the run. This is consistent with a stale compatibility `libcuda` shadowing the installed driver library on a pod whose driver already supports the selected toolkit version.

The Goal1586 runner preflight was updated after this finding to reject this unnecessary compat-path configuration before measurement.

## Measured Run

Command shape:

```bash
cd /root/work/rtdl_rtx3090
export CUDA_PREFIX=/usr/local/cuda-12.4
export PATH=/usr/local/cuda-12.4/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:$LD_LIBRARY_PATH
export RTDL_OPTIX_PTX_ARCH=compute_86
PYTHONPATH=src:. python3 scripts/goal1586_v1_5_4_optix_collect_k_multi_session_validation_runner.py \
  --sessions 3 \
  --library build/librtdl_optix.so \
  --output-prefix /root/work/goal1591_rtx3090_measured \
  --repeats 5 \
  --targeted-repeats 9 \
  --candidate-preset-repeats 9 \
  --device-label rtx3090_ampere \
  --cuda-prefix /usr/local/cuda-12.4 \
  --ld-library-path /usr/local/cuda-12.4/lib64
```

Runner output:

- Summary JSON: `/root/work/goal1591_rtx3090_measured_summary.json`
- Summary Markdown: `/root/work/goal1591_rtx3090_measured_summary.md`
- Internal diagnostic tests: `Ran 17 tests`, `OK` in each of 3 sessions.
- CUDA preflight: driver CUDA `(13, 0)`, toolkit CUDA `(12, 4)`, no compat path, not skipped.

## Targeted Result Summary

| Candidate count | Candidate preset avg delta ms | Faster sessions | Parity |
|---:|---:|---:|---|
| 49153 | 0.001764 | 1/3 | pass |
| 65536 | 0.002140 | 1/3 | pass |
| 65537 | -0.016966 | 3/3 | pass |

Negative delta means faster than baseline.

## Claim Boundary

This is non-Ada RTX 3090 validation evidence for the experimental `COLLECT_K_BOUNDED` candidate-preset track. It does not promote the primitive, does not change defaults, does not authorize public speedup wording, and does not publish a release.
