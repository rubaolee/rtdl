# Goal3541: v2.8 Final Closeout And v2.9 Kickoff 3-AI Consensus

Date: 2026-06-06

Status: accepted with boundary; v2.8 remains internally closed and v2.9 may
begin under the amended performance-first plan.

## Reviewed Files

- `docs/reports/goal3537_v2_8_final_internal_closeout_after_10s_evidence_2026-06-06.md`
- `docs/reports/goal3538_v2_9_performance_first_kickoff_plan_2026-06-06.md`
- `docs/reports/goal3536_v2_8_vs_v2_3_10s_steady_state_a5000_2026-06-06.md`
- `docs/reports/goal3522_v2_8_internal_closeout_3ai_consensus_2026-06-05.md`

## Review Files

- Claude: `docs/reviews/goal3539_claude_review_v2_8_final_closeout_and_v2_9_kickoff_2026-06-06.md`
- Gemini: `docs/reviews/goal3540_gemini_review_v2_8_final_closeout_and_v2_9_kickoff_2026-06-06.md`

## Verdicts

| Reviewer | Verdict | Summary |
| --- | --- | --- |
| Codex | `accept-with-boundary` | v2.8 closes internally as a foundation; v2.9 starts as performance-first. |
| Claude | `accept-with-boundary` | Accepts the direction but requires all-row diagnostic numbers, hardware continuity, review for honest-regression closure, and Workstream 3 sequencing. |
| Gemini | `accept` | Accepts the closeout and v2.9 plan; agrees the first implementation work should complete the five partial rows. |

## Claude Boundary Incorporated

The Goal3537/Goal3538 reports were amended after Claude review:

1. Goal3537 now carries the Goal3536 all-row diagnostic summary: median
   `1.006x`, geomean `0.946x`.
2. Goal3538 now requires hardware continuity for comparison packets: use the
   same A5000 class evidence chain where possible, or mark cross-hardware rows
   with an explicit caveat and exclude them from a single speedup aggregate.
3. Goal3538 now requires at least one independent external AI review before an
   `honest_regression` classification, especially Barnes-Hut, can close a row.
4. Goal3538 now states that Workstream 3 resident-execution and batching
   implementation begins only after V2.9-G2 produces and reviewers accept a
   full 10-second table with no silent partial rows.

## Consensus

Consensus verdict: `accept-with-boundary`.

v2.8 is closed internally. The final v2.8 performance reading is intentionally
modest: Goal3536 improved measurement discipline and exposed weak rows, but it
does not support broad speedup positioning.

v2.9 is authorized to begin as a performance-first internal development lane
under Goal3538. The first concrete implementation target is V2.9-G1: add
repeat/resident hooks for the five Goal3536 partial rows, then rerun the A5000
10-second table under V2.9-G2.

## Public Boundary

This consensus does not authorize:

- public v2.8 or v2.9 release wording;
- public speedup wording;
- broad RT-core speedup wording;
- package-install or PyPI wording;
- true zero-copy wording;
- whole-app acceleration wording;
- paper-reproduction wording;
- app-specific native-engine shortcuts;
- hidden partner selection.

Any public release or public performance claim still requires a separate
user-requested release packet and fresh review.

## Next Step

Start V2.9-G1:

1. add repeat/resident hooks for Hausdorff X-HD threshold;
2. add repeat/resident hooks for spatial RayJoin promoted contracts;
3. repair robot collision repeat accounting;
4. add Barnes-Hut node-coverage repeat/resident loop;
5. add LibRTS AABB index repeat/phase split;
6. keep all claim-boundary flags false.
