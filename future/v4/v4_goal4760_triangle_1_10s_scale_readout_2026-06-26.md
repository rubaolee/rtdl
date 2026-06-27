# V4 Goal4760 Triangle Counting 1-10s Scale Follow-Up

Status: `triangle_seconds_scale_followup_not_release_matrix_replacement`

This follow-up addresses the objection that the Goal4756 Triangle Counting
headline used millisecond-level single-query hot-path medians. The new run keeps
the same NVIDIA RTX A5000 POD, same input, same V2.14/V3.0.2/V4.0 route
classes, and same correctness contract, but increases the measured query repeat
count to `10000`.

This file does not replace the complete Goal4756 10-app matrix. It is a focused
Triangle Counting seconds-scale explanation.

## Environment

- POD: `root@194.68.245.170 -p 22089`
- GPU: `NVIDIA RTX A5000`
- Driver: `570.195.03`
- Input: `/root/v4_goal4753_final_matrix/k4_32768.edgebin`
- Backend: NVIDIA OptiX / RT-core
- Partner: CuPy
- Warmup: `20`
- Repeat: `10000`

## Scale

| Item | Value |
| --- | ---: |
| Primitive / directed edge count | `196608` |
| Oracle triangle count | `131072` |
| Result count, all versions | `131072` |
| Correctness parity | `true` for V2.14, V3.0.2, V4.0 |

## Results

| Version | Route | Elapsed sec | Hot total sec | Hot median ms | Hot mean ms | Hot max ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| V2.14 | `rt_graph_2a1_generic_rt` | `38.385816` | `33.774959` | `1.261840` | `3.377496` | `134.025197` |
| V3.0.2 | `rt_graph_2a1_segmented_generic_rt` | `8.218793` | `1.822165` | `0.179421` | `0.182216` | `0.454612` |
| V4.0 | `rt_graph_2a1_segmented_generic_rt` | `7.023210` | `1.583440` | `0.155464` | `0.158344` | `0.243478` |

## Ratios

| Ratio | Hot total | Process elapsed | Hot median |
| --- | ---: | ---: | ---: |
| V3.0.2 / V2.14 | `18.536x` | `4.670x` | `7.033x` |
| V4.0 / V2.14 | `21.330x` | `5.466x` | `8.117x` |
| V4.0 / V3.0.2 | `1.151x` | `1.170x` | `1.154x` |

## Interpretation

The earlier Goal4756 table reported V4/V2.14 Triangle Counting as `4.360x`
using a millisecond-level per-query hot median. That number is not the strongest
seconds-scale reading.

At `repeat=10000`, the measured hot-query workload becomes seconds-scale:

- V2.14 hot total: `33.775s`
- V3.0.2 hot total: `1.822s`
- V4.0 hot total: `1.583s`

The fair same-repeat seconds-scale reading is therefore:

```text
V4.0 / V2.14 Triangle Counting hot-total speedup: 21.330x
```

The process-level elapsed-time speedup is lower but still material:

```text
V4.0 / V2.14 Triangle Counting elapsed speedup: 5.466x
```

This confirms that the modern V3/V4 segmented prepared route is not merely a
millisecond artifact. It survives a seconds-scale same-workload run.

## Boundary

This is a focused Triangle Counting follow-up. It does not authorize:

- broad all-app speedup wording;
- replacing the Goal4756 complete 10-app matrix;
- claiming every V4 app has seconds-scale speedup;
- claiming the gain is purely V4-over-V3.

The correct high-level reading remains:

```text
Triangle Counting has a real seconds-scale V3/V4-over-V2.14 improvement. Most
of the architectural change comes from the modern segmented prepared route; V4
preserves and modestly improves it over V3.0.2.
```

## Evidence

- `future/v4/evidence/v4_goal4760_triangle_1_10s_scale_2026-06-26/summary.json`
- `future/v4/evidence/v4_goal4760_triangle_1_10s_scale_2026-06-26/raw/v2_14_triangle_counting.json`
- `future/v4/evidence/v4_goal4760_triangle_1_10s_scale_2026-06-26/raw/v3_0_2_triangle_counting.json`
- `future/v4/evidence/v4_goal4760_triangle_1_10s_scale_2026-06-26/raw/v4_0_triangle_counting.json`
