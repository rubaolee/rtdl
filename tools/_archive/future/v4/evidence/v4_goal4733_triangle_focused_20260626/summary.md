# V4 Goal4733 Triangle Focused POD Rerun

Status: `triangle_focused_pod_rerun_complete_not_release`
Repeat/warmup: `201/20`

| version | mode | hot sec | query median ms | parity | prepared reused |
|---|---|---:|---:|---|---|
| `v2_14` | `rt_graph_2a1_generic_rt` | 0.0010402016341686249 | 1.0402016341686249 | True | None |
| `v3_0_2` | `rt_graph_2a1_segmented_generic_rt` | 0.000170096755027771 | 0.170096755027771 | True | True |
| `v4_current` | `rt_graph_2a1_segmented_generic_rt` | 0.00016302242875099182 | 0.16302242875099182 | True | True |

## Ratios

- V4/V2.14 hot: `6.380727131464089`
- V4/V3.0.2 hot: `1.0433948035922396`
- V4-V3 query median delta ms: `-0.007074326276779175`
- All rows parity: `True`
- V4 residency metadata pass: `True`
- Classification hint: `v3_regression_cleared_by_high_repeat_focused_rerun`

## Non-Authorization

This focused rerun does not authorize final V4 tag, public speedup wording, whole-app high-performance wording, or all-benchmark speedup claims.
