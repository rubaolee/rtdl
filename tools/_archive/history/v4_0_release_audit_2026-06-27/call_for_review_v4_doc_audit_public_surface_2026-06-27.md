# Call For Review: V4.0.0 Documentation Audit Public Surface

Date: 2026-06-27

Please strictly review the RTDL V4.0.0 documentation cleanup result and decide
whether it is suitable as the public user entrypoint for the major V4 release.

## Review Objective

Confirm whether the current public docs/tutorials/examples now satisfy these
requirements:

1. Users see only the current V4.0.0 public version. Old V2/V3/V4 process
   documents, review debt, handoff files, and internal goal numbers should not
   appear in the first-time user path.
2. V4 is clearly described as a V2/V3 superset, not as a version that denies or
   discards older working routes.
3. Tutorials teach the current V4 programming model and progressively explain
   how the 10 benchmark apps are built from V4 operators, inherited prepared
   routes, and explicit partner choices.
4. Example paths are clear, runnable, and bounded.
5. Performance wording is honest:
   - no "all apps are faster" claim;
   - no inherited V3 win described as V4-only;
   - no operator-level win described as a whole-app win;
   - no broad V4-over-V2.14 or V4-over-V3 claim.
6. Historical/audit material is removed from the user learning path while
   remaining traceable for maintainers.
7. No current public page should confuse, alarm, or overburden a new user with
   process history.

## Files To Review

Current public files:

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/learn/operator_catalog.md`
- `docs/learn/performance_wording.md`
- `docs/public_documentation_map.md`
- `tutorials/current/README.md`
- `tutorials/current/01_first_run.md`
- `tutorials/current/02_hello_world.md`
- `tutorials/current/03_backend_choice.md`
- `tutorials/current/04_prepared_runtime.md`
- `tutorials/current/05_measurement_boundaries.md`
- `tutorials/current/06_benchmark_apps.md`
- `examples/README.md`
- `examples/v4/README.md`
- `examples/current/research_benchmarks/README.md`

Audit-boundary files:

- `future/README.md`
- `future/v4/README.md`
- `history/v4_0_release_audit_2026-06-27/README.md`
- `history/v4_0_release_audit_2026-06-27/v4_doc_audit_result_2026-06-27.md`

Moved review files:

- `history/v4_0_release_audit_2026-06-27/reviews/claude_v4_0_0_release_review_2026-06-25.md`
- `history/v4_0_release_audit_2026-06-27/reviews/claude_v4_goals_4647_4658_review_2026-06-25.md`

## Specific Changes To Check

- Former `docs/reviews/` files were moved to
  `history/v4_0_release_audit_2026-06-27/reviews/`.
- `future/` and `future/v4/` are now explicitly marked audit-only.
- `docs/learn/operator_catalog.md` was added as the current public V4 operator
  catalog.
- `tutorials/current/06_benchmark_apps.md` was added to teach how all 10
  benchmark apps are constructed from V4 operators, inherited prepared routes,
  and explicit partner choices.
- Public docs were rewritten to avoid internal review names, goal numbers,
  review-debt language, and release-candidate wording in the first-time user
  path.

## Local Validation Already Run

The local audit reported:

- public Markdown scan found no stale user-facing references to `future/v4`,
  `docs/reviews`, review debt, Claude/Gemini/Antigravity, release-candidate
  wording, or internal goal identifiers;
- V4 public examples and dry-run examples passed;
- `scripts/v4_catalog_regression_gate.py --mode dry-run` passed;
- `tests.v4_frontdoor_test`, `tests.v4_catalog_regression_gate_test`,
  `tests.v4_operator_catalog_test`: 20 tests OK;
- `tests.v4_goal4640_public_docs_cleanup_test`,
  `tests.v4_goal4743_public_docs_current_framing_test`,
  `tests.v4_goal4773_release_authorization_status_test`,
  `tests.v4_goal4774_release_packaging_audit_test`,
  `tests.v4_goal4775_release_staging_manifest_test`: 21 tests OK;
- focused public docs / staging manifest rerun: 11 tests OK;
- `git diff --check`: no whitespace errors, only Windows CRLF warnings.

Please independently judge whether this validation is sufficient.

## Required Verdict

Please use one of these verdict labels:

- `approve_v4_doc_audit_public_surface_clean`
- `approve_with_required_fixes`
- `block_public_docs_until_fixed`

## Required Answers

Please answer:

1. Verdict.
2. P0/P1/P2 findings.
3. Is the current user path clean enough for a V4.0.0 public major-version
   entrypoint?
4. Is `tutorials/current/06_benchmark_apps.md` sufficient as the first
   benchmark-app learning bridge, or does it need more runnable step-by-step
   code?
5. Did you find any overbroad or misleading performance wording?
6. Did you find any historical/audit/process material still leaking into the
   first-time user path?
7. Do you authorize continuing with this documentation audit as the V4.0.0
   public docs hardening commit?
8. If not authorized, list the required file-level fixes.

## Non-Authorization Boundary

This review is only for V4.0.0 documentation/public-surface cleanliness. It must
not authorize:

- broad all-app speedup claims;
- broad V4-over-V2.14 speedup claims;
- broad V4-over-V3 speedup claims;
- whole-application speedup wording;
- true-zero-copy claims;
- Tier-3 callback/PTX public support;
- raw OptiX callback support;
- embedding/C ABI/non-Python host support;
- paper-reproduction performance claims.
