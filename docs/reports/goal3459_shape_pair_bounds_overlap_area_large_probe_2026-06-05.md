# Goal3459 - Large Bounds-Overlap Area Continuation Probe

## Status

Implemented locally; pod validation pending.

Goal3459 measures the Goal3456 bounds-overlap area continuation on the public RayJoin CDB subset used by the recent relation-column probes.

## Scope

This is an internal scale/performance characterization. It measures:

- relation-column production time
- CuPy bounds-overlap continuation time
- row count stability
- grouped-left count stability
- area-sum stability
- nonnegative area invariant

It does not compare against the RayJoin paper and does not claim exact polygon overlay area.

## Boundary

This goal does not authorize:

- v2.8 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay-area or exact witness completion claims

## Validation

Local validation:

- `py -3 -m py_compile scripts\goal3459_shape_pair_bounds_overlap_area_large_probe.py`
- `py -3 -m unittest tests.goal3459_shape_pair_bounds_overlap_area_large_probe_test`

Pod validation target:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python scripts/goal3459_shape_pair_bounds_overlap_area_large_probe.py \
  --iterations 4 \
  --max-rows 65536 \
  --output docs/reports/goal3459_shape_pair_bounds_overlap_area_large_probe_pod_2026-06-05.json
```

## Remaining Work

The exact overlay lane still needs polygon witness/area continuation. Bounds-overlap area is only a generic upper-bound/proxy continuation over the resident payload.
