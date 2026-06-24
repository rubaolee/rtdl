# Goal3442 Shape-Pair Active-Count Device Continuation

**Date:** 2026-06-05
**Status:** implemented and pod-validated
**Scope:** generic OptiX shape-pair active-count continuation

## Purpose

Goal3441 showed that the prepared shape-pair active-count path is not limited by
OptiX traversal. The relation traversal median was about `0.001s`, while the
host full-buffer path spent time in CPU containment, full relation-flag download,
host active-flag scan, and residual orchestration.

Goal3442 adds an opt-in generic device-side continuation:

1. Keep the existing generic OptiX shape-pair traversal for segment-intersection
   flags.
2. Keep those flags on device.
3. Run a generic CUDA continuation that evaluates the same first-vertex
   containment shape used by the current active-count route, reduces active
   pairs to one scalar, and copies back only that scalar.

This is a generic shape-pair relation primitive. No RayJoin, CDB, county, or
soil logic is added to the native engine.

## What Changed

| File | Operation |
| --- | --- |
| `src/native/optix/rtdl_optix_core.cpp` | Added `kShapePairRelationActiveCountDeviceKernelSrc`, a generic CUDA continuation kernel over shape-pair relation flags. |
| `src/native/optix/rtdl_optix_workloads.cpp` | Added prepared right-side device bounds, CUDA module loader, and `count_shape_pair_relation_active_device_with_prepared_right_optix`. |
| `src/native/optix/rtdl_optix_prelude.h` | Declared `rtdl_optix_count_prepared_shape_pair_relation_active_device`. |
| `src/native/optix/rtdl_optix_api.cpp` | Exported the opt-in active-count device-continuation C API. |
| `src/rtdsl/optix_runtime.py` | Added `PreparedOptixShapePairRelation.count_active_device_continuation(...)` and timing mode `active_count_device_continuation`. |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Added app-layer `run_packed_left_device_continuation(...)` for comparison against the host exact path. |
| `scripts/goal3442_shape_pair_active_count_device_continuation_probe.py` | Added a visible-progress pod probe comparing host exact active count and device-continuation active count on the same prepared handle. |
| `tests/goal3442_shape_pair_active_count_device_continuation_test.py` | Added static and optional artifact validation. |

## Boundary

The device-continuation route is opt-in until pod evidence proves count equality
against the existing host exact path on the benchmark input. The report and
artifact do not authorize release, public speedup wording, RayJoin reproduction,
RT-core speedup claims, or true zero-copy claims.

This is not a public speedup claim.

The device continuation uses the generic device parity predicate and generic
first-vertex containment rule. The pod probe therefore treats the current
host path as the oracle and records `all_counts_match` before any performance
interpretation.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3442_shape_pair_active_count_device_continuation_test
py -3 -m py_compile src/rtdsl/optix_runtime.py examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py scripts/goal3442_shape_pair_active_count_device_continuation_probe.py tests/goal3442_shape_pair_active_count_device_continuation_test.py
```

Pod command:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
python3 scripts/goal3442_shape_pair_active_count_device_continuation_probe.py \
  --iterations 4 \
  --left-cdb data/rayjoin_public_cdb/br_county.cdb \
  --right-cdb data/rayjoin_public_cdb/br_county_start256_count1024.cdb \
  --output docs/reports/goal3442_shape_pair_active_count_device_continuation_pod_2026-06-05.json
```

The probe prints one `[goal3442]` line per iteration.

Pod artifact:

- `docs/reports/goal3442_shape_pair_active_count_device_continuation_pod_2026-06-05.json`
- `docs/reports/goal3442_shape_pair_active_count_device_continuation_pod_2026-06-05.stdout`

Pod result on `NVIDIA RTX A5000, 580.126.09`, commit
`6d811efc56b82c07879536cb77eebcf42a15674b`, using `br_county.cdb`
as left shapes and `br_county_start256_count1024.cdb` as the available
right-shape slice:

| Measure | Result |
| --- | ---: |
| Host exact counts | `[4543, 4543, 4543, 4543]` |
| Device-continuation counts | `[4543, 4543, 4543, 4543]` |
| `all_counts_match` | `true` |
| Host active-count median | `0.143683s` |
| Device active-count median | `0.006440s` |
| Median device speedup vs host | `22.132x` |

The first device iteration was cold (`0.399456s`) because it paid CUDA module
initialization/first-use cost. The three warm device iterations were
`0.006430s`, `0.006451s`, and `0.006423s`.

The first implementation undercounted by four because the device continuation
used a strict parity predicate. Goal3442 fixed that by adding an inclusive
point-on-boundary check before parity, matching the host exact path on the pod
input.

## Next

The device-continuation counts match and the timing improves. The next step is
to make the prepared Spatial RayJoin overlay active-count reference route use
the new path by default while preserving the host exact route as the
oracle/debug fallback.
