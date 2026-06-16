# Goal4471 V3.0 M75 Triangle Prepared Replay Phase Split

Goal4471 closes the immediate post-M73 measurement debt: the segmented
Triangle Counting route now emits `phase_split_ms`, so build-once cost and
hot/replay query throughput are explicit.

This does not change the route contract. The app/CuPy partner still lowers
graph two-hop keys into rays and weights, and the RTDL native engine still sees
generic triangle scenes, generic rays, and a weighted any-hit scalar summary.

## Result Table

All rows use `--segment-ray-representation unique_weighted`,
`--segment-query-schedule prepared_segment_replay`, warmup=1, repeat=3, and the
same RTX 4000 Ada pod as M73/M74.

| Dataset | Count | Total | Build once | Median replay query | Replay query total | Amortized backend/query |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 177,820,130 | 9.657s | 2.341s | 0.925s | 2.772s | 1.704s |
| `soc-LiveJournal1` | 285,730,264 | 17.569s | 3.035s | 1.282s | 3.864s | 2.300s |
| `com-orkut` | 627,584,181 | 61.745s | 15.243s | 8.216s | 24.657s | 13.300s |

The emitted counts match the known expected paper-dataset counts from the
Goal2593/Goal4462-4464 chain. The large M75 runs did not rebuild the Python
oracle inline because that oracle is itself too heavy at these scales; an
initial `com-lj --validate-oracle` attempt was killed while building that
oracle, before producing a timing artifact.

## Reading

The old `timing_ms.segment_ray_build_total_ms` field is not the right field for
prepared-replay wording. For prepared replay it repeats the paid-once segment
ray build across the measured repeats. In M75, for example, `com-orkut` reports
15.243s actual build-once cost, while the legacy segment-ray build total is
42.107s because it is accumulated across three measured repeats.

The useful optimization reading is now cleaner:

- `com-lj`: build once is 2.341s, median replay query is 0.925s.
- `soc-LiveJournal1`: build once is 3.035s, median replay query is 1.282s.
- `com-orkut`: build once is 15.243s, median replay query is 8.216s.

So the next real work is not more timing interpretation or cap fiddling. It is
cheaper unique-key compression/ray construction, or a reusable prepared
ray-batch API, while keeping the RTDL native primitive app-agnostic.

## Claim Boundary

Allowed:

- Current-route phase-split wording for prepared segmented Triangle Counting.
- Wording that M75 separates paid-once build cost from hot/replay query cost.
- Explicit user selection of `unique_weighted` plus `prepared_segment_replay`.

Blocked:

- Public triangle-count RT-core speedup wording.
- RTDL beats cuGraph wording.
- RTDL traversal beats RT-Graph authors pure count kernels wording.
- Hidden automatic partner, schedule, cap, or backend selection.
- Graph-specific native engine logic.

## Evidence

- `docs/reports/goal4471_v3_0_m75_triangle_phase_split_packet_2026-06-16.json`
- `docs/reports/goal4471_v3_0_m75_triangle_phase_split_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4471_v3_0_m75_triangle_phase_split_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4471_v3_0_m75_triangle_phase_split_com_orkut_w1r3_2026-06-16.json`
