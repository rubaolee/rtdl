# Call For Review - Goal4947 Layer 1/2 Status And Next Plan

## Requested Reviewer

Claude or Antigravity

## Packet Under Review

`history/internal_docs/goal4947_layer1_layer2_status_and_next_plan_2026-07-04.md`

## Context

This packet summarizes the completed work from Goal4942 through Goal4946 and proposes the next sequence:

- Goal4947: LSI pair columns to Numba execution.
- Goal4948: non-RayJoin genericity gate.
- Goal4949: RayJoin hot-path phase remeasure.
- Goal4950: bounded RayJoin app integration only if measured.
- Goal4951: review and direction decision.

The core completed chain is:

```text
native directed point-location/PIP face_id device column
  -> generic Layer 1 row-buffer
  -> v2.6 neutral Numba handoff
  -> generic Numba uint32_equal_mask execution
```

The packet intentionally does not claim RayJoin whole-app speedup, true zero-copy, release readiness, or Layer 3 writer progress.

## Claude Review Already Received

Claude reviewed the first version of the packet and returned:

```text
approve_goal4947_status_and_next_plan
```

with three non-blocking strategic amendments:

1. Goal4949 must remeasure with real RayJoin hot-path numeric continuations, not demo operators.
2. Layer 3 writer/output assembly remains the larger remaining prize and must be weighed honestly against Layer 2.
3. Goal4948 must prove useful non-RayJoin work, not just another wiring demo.

The packet under review has been amended to include those requirements.

The packet also records the `src/rtdsl/output_assembly.py` drift check: that file is pre-existing Goal4935/4936/4939 work and is not new Layer 3 drift in this packet.

## Requested Verdict Label

`approve_goal4947_status_and_next_plan`

## Review Questions

1. Does the status packet accurately summarize Goals 4942 through 4946?
2. Does it correctly distinguish capability proof from performance proof?
3. Does it correctly state that Goal4946 proved actual native producer -> row-buffer -> Numba execution, not merely handoff planning?
4. Does it preserve the claim boundary: no RayJoin speedup, no true-zero-copy wording, no release wording, no broad Numba superiority?
5. Is Goal4947 the right next step, or should LSI producer-to-Numba execution be delayed?
6. Is Goal4948 needed to satisfy the genericity rule that RayJoin is a test case, not the model?
7. Is Goal4949 correctly placed after LSI/PIP Layer 1/2 execution proof, rather than before?
8. Does the plan correctly keep Layer 3 writer work separate and not restart it without a fresh phase table?
9. Are the Goal4950 and Goal4951 gates sufficiently bounded to prevent premature RayJoin performance claims?
10. Should the project proceed with Goal4947 under this plan?
11. Does the amended packet correctly incorporate Claude's AM1-AM3?
12. Is the `output_assembly.py` drift check sufficient to establish that this packet did not quietly restart Layer 3?

## Non-Authorization Reminder

This review must not authorize:

- public release wording;
- RayJoin whole-app speedup wording;
- true-zero-copy wording;
- broad Numba partner superiority claims;
- Layer 3 writer implementation;
- app-specific output-chain semantics in RTDL core;
- V3/V4 resurrection or public claims.
