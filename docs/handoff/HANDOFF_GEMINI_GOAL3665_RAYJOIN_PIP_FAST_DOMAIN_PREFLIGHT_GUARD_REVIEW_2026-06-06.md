# Handoff: Goal3665 RayJoin PIP Fast-Domain Preflight Guard Review

Date: 2026-06-06

Please perform a read-only independent Gemini review of Goal3665 and write the
review to:

`docs/reviews/goal3666_gemini_review_goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`

## Context

Goal3663 confirmed strong RTDL/OptiX batched repeated-request PIP throughput
on two validated public-CDB slices. A larger `count16545` probe hit the known
Goal3320 closed-shape correctness boundary: the selected generic fast route
reported `47264` positives while exact prepared semantics reported `47262`.

Goal3665 does not try to overclaim that domain. Instead it adds an optional
runner guard:

- `preflight_rayjoin_pip_fast_count_domain(...)` now accepts
  `device_predicate_eps`, so preflight matches the measured tuned route.
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py` adds
  `--rtdl-pip-require-validated-fast-domain`.
- With that flag, the runner performs exact-vs-fast PIP preflight before
  RayJoin timing and fails closed if the selected fast route is not exact for
  the input domain.

Files to inspect:

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `tests/goal3321_rayjoin_pip_validated_domain_preflight_test.py`
- `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py`
- `tests/goal3665_rayjoin_pip_fast_domain_preflight_guard_test.py`
- `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md`
- `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_a5000/summary.json`

## Questions

1. Does the change correctly scope `device_predicate_eps` into the preflight
   without leaking the environment after the call?
2. Does the runner guard happen before RayJoin timing and fail closed on the
   invalid full-county domain?
3. Does the report clearly state that the A5000 smoke is functionality evidence,
   not clean-source performance evidence?
4. Does the work preserve the app-agnostic native-engine boundary?
5. Does it avoid release/public speedup/RTDL-beats-RayJoin claims?

## Validation

Codex local focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3665_rayjoin_pip_fast_domain_preflight_guard_test tests.goal3321_rayjoin_pip_validated_domain_preflight_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test tests.goal3663_rayjoin_pip_batch_executor_cross_slice_test tests.goal3602_v2_9_benchmark_status_after_resident_evidence_test
```

Result: 44 tests OK.

Codex pod smoke:

- `br_county_start256_count512.cdb`: preflight exact `1417`, fast `1417`,
  timing proceeded.
- `br_county_start0_count16545.cdb`: preflight exact `47262`, fast `47264`,
  returned code 1, RayJoin timing did not start.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Please explicitly state that this is independent Gemini review,
distinct from Codex, and that it authorizes no public release or public speedup
claims.
