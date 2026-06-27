# Goal 91 Plan: Test Expansion For RayJoin Reproduction

Date: 2026-04-05

## Current gap themes

- backend-specific regression tests are uneven across mature backends
- long exact-source package checks exist, but the automation around them is not
  yet presented as one milestone-level test surface
- performance harnesses exist across multiple goals, but the current test story
  is fragmented

## Planned outputs

- additional unit tests for backend/runtime invariants
- stronger system tests for accepted long exact-source surfaces
- a consolidated Linux-backed performance verification slice
