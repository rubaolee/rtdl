# Goal2479 Robot Collision Benchmark Roadmap Consensus

Date: 2026-05-21

## Reviewed Artifacts

- `docs/reports/goal2479_robot_collision_benchmark_roadmap_2026-05-21.md`
- `tests/goal2479_robot_collision_benchmark_roadmap_test.py`

## External Reviews

| Reviewer | File | Verdict | Blocking issues |
| --- | --- | --- | --- |
| Gemini | `docs/reviews/goal2479_gemini_review_robot_collision_roadmap_2026-05-21.md` | Approved | None |
| Claude | `docs/reviews/goal2479_claude_review_robot_collision_roadmap_2026-05-21.md` | Approved | None |

## Consensus

Codex, Gemini, and Claude agree that robot collision is a reasonable next RTDL benchmark-app campaign before RayDB for this development lane.

Accepted rationale:

- Robot collision introduces new language/runtime pressure not fully covered by RayJoin, RTNN, Hausdorff/X-HD, or RT-DBSCAN: dynamic transformed query geometry, prepared static scenes with changing query batches, compact any-hit output, and eventually continuous/swept collision.
- RayDB remains valuable, but overlaps more with existing database-reduction and RayJoin-style spatial-query work.
- The roadmap correctly starts with CPU reference and generic contract design before native Embree/OptiX work.
- The native engine boundary remains app-agnostic: robotics semantics stay in Python/app code, while native/runtime concepts stay generic geometry, batching, any-hit, compact columns, prepared scenes, and phase timing.
- Paper reproduction, authors-code comparison, and public speedup wording remain blocked until separate evidence and review exist.

## Review Feedback Resolved

Gemini non-blocking feedback:

- Add native `collision` vocabulary avoidance so native code uses geometry terms such as `intersection`, `overlap`, `hit`, or `any_hit`.
- Make compact output representation a Goal2481 design decision aligned with RTDL buffer/tensor conventions.

Claude non-blocking feedback:

- Avoid a vacuous test assertion by checking the intended compact-output wording directly.
- Mark the paper citation as tentative until Goal2480 confirms full citation/code/data status.
- Require Goal2484 to define warmup protocol before performance measurement.
- Add a protocol that if authors' code becomes available, comparison requires a separate scoping goal before claims.

All four items are now reflected in the roadmap and guarded by `tests/goal2479_robot_collision_benchmark_roadmap_test.py`.

## Final Boundary

Goal2479/2480 may proceed. Native Embree/OptiX work should not start until the CPU reference app and generic RTDL contract design are reviewed. This consensus does not authorize paper reproduction claims, authors-code comparison, or public speedup wording.
