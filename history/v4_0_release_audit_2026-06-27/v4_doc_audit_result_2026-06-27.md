# V4.0 Documentation Audit Result

Date: 2026-06-27

## Purpose

Prepare RTDL V4.0.0 as a clean public documentation surface:

- users see one current V4 version;
- V4 is presented as a V2/V3 superset;
- old review packets, debt records, and historical planning are not first-time
  learning material;
- tutorials teach the current operator model and the 10 promoted benchmark apps;
- examples are runnable without requiring CUDA where marked as dry-run;
- performance claims remain bounded.

## Current User Path

The current user path is:

1. `README.md`
2. `docs/README.md`
3. `docs/current_v4_status.md`
4. `docs/learn/operator_catalog.md`
5. `tutorials/current/README.md`
6. `tutorials/current/06_benchmark_apps.md`
7. `examples/README.md`
8. `docs/app_level_benchmark_summary.md`
9. `docs/learn/performance_wording.md`

## Archive/Audit Boundary

- `history/` stores historical and release-review provenance.
- `future/` is audit-only working/evidence material, not the user learning path.
- Former `docs/reviews` files were moved to
  `history/v4_0_release_audit_2026-06-27/reviews/`.

## Teaching Coverage

The new benchmark-app tutorial maps all 10 promoted apps to current V4 building
blocks:

- RTDBSCAN
- RayDB-style
- Triangle counting
- LibRTS spatial index
- Hausdorff XHD
- Robot collision
- Contact manifold
- RTNN
- Spatial RayJoin
- Barnes-Hut

Each row explains the app need, the V4 route or inherited prepared route, and
the source file to study.

## Verification

Completed local checks:

- public Markdown scan for stale current-user references to `future/v4`,
  review debt, reviewer names, release-candidate wording, and internal goal
  identifiers: clean;
- V4 public examples and dry-run examples: passed;
- `scripts/v4_catalog_regression_gate.py --mode dry-run`: passed;
- `tests.v4_frontdoor_test`, `tests.v4_catalog_regression_gate_test`,
  `tests.v4_operator_catalog_test`: passed;
- `tests.v4_goal4640_public_docs_cleanup_test`,
  `tests.v4_goal4743_public_docs_current_framing_test`,
  `tests.v4_goal4773_release_authorization_status_test`,
  `tests.v4_goal4774_release_packaging_audit_test`,
  `tests.v4_goal4775_release_staging_manifest_test`: passed;
- `git diff --check`: no whitespace errors, only Windows line-ending warnings.

## External Blocker And Fix

External review blocked the first cleanup pass with verdict
`block_public_docs_until_fixed`.

The blocker was accepted. The fixes applied in this pass:

- removed internal release-goal identifiers from the public V4 front-door status
  and quickstart JSON;
- removed `parity/control` reviewer shorthand from current public docs and
  tutorials;
- rewrote `tutorials/current/06_benchmark_apps.md` from a routing/review index
  into a progressive benchmark-app tutorial with runnable planner snippets for
  all 10 promoted apps;
- cleaned public callback-planning example output so it no longer exposes
  internal protocol paths or goal status labels;
- updated `scripts/v4_catalog_regression_gate.py` to run public
  `examples/v4/...` wrappers instead of audit-tree example paths;
- hardened `tests.v4_goal4640_public_docs_cleanup_test` so public Markdown,
  V4 example source, and example JSON output fail on internal goal labels,
  reviewer/debt language, and `parity/control` shorthand.

Post-fix focused validation:

- public surface scan for internal goal labels, reviewer names, review-debt
  wording, release-candidate wording, `future/v4`, `docs/reviews`, and
  `parity/control`: clean;
- `scripts/v4_catalog_regression_gate.py --mode dry-run`: passed;
- focused V4 docs/front-door/catalog/ranked-summary/staging test set: 55 tests
  passed;
- `git diff --check`: no whitespace errors, only Windows line-ending warnings.

## Non-Claims Preserved

The cleaned public docs still do not authorize:

- all benchmark apps are faster;
- broad V4-over-V2.14 speedup wording;
- broad V4-over-V3 speedup wording;
- whole-application speedup wording;
- public true-zero-copy wording;
- Tier-3 callback/PTX support wording;
- raw OptiX callback support wording;
- broad CuPy performance wording;
- embedding, C ABI, or non-Python host binding wording.
