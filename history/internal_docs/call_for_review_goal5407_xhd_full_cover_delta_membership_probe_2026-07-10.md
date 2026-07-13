# Call For Review: Goal5407 X-HD Full-Cover Delta Membership Probe

Please strictly review:

```text
history/internal_docs/goal5407_xhd_full_cover_delta_membership_probe_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5407_full_cover_delta_membership_probe_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5407_full_cover_delta_membership_probe.py
tests/goal5407_full_cover_delta_membership_probe_test.py
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5407_2026-07-10.md
```

## Context

Goal5406 proved that the real RTDL full-public full-cover surface exists:

```text
RTDL full-cover rows     = 24,508,120 = 56 * 437,645
author Goal5387 raw rows = 27,133,990 = 62 * 437,645
delta                    = 2,625,870 = 6 * active_count
```

Goal5407 checks whether sampled author `(source, cell)` rows are members of the
RTDL full-cover surface.

## Requested Review Questions

1. Does the artifact correctly preserve Goal5406's real full-cover row count
   and Goal5387 author row count?
2. Does the per-source distribution show RTDL full-cover is exactly 56 rows for
   every active source?
3. Does the delta arithmetic correctly show a uniform 6 rows per active source?
4. Does the membership probe truly show that the sampled author rows are absent
   from the RTDL full-cover surface?
5. Is the conclusion justified that the remaining gap is not merely a uniform
   row-count delta, but also a row-identity / status-semantics gap?
6. Does the report avoid claiming explicit `-lb` support, row/hash parity,
   Figure 7/11 reproduction, performance parity, exact dataset reproduction, or
   full X-HD paper reproduction?
7. Is the recommended Goal5408 direction correct: reconcile cell-id namespace /
   row identity before changing native code?
8. Are the tests sufficient for this diagnostic stage?

## Expected Verdict Labels

Approve:

```text
approve_goal5407_full_cover_delta_membership_probe__row_identity_gap_found
```

Revise:

```text
revise_goal5407_membership_probe_before_using_as_decision_input
```

Block:

```text
block_goal5407_membership_probe_due_to_invalid_delta_or_membership_evidence
```

## Claim Boundary To Preserve

Allowed:

```text
RTDL full-cover surface is uniform at 56 rows per active source.
Author raw stream is 62 rows per active source on the Goal5387 oracle.
The sampled author rows are absent from the RTDL full-cover surface.
The remaining gap includes row identity / status-semantics, not only row count.
```

Forbidden:

```text
explicit -lb support;
author row/hash parity;
Figure 7 or Figure 11 reproduction;
author-vs-RTDL performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction;
hard-coding 6 or 62 rows per active as a fix.
```
