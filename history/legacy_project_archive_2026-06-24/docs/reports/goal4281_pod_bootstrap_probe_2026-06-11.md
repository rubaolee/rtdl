# Goal4281 Pod Bootstrap Probe

Status: local pod-readiness hardening for v2.10 hardware validation.

## Purpose

Goal4280 added a bounded pod validation bundle, but a fresh pod can still fail
late if CUDA, OptiX headers, CuPy, Numba, or `librtdl_optix` are missing. Goal4281
adds a fast bootstrap probe that reports these prerequisites before the long
benchmark bundle starts.

## Delivered

| File | Action | Reason |
| --- | --- | --- |
| `scripts/rtdl_pod_bootstrap_probe.py` | Added pod setup probe. | Checks NVIDIA visibility, compiler/toolchain availability, OptiX header discovery, partner module imports, and RTDL OptiX library presence. |
| `docs/audit/runbooks/v2_10_pod_bootstrap_probe.md` | Added current bootstrap runbook. | Gives short commands for human, JSON, and strict automation modes. |
| `docs/audit/runbooks/v2_10_pod_validation_bundle.md` | Linked the probe as the first step. | Prevents starting the long bundle before setup blockers are visible. |
| `tests/goal4281_pod_bootstrap_probe_test.py` | Added focused tests. | Verifies JSON/text output, strict-mode behavior, non-authorizing flags, and runbook wiring. |

## Boundary

The probe does not install dependencies, build OptiX, run benchmark timing, or
authorize release/performance claims. It is a readiness check for pod setup.

## Validation

Focused validation command:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal4281_pod_bootstrap_probe_test \
  tests.goal4280_v2_10_pod_validation_bundle_test
```

Focused bootstrap-probe gate: 6 tests ran, all passed.

Expanded v2.10 local gate: 37 tests ran, all passed.
