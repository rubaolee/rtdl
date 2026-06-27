# Call For Review: Phoenix V3 M21 All-App POD Protocol

Reviewer: Claude external critical reviewer

Requested verdict labels:

```text
authorize_m21_one_all_app_pod_run
revise_m21_protocol_before_run
deny_m21_all_app_run_do_more_focused_work
approve_blocked_not_release
```

This is not a release review. This is not a public speedup review. This is a run-authorization review for one serious same-RT-hardware V2.14 vs current Phoenix V3 all-app paired POD run.

Protocol packet:

```text
docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.json
docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
docs/reports/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
```

Implementation change to review:

```text
scripts/phoenix_v3_serious_paired_v2x_runner.sh
scripts/v3_phoenix_m21_all_app_protocol_gate.py
```

## Context

M20 verdict authorized protocol preparation only:

```text
authorize_m20_all_app_protocol_preparation_no_run
```

Three focused productized material probes are now closed:

```text
aabb_runner_m2_1
hausdorff_threshold_runner_m5_after_m6_1
triangle_m19_env_corrected_productized_runner
```

The remaining question is whether the focused fixes transfer into the full all-app paired context.

## What I Need You To Review

Please review the M21 protocol critically and answer:

1. Does the protocol satisfy every M20 required item?
2. Are the fail-closed bars sufficient and correctly stated?
3. Is the non-release boundary explicit enough?
4. Is the frozen case-ID whitelist preserved tightly enough?
5. Is the same hardware and project-venv interpreter gate strong enough after the runner patch?
6. Is the LibRTS OptiX AABB watch-row status correct?
7. Are the correctness/oracle gates sufficient before performance rows are accepted?
8. Is the new M21 protocol gate the right post-run evaluator, rather than the older baseline-oriented Set-A/B gate?
9. Is the post-run interpretation strict enough to prevent claiming release from blocker clearance?
10. Should one all-app POD run be authorized now, or should more focused work happen first?

## Explicit Non-Authorization Unless You Say Otherwise

Unless your verdict is exactly `authorize_m21_one_all_app_pod_run`, the run remains unauthorized.

No matter what, this review cannot authorize:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```

If you authorize the run, please state:

```text
one_all_app_pod_run_authorized: true
max_run_count: 1
expected_resource_window_hours: 5.5-7.0
hard_cap_hours_before_new_review: 8.0
```

If you do not authorize the run, please name the concrete blocking protocol defect or focused engineering work required before another review.

## Goal-Level Decision Audit

1. Was I foolish?

No for asking review before running.

2. If yes, what actions made the decision foolish?

It would be foolish to let the existence of three focused probes turn into automatic all-app POD spend.

3. Was there another path?

Yes: run immediately. That path repeats measure-first discipline failure.

4. Can I now try a different path?

Yes: require a clear external authorization verdict before spending POD time.
