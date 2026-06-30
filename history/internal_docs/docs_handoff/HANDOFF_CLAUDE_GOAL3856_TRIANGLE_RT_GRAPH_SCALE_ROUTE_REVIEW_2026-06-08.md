# Handoff: Claude Review for Goal3856 Triangle-Counting RT-Graph Scale Route

Please perform an independent read-only review of Goal3856 on current `main`.

## Scope

Review commit `1d38d156` and these files:

- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `docs/reports/goal3828_current_benchmark_scale_profile_registry_2026-06-07.md`
- `docs/reports/goal3856_triangle_counting_rt_graph_scale_route_2026-06-08.md`
- `docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/`
- `tests/goal3856_triangle_counting_rt_graph_scale_route_test.py`

## Questions

1. Does `--rt-graph-copies` preserve the existing edge-file behavior while allowing repeated fixture inputs for RT-Graph generic modes?
2. Does the current scale-profile row now use the intended `rt_graph_2a1_generic_rt` prepared generic ray/triangle summary route instead of the old `mode=run` host-indexed fallback?
3. Is the A5000 artifact internally consistent: oracle count `4096`, RTDL weighted count `4096`, primitive/ray counts `10240/4096`, hot query median about `0.214 ms`, no row materialization, and zero claim-flag violations?
4. Does the report avoid overclaiming, especially by treating Goal3856 as a route correction rather than a public same-contract speedup claim?
5. Are there any required-before-next-step fixes for the registry, report wording, or tests?

## Requested Output

Write the review to:

`docs/reviews/goal3857_claude_review_goal3856_triangle_counting_rt_graph_scale_route_2026-06-08.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

If your environment allows tests, run:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal3856_triangle_counting_rt_graph_scale_route_test tests.goal3828_current_benchmark_scale_profile_registry_test
```

If the harness blocks test execution, say so and ground the review in static/source/artifact checks.
