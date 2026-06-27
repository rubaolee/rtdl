# V4 Goal4750 Review Debt: Unified RT-Core Runner

Status: `open_external_review_debt__engineering_continues`

Goal4750 changed the final V4.0 benchmark machinery from a 27/30 dry-run with
three V4 repair rows into a 30/30 command-bound NVIDIA RT-core matrix plan.

## What Changed

- All 10 promoted benchmark apps now emit V2.14, V3.0.2, and V4.0 command rows.
- `robot_collision`, `contact_manifold`, and `spatial_rayjoin` are treated as
  inherited V4.0 superset compatibility rows, not missing V4 routes.
- The inherited rows remain ineligible for V4-new speed credit unless later
  evidence proves a new V4 optimization.
- The runner records the current POD key, old-tag v4compat library contract,
  command, stdout/stderr paths, fixture requirements, and correctness-before-speed
  rule for every row.

## Local Gate

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v4_goal4749_final_rt_core_protocol_test tests.v4_goal4750_unified_rt_core_runner_test tests.v4_goal4751_app_compatibility_catalog_test tests.v4_frontdoor_test
```

Result: `25 tests OK`.

## Required External Review Questions

1. Does Goal4750 correctly implement the user's V4.0 superset rule?
2. Are the 30 command templates appropriate as the Goal4753 POD runner input?
3. Are Robot/Contact/Spatial correctly classified as runnable inherited compatibility
   rows while still blocking V4-new speed credit?
4. Does the runner avoid `n/a`, Embree primary denominators, and hidden missing rows?
5. Is it acceptable to proceed to POD execution before this debt is backfilled?

## Non-Authorization

This debt file does not authorize release, public V4-over-V2.14 speedup claims,
whole-app high-performance wording, true-zero-copy wording, or final tag.
