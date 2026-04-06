# Codex Consensus: Goal 110 v0.2 Workload Family

## Scope

Reviewed files:

- `docs/goal_110_v0_2_segment_polygon_hitcount_closure.md`
- `docs/reports/goal110_v0_2_workload_family_selection_2026-04-05.md`
- `docs/reports/goal110_v0_2_workload_family_critique_2026-04-05.md`

## Review inputs

- Nash: `APPROVE-WITH-NOTES`
- Chandrasekhar: `APPROVE-WITH-NOTES`
- Codex: `APPROVE`

## Agreed result

Goal 110 should target:

- `segment_polygon_hitcount`

as the first v0.2 workload-family closure.

## Why this survives review

- It is a real spatial filter/refine family rather than a novelty demo.
- It has cleaner exact semantics than `point_nearest_segment`.
- It avoids immediately reopening the most fragile parity and scalability edges of the broader `lsi` story.
- It still expands RTDL beyond the v0.1 RayJoin-heavy slice with a coherent backend and correctness story.

## Important boundary

This choice is accepted as the best first closure target, not as proof that `segment_polygon_hitcount` is the strongest long-term RTDL workload family.

If the eventual implementation remains in the current local `native_loop` bucket, the final Goal 110 package must present that result as:

- workload-family closure
- semantic/backend closure

and not as automatic proof of RT-backed maturity.

## Final position

Goal 110 is now scoped tightly enough to proceed into real implementation work.
