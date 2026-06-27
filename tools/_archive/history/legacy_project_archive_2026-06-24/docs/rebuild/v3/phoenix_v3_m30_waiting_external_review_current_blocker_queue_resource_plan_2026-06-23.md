# Phoenix V3 Current Blocker Queue And POD Resource Plan While M30 Waits

Date: 2026-06-23

Status: `m30_waiting_external_review_no_all_app`

```text
release_authorized: false
all_app_pod_spend_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
v4_work_authorized: false
```

## Current Position

Phoenix V3 is not release-ready.

The latest serious same-RT-hardware all-app result remains the controlling
release-bar failure:

```text
M22 overall geomean V3 vs V2.14: 1.049x
M22 Set-A geomean: 1.013x
apps above 1.05x: 4 / 10
Barnes-Hut app geomean: 0.831x
release verdict: approve_blocked_not_release
```

M30 is currently waiting for a real external review. The Claude file-reading
review stalled, and the facts-only fallback hit a Claude session limit:

```text
You've hit your session limit · resets 12:50pm (America/New_York)
```

That message is not a technical verdict and does not count as 2-AI consensus.

## Closed Or Partly Closed Since M22

| Item | Status | Meaning |
| --- | --- | --- |
| M23 RayJoin current V3 `point_order_mode` crash | closed by Codex+Claude | Current RayJoin shape-pair row no longer crashes; not a release claim. |
| M24 Barnes-Hut prepared query residency fix | closed with boundary by Codex+Claude | Focused blocker-row set clears the severe-regression floor; prepared/repeated-query boundary must be carried. |
| M25 LibRTS AABB OptiX investigation | partial, not closed | Productized runner evidence exists, but strict single-shot OptiX watch row stayed at `0.922x`. |
| M27 LibRTS retain-output fix and triage | accepted with boundary | Code fix stays; OptiX cold watch row is `improved_not_closed`; Embree 32768 is a stability watch blocker. |
| M28/M29 Barnes-Hut Set-A family freeze/classification | closed as focused, not release | First-family chain exists, but M29 confirms it is a V3 capability addition, not same-contract V3-over-v2.14 speedup. |

## Open Blockers

1. **M30 external review missing.**
   RTNN prepared repeat50 runner cannot be counted in the current M28/M29 chain
   until Claude or another accepted external reviewer returns a real verdict.

2. **LibRTS AABB OptiX cold watch row remains open.**
   M27 status: `improved_not_closed`. This is Set-B/control, not Set-A, but it
   still blocks a clean release packet because the watch row has visible
   outliers and is not formally closed.

3. **LibRTS Embree 32768 remains a stability watch blocker.**
   M27 consensus: not a deterministic geomean blocker, but not explanation-only
   either because current variance is much higher than V2.14.

4. **V2.14 baseline confounders remain.**
   M22 recorded V2.14 failures in Spatial RayJoin and Triangle Counting rows.
   They must be fixed, formally excluded, or marked unverified before those
   comparisons support release-adjacent claims.

5. **All-app release bar remains far away.**
   M22 failed `1.20x` overall geomean and `8/10` app-win gates. Focused
   blocker fixes may justify a future rerun, but they do not themselves prove
   the all-app result.

## POD Plan

### Before Claude Reset

Use no POD unless a local-only blocker review identifies a tiny focused check.
Current useful work is documentation, protocol tightening, and rerun-script
preparation.

### After Claude Reset

First action:

```text
rerun docs/reviews/call_for_review_phoenix_v3_m30_second_set_a_rtnn_prepared_runner_facts_only_2026-06-23.md
```

Expected outcomes:

| M30 review outcome | POD action |
| --- | --- |
| `accept_m30_rtnn_as_second_set_a` or `accept_with_amendments` | no RTNN POD needed; write consensus and move to open blockers |
| `blocked_needs_focused_rerun` | run only focused RTNN rerun, estimated `0.5-2h` POD |
| `reject_not_second_set_a` | do not rerun RTNN; choose next true Set-A candidate or return to blocker queue |

### Next Real POD Spend

Likely focused POD, not all-app:

| Work | Estimated POD time | Purpose |
| --- | ---: | --- |
| M30 RTNN focused rerun, only if Claude requires it | `0.5-2h` | Close provenance/scope doubt. |
| LibRTS OptiX cold/Embree stability closure | `1-3h` | Resolve Set-B/control watch blockers. |
| V2.14 baseline confounder repair/verification | `1-3h` | Make Spatial RayJoin/Triangle comparisons usable or formally excluded. |
| Full all-app paired rerun | `2-5h` | Still forbidden until blockers close and protocol is reauthorized. |

Near-term spend target:

```text
next 12 hours: 0-3 POD hours unless Claude demands RTNN rerun
expected cost at $0.25/hour: $0-$0.75
```

Realistic path to a release-candidate all-app rerun:

```text
optimistic: 1-2 days, 4-8 POD hours
realistic: 2-4 days, 8-16 POD hours
stop early if LibRTS or baseline confounders do not close cleanly
```

These are planning estimates, not release promises.

## What Not To Do

- Do not rerun all-app while M30 lacks external review.
- Do not rerun all-app while LibRTS watch rows remain open.
- Do not count LibRTS/AABB single-shot as Set-A.
- Do not use M24 Barnes-Hut repeated-query speedups as whole-app Barnes-Hut
  force-solver speedups.
- Do not quote RTNN repeat50 as single-shot RTNN speedup.
- Do not use Set-B wins to compensate for missing Set-A runtime effect.

## Goal-Level Decision Audit

Decision: keep M30 open, defer all-app, and use the waiting period for blocker
queue and POD resource planning.

1. Was I foolish?
   No. M30 lacks a real external verdict, and M22/M27 still leave blockers.

2. If yes, what actions made the decision foolish?
   The foolish action would be to treat focused repairs and a blocked Claude
   review as permission for all-app or release wording.

3. Was there another path?
   Yes. Spend POD immediately on all-app or another broad rerun. That would
   repeat the earlier failure mode: expensive blended evidence before blockers
   are closed.

4. Can I now try a different path that truly solves the problem?
   Yes. Retry M30 after Claude reset, then close the specific remaining
   blockers with focused evidence before any future all-app protocol run.

## Non-Authorization

This plan authorizes no Phoenix V3 release, no all-app run, no public speedup
claim, no broad V3-over-V2 claim, no RT-core speedup claim, no single-shot RTNN
speedup claim, no true-zero-copy claim, no automatic partner-selection claim,
and no V4 work.
