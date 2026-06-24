# Goal3459 - Large Bounds-Overlap Area Continuation Probe

## Status

Implemented and pod-validated on an NVIDIA RTX A5000 pod.

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

Pod validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python -u scripts/goal3459_shape_pair_bounds_overlap_area_large_probe.py \
  --iterations 4 \
  --max-rows 65536 \
  --output docs/reports/goal3459_shape_pair_bounds_overlap_area_large_probe_pod_2026-06-05.json
```

Observed pod evidence at commit `db7f9ed4` on `NVIDIA RTX A5000, 580.126.09`:

- input: `br_county.cdb` (15,700 left shapes) vs `br_county_start256_count1024.cdb` (949 right shapes)
- stable active relation rows: 4,543 across all four iterations
- stable grouped-left rows: 1,261 across all four iterations
- stable bounds-overlap area sum: 150.69938331940557
- median relation-column production time: 0.003933854401111603 seconds
- median CuPy bounds-overlap continuation time: 0.0009836149401962757 seconds
- all row areas were nonnegative
- all release, public speedup, RT-core speedup, true-zero-copy, RayJoin-paper reproduction, RTDL-beats-RayJoin, and full-overlay-area claim flags remained false

Artifacts:

- `docs/reports/goal3459_shape_pair_bounds_overlap_area_large_probe_pod_2026-06-05.json`
- `docs/reports/goal3459_shape_pair_bounds_overlap_area_large_probe_pod_2026-06-05.stdout`

## Remaining Work

The exact overlay lane still needs polygon witness/area continuation. Bounds-overlap area is only a generic upper-bound/proxy continuation over the resident payload.
