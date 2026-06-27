# Codex Consensus - Phoenix V3 Robot Collision Flag-Stream No-Probe Paired M7 Review

Status: Claude + Codex 2-AI consensus complete.

Reviewed packet:

```text
docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.json
```

External review:

```text
docs/reviews/claude_phoenix_v3_robot_collision_flag_stream_no_probe_paired_m7_review_2026-06-21.md
```

Claude verdict: approve with amendments. P0 blockers: none.

## Amendments Applied

Claude required two P1 repairs before M7 promotion:

1. Correct the packet shape from `2,048` static obstacle triangles to
   `2,048` static obstacles / `4,096` static obstacle triangles.
2. Add a public wording disclosure that the `5.086x` tail and `5.075x`
   total-run-window metrics measure the prepared query execution phase, while
   the `1.171x` wrapper metric is the conservative process-level bound that
   includes all costs except the CPU probe-reference oracle.

Both amendments are now applied in the Markdown and JSON packets.

## Consensus Verdict

Codex accepts Claude's amended approval.

The row is M7-qualified only under the exact row-scoped boundary:

```text
RTDL V3 includes a generic collision_flag_stream route where, on the 8,192-pose
/ 147,456-segment discrete sampled probe contract on a single RTX 4000 Ada pod,
prepared OptiX grouped segment any-hit flags beat the same-contract Embree route
across five no-probe paired process samples: tail prepared invocation speedup
mean 5.086x, total-run window speedup mean 5.075x, and no-probe wrapper speedup
mean 1.171x with weakest no-probe wrapper speedup 1.083x. CPU probe-reference
validation was run separately and matched both backends. This is sampled
flag-stream evidence, not full robot planning, exact solid collision, or
continuous collision. The tail and window speedups measure the prepared query
execution phase; the wrapper speedup is the conservative process-level bound
that includes all costs except the CPU probe-reference oracle.
```

Machine-readable decision:

```text
generic_capability: collision_flag_stream
candidate_row_id: collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped
m7_promotion_authorized: true
row_scoped_public_speedup_claim_authorized: true
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Why This Counts As V3 Work

This is V3 engine work, not a special native app engine, because the evidence
tests the existing reusable prepared grouped segment any-hit flag-stream
contract across Embree and OptiX with the same shape, same contract, and same
output signatures. The app supplies robot-shaped grouped segments; the measured
capability is the generic `collision_flag_stream` execution route.

This does not mean robot collision as a whole is solved. It means one reusable
V3 row has a serious same-contract RTX speedup when CPU oracle validation is
kept out of the performance path and documented separately.

## Forbidden Wording

Do not say:

```text
Robot collision V3 is 5x faster end to end.
RTDL accelerates full robot planning.
RTDL supports exact solid collision for this row.
RTDL supports continuous collision for this row.
V3 is broadly faster than V2 for robot collision.
This row proves zero-copy.
OptiX is 5x faster than Embree for robot collision queries.
OptiX prepared invocation is 5x faster end to end.
The prepared invocation speedup of 5x is the per-call wall-clock cost including backend setup.
OptiX handles the full prepare-and-query cycle 5x faster than Embree.
```

## Goal-Level Decision Audit

Decision: promote this exact no-probe paired `collision_flag_stream` row to
row-scoped M7 after Claude's P1 amendments were applied.

1. Was I foolish?

   No. The decision is evidence-backed, externally reviewed, and bounded to the
   exact contract, shape, and timing definitions.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would have been to ignore Claude's P1
   timing-scope warning or to publish the old validation-inclusive wall result
   as a speedup.

3. Was there another path?

   Yes. I could keep `collision_flag_stream` blocked as a no-go. That would be
   safer but would discard the now-reviewed no-probe paired evidence that fixes
   the previous CPU-oracle wall-accounting blocker.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is to regenerate the M7 classification packet so this row
   is counted exactly once, then rerun wording and V3 rebuild gates.
