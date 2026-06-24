# Goal4295: Pod Probe Executes Discovered NVCC Path

Date: 2026-06-11

## Purpose

Fix a small readiness-reporting issue found during the Goal4294 A40 pod run.

After Goal4293, `scripts/rtdl_pod_bootstrap_probe.py` could discover `nvcc`
under CUDA prefix candidates such as `/usr/local/cuda-12.8/bin/nvcc`, but the
version probe still executed plain `nvcc --version`. On pods where CUDA is
installed but not on `PATH`, this made the JSON internally confusing:

- `checks.nvcc.path` pointed at a real compiler.
- `checks.nvcc.probe.ok` could still be false because `nvcc` was not on `PATH`.

## Change

The probe now executes the exact discovered path:

```python
_run([nvcc_path, "--version"], timeout=10)
```

This keeps the probe consistent with the CUDA-prefix discovery logic and avoids
penalizing otherwise usable pods for a missing `PATH` entry.

## Boundary

This is a probe/reporting hardening only. It does not install CUDA, does not
select a CUDA version for builds, does not authorize release/performance claims,
and does not change any benchmark behavior.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4295_pod_probe_absolute_nvcc_execution_test
```

## Verdict

`accept`: the bootstrap probe now reports discovered CUDA-prefix compilers more
faithfully.
