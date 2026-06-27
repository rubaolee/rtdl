# Call For Review: V4.0.0 Public Documentation Fix Response

Date: 2026-06-27

## Context

Your prior public documentation audit returned:

```text
block_public_docs_until_fixed
```

The block was accepted. Please re-review the fix response and decide whether the
public documentation path is now clean enough to continue V4.0.0 public docs
hardening.

## Files To Review

- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/learn/performance_wording.md`
- `tutorials/current/05_measurement_boundaries.md`
- `tutorials/current/06_benchmark_apps.md`
- `examples/v4/custom_predicate_early_exit_planning.py`
- `future/v4/examples/operator_callback_planning.py`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `scripts/v4_catalog_regression_gate.py`
- `tests/v4_goal4640_public_docs_cleanup_test.py`
- `history/v4_0_release_audit_2026-06-27/v4_doc_audit_result_2026-06-27.md`

## Fixes Claimed

1. Public V4 docs no longer expose internal goal identifiers, reviewer names,
   review-debt language, release-candidate wording, `future/v4`, `docs/reviews`,
   or `parity/control` shorthand.
2. `tutorials/current/06_benchmark_apps.md` was rewritten as a real progressive
   tutorial with runnable planner snippets for all 10 benchmark apps.
3. Public quickstart and callback-planning example JSON no longer expose
   internal goal/protocol labels or audit-tree paths.
4. The catalog dry-run script now invokes public `examples/v4/...` wrappers.
5. The docs cleanup test now fails on internal goal labels, reviewer/debt
   language, release-candidate wording, `future/v4`, `docs/reviews`,
   `parity/control`, and goal labels in public example JSON output.

## Local Validation

Commands run:

```powershell
rg -n "Goal[0-9]+|goal[0-9]+|v4_goal|parity/control|review debt|Claude|Gemini|Antigravity|release candidate|future/v4|docs/reviews" README.md docs tutorials examples\v4 future\v4\examples\v4_frontdoor_quickstart.py future\v4\examples\operator_callback_planning.py --glob "*.md" --glob "*.py"

$env:PYTHONPATH='src;.'
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run

$env:PYTHONPATH='src;.'
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test tests.v4_operator_catalog_test tests.v4_goal4652_app_route_binding_test tests.v4_goal4660_ranked_summary_candidate_test tests.v4_goal4678_ranked_summary_disposition_test tests.v4_goal4773_release_authorization_status_test tests.v4_goal4775_release_staging_manifest_test

git diff --check
```

Observed:

- public surface scan: no matches;
- catalog dry-run: passed;
- focused test set: 55 tests passed;
- `git diff --check`: no whitespace errors, only Windows line-ending warnings.

## Questions

1. Are the P0 public-doc leakage findings fixed?
2. Is `tutorials/current/06_benchmark_apps.md` now acceptable as a first
   benchmark-app learning bridge?
3. Are the validation tests now strong enough to catch the previous failure
   mode?
4. Do any current public docs or public examples still confuse users with
   internal release-defense language?
5. Verdict: choose one:
   - `approve_public_docs_hardening_continue`
   - `approve_with_minor_edits`
   - `block_public_docs_until_fixed`

## Non-Authorization Boundary

This review does not authorize new broad speedup claims, raw OptiX callback
claims, public true-zero-copy claims, embedding/C-ABI claims, or non-Python host
binding claims.
