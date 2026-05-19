# Gemini Handoff: Goal2392 RT-DBSCAN Benchmark Campaign Review

Please review the Goal2392 RT-DBSCAN benchmark campaign as an independent
Gemini review distinct from Codex.

## Files To Inspect

- `docs/reports/goal2392_rt_dbscan_benchmark_campaign_2026-05-19.md`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/README.md`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `tests/goal2392_rt_dbscan_benchmark_campaign_test.py`
- `tests/goal1981_exact_radius_graph_components_dbscan_partner_reference_test.py`
- `tests/goal1985_spatial_bucket_dbscan_partner_reference_test.py`

## Context

The target paper is:

- Vani Nagarajan and Milind Kulkarni, "RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware," IPDPS 2023.
- DOI: `10.1109/IPDPS54959.2023.00100`

Codex added the first RT-DBSCAN research-benchmark slice:

- a `rt_dbscan/` benchmark directory;
- a 3-D synthetic benchmark app with `cpu_reference`, `rtdl_cpu_rows`,
  `partner_spatial_bucket_3d`, `partner_core_flags_3d`, and
  `optix_prepared_rows` modes;
- generic 3-D partner count/threshold and spatial-bucket component helpers;
- no DBSCAN-specific native ABI.

## Review Questions

1. Does Goal2392 correctly interpret RT-DBSCAN as generic fixed-radius neighbor
   search plus core-point threshold plus radius-graph/component continuation?
2. Did the implementation avoid app-specific DBSCAN native engine API or native
   app-domain leakage?
3. Are the public claim boundaries correct, especially that this is not a paper
   reproduction, not a paper-speedup claim, and not yet a device-resident
   continuation?
4. Are the current gaps named correctly: 3-D OptiX device-column threshold
   output, device-resident radius-graph components/union-find, representative
   datasets, and strong CUDA/grid baseline?
5. Are the tests sufficient for this initial slice, and what should be added
   before pod performance work?

## Required Output

Write your review to:

`docs/reviews/goal2393_gemini_review_goal2392_rt_dbscan_campaign_2026-05-19.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Keep release/performance claims conservative.
