# V4 Goal4745 Machine Release Decision Current Boundary Refresh

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision:
`machine_release_decision_refreshed_to_goal4742_goal4744_current_boundary`

## Purpose

Goal4745 updates the machine-readable V4 release decision and guardrail payloads
so they no longer present older Goal4655/Goal4718 labels as current truth.

The current machine boundary is:

```text
bounded_high_performance_python_edsl_release_candidate__not_all_benchmark_apps_faster
```

The current front-door/local gate is Goal4744.

## Changed Code

- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_goal4644_post_release_guardrails.py`
- `tests/v4_goal4632_release_decision_test.py`
- `tests/v4_goal4644_post_release_guardrails_test.py`
- `tests/v4_goal4745_machine_release_decision_refresh_test.py`

## What Changed

- `v4_goal4632_release_decision()` now reports
  `current_app_level_decision_label` instead of old Goal4655/Goal4718 labels.
- Release blockers now point to Goal4743/Goal4744 external review debt.
- Release gates now include:
  - `G13_public_docs_current_frontdoor_cleanup`
  - `G14_full_v4_local_gate_after_current_frontdoor_cleanup`
- Public wording now says the current app-level boundary does not support broad
  legacy all-app high-performance wording, without pointing users at old
  Goal4669.
- Post-release guardrails now expose the current Goal4742 decision label.

## Validation

Commands:

```text
py -m unittest tests.v4_goal4632_release_decision_test tests.v4_goal4643_publication_decision_test tests.v4_goal4644_post_release_guardrails_test tests.v4_goal4744_full_v4_local_gate_record_test
py -m unittest discover -s tests -p "v4*_test.py"
```

Observed:

```text
Ran 16 tests
OK

Ran 558 tests
OK
```

## Interpretation

The machine release decision is now aligned with the current public V4 boundary.
This prevents a reviewer or user tool from seeing clean docs but stale machine
state.

This does not authorize a final V4 tag. It strengthens consistency before final
release-candidate review.

## Goal-Level Decision Audit

1. Was I being foolish?

No. It would have been foolish to clean README/docs while leaving machine
release state on older Goal labels.

2. If yes, what action made the decision foolish?

Not applicable.

3. Was there another path?

Yes. Treat the machine decision as historical and leave it stale. That would
invite tooling/reviewer drift.

4. Can I now try a different path that actually solves the problem?

Yes. Move to the final review packet with docs, front-door API, scope gate, and
machine release decision all aligned on the same boundary.

## Non-Authorization

Goal4745 authorizes no final V4 tag, no all-benchmark speedup claim, no broad
V4-over-V2.14 wording, no arbitrary callback claim, no raw OptiX callback
claim, no true-zero-copy claim, no non-Python embedding/C ABI claim, and no
app-specific native kernel.
