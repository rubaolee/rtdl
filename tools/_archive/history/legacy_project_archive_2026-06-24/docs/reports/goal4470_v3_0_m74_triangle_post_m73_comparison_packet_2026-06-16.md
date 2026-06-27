# Goal4470 V3.0 M74 Triangle Post-M73 Comparison Packet

Goal4470 refreshes the Triangle Counting comparison after Goal4469 prepared
segment replay. The previous current comparison packet was Goal4467, before
unique-weighted rays and prepared segment replay.

This is current internal route evidence, not public speedup wording.

## Current Table

| Dataset | Count | RTDL M71 total | RTDL M73 total | M73 vs M71 | cuGraph total | cuGraph vs M73 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 177,820,130 | 14.153s | 9.552s | 1.48x faster | 1.713s | 5.58x faster |
| `soc-LiveJournal1` | 285,730,264 | 25.747s | 17.986s | 1.43x faster | 2.378s | 7.56x faster |
| `com-orkut` | 627,584,181 | 115.032s | 62.428s | 1.84x faster | 7.229s | 8.64x faster |

M73 narrows the cuGraph end-to-end gap from the Goal4467 range
8.26x-15.91x to 5.58x-8.64x. That is progress, not victory.

## Authors Code Reading

| Dataset | RTDL M73 total | Authors `rt_tc` full pipeline | Authors `rt_tc` count | Authors `bs_tc` full pipeline | Authors `bs_tc` count |
| --- | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 9.552s | 43.177s | 0.073s | 42.671s | 0.011s |
| `soc-LiveJournal1` | 17.986s | 69.118s | 0.103s | 65.919s | 0.014s |
| `com-orkut` | 62.428s | failed after 149.152s | n/a | failed after 147.387s | n/a |

For `com-lj` and `soc-LiveJournal1`, RTDL M73 is faster than the authors full
pipeline on this pod because the authors full pipeline is dominated by
preprocessing and graph-to-ray/GPU construction. That must not be read as RTDL
having a faster counting kernel. The authors pure count kernels remain
12.97x-98.00x faster than RTDL M73 query.

For `com-orkut`, RTDL completes exactly where the authors full-pipeline runs
were SIGKILLed on this pod, but cuGraph remains 8.64x faster end to end.

## Boundary

Allowed:

- Current internal statement: RTDL now completes all three large rows exactly
  with M73 prepared segment replay.
- Current internal statement: M73 improves RTDL totals by 1.43x-1.84x versus
  the M71 duplicate-ray totals.
- Current internal statement: the cuGraph gap narrowed but remains large.

Blocked:

- Public RT-core triangle-count speedup wording.
- RTDL beats cuGraph wording.
- RTDL traversal beats authors pure kernels wording.
- Paper-system reproduction wording.
- Hidden automatic partner or schedule selection.

## Evidence

- `docs/reports/goal4470_v3_0_m74_triangle_post_m73_comparison_packet_2026-06-16.json`
- `docs/reports/goal4469_v3_0_m73_triangle_prepared_segment_replay_packet_2026-06-16.json`
- `docs/reports/goal4469_v3_0_m73_triangle_prepared_unique_weighted_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4469_v3_0_m73_triangle_prepared_unique_weighted_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4469_v3_0_m73_triangle_prepared_unique_weighted_com_orkut_w1r3_2026-06-16.json`
- `docs/reports/goal4467_v3_0_m71_triangle_current_comparison_packet_2026-06-16.json`
