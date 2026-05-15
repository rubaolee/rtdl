# Handoff: Goal2062 Road Hazard Prepared-Only Scaling Review

Please perform a read-only independent review of Goal2062.

Context:

- Goal2060 found that the road-hazard `count=8192` runner wasted pod time in the one-shot baseline.
- Goal2062 adds `--skip-one-shot-baseline` to `scripts/goal1869_road_hazard_v2_partner_perf.py`.
- The skipped baseline is explicitly marked in the JSON artifact; one-shot ratios become null rather than fabricated.
- A NVIDIA L4 pod run at `count=8192`, `iterations=3`, `partners=cupy` passed with strict parity.
- v2 prepared partner road-hazard priority flags are about 8.9x faster than the same-contract v1.8 prepared OptiX row path.

Review these artifacts:

- `scripts/goal1869_road_hazard_v2_partner_perf.py`
- `docs/reports/goal2062_road_hazard_cupy_l4_8192_prepared_only.json`
- `docs/reports/goal2062_road_hazard_prepared_only_scaling_l4_2026-05-15.md`
- `tests/goal2062_road_hazard_prepared_only_scaling_l4_test.py`

Requested checks:

1. Confirm the runner skip mode is honest and does not pretend one-shot timing was measured.
2. Confirm the 8192 L4 artifact supports the prepared same-contract speedup claim.
3. Confirm strict parity, prepared scene reuse, witness output reuse, and whole-app true-zero-copy metadata are present.
4. Confirm the report blocks v2.0 release readiness, broad all-app speedup, broad RT-core speedup, package-install readiness, and skipped one-shot speedup claims.
5. Confirm whether the verdict should be `accept-with-boundary`.

Please write the review to:

- `docs/reviews/goal2063_gemini_review_goal2062_road_hazard_prepared_only_scaling_2026-05-15.md`
