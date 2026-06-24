# Goal4469 V3.0 M73 Triangle Prepared Segment Replay

Goal4469 follows the Goal4468 unique-weighted segment-ray result. M72 reduced
RT traversal pressure, but rebuilt/compressed the same segment rays for every
warmup/repeat pass. M73 adds an explicit schedule:

`--segment-query-schedule prepared_segment_replay`

For each segment, the CuPy partner builds the unique-weighted ray batch once,
RTDL replays all warmup/repeat queries against that segment, then the segment is
released. Memory remains bounded to one segment, and the engine contract stays
generic: rays, triangles, weights, weighted any-hit summary.

## Result Table

All rows are exact and use warmup=1, repeat=3.

| Dataset | Count | Logical rays | Prepared rays | M71 duplicate total | M72 unique per-run total | M73 prepared replay total | M73 vs M71 | M73 vs M72 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 177,820,130 | 928,731,472 | 528,793,097 | 14.153s | 14.073s | 9.552s | 1.48x | 1.47x |
| `soc-LiveJournal1` | 285,730,264 | 1,383,299,326 | 750,099,466 | 25.747s | 25.105s | 17.986s | 1.43x | 1.40x |
| `com-orkut` | 627,584,181 | 8,579,930,671 | 4,759,226,031 | 115.032s | 116.527s | 62.428s | 1.84x | 1.87x |

## Reading

This is the first Triangle Counting V3 step that clearly improves the large-row
formal totals, not only the traversal subphase.

Across the three large rows, M73 is 1.43x-1.84x faster than the M71
duplicate-ray totals and 1.40x-1.87x faster than the M72 unique-per-run totals.

The reason is simple: M72 paid unique compression once per segment per measured
run. M73 pays it once per segment, replays repeated queries, and releases the
segment. That is the right schedule for a prepared/repeated workload and a
cleaner benchmark measurement loop.

This still does not authorize public RT-core triangle-count speedup wording.
cuGraph remains faster end to end, and the RT-Graph authors pure count kernels
remain much faster than RTDL traversal. M73 is an internal current-route
engineering improvement.

## Claim Boundary

Allowed:

- Current-route wording that prepared segment replay improves large-row totals.
- Current-route wording that unique-weighted rays reduce traversal pressure.
- Explicit user selection of `unique_weighted` plus `prepared_segment_replay`.

Blocked:

- Public triangle-count RT-core speedup wording.
- RTDL beats cuGraph wording.
- RTDL traversal beats authors pure kernels wording.
- Hidden automatic schedule or partner selection.
- Graph-specific native engine callbacks.

## Next Action

The next decision is whether to make this explicit schedule the recommended
prepared Triangle Counting route, while keeping one-shot build cost separate
from replay throughput. Further useful work is cheaper unique-key compression
or a reusable prepared ray-batch API; more cap tuning is lower value unless
hardware changes.

## Evidence

- `docs/reports/goal4469_v3_0_m73_triangle_prepared_segment_replay_packet_2026-06-16.json`
- `docs/reports/goal4469_v3_0_m73_triangle_prepared_unique_weighted_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4469_v3_0_m73_triangle_prepared_unique_weighted_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4469_v3_0_m73_triangle_prepared_unique_weighted_com_orkut_w1r3_2026-06-16.json`
- `docs/reports/goal4468_v3_0_m72_triangle_unique_weighted_comparison_packet_2026-06-16.json`
- `docs/reports/goal4467_v3_0_m71_triangle_current_comparison_packet_2026-06-16.json`
