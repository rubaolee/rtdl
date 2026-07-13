# Call For Review: Goal4952 Post-4951 Performance Decision

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4952_post_4951_performance_decision_report_2026-07-04.md`
- `history/internal_docs/goal4951_compiled_path_split_rayjoin_gate_2026-07-04.md`
- `history/internal_docs/antigravity_goal4951_compiled_path_split_rayjoin_gate_review_2026-07-04.md`
- `history/internal_docs/goal4951_pod_artifacts/plain_section57_overlay.json`
- `history/internal_docs/goal4951_pod_artifacts/compiled_section57_overlay_rerun.json`

Requested verdict:

`approve_goal4952_stop_cpu_numba_materializer_authorize_goal4953_audit`

or, if blocked:

`block_goal4952_decision_until_amended`

## Context

Goal4951 proved a compiled generic path-split materializer can preserve
correctness, but it failed the writer performance gate:

- plain writer: `2.583328s`
- compiled path-split rerun writer: `4.155936s`
- relative speed: `0.622x`
- required minimum: `>=1.10x`

Antigravity approved Goal4951 closure as:

`approve_goal4951_correct_but_not_faster_stop`

Goal4952 turns that evidence into the next decision:

- stop the CPU/Numba materializer line;
- do not implement another writer route yet;
- authorize only Goal4953, a fine-grained measurement of the current fastest
  plain writer.

## Questions For Reviewer

1. Does Goal4952 correctly interpret Goal4951: correctness passed, performance
   failed, route killed?

2. Is it correct to stop this specific route:

   `app adapter -> CPU/Numba compiled generic path-split materializer -> Python text formatter`

   rather than trying another small variant of the same idea?

3. Does Goal4952 avoid overclaiming that all Layer 3 work is impossible?

4. Is the next authorized goal correctly limited to measurement:

   `Goal4953 Plain Writer Fine-Grained Phase Audit`

   with no native/device writer implementation yet?

5. Are the Goal4953 required phase measurements sufficient to decide whether a
   native/device writer is justified?

6. Does Goal4952 preserve the red lines:

   - no RayJoin output text format in RTDL core;
   - no public API exposure;
   - no performance claim;
   - no further implementation without a new reviewed goal?

7. Should Goal4952 close with:

   `completed_post_4951_decision__stop_cpu_numba_materializer__authorize_plain_writer_phase_audit`

## Non-Authorization Boundary

Approval authorizes only Goal4953 measurement. It does not authorize:

- native writer implementation;
- device writer implementation;
- another CPU/Numba materializer wrapper;
- default route promotion;
- public API exposure;
- RayJoin-specific output format in RTDL core.
