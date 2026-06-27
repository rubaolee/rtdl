# V4 Goal4725 RTNN Measured No-Win Row

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `rtnn_closed_as_measured_no_win_candidate_not_v4_speed_evidence`

## Purpose

Goal4725 closes the RTNN row in the complete 10-app V2.14-vs-V4 matrix. RTNN
already has serious-scale same-hardware evidence, so rerunning it before
recording the decision would waste POD time.

Machine-readable row:

- `future/v4/evidence/v4_goal4725_rtnn_measured_no_win_row_2026-06-26.json`

## Evidence

Source evidence:

- `future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json`
- `future/v4/v4_goal4678_ranked_summary_disposition_2026-06-25.md`

Same hardware:

- GPU: NVIDIA RTX A5000
- Driver: 570.195.03
- POD: `root@194.68.245.170:22089`

## Result

| Points | V4/V2.14 hot | V4/V3.0.2 hot | Reading |
| ---: | ---: | ---: | --- |
| 65536 | 1.1447x | 1.0660x | small hot gain, but prepare is much slower; not formal app-level evidence |
| 262144 | 0.9985x | 1.0054x | serious-scale parity |
| 1048576 | 0.9939x | 0.9926x | serious-scale below parity |

The V4 route executes, validates, and keeps the hot path free of host
materialization, but it does not produce material app-level speedup at serious
scale. RTNN is therefore closed as:

```text
measured_no_win_deferred_from_v4_high_performance_release_path
```

## Boundary

Allowed wording:

- closest old-version RTNN ranked-summary front door versus V4 candidate route.

Forbidden wording:

- exact same runner V2/V3/V4 speedup;
- RTNN V4 speedup claim;
- RTNN as formal high-performance V4 evidence.

## Next

Proceed to Goal4726: `robot_collision` full-route or same-primitive
improvement/no-go protocol.

## Validation

Local validation:

- `py -m unittest tests.v4_goal4725_rtnn_measured_no_win_row_test tests.v4_goal4724_remaining_app_route_gap_audit_test tests.v4_goal4678_ranked_summary_disposition_test`

## Goal-Level Decision Audit

1. Was I being stupid?
   No. This goal avoids the stupid path: spending fresh POD time on a route that
   already showed serious-scale parity/slower behavior.

2. If yes, what action made the decision stupid?
   Not applicable. The stupid action would have been to keep RTNN open as if it
   might still be a high-performance candidate without a new generic lever.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Close RTNN as measured no-win and move the engineering queue to the next
   unresolved app.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4726 starts the `robot_collision` closure path.

## Non-Authorization

Goal4725 authorizes no POD spend, no final V4 tag, no public speed claim, no
RTNN speedup claim, no whole-app high-performance claim, no broad V4-over-V2.14
claim, no app-specific native kernel, no arbitrary callback support, and no
hidden V2/V3 fallback.
