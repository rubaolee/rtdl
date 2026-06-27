# Handoff: Gemini Review for Goal2997 Numba Compact Mask

Please perform an independent read-only review of Goal2997 and write the review
to:

`docs/reviews/goal2998_gemini_review_goal2997_numba_compact_mask_l4_2026-06-01.md`

## Scope

Review current `main` after commit `76b80e8b`.

Primary artifacts:

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `scripts/goal2997_numba_compact_mask_pod_runner.py`
- `docs/reports/goal2997_numba_compact_mask_prepared_2026-06-01.md`
- `docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.md`
- `docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.json`
- `tests/goal2997_numba_compact_mask_prepared_test.py`
- `tests/goal2997_numba_compact_mask_l4_pod_test.py`
- `src/rtdsl/v2_6_roadmap.py`
- `src/rtdsl/v2_5_internal_readiness.py`

## Questions To Answer

1. Is `compact_mask_i64` implemented as a generic Numba continuation primitive,
   without RayJoin/triangle-counting/app-specific engine logic?
2. Does `partner_mask_indices(mask, partner="numba")` require the v2.6 neutral
   partner handoff and avoid torch carrier/conversion?
3. Does the implementation preserve stable input order, and is the
   host-prefix-sum boundary honestly documented?
4. Is the L4 pod evidence valid runtime conformance evidence? Check rows,
   selected count, source commit, toolchain metadata, CPU parity flags, and
   claim-boundary fields.
5. Are the roadmap/readiness updates honest, especially that Goal2997 is not
   release evidence or speedup evidence?

## Expected Review Format

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

Lead with findings if any. If accepted, list residual boundaries. Do not
authorize v2.6 release, public speedup claims, whole-app speedup claims, broad
RT-core claims, true-zero-copy claims, automatic partner selection claims, or
Numba speedup claims.

If shell execution is available, run:

`PYTHONPATH=src:. python -m unittest tests.goal2997_numba_compact_mask_l4_pod_test tests.goal2997_numba_compact_mask_prepared_test`

If shell execution is unavailable, disclose that and perform static/artifact
review only.
