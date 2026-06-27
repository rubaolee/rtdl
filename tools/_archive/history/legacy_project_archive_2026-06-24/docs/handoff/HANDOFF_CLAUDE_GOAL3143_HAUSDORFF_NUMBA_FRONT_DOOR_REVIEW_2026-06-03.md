# Handoff: Goal3143 Hausdorff Numba Front-Door Review

Please perform an independent Claude review of Goal3143 and write the review to:

`docs/reviews/goal3144_claude_review_goal3143_hausdorff_partner_exact_numba_front_door_2026-06-03.md`

## Files To Inspect

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `scripts/goal3143_hausdorff_partner_exact_numba_pod_probe.py`
- `tests/goal3143_hausdorff_partner_exact_numba_front_door_test.py`
- `docs/reports/goal3143_hausdorff_partner_exact_numba_front_door_2026-06-03.md`
- `docs/reports/goal3143_pod_artifacts/hausdorff_partner_exact_numba_pod_probe_2026-06-03.json`

## Review Questions

1. Does `partner_exact + partner="numba"` now use a shared generic front door rather than the older app-specific backend name?
2. Is the implementation app-agnostic at the engine/runtime layer, using generic typed-column operations only?
3. Is the optional `materialize_nearest_distances` distinction correct: default rich adapter behavior preserves nearest-distance columns, while the scalar benchmark app can skip them?
4. Do the tests and RTX 4000 Ada artifact support the claimed correctness and warmed timing observations?
5. Are all public/release/speedup/RT-core/zero-copy claim boundaries still blocked?

## Required Output

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please lead with findings by severity, then give a short verdict and any required before-next-step fixes. This is not a release review and should not authorize v2.8 release, public speedup, true-zero-copy, or RT-core claims.
