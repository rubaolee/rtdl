# Goal4293: Pod Probe CUDA-Prefix NVCC Discovery

Date: 2026-06-11

## Trigger

The A40 pod reported `nvcc unavailable` even though `nvcc` existed at
`/usr/local/cuda-12.8/bin/nvcc`. The bootstrap probe only checked PATH, while
the Makefile already supports CUDA prefix discovery.

## Fix

`scripts/rtdl_pod_bootstrap_probe.py` now searches common CUDA prefixes when
`shutil.which("nvcc")` does not find a PATH entry:

- `CUDA_HOME`
- `CUDA_PATH`
- `/usr/local/cuda`
- `/usr/local/cuda-13.0`
- `/usr/local/cuda-12.8`
- `/usr/local/cuda-12.6`
- `/usr/local/cuda-12.5`
- `/usr/local/cuda-12.4`
- `/usr/lib/cuda`
- `/opt/cuda`

## Boundary

This is a readiness-probe correction only. It does not install CUDA, build
OptiX, run hardware validation, move tags, or authorize release/performance claims.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4293_pod_probe_cuda_prefix_nvcc_test
```

## Verdict

`accept`: the probe now agrees with the Makefile's CUDA-prefix model and avoids
false `nvcc unavailable` blockers on CUDA-prefix pods.
