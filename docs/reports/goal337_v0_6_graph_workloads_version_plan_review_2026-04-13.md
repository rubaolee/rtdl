# Goal 337 Review: v0.6 Graph Workloads Version Plan

Date: 2026-04-13

## Decision

Goal 337 is accepted.

## Why

The `v0.6` starting boundary is now clear and externally reviewed:

- version theme:
  - graph applications
- first workloads:
  - `bfs`
  - `triangle_count`
- anchor:
  - SIGMETRICS 2025 graph case-study paper

Gemini's review judged the plan coherent, bounded, and honest. The proposed
goal ladder is also reasonable for beginning a new version after the `v0.5.0`
release.

## Boundaries preserved

- this is still planning only
- no graph workload implementation is claimed yet
- no paper reproduction is claimed yet
- Linux remains the first intended performance platform
- Windows and macOS remain correctness-first platforms unless later evidence
  justifies more

## Result

`v0.6` can now formally start from:

- `bfs`
- `triangle_count`

The next correct slice is the graph workload charter.
