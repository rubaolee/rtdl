# Goal3441 Shape-Pair Active-Count Phase Timings

**Date:** 2026-06-05  
**Status:** implemented and pod-validated
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
- active-flag scan/reduction over the downloaded relation flags;
- total candidate pair count;
- active pair count.

The focused probe also records `measured_native_phase_sum_sec` and
`unattributed_host_orchestration_sec`, so the timing artifact can separate
explicitly timed native work from residual host/runtime overhead.

This is diagnostic infrastructure. It is not a speedup claim.

## What Changed

| File | Operation |
| --- | --- |
| `src/native/optix/rtdl_optix_workloads.cpp` | Added thread-local shape-pair phase timing storage, reset logic, timing instrumentation, active-scan timing, and `rtdl_optix_shape_pair_relation_get_last_phase_timings`. |
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

Pod artifact:

- `docs/reports/goal3441_shape_pair_active_count_phase_timings_pod_2026-06-05.json`
- `docs/reports/goal3441_shape_pair_active_count_phase_timings_pod_2026-06-05.stdout`

Pod result on `NVIDIA RTX A5000, 580.126.09`, commit
`01825de8aab0a67cf4bb925ca6bd6e51b957befc`, using
`br_county.cdb` as left shapes and `br_county_start256_count1024.cdb`
as the available right-shape slice:

| Measure | Median seconds | Notes |
| --- | ---: | --- |
| Total Python-visible active-count call | `0.147027` | 15,700 left shapes x 949 right shapes = 14,899,300 relation pairs |
| Measured native phase sum | `0.083365` | Sum of the explicit native phase timers below |
| Unattributed host/runtime orchestration | `0.062244` | Residual after explicit native phases; includes current full-buffer path overhead not separately decomposed here |
| CPU containment supplement | `0.055393` | Largest explicit phase |
| Device flag download | `0.013836` | Full relation flag buffer transfer |
| Active-flag scan/reduction | `0.011633` | Host-side scan over relation flags |
| OptiX traversal | `0.000955` | Not the bottleneck |
| Left-side prepare | `0.000795` | Small |
| Left-side upload | `0.000682` | Small median, one run had a larger upload blip |

Interpretation: the relation traversal itself is already cheap. The next
performance target should not be another RT traversal tweak. The useful targets
are (1) moving containment and active-count reduction toward a device-side
active-count-only relation path, and (2) avoiding or shrinking the full relation
flag buffer download and host scan.

## Next

Use the phase breakdown to decide the next performance move. On the pod result,
containment plus full-buffer download/scan plus residual orchestration dominate.
The next target is a device-side active-count-only relation path that avoids
materializing and scanning the full flag buffer on the host. A prepared
right-side bounds candidate index remains a secondary generic optimization for
the containment supplement. The OptiX relation kernel itself is not currently
the bottleneck.
