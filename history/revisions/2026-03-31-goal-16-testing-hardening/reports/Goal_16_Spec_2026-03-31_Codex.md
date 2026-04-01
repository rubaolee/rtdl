# Goal 16: Testing Hardening and Comprehensive Test Package

## Goal

Strengthen RTDL's testing layer by adding a comprehensive testing package that improves confidence in:

- DSL/compiler correctness
- CPU vs Embree parity
- report/benchmark pipeline stability
- deterministic example behavior
- native comparison harness correctness

The package should be substantial enough that the repo has a clearly stronger unit/integration/system test story than the current baseline.

## Required workflow

This round must use the multi-agent process explicitly:

1. Codex writes the goal/spec.
2. Claude reviews the goal before implementation.
3. Gemini reviews the goal and agrees on how completion should be checked.
4. Claude proposes a comprehensive testing package.
5. Codex reviews Claude's proposal and either accepts it or requests revisions.
6. Codex implements or adapts the accepted package in the repo.
7. Codex runs a thorough test pass.
8. Claude reviews the implemented result.
9. Gemini reviews the implemented result and approves closure.
10. The round closes only if Codex + Claude agree, with Gemini aware and approving.

## In scope

- new or expanded test modules
- stronger test utilities if needed
- a clearer top-level test command or script if justified
- negative tests for weak or under-covered paths
- broader parity checks for CPU / Embree / native comparison paths
- report-generation or artifact-smoke tests when practical
- documentation updates if test usage changes

## Out of scope

- adding a new workload feature
- changing the basic semantics of existing workloads unless needed to fix a bug found by tests
- NVIDIA / OptiX runtime work
- broad benchmark expansion unrelated to test hardening

## Acceptance criteria

Goal 16 is complete only if all of the following are true:

- Claude's testing-package proposal is reviewed and either accepted or revised to consensus.
- The repo gains materially stronger test coverage or stronger test structure, not just cosmetic test renaming.
- A thorough test pass is run successfully after implementation.
- Any real defects found during the hardening pass are fixed.
- Claude reviews the implemented result and does not report blockers.
- Gemini reviews the implemented result and agrees the goal is complete.
- The round is archived in history and the docs remain consistent.

## Evidence expected at closure

- new/updated test files
- validation output from the thorough test pass
- Claude final review
- Gemini final approval
- Codex final consensus note
