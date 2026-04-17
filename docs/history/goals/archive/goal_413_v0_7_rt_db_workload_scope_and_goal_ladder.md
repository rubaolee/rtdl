# Goal 413: v0.7 RT Database Workload Scope And Goal Ladder

## Goal

Open `v0.7` as the bounded RTDL database-style workload line and define the
implementation ladder from the accepted RTScan/RayDB analysis.

## Required outcome

- `v0.7` is explicitly separate from the released `v0.6.1` graph line
- the next-version scope is bounded to RT-friendly analytical workloads
- the implementation ladder is concrete enough to execute goal by goal
- the non-goals are explicit so `v0.7` does not drift into a DBMS claim

## Scope boundary

`v0.7` is about:

- denormalized analytical data
- predicate-driven scan/filter workloads
- fused grouped aggregate workloads
- offline/amortized encoding and BVH build assumptions

`v0.7` is not about:

- a SQL engine
- online joins as a first-class RT workload
- transactions or OLTP
- arbitrary relational operator closure

## Deliverables

- one `v0.7` goal-sequence document
- one report that explains:
  - why `v0.7` is the right version boundary
  - what the first implementation goals are
  - what must stay out of scope

## Review requirement

This goal requires at least 2-AI consensus before closure.
