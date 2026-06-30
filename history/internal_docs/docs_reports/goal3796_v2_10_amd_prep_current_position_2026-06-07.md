# Goal3796 v2.10 AMD Prep Current Position

Status: implemented locally.

## Current Position

The v2.10 HIPRT/AMD preparation lane is engineering-complete on the available
NVIDIA CUDA/Orochi control hardware:

- 10 promoted benchmark apps are mapped to app-agnostic HIPRT contracts.
- 0 apps remain blocked on missing Numba reference coverage.
- 0 apps remain in `needs_major_followup` in the current adequacy matrix.
- The Goal3785 AMD runner rejects non-AMD hardware and records bounded control
  artifacts instead of minting AMD evidence.
- The runner now auto-discovers common HIPRT SDK paths, including
  version-suffixed `hiprtSdk-*` directories.
- The latest A5000 control packet is Goal3792:
  34 modules, 185 tests, `OK`, scoped source clean, at commit `a7a10228`.
- Gemini has reviewed Goals3783-3792 with verdict `accept`.
- Claude review remains intentionally deferred until after the user-specified
  `2026-06-07 19:00 America/New_York` gate.

## Hardware-Bound Next Step

Actual AMD validation requires an AMD GPU host. On that host, from the repository
root:

```bash
export PYTHONPATH=src:.
python3 scripts/goal3785_amd_hiprt_functional_pod_runner.py
```

If HIPRT SDK auto-discovery does not match the pod layout:

```bash
export PYTHONPATH=src:.
python3 scripts/goal3785_amd_hiprt_functional_pod_runner.py --hiprt-prefix /path/to/hiprtSdk
```

The accepted artifact path is:

`docs/reports/goal3784_amd_hiprt_functional_pod_validation.json`

## What The Current A5000 Pod Can Still Do

The current NVIDIA A5000 pod can continue to provide:

- control regressions for HIPRT/Orochi implementation behavior;
- Numba CUDA executable checks;
- OptiX/NVIDIA performance or correctness probes, if a separate performance
  target is chosen.

It cannot provide:

- AMD functional evidence;
- AMD performance evidence;
- AMD release authorization;
- broad cross-vendor RT-core claims.

## Boundary

Goal3796 does not authorize release action, public speedup wording, AMD
performance wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction claims, zero-copy claims, automatic partner selection, or
app-specific native-engine logic.

It is a current-position report for pod planning and review coordination.

## Validation

Focused validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3796_v2_10_amd_prep_current_position_test
```
