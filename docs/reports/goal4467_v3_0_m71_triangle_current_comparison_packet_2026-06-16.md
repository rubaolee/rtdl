# Goal4467 V3.0 M71 Triangle Current Comparison Packet

Goal4467 refreshes the Triangle Counting large-row comparison after M69/M70
optimization. It uses current RTDL rows, not stale Goal4462/4463/4464 timings,
for the three large paper datasets that previously exposed RTDL OOM or scene
scale limits.

This is an honest comparison packet, not public speedup wording.

## Current RTDL Rows

All current RTDL rows use generic RTDL ray/triangle primitives with a CuPy app
partner. No graph-specific native engine logic is added.

| Dataset | Current RTDL route | Caps | Count | Total | Query median | Ray build median |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `com-lj` | segmented rays, one global scene | 15M ray cap | 177,820,130 | 14.153s | 2.019s | 0.629s |
| `soc-LiveJournal1` | segmented source scenes | 8M scene / 15M ray | 285,730,264 | 25.747s | 3.048s | 0.936s |
| `com-orkut` | segmented source scenes | 2M scene / 15M ray | 627,584,181 | 115.032s | 19.136s | 5.610s |

All three rows match the expected paper triangle counts.

## Against cuGraph

cuGraph remains much faster end to end on the same large rows in the Goal2593
evidence family.

| Dataset | Current RTDL total | Goal2593 cuGraph total | cuGraph vs RTDL |
| --- | ---: | ---: | ---: |
| `com-lj` | 14.153s | 1.713s | 8.26x faster |
| `soc-LiveJournal1` | 25.747s | 2.378s | 10.83x faster |
| `com-orkut` | 115.032s | 7.229s | 15.91x faster |

Conclusion: current RTDL is now scalable and exact on these large rows, but it
does not beat cuGraph. Any wording that says otherwise is wrong.
In summary, cuGraph remains 8.26x-15.91x faster than current RTDL total time.

## Against Authors Code

The authors code has two very different readings:

- Full pipeline reading: includes preprocessing, graph-to-RT/GPU construction,
  ray generation, and subprocess/file overhead.
- Pure count-kernel reading: the authors specialized kernels are extremely
  fast once their prepared representation exists.

| Dataset | Current RTDL total | Authors `rt_tc` full pipeline | Authors `rt_tc` count | Authors `bs_tc` full pipeline | Authors `bs_tc` count |
| --- | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 14.153s | 43.177s | 0.073s | 42.671s | 0.011s |
| `soc-LiveJournal1` | 25.747s | 69.118s | 0.103s | 65.919s | 0.014s |
| `com-orkut` | 115.032s | failed after 149.152s | n/a | failed after 147.387s | n/a |

For `com-lj` and `soc-LiveJournal1`, current RTDL is faster than the authors
full pipeline on this pod because the authors pipeline is dominated by
preprocessing and ray/GPU construction. That is a full-pipeline observation, not
a claim that RTDL's traversal/count kernel is faster. The authors pure count
kernels are tens to hundreds of times faster than the current RTDL query phase.
In short, authors pure count kernels are much faster than current RTDL query.

For `com-orkut`, current RTDL completes exactly where both authors full
pipelines were killed on this pod, but cuGraph remains about 15.91x faster than
current RTDL total time.

## What This Means

RTDL's current value for Triangle Counting is now clear:

- It can express the RT-Graph RT-2A1 shape through generic RTDL primitives and
  Python/CuPy partner logic.
- It can run the large former-OOM rows exactly without global two-hop
  materialization, and for `soc`/`orkut` without a global triangle scene.
- It is more programmable and less specialized than authors C++/CUDA/OptiX
  kernels, but it does not match their pure count-kernel efficiency.
- It remains slower than cuGraph end to end on these graph-triangle rows.

The next serious optimization target is not cap tuning. It is a different
duplicate-ray representation or traversal contract that reduces the 8.58B
logical-ray burden without adding graph-specific native engine logic.

## Claim Boundary

Allowed:

- Internal current-route comparison wording.
- RTDL completes `com-lj`, `soc-LiveJournal1`, and `com-orkut` exactly with the
  documented current configurations.
- cuGraph is still the strongest end-to-end baseline in this packet.
- Authors pure kernels remain much faster than current RTDL query traversal.

Blocked:

- Public RT-core triangle-count speedup wording.
- RTDL beats cuGraph wording.
- RTDL traversal beats authors pure kernels wording.
- Paper-system reproduction wording.
- Hidden automatic partner/cap selection.

## Evidence

- `docs/reports/goal4467_v3_0_m71_triangle_current_comparison_packet_2026-06-16.json`
- `docs/reports/goal4467_v3_0_m71_triangle_current_com_lj_15m_2026-06-16.json`
- `docs/reports/goal4467_v3_0_m71_triangle_current_soc_livejournal1_8m_scene_15m_ray_2026-06-16.json`
- `docs/reports/goal4467_v3_0_m71_triangle_current_com_orkut_2m_scene_15m_ray_2026-06-16.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_com_lj_author_cugraph.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_soc_lj_author_cugraph.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_com_orkut_cugraph.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_com_orkut_author_rt.json`
- `docs/reports/goal2593_paper_dataset_raw/goal2593_eval_com_orkut_author_bs.json`
