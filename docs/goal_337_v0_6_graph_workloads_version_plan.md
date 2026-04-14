# Goal 337: v0.6 Graph Workloads Version Plan

## Why this goal exists

RTDL `v0.5.0` closed the nearest-neighbor language/runtime line. The next
version should not start from unbounded ideation. It should start from a
bounded application family that is already justified by the research direction
around ray-tracing cores.

The immediate anchor is the SIGMETRICS 2025 paper:

- Zhixiong Xiao, Mengbai Xiao, Yuan Yuan, Dongxiao Yu, Rubao Lee, and
  Xiaodong Zhang,
  *A Case Study for Ray Tracing Cores: Performance Insights with Breadth-First
  Search and Triangle Counting in Graphs*,
  DOI: `10.1145/3727108`

This goal formalizes that `v0.6` should focus on graph applications rather than
starting another unbounded backend-first cycle.

## Scope

This goal is planning-only.

In scope:

- define the intended `v0.6` application family
- define the first workloads that belong in the version
- define the first likely goal ladder for implementation and evaluation
- define what is explicitly out of scope for the first `v0.6` slice

Out of scope:

- implementing graph workloads
- claiming graph workload correctness or performance
- claiming paper reproduction
- changing the released `v0.5.0` support surface

## Planned v0.6 entry workloads

The first bounded `v0.6` application workloads should be:

- breadth-first search (`bfs`)
- triangle counting (`triangle_count`)

Reason:

- both are explicitly named in the SIGMETRICS 2025 graph case-study paper
- both are graph applications, not just another geometry workload
- together they exercise two different graph patterns:
  - frontier traversal
  - neighborhood intersection / local connectivity counting

## Version boundary

What `v0.6` should mean:

- RTDL grows from geometry and NN kernels into graph-application workloads
  that are still motivated by ray-tracing-core research
- the language/runtime remains the center
- graph applications are added as bounded workload families, not as an
  unbounded graph system rewrite

What `v0.6` should not mean:

- a promise to cover every graph algorithm from the paper ecosystem
- a promise of full cross-platform performance from day one
- a promise of immediate paper reproduction without first closing truth paths

## Initial goal ladder

The expected first `v0.6` ladder is:

1. graph workload charter and semantics
2. graph dataset / representation contract
3. BFS truth path
4. triangle-count truth path
5. first bounded backend closure for BFS
6. first bounded backend closure for triangle count
7. bounded Linux performance and paper-correlation report

## Honest boundaries

- Linux should remain the first serious performance platform
- Windows and macOS should start as correctness platforms unless and until
  there is evidence to claim more
- `v0.6` should begin with bounded graph workloads, not a broad graph DSL claim
- the SIGMETRICS 2025 paper is the motivation anchor, not an automatic claim
  that RTDL already reproduces that paper

## Exit condition

This goal is complete when the repo has:

- a saved `v0.6` version-planning report
- a saved external review on the plan
- a saved Codex consensus note

Then the next work can start from a stable version boundary instead of
improvised scope.
