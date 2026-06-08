# Goal3910 RayJoin LSI/Overlay Shared Loaded-Case Reuse

Date: 2026-06-08

## Purpose

Goal3908 identified the RayJoin representative wrapper as dominated by the LSI/overlay subprobe. Goal3909 added nested phase timing. Goal3910 removes one avoidable source of benchmark/app-layer duplication before the next pod pass: the LSI/overlay subprobe now loads each CDB-derived case once and feeds the same loaded app inputs to the Numba baseline and RTDL/OptiX prepared route.

## Change

`scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py` now has loaded-case helpers:

- `run_numba_baseline_loaded_case(...)`
- `run_rtdl_optix_loaded_case(...)`

The normal standalone functions still exist, but `run_probe(...)` now uses a shared loaded case for each selected case. The payload records `shared_loaded_case_reuse_enabled: true`, `shared_load_case_sec`, and RTDL/OptiX route labels ending in `_loaded_case_reuse`.

## Boundary

This is not a native-engine change. It does not add RayJoin-specific engine logic, automatic dispatch, or new public speedup claims. It is an app/benchmark orchestration cleanup over existing generic prepared RTDL/OptiX primitives and existing Numba same-contract baselines.

## Local Validation

The focused local tests mock the heavy backend calls and validate that:

- `_load_rayjoin_case(...)` is invoked once per case by `run_probe(...)`;
- the loaded case is passed to both the Numba and RTDL/OptiX helpers;
- the payload advertises shared loaded-case reuse and keeps claim boundaries false.

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3910_rayjoin_lsi_overlay_shared_case_reuse_test tests.goal3909_rayjoin_lsi_overlay_subprobe_phase_timing_test tests.goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline_test
```

Expected result: all tests pass.

## Pod Status

No A5000 timing evidence is included in this report. A later clean pod run should compare Goal3908/Goal3909-style wrapper timing against this shared loaded-case path.
