# Call For Review — Goal4898 Planar-Map LSI Prepared-Query Session

Date: 2026-07-03

Please review Goal4898 critically.

## Files To Review

- `history/internal_docs/goal4898_planar_map_lsi_prepared_query_session_report_2026-07-03.md`
- `history/internal_docs/goal4898_prepared_query_probe_2026-07-03.json`
- `history/internal_docs/goal4898_direct_vs_grouped_probe_2026-07-03.json`
- `history/internal_docs/goal4898_prepared_query_overlay_summary_2026-07-03.json`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `tests/goal4851_planar_map_lsi_public_front_door_test.py`
- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`

## Requested Verdict Labels

Choose one:

- `approve_goal4898_bounded_prepared_query_session`
- `approve_with_required_amendments`
- `block_as_not_a_real_generic_runtime_improvement`
- `block_due_to_correctness_or_boundary_regression`

## Questions

1. Is `PreparedOptixPlanarMapLsi2D.prepare_query()` a genuine generic RTDL runtime/API improvement rather than a RayJoin-specific shortcut?
2. Does the report correctly bound the performance claim to repeated/hot query-side reuse, not single-shot overlay speedup?
3. Is it correct not to implement a direct pair-id-row route yet, given the measured direct-vs-grouped tradeoff?
4. Does the harness change preserve the public-primitives route and avoid importing bundled `rtdsl.rayjoin_overlay`?
5. Does the representative overlay evidence preserve byte-for-byte correctness?
6. Are the validation tests sufficient for this API-level change?
7. Does the report honestly redirect the next optimization target away from LSI and toward load/pack plus output writer?
8. Are there any hidden overclaims, V3/V4 leaks, raw callback claims, or broad performance claims?

## Non-Authorization

This review must not authorize:

- broad RayJoin speedup claims;
- full eight-pair Section 5.7 claims;
- V3/V4 release claims;
- raw OptiX callback exposure;
- app-specific hidden RayJoin runtime shortcuts;
- public claims that prepared-query sessions solve single-shot overlay wall time.
