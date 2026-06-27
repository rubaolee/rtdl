# V4 Goal4640 Public Docs Cleanup Decision

Status: complete pending external review.

Decision label:

`complete_public_v4_docs_cleanup_pending_external_review`

## Purpose

Goal4640 cleans the user-visible V4 surface after the Goal4639 serious
scorecard pass. The goal is not to authorize final V4 release. The goal is to
make the current public front door simple, V4-only, runnable, and honest before
clean-tree reproducibility and final 3-AI release authorization.

## What Changed

Public front door:

- `README.md` now presents RTDL V4 as the current user surface.
- `docs/README.md` now indexes current V4 docs only.
- `docs/current_v4_status.md` records the scorecard state and claim boundary.
- `docs/public_documentation_map.md` now separates first-time user, quick-check,
  and reviewer paths.
- `docs/current_v3_status.md` was archived to
  `history/legacy_project_archive_2026-06-24/docs_current_v3_status_2026-06-25.md`.

Tutorials:

- `tutorials/README.md` and `tutorials/current/*` now teach V4 front-door use,
  operator choice, measured runtime surfaces, and performance boundaries.

Examples:

- `examples/README.md` points users at `examples/v4/`.
- `examples/v4/` now provides clean runnable entrypoints for the V4 examples.
- `examples/current/README.md` is now explicitly a maintainer inventory, not the
  first-time user path.

V4 docs:

- `future/v4/README.md` is a concise V4 front door with Goal4639 status.
- `future/v4/tier2_operator_catalog.md` is a concise measured operator catalog.
- Fixed-radius, ray/triangle, point-group, callback-planning, scope, and catalog
  generated docs now use "scorecard passed / final release authorization
  pending" wording instead of stale development-preview wording.

Machine-readable status:

- `src/rtdsl/v4.py` front-door status is now
  `v4_scorecard_passed_front_door_pending_final_authorization`.
- `src/rtdsl/v4_operator_catalog.py` catalog status is now
  `v4_scorecard_passed_catalog_pending_final_authorization`.
- `src/rtdsl/v4_scope.py` scope status is now
  `v4_0_scorecard_scope_defined_pending_final_authorization`.
- `src/rtdsl/v4_goal4640_public_docs_cleanup_decision.py` records the Goal4640
  decision.
- `src/rtdsl/v4_release_decision.py` no longer lists
  `goal4640_user_docs_cleanup_not_done` as a release blocker.

## Verification

Targeted Goal4640/V4 docs tests:

```text
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_fixed_radius_docs_and_example_test tests.v4_scope_gate_test tests.v4_catalog_regression_gate_test
```

Result:

```text
Ran 24 tests in 25.361s
OK
```

Full V4 test group:

```text
py -3 -m unittest tests.v4*_test.py
```

Result:

```text
Ran 164 tests in 26.750s
OK
```

Direct example/gate checks:

- `examples/v4/v4_frontdoor_quickstart.py`: passed.
- `scripts/v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16`: passed.
- Public docs stale-word scan over README/docs/tutorials/examples/V4 front-door
  docs: no hits for current-V3 or stale development-preview wording.

## Claim Boundary

Allowed now:

- V4 has eight measured generic Tier-2 operator surfaces.
- The frozen Goal4639 scorecard passed: `8/8` measured surfaces and `4/4`
  strong families.
- The current public front door is pending final 3-AI release authorization.

Still not authorized:

- final V4 release;
- broad V4 speedup wording;
- whole-application speedup wording;
- public true-zero-copy wording;
- Tier-3 callback/PTX support wording;
- raw OptiX callback support wording;
- CuPy performance wording;
- embedding, C ABI, or non-Python host binding wording;
- app-specific native engine kernels.

## Remaining Release Blockers

- Goal4641 clean-tree reproducibility gate is not done.
- Goal4642 final 3-AI release authorization is not done.
- Existing Antigravity review debts for Goal4633, Goal4635, Goal4637, Goal4638,
  and Goal4639 remain recorded until reviewed or explicitly waived by final
  release authorization.

## Goal-Level Decision Audit

Was I stupid?

No for this goal. The work directly addressed the public-surface blocker instead
of creating another process layer.

If yes, what actions made the decision stupid?

Not applicable.

Was there another possibility that avoids getting stuck on a bad path?

Yes: the tempting bad path was to keep `future/v4` as the only V4 entry and call
that "done." I avoided that by adding clean `examples/v4` entrypoints, replacing
the root/docs/tutorial examples with V4 wording, and archiving the current-V3
status file.

Can I start a different path that actually solves the problem?

The next path is Goal4641: clean-tree reproducibility. Goal4640 should not keep
expanding. If public docs pass review, move on to clean-tree validation and then
Goal4642 final release authorization.

## Non-Authorization

This Goal4640 decision does not authorize final V4 release. It only closes the
public documentation and runnable-example cleanup blocker.
