# V4 Goal4751 Review Debt: Superset App Compatibility Catalog

Status: `open_external_review_debt__engineering_continues`

Goal4751 exposes V4.0 app-level compatibility as a front-door catalog. Its key
correction is that V4.0 must include V2.14/V3 app capabilities instead of treating
old successful routes as enemies of V4.

## What Changed

- `rtdsl.v4.claim_boundary_v4()` now reports the app compatibility catalog.
- `rtdsl.v4.plan_v4_app_compatibility(app)` returns one row for each promoted app.
- All 10 apps are currently `compatibility_route_protocol_ready`.
- `repair_required_apps` is now empty.
- Inherited compatibility never counts as V4-new speed credit.

## Local Gate

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v4_goal4751_app_compatibility_catalog_test tests.v4_frontdoor_test
```

Included in the broader 25-test pass for Goals 4749-4751.

## Required External Review Questions

1. Does the compatibility catalog answer the user-facing question clearly:
   "Can a V4 user still use the old benchmark app capability?"
2. Does it avoid overclaiming inherited compatibility as V4-new performance?
3. Is it acceptable that app-level compatibility is cataloged separately from the
   V4 operator-pushdown planner, so the planner still rejects app-identity kernels?
4. Are the remaining release blockers now correctly moved to POD timing and docs,
   rather than route existence?

## Non-Authorization

This debt file does not authorize release, public V4-over-V2.14 speedup claims,
whole-app high-performance wording, true-zero-copy wording, or final tag.
