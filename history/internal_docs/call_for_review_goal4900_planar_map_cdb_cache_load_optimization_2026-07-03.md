# Call For Review — Goal4900 Generic Planar-Map CDB Packed Cache Load Optimization

Date: 2026-07-03

Please critically review Goal4900.

## Primary Report

- `history/internal_docs/goal4900_planar_map_cdb_cache_load_optimization_report_2026-07-03.md`

## Evidence Files

- `history/internal_docs/goal4900_load_cache_bounds_probe_2026-07-03.json`
- `history/internal_docs/goal4900_load_cache_bounds_probe_with_env_2026-07-03.json`
- `history/internal_docs/goal4900_numba_cache_overlay_summary_2026-07-03.json`
- `history/internal_docs/goal4899_author_python_rtdl_numba_rtdl_comparison_2026-07-03.json`

## Code Surfaces To Inspect

- `src/rtdsl/datasets.py`
- `tests/goal4895_planar_map_cdb_packed_loader_test.py`
- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`

## Requested Verdict Labels

- `approve_goal4900_generic_cache_load_optimization`
- `approve_with_required_amendments`
- `block_due_to_overclaim`
- `block_due_to_correctness_or_semantics_regression`

## Questions

1. Is the implemented change genuinely a generic planar-map CDB packed-loader/cache improvement rather than a RayJoin-specific shortcut?
2. Does the report correctly preserve the boundary that this is a load/cache win, not an LSI/PIP traversal or Numba primitive-traversal win?
3. Does the byte-equality artifact support saying correctness was preserved on the Australia representative overlay?
4. Are the reported speedups bounded correctly: total route about `2.16x`, load about `132.7x`, no broad RayJoin or full Section 5.7 claim?
5. Are bounds persistence and lazy backfill safe and properly tested for old cache entries?
6. Is the `--cache-dir` harness change acceptable as an explicit user/app knob without leaking ambient environment state after load?
7. Is the next-gap conclusion correct: after Goal4900, the highest-priority target is the `~9.8s` unattributed wrapper/startup/JIT/accounting overhead, not more blind CDB-cache tuning?
8. Should Goal4900 close and authorize a next measurement goal to split startup/JIT/app-glue overhead from recorded phases?

## Non-Authorization Boundary

This review must not authorize:

- broad RTDL/RayJoin speedup claims;
- full eight-pair Section 5.7 claims;
- claims that Numba accelerates RTDL primitive traversal;
- claims that RTDL LSI/PIP kernel speed improved because of Goal4900;
- V3/V4 release resurrection;
- public release/tag decisions.
