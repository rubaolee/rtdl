# Goal 338: v0.6 Graph Workload Charter

## Why this goal exists

Goal 337 set the version boundary for `v0.6`. The next step is to define the
first graph workload family clearly enough that implementation can begin
without drifting into an unbounded graph system claim.

## Scope

In scope:

- define the first `v0.6` graph workload family
- define the intended semantic level for:
  - `bfs`
  - `triangle_count`
- define likely truth-path expectations
- define initial platform and backend boundaries

Out of scope:

- implementing graph workloads
- claiming performance
- claiming paper reproduction
- defining every future graph algorithm

## Exit condition

This goal is complete when the repo has:

- a saved graph workload charter report
- a saved external review
- a saved Codex consensus note

Then RTDL can start bounded `v0.6` implementation work from a stable workload
charter instead of only a version-level plan.
