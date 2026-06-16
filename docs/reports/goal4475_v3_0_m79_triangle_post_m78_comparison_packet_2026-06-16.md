# Goal4475 V3.0 M79 Triangle Post-M78 Comparison Packet

Goal4475 refreshes the Triangle Counting comparison after Goal4474 prepared
ray batches. The current best internal RTDL route is explicit segmented RT-2A1
with `numba_direct` unique-key fill plus the generic prepared ray-batch weighted
any-hit primitive.

This is current internal route evidence, not public speedup wording.

## Current Table

| Dataset | Count | RTDL M73 total | RTDL M78 total | M78 vs M73 | cuGraph total | cuGraph vs M78 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 177,820,130 | 9.552s | 5.404s | 1.77x faster | 1.713s | 3.15x faster |
| `soc-LiveJournal1` | 285,730,264 | 17.986s | 11.669s | 1.54x faster | 2.378s | 4.91x faster |
| `com-orkut` | 627,584,181 | 62.428s | 35.379s | 1.76x faster | 7.229s | 4.89x faster |

M78 narrows the cuGraph end-to-end gap from Goal4470/M73's 5.58x-8.64x
to 3.15x-4.89x. That is a large improvement, not a win over cuGraph.

## Authors Code Reading

| Dataset | RTDL M78 total | RTDL M78 query median | Authors `rt_tc` full pipeline | Authors `rt_tc` count | Authors `bs_tc` full pipeline | Authors `bs_tc` count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 5.404s | 0.180s | 43.177s | 0.073s | 42.671s | 0.011s |
| `soc-LiveJournal1` | 11.669s | 0.264s | 69.118s | 0.103s | 65.919s | 0.014s |
| `com-orkut` | 35.379s | 1.732s | failed after 149.152s | n/a | failed after 147.387s | n/a |

For `com-lj` and `soc-LiveJournal1`, RTDL M78 is 7.99x and 5.92x faster
than the authors `rt_tc` full pipeline on this pod. That reading is valid only
as a full-pipeline wall-time comparison: the authors full pipeline is dominated
by preprocessing and ray/GPU construction.

It must not be worded as a faster counting kernel. The authors pure `rt_tc`
count kernels are still 2.46x and 2.56x faster than RTDL M78 query median, and
their `bs_tc` count kernels are still 16.94x and 19.31x faster than RTDL M78
query median on the two rows where the authors pure timings completed.

For `com-orkut`, RTDL completes exactly where the authors full-pipeline runs
were SIGKILLed on this pod, but cuGraph remains 4.89x faster end to end.

## RT-Core Reading

Goal4474 prepared ray batches moved repeated ray-column packing out of the
measured query path. The current M78 query medians are 0.180s, 0.264s, and
1.732s, with native traversal medians of 0.175s, 0.257s, and 1.687s on the
three rows. This is a real RTDL route improvement.

It still does not prove public RT-core triangle-count acceleration. The
remaining end-to-end cost is dominated by graph workload transformation,
partner materialization, segment/ray construction, and scalar summary handling,
not by raw RT traversal alone.

## Boundary

Allowed:

- Current internal statement: M78 improves RTDL large-row totals by 1.54x-1.77x
  versus M73.
- Current internal statement: the cuGraph gap narrowed to 3.15x-4.89x but
  cuGraph remains faster end to end.
- Current internal statement: RTDL M78 beats the authors full pipeline on
  `com-lj` and `soc-LiveJournal1`, and completes `com-orkut` where the authors
  full pipeline failed on this pod.

Blocked:

- Public RT-core triangle-count speedup wording.
- RTDL beats cuGraph wording.
- RTDL traversal beats authors pure kernels wording.
- Paper-system reproduction wording.
- Hidden automatic partner or schedule selection.

## Evidence

- `docs/reports/goal4475_v3_0_m79_triangle_post_m78_comparison_packet_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_packet_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_numba_direct_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_numba_direct_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4474_v3_0_m78_triangle_prepared_ray_batch_numba_direct_com_orkut_w1r3_2026-06-16.json`
- `docs/reports/goal4470_v3_0_m74_triangle_post_m73_comparison_packet_2026-06-16.json`
