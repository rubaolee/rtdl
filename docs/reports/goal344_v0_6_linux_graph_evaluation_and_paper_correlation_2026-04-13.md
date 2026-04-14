# Goal 344 Report: v0.6 Linux Graph Evaluation and Paper-Correlation Plan

Date: 2026-04-13

## Summary

This slice defines how the opening `v0.6` graph workloads should be evaluated
on Linux and how any relationship to the SIGMETRICS 2025 graph paper should be
described.

## Linux evaluation boundary

The first Linux evaluation slice should be:

- bounded
- correctness-first
- explicit about dataset family
- explicit about backend set

The first evaluation should not mix too many variables at once.

## Recommended evaluation shape

For each opening workload:

- one truth path
- one compiled CPU baseline
- at most one first accelerated Linux backend
- one bounded case table

Recommended reported fields:

- workload
- graph family
- graph size summary
- backend
- output parity status
- elapsed time

## Paper-correlation meaning

For `v0.6`, "paper correlation" should mean:

- RTDL workloads are motivated by the same named workload family as the
  SIGMETRICS 2025 graph paper
- bounded behavioral and evaluation choices are informed by that paper
- any comparison language stays at the level of workload-family alignment and
  bounded result correlation

It should **not** mean:

- full paper reproduction
- exact system equivalence
- direct claim of the same implementation strategy

## Non-claims

The first `v0.6` Linux evaluation must not claim:

- full SIGMETRICS 2025 reproduction
- full graph-system coverage
- multi-platform performance closure
- broad graph-analytics benchmark leadership

## Recommendation

Use Linux as the first bounded evaluation platform and keep the paper language
at workload-family correlation, not reproduction, until stronger evidence
exists.
