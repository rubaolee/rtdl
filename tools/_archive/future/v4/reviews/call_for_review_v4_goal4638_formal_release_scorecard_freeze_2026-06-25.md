# Call For Review: V4 Goal4638 Formal Release Scorecard Freeze

Please critically review Goal4638. This is the owner-approved formal release
scorecard freeze for the next serious POD scorecard run. It is not a request to
authorize V4 release.

## Requested Verdict Labels

Choose exactly one:

- `approve_goal4638_formal_scorecard_freeze_continue_goal4639`
- `approve_with_required_amendments_before_goal4639`
- `reject_goal4638_freeze_do_not_run_goal4639`

## Controlling Artifacts

- `future/v4/v4_formal_high_performance_release_hardening_goals_4633_4644_2026-06-25_owner_review.md`
- `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`
- `src/rtdsl/v4_goal4638_formal_scorecard_freeze.py`
- `tests/v4_goal4638_formal_scorecard_freeze_test.py`
- `src/rtdsl/v4_release_decision.py`
- `tests/v4_goal4632_release_decision_test.py`

## Supporting Evidence Only

The following catalog GPU gate is valid release-hardening evidence, but it is
not the owner-approved Goal4638 exit gate:

- `future/v4/v4_goal4638_catalog_regression_gpu_gate_after_aabb_2026-06-25.md`
- `future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.json`
- `future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.md`
- `src/rtdsl/v4_goal4638_catalog_regression_decision.py`

## What Changed

1. Corrected the Goal4638 controlling artifact from the catalog GPU gate to the
   formal release scorecard freeze.
2. Frozen the Goal4639 scorecard classifications:
   - strong/release-in-scope families: `rt_dbscan`, `raydb_style`,
     `triangle_counting`, `librts_spatial_index`;
   - partial controls: `hausdorff_xhd`, `robot_collision`,
     `contact_manifold`, `rtnn`;
   - deferred/excluded: `spatial_rayjoin`, `barnes_hut`.
3. Frozen all 8 measured V4 surfaces and zero candidate surfaces.
4. Frozen the claim boundary: no all-benchmark, whole-app, broad V4, public
   true-zero-copy, CuPy-performance, Tier-3 callback, C ABI, embedding, or
   non-Python-host wording.
5. Updated `v4_release_decision.py` so G8 is now
   `G8_formal_release_scorecard_freeze` with `passed_for_release: false`
   until external review clears the freeze. The catalog GPU gate is recorded as
   supporting evidence only.

## Verification Already Run

Local Windows V4 test sweep:

```powershell
py -m unittest tests.v4_goal4638_formal_scorecard_freeze_test tests.v4_goal4632_release_decision_test
```

Result: `9 tests OK`.

Full local V4 sweep:

```powershell
$modules = rg --files tests | Where-Object { $_ -match 'v4' -and $_ -like '*.py' } | ForEach-Object { $_.Replace('\','.') -replace '/','.' -replace '\.py$','' } | Sort-Object
py -m unittest @modules
```

Result: `153 tests OK`.

## Review Questions

1. Is the correction accepted: catalog GPU gate demoted to supporting evidence,
   formal scorecard freeze restored as the controlling Goal4638 exit?
2. Are the 10 benchmark-family classifications acceptable, or do any look like
   post-result metric gaming?
3. Are the 8 measured surfaces and zero candidates consistent with the current
   V4 coverage state?
4. Are the Goal4639 thresholds strong enough: correctness required, no silent
   skips, partial/deferred excluded from release geomean, and only bounded
   operator-level wording allowed?
5. Is it correct that Goal4639 remains blocked until this freeze receives at
   least one substantive external approval and any missing reviewer seat is
   explicitly tracked as review debt?
6. Does `v4_release_decision.py` now represent the release path honestly by
   keeping G8 not passed for release and keeping Goal4639 as a visible blocker?

## Non-Authorization

This review must not authorize V4 release, V4 release-candidate wording, broad
V4 speedup claims, whole-app speedup claims, all-benchmark speedup claims,
public true-zero-copy claims, Tier-3 callback support, raw OptiX callback
support, CuPy performance claims, C ABI, embedding, non-Python host claims, or
app-specific native kernels.
