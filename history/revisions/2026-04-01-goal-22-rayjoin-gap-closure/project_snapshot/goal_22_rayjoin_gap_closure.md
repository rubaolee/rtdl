# Goal 22: RayJoin Embree Gap Closure

## Goal

Address only the blockers frozen by Goal 21 that are required before the bounded local reproduction runs can happen.

## Scope

Goal 22 is intentionally narrow. It may include:

- dataset acquisition and conversion helpers for the missing RayJoin paper families
- machine-readable matrix/provenance/profile registries
- Table 3 generator support
- Table 4 generator support for the overlay-seed analogue
- Figure 15 generator support
- report metadata needed to distinguish:
  - exact reproduction
  - derived local reproduction
  - synthetic scalability analogue
  - overlay-seed analogue

## Non-Goals

Goal 22 does not include:

- running the final full reproduction package
- changing the NVIDIA roadmap
- adding unrelated new workloads
- changing the frozen Goal 21 matrix unless a real blocker forces it

## Acceptance Bar

Goal 22 is complete when:

1. the missing dataset/provenance machinery needed by Goal 23 exists
2. Table 3 / Table 4 / Figure 15 generation paths exist
3. the overlay-seed analogue boundary is encoded in the reporting path
4. any still-missing public dataset is labeled clearly rather than silently skipped
5. Gemini approves the implementation and Claude accepts the goal-level closure
