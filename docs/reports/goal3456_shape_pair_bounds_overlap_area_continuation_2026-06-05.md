# Goal3456 - Shape-Pair Bounds-Overlap Area Continuation

## Status

Implemented locally; pod validation pending.

Goal3456 adds the first generic consumer of the Goal3453/3455 relation geometry payload: a CuPy continuation that computes axis-aligned bounds-overlap area for active shape-pair relation rows and optionally groups those areas by left or right id.

## Scope

The continuation is:

- generic: it consumes relation ids, relation ordinals, and geometry payload columns
- partner-explicit: users call `shape_pair_relation_bounds_overlap_area_cupy(...)`
- app-agnostic: no RayJoin, CDB, county, soil, or overlay-specific engine logic
- honest: it computes bounds-overlap area, not exact polygon overlay area

## Boundary

This goal does not authorize:

- v2.8 release
- public speedup wording
- RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay-area or exact witness completion claims

## Validation

Local validation target:

- `py -3 -m py_compile src\rtdsl\geometry_relation_continuations.py scripts\goal3456_shape_pair_bounds_overlap_area_continuation_probe.py`
- `py -3 -m unittest tests.goal3456_shape_pair_bounds_overlap_area_continuation_test`

Pod validation target:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python scripts/goal3456_shape_pair_bounds_overlap_area_continuation_probe.py \
  --output docs/reports/goal3456_shape_pair_bounds_overlap_area_continuation_pod_2026-06-05.json
```

Expected row areas for the sparse rectangle fixture:

| left_id | right_id | bounds_overlap_area |
| ---: | ---: | ---: |
| 3 | 10 | 1.0 |
| 3 | 11 | 0.25 |
| 20 | 13 | 1.0 |

Expected grouped sums by left id:

| left_id | bounds_overlap_area_sum |
| ---: | ---: |
| 3 | 1.25 |
| 20 | 1.0 |

## Remaining Work

Full RayJoin-style overlay still requires an exact polygon witness/area continuation. This goal only proves that the resident relation stream, ordinals, and geometry payload can feed a real device-side area-style partner continuation.
