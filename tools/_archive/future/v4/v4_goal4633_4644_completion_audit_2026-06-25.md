# V4 Goal4633-4644 Completion Audit

Date: 2026-06-25

Status: `goal4633_4644_complete_with_goal4644_claude_review`

Publication commit:

`c58642326f57f6326274b448caa8d75b3c7ef9de`

Published label:

`RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines`

This audit proves the requested Goal4633-4644 chain from the current worktree
state. It does not expand V4.0 scope beyond the authorized label.

## Goal Status Table

| Goal | Result | Primary evidence |
| --- | --- | --- |
| Goal4633 | weighted-sum promoted to measured Torch CUDA Tier-2 surface | `future/v4/v4_goal4633_weighted_sum_promotion_decision_2026-06-25.md`; `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md`; `tests/v4_goal4633_weighted_sum_promotion_decision_test.py` |
| Goal4634 | coverage audit refreshed after weighted-sum | `future/v4/v4_goal4634_coverage_audit_refresh_after_weighted_sum_2026-06-25.md`; `src/rtdsl/v4_coverage_audit.py`; `tests/v4_goal4633_weighted_sum_promotion_decision_test.py` |
| Goal4635 | component-union generic operator promoted | `future/v4/v4_goal4635_component_union_promotion_decision_2026-06-25.md`; `src/rtdsl/v4_goal4635_component_union_promotion_decision.py`; `tests/v4_goal4635_component_union_target_test.py` |
| Goal4636 | second/third coverage probes completed; failed probes rejected; AABB index passed | `future/v4/v4_goal4636_threshold_summary_pod_gate_decision_2026-06-25.md`; `future/v4/v4_goal4636b_grouped_any_hit_pod_gate_decision_2026-06-25.md`; `future/v4/v4_goal4636c_aabb_index_pod_gate_decision_2026-06-25.md`; `tests/v4_goal4636_threshold_summary_target_test.py`; `tests/v4_goal4636_grouped_any_hit_target_test.py`; `tests/v4_goal4636_aabb_index_target_test.py` |
| Goal4637 | AABB front-door/catalog promotion completed | `future/v4/v4_goal4637_aabb_frontdoor_catalog_promotion_2026-06-25.md`; `src/rtdsl/v4_goal4637_aabb_frontdoor_catalog_decision.py`; `tests/v4_goal4636_aabb_index_target_test.py` |
| Goal4638 | formal release scorecard frozen and supporting catalog gate passed | `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`; `future/v4/v4_goal4638_catalog_regression_gpu_gate_after_aabb_2026-06-25.md`; `tests/v4_goal4638_formal_scorecard_freeze_test.py` |
| Goal4639 | serious release scorecard POD gate passed | `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`; `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`; `tests/v4_goal4639_release_scorecard_test.py`; `tests/v4_goal4639_release_scorecard_decision_test.py` |
| Goal4640 | user-facing public docs cleanup completed | `future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md`; `README.md`; `docs/current_v4_status.md`; `docs/learn/performance_wording.md`; `future/v4/README.md`; `tests/v4_goal4640_public_docs_cleanup_test.py` |
| Goal4641 | clean-tree reproducibility gate completed | `future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md`; `src/rtdsl/v4_goal4641_clean_tree_reproducibility_decision.py`; `tests/v4_goal4641_clean_tree_reproducibility_test.py` |
| Goal4642 | final 3-AI authorization completed | `future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md`; `future/v4/reviews/antigravity_v4_goal4642_final_3ai_release_authorization_review_amended_2026-06-25.md`; `future/v4/reviews/codex_independent_v4_goal4642_final_authorization_review_and_amendment_recheck_2026-06-25.md`; `future/v4/reviews/codex_main_v4_goal4642_final_release_owner_authorization_2026-06-25.md`; `tests/v4_goal4642_final_authorization_packet_test.py` |
| Goal4643 | V4.0.0 publication completed | `future/v4/v4_goal4643_publication_decision_2026-06-25.md`; `src/rtdsl/v4_goal4643_publication_decision.py`; `VERSION`; `pyproject.toml`; `tests/v4_goal4643_publication_decision_test.py` |
| Goal4644 | post-release guardrails active and externally reviewed | `future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md`; `src/rtdsl/v4_goal4644_post_release_guardrails.py`; `future/v4/reviews/claude_v4_goal4644_post_release_guardrails_review_2026-06-25.md`; `tests/v4_goal4644_post_release_guardrails_test.py` |

## Current Measured Release Surface

- measured V4.0 surfaces: `8`
- candidate V4.0 release surfaces: `0`
- deferred/excluded V4.0 rows: `2`
- published public label: bounded to generic RT-core operator surfaces

The release still forbids:

- broad V4 speedup;
- whole-application speedup;
- all-benchmark speedup;
- public true-zero-copy;
- Tier-3 callback support;
- raw OptiX callback support;
- CuPy performance;
- C ABI / embedding / non-Python host;
- app-specific native kernels;
- Barnes-Hut covered by V4.0;
- Spatial RayJoin covered by V4.0;
- LibRTS paper reproduction.

## External Review / Cadence

Goal4642 final release authorization had three independent seats:

- Antigravity;
- independent Codex review;
- main Codex release-owner audit.

Goal4644 post-release guardrails received current external review:

- `future/v4/reviews/claude_v4_goal4644_post_release_guardrails_review_2026-06-25.md`
- verdict: `accept_goal4644_post_release_guardrails`
- amendments required: none

Antigravity Goal4644 attempt:

- `future/v4/reviews/antigravity_v4_goal4644_post_release_guardrails_review_blocked_2026-06-25.md`
- status: `blocked_empty_output_not_counted_as_review`
- not counted as a review seat.

Cadence preserved:

- next external review is due after another 6 hours of continued V4 work or at
  the next major decision;
- next 3-AI consensus is due after another 24 hours of continued V4 work or at
  the next release-level decision.

## Verification Commands

Targeted publication/guardrail group:

```text
py -3 -m unittest tests.v4_goal4644_post_release_guardrails_test \
  tests.v4_goal4643_publication_decision_test \
  tests.v4_frontdoor_test tests.v4_scope_gate_test \
  tests.v4_catalog_regression_gate_test
```

Result:

```text
Ran 20 tests in 18.938s
OK
```

Full V4 test group:

```text
$mods = Get-ChildItem tests -Filter 'v4*_test.py' | ForEach-Object { 'tests.' + $_.BaseName }
py -3 -m unittest $mods
```

Result:

```text
Ran 179 tests in 28.360s
OK
```

Catalog dry-run:

```text
py -3 scripts/v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16
```

Result:

```text
status: passed
release_authorized: true
measured_surface_count: 8
candidate_surface_count: 0
```

Quickstart:

```text
py -3 examples/v4/v4_frontdoor_quickstart.py
```

Result:

```text
status: ok
formal_release_authorized: true
measured_surface_count: 8
candidate_surface_count: 0
```

## Goal-Level Decision Audit

Was I stupid?

No for this completion audit. It records current evidence instead of using the
audit as a substitute for tests or external review.

If yes, what actions would have made the decision stupid?

It would be stupid to mark completion using the audit alone, to ignore failed
review attempts, or to erase forbidden claims because V4.0.0 is now published.

Was there another possibility that avoids getting stuck on a bad path?

Yes. The better path is the one used here: verify the machine state, add missing
Goal4644 guardrails, run tests, obtain Claude review, and leave optional
Antigravity debt explicit.

Can I start a different path that actually solves the problem?

Yes. Future work must start as V4.x goals and cannot silently mutate V4.0.0
scope.

## Completion Decision

Goal4633-4644 is complete for the bounded V4.0.0 generic RT-core operator
release: eight documented operators beat stated brute-force partner/CPU
baselines. The public headline must use the ratio distribution and denominators,
not the raw 5.185x geomean.

This audit does not authorize any additional V4.0 capability beyond the
published label and the measured surfaces already recorded by Goal4642/4643.
