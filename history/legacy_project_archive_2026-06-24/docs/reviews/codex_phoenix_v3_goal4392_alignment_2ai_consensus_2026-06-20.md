# Codex Phoenix V3 Goal4392 Alignment 2-AI Consensus

Status: accepted planning baseline, not release authorization.

Date: 2026-06-20.

## Consensus Inputs

Codex artifacts:

```text
docs/rebuild/v3/phoenix_v3_goal4392_alignment_audit_2026-06-20.md
docs/rebuild/v3/phoenix_v3_high_performance_candidate_matrix_2026-06-20.md
```

External AI review:

```text
docs/reviews/claude_phoenix_v3_goal4392_alignment_review_2026-06-20.md
VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS
```

Governing formal plan:

```text
docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md
docs/reports/goal4392_3ai_consensus_v3_0_overall_plan_2026-06-15.md
```

Verification:

```text
py -3 scripts\v3_release_wording_gate.py --pretty
py -3 -m unittest tests.v3_release_wording_gate_test tests.goal4392_v3_0_overall_plan_test
```

Both verification commands passed after amendment intake.

## Decision

Codex and Claude agree that Phoenix is acceptable as the next V3 planning
baseline only after the required amendments.

The accepted control rule is:

```text
Goal4392 governs Phoenix.
Generic V3 capability first.
Benchmark-app evidence second.
Public performance wording last.
```

This consensus does not authorize release. It does not authorize broad
V3-over-V2 timing superiority wording. It does not authorize post-M150
embedding/C ABI/SDK/external-runtime/true-zero-copy product scope as V3.

## Claude Required Amendments And Intake

| Claude amendment | Intake |
| --- | --- |
| No benchmark row may remain in Phoenix release evidence unless it instantiates a named generic V3 capability. | Added to the Goal4392 alignment audit and candidate matrix. |
| The current 1.012x V3-over-V2.14 geomean must be a release-blocking fact for broad performance wording. | Added to the Goal4392 alignment audit and candidate matrix. |
| Post-M150 exclusions need a concrete denylist gate, not only intent. | Added post-M150 leak patterns and context rules to `scripts/v3_release_wording_gate.py`; gate now scans the Phoenix docs. |

## Next Authorized Work

The next Phoenix work is not another broad benchmark sweep. It is:

1. Build the current M1-M7 compliance table from M0-M149 artifacts.
2. For each P0 route, name the generic V3 capability it instantiates.
3. Remove rows that cannot be mapped to a generic V3 capability.
4. Only then run focused pod/code work for rows that can change the V2.14-vs-V3
   answer or close a Goal4392 capability gap.

## Goal-Level Decision Audit

Decision: accept the amended Phoenix/Goal4392 alignment as the next planning
baseline.

1. Was I foolish?

   The corrected decision is not foolish. The earlier route-first framing was
   partially foolish because it risked repeating benchmark-patch behavior.

2. What actions made that earlier decision foolish?

   I drafted the first Phoenix queue from current performance rows before
   explicitly restoring Goal4392 as the V3 control plane.

3. Was there another path?

   Yes. Read Goal4392 first, map every route to a generic capability, and use
   benchmarks as evidence rather than architecture.

4. Can I now try a different path that actually solves the problem?

   Yes. The next work is the M1-M7 compliance table, followed by focused P0
   evidence and tuning only where it advances the generic V3 language.

## Final Consensus Statement

Phoenix is back on the right V3 path if it remains Goal4392-controlled:
execution graph, prepared plans, generic continuations, explicit partners,
phase accounting, backend-neutral contracts, and serious evidence. It is not
yet release-ready, and its current paired performance evidence blocks broad
V3-over-V2 timing superiority wording.
