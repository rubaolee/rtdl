# Codex Phoenix V3 M1-M7 Compliance 2-AI Consensus

Status: accepted with required amendments applied, not release authorization.

Date: 2026-06-20.

## Consensus Inputs

Codex compliance table:

```text
docs/rebuild/v3/phoenix_v3_m1_m7_compliance_table_2026-06-20.md
```

External AI review:

```text
docs/reviews/claude_phoenix_v3_m1_m7_compliance_review_2026-06-20.md
VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS
```

Verification:

```text
py -3 scripts\v3_release_wording_gate.py --pretty
py -3 -m unittest tests.v3_release_wording_gate_test
```

Both passed after amendment intake.

## Decision

Codex and Claude agree that the Phoenix M1-M7 compliance table is acceptable as
the current V3 gate map after required amendments.

The accepted state is:

```text
M1 complete
M2 complete as no-execution skeleton
M3-M7 partial
Phoenix M7-qualified release rows: 0
release_authorized: false
public_speedup_claim_authorized: false
```

## Required Amendments Applied

| Claude requirement | Applied change |
| --- | --- |
| `partial` must have quantified completion criteria. | Added numerator, denominator, and completion bar definitions for M3-M7. |
| Dropping non-generic rows must not cherry-pick the 1.012x geomean denominator. | Added a geomean denominator rule: the 46-row paired artifact remains the broad-population figure; subset geomeans must be labeled as subsets. |
| Avoid overclaim from M1-M7 status. | Wording gate scans the compliance table and requires `Phoenix M7-qualified release rows: 0` plus `subset geomean`. |

## Next Authorized Work

The next Phoenix goal is a machine-readable P0 route-to-generic-capability map.
It must:

1. enumerate candidate rows from the current all-app and paired evidence;
2. assign each row one named generic V3 capability or mark it removed/internal;
3. preserve the original 46-row paired denominator for broad V3-vs-V2 status;
4. compute subset denominators separately;
5. choose the first pod rerun by Goal4392 capability gap, not by largest
   historical speedup.

## Goal-Level Decision Audit

Decision: accept the amended M1-M7 compliance table as Phoenix's current V3 gate
map.

1. Was I foolish?

   The corrected decision is not foolish. It makes partial milestones
   falsifiable instead of vague.

2. What actions would have made it foolish?

   Calling M3-M7 partial work "done" or recalculating V3 performance over a
   cherry-picked subset would have been foolish.

3. Was there another path?

   Yes. I could have gone straight to pod tuning. That would skip the gate map
   and repeat the old route-first failure.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is to build the route-to-generic-capability map and use it
   to drive focused pod work without overclaiming V3.

## Final Consensus Statement

Phoenix now has a current Goal4392 gate map. M1/M2 are real, M3-M7 are partial,
and release evidence is zero rows until the route map and M7 packet make rows
fully compliant. This is the right basis for the next performance work.
