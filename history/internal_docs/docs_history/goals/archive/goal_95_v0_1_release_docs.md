# Goal 95: v0.1 Release Docs

## Objective

Produce the release-facing documentation needed to make RTDL v0.1 usable and
understandable without reading dozens of individual goal reports.

## Scope

The release docs should cover:

- what RTDL v0.1 is
- what workloads/backends are actually accepted
- how to run the main validated surfaces
- what the timing boundaries mean
- what the current non-goals and limitations are
- where the performance claims are strong versus provisional

## Required outputs

- refreshed release-facing README/docs entry points
- v0.1 support/status table
- quick-start / runbook section
- reproducibility guidance
- concise release Q/A for likely user/reviewer questions

## Constraints

- do not over-promise unsupported API/backend/workload surfaces
- prefer centralized release docs over scattered pointers
- keep paper claims and repository claims aligned but separate

## Acceptance

Goal 95 is done when:

- a new reader can understand the v0.1 package from the release docs alone
- the docs match the accepted backend/performance status
- the docs have 2+ AI review before publish
