# Goal3428 Closed-Shape Ordinal Chunk Guard

**Date:** 2026-06-05  
**Status:** implemented and pod-validated  
**Scope:** follow-up hardening for Goal3424 instance-aware closed-shape candidate streams

## Purpose

Goal3424 added optional instance identity columns (`point_ordinal`, `shape_ordinal`) to the generic closed-shape candidate stream so partner refiners can distinguish duplicate public IDs. Independent Claude review accepted the design but found one dormant correctness bug: the OptiX candidate-column launch loop did not refresh `lp.point_index_offset` inside the point-chunk loop.

The current CDB validation dataset fits in one point chunk, so Goal3424's pod evidence remains valid. For future larger datasets, however, chunks after the first would have emitted point ordinals relative to zero rather than relative to their chunk start. That would corrupt the partner-side instance lookup.

## Change

`src/native/optix/rtdl_optix_workloads.cpp` now sets:

```cpp
lp.point_index_offset = static_cast<uint32_t>(point_offset);
```

inside `run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix`, immediately after the chunk's point-id pointer is selected and before `lp.probe_count` is uploaded.

This keeps the ordinal contract app-agnostic: the native engine emits generic input-row ordinals and prepared primitive ordinals. It does not infer public-ID policy, RayJoin semantics, or ownership rules.

## Test Coverage Added

`tests/goal3424_closed_shape_instance_identity_refinement_test.py` now checks:

- The candidate-column chunk loop refreshes `lp.point_index_offset` from `point_offset`.
- A tiny duplicate-public-ID CuPy regression, when CuPy is available, returns two `(point_id, shape_id)` rows by using distinct `point_ordinal` / `shape_ordinal` pairs.

The synthetic case is intentionally small:

- Two points share public id `7` but occupy different squares.
- Two shapes share public id `9` but have different vertex rings.
- Candidate rows use public ids `(7, 9)` for both hits and ordinals `(0, 0)` and `(1, 1)` to select the correct instances.

## Local Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3424_closed_shape_instance_identity_refinement_test tests.goal3427_prepared_cupy_refiner_timing_test
```

Result:

```text
Ran 9 tests in 0.037s
OK (skipped=1)
```

The skip is expected on the Windows host when CuPy/CUDA is unavailable.

## Pod Validation

Pod:

```text
NVIDIA RTX A5000, driver 580.126.09
CuPy 14.1.1
RTDL commit e53c919d
```

Command summary:

```bash
git reset --hard origin/main
export OPTIX_PREFIX=/root/vendor/optix-sdk
make build-optix
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so
python3 -m unittest \
  tests.goal3424_closed_shape_instance_identity_refinement_test \
  tests.goal3427_prepared_cupy_refiner_timing_test
```

Result:

```text
Ran 9 tests in 1.153s
OK
```

## Claim Boundary

This hardening does not authorize release, RayJoin paper reproduction, public speedup claims, true zero-copy claims, hidden dispatch, automatic retry, or native default-route claims. It closes a correctness guard for larger chunked candidate streams.
