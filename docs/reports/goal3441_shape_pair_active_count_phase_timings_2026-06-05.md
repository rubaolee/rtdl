# Goal3441 Shape-Pair Active-Count Phase Timings

**Date:** 2026-06-05  
**Status:** implemented; pod artifact pending  
**Scope:** generic OptiX shape-pair active-count diagnostic telemetry

## Purpose

Goal3438 showed that the prepared Spatial RayJoin overlay-seed active-count
route is stable but still around `0.148s` on the available public
county-vs-county-slice input. Before changing algorithms, Goal3441 adds generic
phase telemetry to the existing shape-pair relation active-count path.

The purpose is to distinguish:

- left-side host preparation;
- left-side upload/allocation;
- OptiX traversal;
- device flag download;
- CPU containment supplement;
- total candidate pair count;
- active pair count.

This is diagnostic infrastructure. It is not a speedup claim.

## What Changed

| File | Operation |
| --- | --- |
| `src/native/optix/rtdl_optix_workloads.cpp` | Added thread-local shape-pair phase timing storage, reset logic, timing instrumentation, and `rtdl_optix_shape_pair_relation_get_last_phase_timings`. |
| `src/native/optix/rtdl_optix_prelude.h` | Declared the new generic timing accessor. |
| `src/rtdsl/optix_runtime.py` | Added `PreparedOptixShapePairRelation.last_phase_timings()` and `get_last_shape_pair_relation_phase_timings()`. |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Includes `native_phase_timings` in the overlay active-count prepared-handle payload. |
| `scripts/goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py` | Carries overlay native timing metadata when the Goal3438 probe is rerun on a rebuilt backend. |
| `scripts/goal3441_shape_pair_active_count_phase_timing_probe.py` | Added a focused visible-progress pod probe for the overlay active-count timing breakdown. |
| `tests/goal3441_shape_pair_active_count_phase_timings_test.py` | Added regression coverage for native, Python, app, probe, report, and optional pod artifact surfaces. |

## Boundary

The native engine still sees generic shape-pair relation flags and generic
active-count semantics. No RayJoin-specific or CDB-specific native code was
added.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `rayjoin_paper_reproduction_claim_authorized: False`
- `rtdl_beats_rayjoin_claim_authorized: False`

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3441_shape_pair_active_count_phase_timings_test tests.goal3438_spatial_rayjoin_prepared_subroute_reuse_test
```

Expected result:

```text
OK
```

Pod command:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
python3 scripts/goal3441_shape_pair_active_count_phase_timing_probe.py \
  --iterations 4 \
  --left-cdb data/rayjoin_public_cdb/br_county.cdb \
  --right-cdb data/rayjoin_public_cdb/br_county_start256_count1024.cdb \
  --output docs/reports/goal3441_shape_pair_active_count_phase_timings_pod_2026-06-05.json
```

The probe prints one progress line per iteration beginning with `[goal3441]`.

## Next

Use the phase breakdown to decide the next performance move. If containment
dominates, the next safe generic optimization is a prepared right-side bounds
candidate index for the CPU containment supplement. If traversal dominates, the
next target is a device-side active-count-only relation path that avoids the
full flag buffer.
