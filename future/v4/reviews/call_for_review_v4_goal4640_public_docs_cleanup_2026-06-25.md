# Call For Review: V4 Goal4640 Public Docs Cleanup

Reviewer: Claude or Antigravity

Requested verdict labels:

- `approve_goal4640_public_docs_cleanup_continue_goal4641`
- `approve_with_required_amendments_before_goal4641`
- `reject_goal4640_public_docs_cleanup_overclaims_or_incomplete`

## Context

Goal4639 passed the frozen serious V4 scorecard:

- `8/8` measured surfaces passed
- `4/4` strong benchmark families passed
- `0` failed scorecard surfaces
- representative operator-scorecard geomean `5.185x`

Goal4640 is not final release authorization. It is the public docs/example
cleanup step before Goal4641 clean-tree reproducibility and Goal4642 final
3-AI release authorization.

## Files To Review

Primary Goal4640 decision:

- `future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md`
- `src/rtdsl/v4_goal4640_public_docs_cleanup_decision.py`
- `tests/v4_goal4640_public_docs_cleanup_test.py`

Public docs and examples:

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/public_documentation_map.md`
- `docs/learn/README.md`
- `docs/learn/performance_wording.md`
- `docs/learn/source_tree_doctor.md`
- `tutorials/README.md`
- `tutorials/current/README.md`
- `tutorials/current/01_first_run.md`
- `tutorials/current/02_hello_world.md`
- `tutorials/current/03_backend_choice.md`
- `tutorials/current/04_prepared_runtime.md`
- `tutorials/current/05_measurement_boundaries.md`
- `examples/README.md`
- `examples/v4/README.md`
- `examples/v4/*.py`
- `examples/current/README.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/fixed_radius_device_array_frontdoor.md`
- `future/v4/ray_triangle_device_array_frontdoor.md`
- `future/v4/point_group_device_array_frontdoor.md`
- `future/v4/callback_and_operator_planning.md`
- `future/v4/v4_0_scope_gate.md`

Release-decision integration:

- `src/rtdsl/v4.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_release_decision.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_fixed_radius_docs_and_example_test.py`
- `tests/v4_scope_gate_test.py`
- `tests/v4_goal4632_release_decision_test.py`

## Verification Already Run

Targeted Goal4640/docs group:

```text
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_fixed_radius_docs_and_example_test tests.v4_scope_gate_test tests.v4_catalog_regression_gate_test
Ran 24 tests in 25.361s
OK
```

Release-decision subset:

```text
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_goal4632_release_decision_test
Ran 10 tests in 3.846s
OK
```

Full V4 test group:

```text
py -3 -m unittest tests.v4*_test.py
Ran 165 tests in 26.359s
OK
```

Public stale-word scan:

- no hits for `V3.0.0`, `current V3`, `not a release announcement`,
  `development surface`, stale weighted-sum candidate wording, or
  `future/v4/examples` commands in the public docs set.

## Questions

1. Is the public docs cleanup sufficient to stop first-time users from falling
   into old V3 or stale V4 development-preview information?
2. Do the public docs accurately state the current V4 status: scorecard passed,
   final release authorization pending?
3. Do any public docs overclaim broad V4 speedup, whole-app speedup, true
   zero-copy, Tier-3 callback support, raw OptiX callbacks, CuPy performance,
   embedding/C-ABI, non-Python host bindings, or app-specific native kernels?
4. Are the `examples/v4` entrypoints acceptable as clean user-visible paths
   while reusing the already-gated `future/v4/examples` implementations?
5. Is it correct that `goal4640_user_docs_cleanup_not_done` has been removed
   from `v4_release_decision.py`, while clean-tree, final 3-AI authorization,
   and existing review debts remain blockers?
6. Are any amendments required before Goal4641 starts?

## Non-Authorization

This review must not authorize final V4 release. It can only approve or reject
Goal4640 public-doc/example cleanup and continuation to Goal4641.
