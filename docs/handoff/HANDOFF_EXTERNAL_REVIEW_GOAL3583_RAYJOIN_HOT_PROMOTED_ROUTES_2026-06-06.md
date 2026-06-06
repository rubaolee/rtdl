# External Review Handoff: Goal3583 RayJoin Hot Promoted Routes

Date: 2026-06-06

Please perform an independent review of Goal3583.

## Scope

Goal3583 fixes and measures the RayJoin strengthened-runner promoted routes:

- source commit: `3b845c1085add4ae304123fcd78985359c61acf0`
- evidence commit: `16ff307d`
- report: `docs/reports/goal3583_rayjoin_hot_promoted_routes_2026-06-06.md`
- standard artifact: `docs/reports/goal3583_rayjoin_hot_promoted_routes_a5000/summary.json`
- stress artifact: `docs/reports/goal3583_rayjoin_hot_promoted_routes_stress_a5000/summary.json`
- validation test: `tests/goal3583_rayjoin_hot_promoted_routes_a5000_test.py`

Goal3583 changes the RayJoin promoted OptiX routes so they measure hot
prepared-query medians:

- app route changes:
  `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- runner changes:
  `scripts/goal2636_strengthen_benchmark_rows.py`
- runner contract test:
  `tests/goal3582_rayjoin_promoted_strengthened_runner_test.py`

## Reviewer Questions

1. Does Goal3583 correctly diagnose the prior bad-looking Goal3582 packet as a
   cold-process measurement-contract issue rather than a native RT traversal
   performance failure?
2. Do the app and runner changes correctly measure the promoted RayJoin routes
   as hot prepared-query medians (`--repeat 5 --warmup 1`,
   `phases_sec.prepared_query_sec`)?
3. Does the implementation remain app-agnostic in the native engine, with
   RayJoin interpretation and CuPy PIP refinement kept in the Python/app layer?
4. Are the standard and stress A5000 results accurately reported?
   - standard: PIP 5.119x, LSI 126.744x, overlay active count 978.838x
   - stress: PIP 5.929x, LSI 148.911x, overlay active count 4624.372x
5. Are the claim boundaries strong enough? The report must not authorize full
   RayJoin paper reproduction, paper-scale claims, broad RT-core speedup claims,
   RTDL-beats-RayJoin claims, full-overlay materialization claims, true zero-copy
   claims, or release claims.
6. What should the next RayJoin performance target be: composite app scoring,
   full-overlay continuation, external same-contract CUDA/OptiX baseline, or
   something else?

## Required Review Output

Please write one review file:

- Claude: `docs/reviews/goal3584_claude_review_goal3583_rayjoin_hot_promoted_routes_2026-06-06.md`
- Gemini: `docs/reviews/goal3585_gemini_review_goal3583_rayjoin_hot_promoted_routes_2026-06-06.md`

Use one of the standard verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

If the verdict is not `accept`, list the exact required follow-up work.
