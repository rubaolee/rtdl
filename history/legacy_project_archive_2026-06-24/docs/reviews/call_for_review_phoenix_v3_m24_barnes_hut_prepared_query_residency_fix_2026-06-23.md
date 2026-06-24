# Call For Review: Phoenix V3 M24 Barnes-Hut Prepared Query Residency Fix

Please perform a critical external review of:

- `docs/reports/phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_2026-06-23.md`
- code changes:
  - `src/rtdsl/generic_primitives.py`
  - `src/rtdsl/embree_runtime.py`
  - `examples/current/apps/simulation/rtdl_barnes_hut_force_app.py`
  - `tests/goal1298_v1_5_generic_fixed_radius_threshold_count_test.py`
  - `tests/v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test.py`

Required verdict labels:

- `accept_blocker_closed`
- `accept_with_boundary`
- `approve_blocked_not_release`
- `reject_not_closed`

Facts to review:

- M22 Barnes-Hut app geomean was `0.831x`, below the M21 severe-regression
  floor.
- Focused repro before this fix:
  - current 32768 OptiX query: `0.071077s`
  - V2.14 32768 OptiX query: `0.041552s`
  - current 131072 OptiX query: `0.295900s`
  - V2.14 131072 OptiX query: `0.296358s`
- Micro-probe showed native traversal was already fast when query points were
  prepacked:
  - non-prepacked OptiX scalar query median around `0.033s`
  - prepacked OptiX scalar query median around `0.00017s`
- Implemented generic `GenericPreparedFixedRadiusCountThreshold2D.prepare_query_points(...)`.
- Implemented `PackedPoints` support in Embree prepared fixed-radius count-threshold.
- Barnes-Hut node coverage now prepares query points once and records
  `query_points_prepare_sec` separately.
- Focused fixed current rerun:
  - Embree 32768: `0.084814s`
  - OptiX 32768: `0.000447s`
  - Embree 131072: `0.254535s`
  - OptiX 131072: `0.001498s`
  - fixed current vs V2.14 focused four-row geomean: `15.811x`
- Repeat-50 evidence:
  - 32768 query total: V2.14 `2.161036s`, fixed current `0.008010s`
  - 32768 speedup including one current query prepare: `17.818x`
  - 131072 query total: V2.14 `12.044135s`, fixed current `0.038259s`
  - 131072 speedup including one current query prepare: `22.812x`
- Boundary: these are prepared hot-query/repeated-query results, not whole
  Barnes-Hut force-solver or single-run whole-app wall speedup claims.

Questions:

1. Is the blocker closed for Barnes-Hut primary-metric severe regression, or
   does the metric split require more evidence before closure?
2. Is the implementation generic enough for V3 runtime work, or is it
   app-specific benchmark tuning?
3. Is the repeat-50 evidence sufficient to show real user value rather than
   only moving packing out of the measured field?
4. Are the report boundaries strict enough to prevent public overclaiming?
5. What, if anything, must be fixed before M24 can close with 2-AI consensus?

Non-authorization:

This review must not authorize V3 release, broad V3-over-V2 speedup wording,
whole-app Barnes-Hut claims, external zero-copy/embedding claims, or all-app
rerun. It only reviews whether M24 can close as a focused Barnes-Hut blocker
fix candidate.
