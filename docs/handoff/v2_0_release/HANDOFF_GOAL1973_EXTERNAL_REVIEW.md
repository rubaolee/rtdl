# Goal1973 External Review Task: Goal1972 Graph Metric-Table Partner Reduction

Please perform a read-only independent review of Goal1972.

## Context

Goal1972 follows the Goal1969 polygon candidate fix. It addresses the previous
`graph_analytics` concern: the v2 control path was fast because it used a
closed-form RawKernel writing formula outputs from `copies`, which made the
timing suspicious as reusable v2 evidence.

Goal1972 replaces that graph closed-form kernel with a generic partner metric
table reduction helper:

- `src/rtdsl/partner_adapters.py`
  - new `partner_metric_table_reduce_by_key(...)`
  - supports `reduce="sum"|"max"|"min"`
  - uses sort/searchsorted to map opaque metric keys to requested output keys
- `src/rtdsl/__init__.py`
  - exports the helper
- `examples/rtdl_control_apps_cupy_rawkernel.py`
  - graph control row now builds generic metric/value rows and reduces them
    with the helper
  - no `GRAPH_RAWKERNEL_SOURCE`
- `tests/goal1972_graph_metric_table_partner_reduction_test.py`
- `docs/reports/goal1972_graph_metric_table_partner_reduction_2026-05-14.md`
- `docs/reports/goal1972_pod_graph_metric_table_control_perf.json`

Implementation commit: `8e316bf2`

Pod evidence commit: `e769ae5b`

## Evidence To Check

Pod artifact:

- GPU: NVIDIA RTX 2000 Ada Generation
- `graph_analytics`, `copies=1000`
- v1.8 median: `18.060916s`
- v2 metric-table median: `0.000054s`
- ratio: `0.000003x`
- correctness matched v1.8 oracle

Important boundary: this does **not** prove arbitrary graph traversal
acceleration. The authored input rows are small, but the prior closed-form
shortcut is gone.

## Review Questions

1. Does Goal1972 genuinely remove the graph closed-form shortcut?
2. Is `partner_metric_table_reduce_by_key` generic partner algebra rather than
   app-specific engine logic?
3. Are the performance claims bounded correctly?
4. Are the tests/report sufficient for this narrow slice?

## Required Output

Write one review file using your AI-family name in the filename:

- Claude: `docs/reviews/goal1973_claude_review_goal1972_graph_metric_table_partner_reduction_2026-05-14.md`
- Gemini: `docs/reviews/goal1974_gemini_review_goal1972_graph_metric_table_partner_reduction_2026-05-14.md`

Use one of the allowed verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not mutate source code. If you find issues, write them in the review.
