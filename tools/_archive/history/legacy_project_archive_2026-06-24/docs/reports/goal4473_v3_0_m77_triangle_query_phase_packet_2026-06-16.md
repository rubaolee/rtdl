# Goal4473 V3.0 M77 Triangle Query Phase Telemetry

Goal4473 answers the open M76 question: when `numba_direct` reduces segment-ray
build but query medians sometimes move against it, is the regression in native
RTDL query packing, RT traversal, or the non-native replay envelope?

Implementation: add backend query-phase telemetry for prepared segmented
Triangle Counting replays. Each measured replay now reports native
`query_pack` and `traversal` phase summaries, then this packet compares
same-commit `cupy_repeat` and `numba_direct` on the three large paper rows.

## Result Table

All rows use `unique_weighted`, `prepared_segment_replay`, warmup=1, repeat=3,
15M ray cap where applicable, and the same RTX 4000 Ada pod. Counts match
between `cupy_repeat` and `numba_direct` for all rows.

| Dataset | Total speedup | Backend speedup | Build-once speedup | Segment-ray build speedup | Query wall median | Native pack median | Native traversal median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 1.09x | 1.03x | 1.10x | 1.18x | 0.928s -> 0.931s | 18.10ms -> 17.41ms | 0.176s -> 0.177s |
| `soc-LiveJournal1` | 1.08x | 1.04x | 1.24x | 1.34x | 1.283s -> 1.340s | 25.71ms -> 26.50ms | 0.259s -> 0.259s |
| `com-orkut` | 1.12x | 1.10x | 1.56x | 1.64x | 8.316s -> 8.560s | 159.79ms -> 160.32ms | 1.694s -> 1.696s |

Triangle counts are 177,820,130; 285,730,264; and 627,584,181.

## Reading

The build-side conclusion survives M77:

- `numba_direct` reduces segment-ray build on all large rows by 1.18x, 1.34x,
  and 1.64x.
- It improves measured backend time by 1.03x, 1.04x, and 1.10x.
- In this same-commit telemetry packet it also improves end-to-end total on all
  three rows by 1.08x-1.12x.

The query-side explanation is now sharper. Native RTDL `query_pack` plus
`traversal` medians are essentially identical between `cupy_repeat` and
`numba_direct`, and traversal is about 1.00x on every large row. Therefore the
small query-wall movement against `numba_direct` on `soc-LiveJournal1` and
`com-orkut` is not evidence that RT traversal became slower; it is envelope
time outside the currently measured native pack/traversal phases.

Current decision: keep `numba_direct` as an explicit, evidence-backed
key-builder option. Do not silently auto-select it yet. The next useful target
is shrinking or modeling the prepared replay envelope, for example a reusable
prepared ray-batch/replay API or same-stream continuation around query dispatch.
More key-fill work is lower priority than reducing the non-native query
envelope.

## Claim Boundary

Allowed:

- Internal current-route wording that `numba_direct` reduces segment-ray build,
  backend time, and this M77 total on all three large paper rows.
- Internal wording that native query pack/traversal is not the observed
  query-wall regression source in M77.
- Explicit user selection of `--segment-unique-key-builder numba_direct`.

Blocked:

- Hidden automatic key-builder selection.
- Public triangle-count RT-core speedup wording.
- RTDL beats cuGraph wording.
- Whole-app acceleration wording.
- Graph-specific native engine callbacks or app-specific native ABI.

## Evidence

- `docs/reports/goal4473_v3_0_m77_triangle_query_phase_packet_2026-06-16.json`
- `docs/reports/goal4473_v3_0_m77_triangle_query_phase_cupy_repeat_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4473_v3_0_m77_triangle_query_phase_numba_direct_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4473_v3_0_m77_triangle_query_phase_cupy_repeat_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4473_v3_0_m77_triangle_query_phase_numba_direct_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4473_v3_0_m77_triangle_query_phase_cupy_repeat_com_orkut_w1r3_2026-06-16.json`
- `docs/reports/goal4473_v3_0_m77_triangle_query_phase_numba_direct_com_orkut_w1r3_2026-06-16.json`
