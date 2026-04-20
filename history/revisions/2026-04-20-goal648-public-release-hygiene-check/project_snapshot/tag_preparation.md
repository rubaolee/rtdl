# RTDL v0.9.2 Tag Preparation

Date: 2026-04-19

Status: superseded internal candidate; not tagged as a public release

Public status note: this `v0.9.2` tag plan was not executed. The candidate work
was absorbed into the released `v0.9.4` Apple RT consolidation, and the current
public release is `v0.9.5`.

## Proposed Tag Boundary

Tag `v0.9.2` should represent:

- Apple RT full-surface compatibility dispatch for the current 18 predicates
- native Apple Metal/MPS RT slices for:
  - 3D `ray_triangle_closest_hit`
  - 3D `ray_triangle_hit_count`
  - 2D `segment_intersection`
- prepared Apple RT closest-hit reuse
- masked chunked traversal for Apple RT hit-count and segment-intersection
- public documentation that clearly separates native Apple RT from
  CPU-reference compatibility dispatch
- performance wording bounded to Goal600 evidence

## Required Before Tagging

Before creating a `v0.9.2` tag:

- confirm no newer external tester report is unresolved
- confirm current worktree is clean
- confirm this release package has been reviewed
- confirm the user explicitly authorizes the release/tag action

## Current Evidence

Local pre-release gate:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_v0_9_2_apple_rt_pre_release_gate_2026-04-19.md`

Performance artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.md`

External reviews:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_external_pre_release_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_claude_pre_release_review_2026-04-19.md`

## Non-Claims To Preserve

The tag must not imply:

- broad Apple RT speedup
- Apple RT is more mature than Embree
- all `run_apple_rt` predicates are Apple hardware-backed
- native Apple RT support outside Apple Silicon macOS
- arbitrary rendering-engine support

## Current Tag Status

Do not create a `v0.9.2` tag from this historical plan. The public line moved
through `v0.9.4` and then `v0.9.5`.
