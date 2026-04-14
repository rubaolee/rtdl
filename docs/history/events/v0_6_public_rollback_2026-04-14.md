# v0.6 Public Rollback Event

Date: 2026-04-14

## Event

The public repository state was rolled back from the `v0.6` line to the
released `v0.5` line.

## Why

The current `v0.6` line was judged misaligned with the intended RTDL direction
for graph work.

Specifically:

- the released `v0.6.0` package represented a bounded graph-workload/runtime
  line
- it did **not** yet represent the intended ray-tracing-based graph approach
  from the SIGMETRICS 2025 graph paper
- it did **not** yet provide a true RTDL-kernel-level graph execution model for
  users

Because of that mismatch, the project decision was:

- do not keep the current `v0.6` line as the public branch state
- return the public branch surface to `v0.5`
- preserve later `v0.6.x` replanning work only as local/non-public material
  until the graph line is rebuilt around the correct RT model

## Public Git State Change

Public branches were moved back to:

- `main` -> `fd9f098199731cc20a73ff4e790a579b16439138`
- `codex/v0_4_main_publish` -> `fd9f098199731cc20a73ff4e790a579b16439138`

That commit is the `v0.5` release line:

- `Final v0.5 release package`

## Tag State

Tags currently remain:

- `v0.5.0` -> `dbf77e005631e70fccffbfa344b75ee040d423b1`
- `v0.6.0` -> `03841c78215e76092004ce8a31d2869ec500b2d1`

This rollback event means:

- `v0.6.0` should not be treated as the active public branch line
- future graph work must be rebuilt from the correct RT-aligned design

## Practical Consequence

The next graph line should start from:

- RT graph reframe
- RTDL graph kernel-surface design
- backend work only after that RT model is explicit

## Boundary

This event log records the public-branch rollback decision.

It does not itself redefine the historical contents of the `v0.6.0` tag.
