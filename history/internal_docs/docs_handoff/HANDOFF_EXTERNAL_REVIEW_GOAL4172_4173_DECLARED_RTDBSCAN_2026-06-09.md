# Handoff: Review Goal4172-4173 Declared All-Predicate RT-DBSCAN Route

Please perform an independent read-only review of the Goal4172 and Goal4173
chain.

## Files To Read

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `docs/reports/goal4172_declared_all_predicate_rtdbscan_route_2026-06-09.md`
- `docs/reports/goal4173_declared_all_predicate_rtdbscan_2m_probe_2026-06-09.md`
- `docs/reports/goal4173_declared_all_predicate_rtdbscan_2m_probe_pod.json`
- `tests/goal4172_declared_all_predicate_rtdbscan_route_test.py`
- `tests/goal4173_declared_all_predicate_rtdbscan_2m_probe_test.py`
- Existing context artifacts:
  - `docs/reports/goal4169_rtdbscan_road3d_2m_scale_probe_2026-06-09.md`
  - `docs/reports/goal4171_rtdbscan_road3d_2m_oneshot_probe_2026-06-09.md`

## Questions

1. Does Goal4172 correctly add an explicit caller-declared all-predicate route
   without adding native app-specific engine logic?
2. Does the route honestly require external proof and avoid hidden/automatic
   dispatch?
3. Does Goal4173 support the bounded claim that the declared route removes
   predicate-measurement overhead on the 2M road3d all-predicate row?
4. Are the timing numbers and signatures in the pod artifact interpreted
   correctly?
5. Is the claim boundary correct, especially that the declared subpath has no
   RT count-threshold execution and no RT-core acceleration claim?
6. What, if anything, must be fixed before this can remain in the v2.x
   performance evidence chain?

## Required Output

Write one review file with verdict `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Preferred output paths:

- Claude:
  `docs/reviews/goal4174_claude_review_goal4172_4173_declared_rtdbscan_2026-06-09.md`
- Gemini:
  `docs/reviews/goal4174_gemini_review_goal4172_4173_declared_rtdbscan_2026-06-09.md`

Do not edit source code. Do not authorize release, route promotion, public
speedup wording, broad RT-core wording, whole-app benchmark claims,
paper-reproduction claims, native ABI additions, or true-zero-copy claims.
