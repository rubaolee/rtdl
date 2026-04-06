# Goal 112 Segment-Polygon Performance Maturation Plan

Date: 2026-04-05
Author: Codex
Status: proposed

## Planning question

What is the smallest honest performance step that strengthens the Goal 110
family without pretending it is already an RT-core-native win?

## Proposed answer

Goal 112 should begin with:

- one explicit performance matrix for `segment_polygon_hitcount`
- on the accepted authored, fixture-backed, and derived cases
- across:
  - `cpu`
  - `embree`
  - `optix`

and should distinguish:

- `current_run`
  - direct `run_<backend>(...)` path
- `prepared_bind_and_run`
  - pre-created prepared kernel plus timed `bind(...).run()`
- `prepared_reuse`
  - one bound prepared execution reused across timed `.run()` calls

## Why this is the right first move

- it directly supports Goal 110
- it does not overreach into unrelated performance work
- it gives us a defensible current position even if raw speed does not improve
- it may expose one concrete avoidable overhead worth fixing

## First implementation targets

1. add or adapt a benchmark path that can measure this family on:
   - cpu
   - embree
   - optix
2. produce artifacts for:
   - authored minimal
   - county fixture
   - derived tiled x4
3. identify one concrete bottleneck or one concrete “already good enough”
   result

## Explicit measurement contract

The report should treat:

- `cpu_python_reference`
  - correctness context only
  - not part of the timed performance matrix
- `cpu`
  - timed current-run baseline
- `embree`
  - timed current-run, prepared-bind-and-run, prepared-reuse
- `optix`
  - timed current-run, prepared-bind-and-run, prepared-reuse

If a backend is unavailable on a host, the artifact must record:

- `available: false`

and must not silently invent parity/timing fields.

## Keep / pause rule

Keep Goal 112 focused only if the work remains tied to the Goal 110 family.

Pause or cut back if it starts turning into:

- broad benchmark churn
- unrelated backend heroics
- inflated claims not supported by the current lowering/runtime boundary
