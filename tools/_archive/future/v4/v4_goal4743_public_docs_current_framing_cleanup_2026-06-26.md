# V4 Goal4743 Public Docs Current Framing Cleanup

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision:
`public_docs_updated_to_goal4742_bounded_v4_framing`

## Purpose

Goal4743 updates the public user-facing docs to match the current Goal4742 V4
truth:

- V4 is a bounded high-performance Python eDSL/operator-pushdown release
  candidate.
- It has three historical benchmark-app candidate rows.
- It has a true V4 custom predicate early-exit workflow row.
- It does not claim that all 10 historical benchmark apps are faster than
  V2.14.

## Updated Files

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/learn/performance_wording.md`
- `docs/public_documentation_map.md`
- `tutorials/current/README.md`
- `tutorials/current/05_measurement_boundaries.md`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_goal4643_publication_decision.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `future/v4/v4_0_scope_gate.md`
- `tests/v4_frontdoor_test.py`
- `tests/v4_scope_gate_test.py`
- `tests/v4_goal4643_publication_decision_test.py`

## What Changed

The stale Goal4669-only app tables were replaced or corrected with the current
Goal4742 matrix:

- Hausdorff XHD, Triangle counting, and Barnes-Hut are the three candidate
  benchmark-app rows.
- RayDB is now a repaired modest row (`1.103x` vs V2.14, `1.105x` vs V3.0.2).
- Triangle's old V4/V3 regression is no longer presented as current.
- Robot is described as same-primitive boundary repaired with no V4-over-V2.14
  speed credit.
- Spatial RayJoin is described as no-current-full-V4-route with a failed
  shape-pair subprobe.
- Custom predicate early-exit is kept as a V4 eDSL/operator-pushdown workflow
  row, not a legacy 10-app win.
- Public index/tutorial/front-door references now point to Goal4742 as the
  current boundary rather than Goal4669/Goal4655 as current user truth.
- Non-claim wording now explicitly blocks broad V4-over-V2.14 speedup wording.
- `claim_boundary_v4()`, the V4 quickstart payload, and the V4 scope gate now
  expose Goal4742 as the current front-door/status boundary rather than
  Goal4655/Goal4718.
- `rtdsl.v4` no longer re-exports the old Goal4718 release-matrix helpers from
  the unified front door; those historical helpers remain in their dedicated
  historical module.
- `docs/current_v4_status.md` was reduced from an internal development ledger
  into a current user status page.

## Validation

Command:

```text
py -m unittest tests.v4_goal4743_public_docs_current_framing_test tests.v4_goal4646_pretag_wording_fixes_test tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_scope_gate_test tests.v4_goal4742_current_release_framing_test tests.v4_goal4643_publication_decision_test tests.v4_goal4644_post_release_guardrails_test tests.v4_goal4718_release_matrix_after_custom_predicate_test
```

Observed:

```text
Ran 39 tests
OK
```

Stale-current-goal scan:

```text
rg -n "Goal4669|Goal4655|Goal4718 V4 workflow row|bounded_operator_v4_only__app_level_high_performance_not_supported" README.md docs\README.md docs\current_v4_status.md docs\app_level_benchmark_summary.md docs\learn\performance_wording.md future\v4\README.md future\v4\tier2_operator_catalog.md tutorials\current\README.md tutorials\current\05_measurement_boundaries.md
```

Observed: no matches in the current public entry files.

Front-door stale-field scan:

```text
rg -n "goal4655_decision_label|legacy_goal4655_decision_label|front_door_status.*goal4718|v4_python_edsl_operator_pushdown_front_door_goal4718|v4_python_edsl_operator_pushdown_scope_goal4718|goal4669_legacy_app_level_high_performance_not_supported" src\rtdsl\v4.py src\rtdsl\v4_scope.py future\v4\examples\v4_frontdoor_quickstart.py future\v4\v4_0_scope_gate.md tests\v4_frontdoor_test.py tests\v4_scope_gate_test.py README.md docs\README.md docs\current_v4_status.md docs\app_level_benchmark_summary.md docs\learn\performance_wording.md future\v4\README.md
```

Observed: no matches in current front-door/public-entry files. The only matches
remaining in the scanned tree are under `docs/reviews/`, i.e. historical review
records rather than the user path.

## Claim Boundary

Goal4743 authorizes no final V4 tag. It authorizes only that public docs now
match the bounded Goal4742 release framing.

## Goal-Level Decision Audit

1. Was I being foolish?

No. Updating public docs after changing the matrix is required; leaving stale
RayDB/Triangle numbers at the front door would mislead users.

2. If yes, what action made the decision foolish?

Not applicable.

3. Was there another path?

Yes. Leave docs stale until final review. That would let users read old failed
rows as current truth.

4. Can I now try a different path that actually solves the problem?

Yes. Move to clean gate execution and final release-candidate review packet.

## Non-Authorization

Goal4743 authorizes no final V4 tag, no all-benchmark speedup claim, no broad
V4-over-V2.14 wording, no arbitrary callback claim, no raw OptiX callback
claim, no true-zero-copy claim, no non-Python embedding/C ABI claim, and no
app-specific native kernel.
