# Goal4474 V3.0 M78 Triangle Prepared Ray Batch Weighted Sum

Goal4474 removes the main M77 query envelope cost for prepared segmented
Triangle Counting. The change is generic: prepared OptiX 3-D triangle scenes now
support a prepared ray-batch weighted any-hit sum with partner-owned device
weights. The Triangle app prepares each segment ray batch once, replays the
weighted sum, then releases it.

This does not add graph-specific native engine logic. The engine still sees a
generic prepared triangle scene, a generic prepared 3-D ray batch, and generic
uint64 weights.

## Result Table

All rows use `unique_weighted`, `prepared_segment_replay`, warmup=1, repeat=3,
and the same RTX 4000 Ada pod. Counts match M77 and the known expected paper
counts.

| Dataset | Key builder | Total M77 -> M78 | Total speedup | Query median M77 -> M78 | Query speedup | M78 prepared ray-batch build |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | `cupy_repeat` | 9.515s -> 7.399s | 1.29x | 0.928s -> 0.180s | 5.15x | 0.676s |
| `com-lj` | `numba_direct` | 8.765s -> 5.404s | 1.62x | 0.931s -> 0.180s | 5.18x | 0.672s |
| `soc-LiveJournal1` | `cupy_repeat` | 17.609s -> 14.055s | 1.25x | 1.283s -> 0.264s | 4.86x | 0.961s |
| `soc-LiveJournal1` | `numba_direct` | 16.339s -> 11.669s | 1.40x | 1.340s -> 0.264s | 5.07x | 0.961s |
| `com-orkut` | `cupy_repeat` | 62.477s -> 42.884s | 1.46x | 8.316s -> 1.729s | 4.81x | 6.149s |
| `com-orkut` | `numba_direct` | 55.923s -> 35.379s | 1.58x | 8.560s -> 1.732s | 4.94x | 6.118s |

## Reading

M77 showed that query wall time was not native RT traversal. M78 confirms the
cause: repeated per-replay ray-column packing in the native call path. Moving
that work to a prepared ray batch cuts query median by about 4.8x-5.2x across
the large rows.

The cost is now explicit build-once work. For `numba_direct`, prepared ray-batch
build costs about 0.67s, 0.96s, and 6.12s on the three rows, but it is paid once
per segment set instead of on every replay query. That is the correct
prepare-once/query-many shape for this route.

Current best internal Triangle Counting row is now `numba_direct` plus prepared
ray batch: 5.404s on `com-lj`, 11.669s on `soc-LiveJournal1`, and 35.379s on
`com-orkut`, all exact.

## Claim Boundary

Allowed:

- Internal wording that M78 removes repeated ray-column packing from the
  prepared replay query path.
- Internal wording that `numba_direct` plus prepared ray batch is the current
  fastest measured Triangle Counting route on the three large rows.
- Generic primitive/runtime wording: prepared triangle scene plus prepared ray
  batch plus device weights.

Blocked:

- Public triangle-count RT-core speedup wording.
- RTDL beats cuGraph wording until the comparison packet is refreshed after M78.
- Whole-app acceleration wording.
- Graph-specific native engine callbacks or app-specific native ABI.

## Evidence

- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_packet_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_cupy_repeat_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_numba_direct_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_cupy_repeat_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_numba_direct_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_cupy_repeat_com_orkut_w1r3_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_numba_direct_com_orkut_w1r3_2026-06-16.json`
