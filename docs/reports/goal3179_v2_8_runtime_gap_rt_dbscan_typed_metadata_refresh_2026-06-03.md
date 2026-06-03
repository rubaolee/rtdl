# Goal3179: RT-DBSCAN Runtime-Gap Refresh After Typed Metadata

## Purpose

Goal3158 already added typed producer metadata for the fixed-radius graph
component front door used by the RT-DBSCAN grouped-stream path. The v2.8
runtime-gap matrix still described typed producer metadata as remaining work.

Goal3179 refreshes only that status wording.

## What Changed

- Updated the `rt_dbscan` row in `src/rtdsl/v2_8_benchmark_runtime_gap.py`.
- Added `Goal3158` and `Goal3179` to the row evidence refs.
- Added `tests/goal3179_v2_8_runtime_gap_rt_dbscan_typed_metadata_refresh_test.py`.

## Updated State

typed producer metadata now exists for the current RT-DBSCAN front-door path.
The current best path is still:

- fixed-radius/core-summary primitives;
- v2.8 fixed-radius graph component front door;
- measured OptiX+CuPy grouped-stream continuation;
- typed adjacency/grouped-stream producer metadata from Goal3158.

## Still Open

The remaining RT-DBSCAN v2.8 work is not native app-specific logic. It is shared
runtime hardening:

- broader partner conformance beyond the current measured CuPy grouped-stream
  reference;
- larger device-resident continuation coverage;
- claim-bounded evidence that does not promote true-zero-copy, public speedup,
  broad RT-core speedup, or release wording.

Required false flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Passed:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3179_v2_8_runtime_gap_rt_dbscan_typed_metadata_refresh_test `
  tests.goal3158_fixed_radius_graph_typed_producer_metadata_test `
  tests.goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_test `
  tests.goal3156_rt_dbscan_v2_8_front_door_route_test `
  tests.goal3155_fixed_radius_graph_component_front_door_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Result: 25 tests passed.

Pod validation from a clean `origin/main` reset also passed:

```bash
cd /root/rtdl_goal3151
git fetch origin main
git reset --hard origin/main
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
/root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3179_v2_8_runtime_gap_rt_dbscan_typed_metadata_refresh_test \
  tests.goal3158_fixed_radius_graph_typed_producer_metadata_test \
  tests.goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_test \
  tests.goal3156_rt_dbscan_v2_8_front_door_route_test \
  tests.goal3155_fixed_radius_graph_component_front_door_test \
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Pod head: `04cd50dc`.

Result: 25 tests passed.

## Boundary

Goal3179 is a status refresh. It changes no kernels, no app semantics, no partner
selection behavior, and no public claims.
