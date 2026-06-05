# Handoff: Claude Review For Goal3511 Steady-State Relation Stream

Please perform an independent read-only review of Goal3511 and write the review
to:

`docs/reviews/goal3516_claude_review_goal3511_steady_state_relation_stream_2026-06-05.md`

## Context

Goal3511 is part of the v2.8 internal closeout evidence bookkeeping agreed in
Goal3515. It adds explicit timing fields to separate one-time setup/JIT/host
orchestration from the prepared resident shape-pair active relation
device-column stream used by the public-CDB overlay area route.

This is not a release request and not a speedup claim request.

Relevant commits:

- `b156242b` - `Goal3511 add overlay relation stream steady-state timing`
- `51f98850` - `Goal3516 close overlay cache evidence bookkeeping`

## Files To Inspect

- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`
- `tests/goal3511_overlay_area_steady_state_relation_stream_test.py`
- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_2026-06-05.md`
- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json`
- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_cache_write_pod_2026-06-05.json`
- Prior context:
  - `docs/reports/goal3447_shape_pair_active_relation_device_columns_2026-06-05.md`
  - `docs/reports/goal3507_overlay_area_prepared_payload_cache_2026-06-05.md`
  - `docs/reports/goal3509_overlay_area_binary_prepared_payload_cache_2026-06-05.md`
  - `docs/reviews/goal3508_claude_review_goal3507_overlay_payload_cache_2026-06-05.md`
  - `docs/reviews/goal3510_claude_review_goal3509_binary_overlay_payload_cache_2026-06-05.md`

## Required Review Questions

Please answer explicitly:

1. Does Goal3511 correctly separate monolithic `relation_discovery` from the
   measured active relation device-column pass?
2. Does the pod artifact support the reported steady-state result:
   final active relation device columns `0.00387s`, warmups `0.3716s`,
   `0.00746s`, `0.00716s`, and monolithic `relation_discovery` `1.4564s`?
3. Does Goal3511 avoid overstating this as RT traversal speedup, whole-app
   speedup, public speedup, or RayJoin reproduction?
4. Does correctness remain stable: relation counts, supported rows, positive row
   count, planned triangle pairs, total area error, and max row error?
5. Is the next-step interpretation sound: the next target is a clear prepared
   execution API/user pattern, not another immediate RT traversal tweak?
6. Are there any required fixes before Goal3516 evidence bookkeeping can close?

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

The likely correct verdict, if no issue is found, is `accept-with-boundary`:
Goal3511 is useful timing/evidence hygiene, but it does not authorize release or
public speedup wording.
