# Goal 1 Spec

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-1-deterministic-codegen

## Objective

Strengthen RTDL as a compiler artifact before GPU/runtime integration by making backend planning and code generation deterministic, explicit, and testable.

## Current Baseline

The repository already supports:

- Python-hosted RTDL frontend
- frontend IR compilation
- RayJoin lowering for a narrow segment-vs-segment path
- generation of `plan.json`, `device_kernels.cu`, and `host_launcher.cpp`
- unit tests for the current narrow path

The current gaps are:

- `plan.json` is useful but still loosely specified
- generated artifact testing is mostly substring-based and single-example
- deterministic artifact expectations are not enforced as golden outputs
- validation/error coverage is still narrow
- generated host/device contracts are not systematically verified across examples and invalid inputs

## Goal 1 Scope

This round should implement:

1. A stronger backend plan contract
   `plan.json` should expose stable, explicit fields for plan consumers and tests.

2. Deterministic generated artifacts
   Generated metadata and code should be stable for the same RTDL input.

3. Golden tests
   The repository should contain snapshot-style expectations for generated artifacts on the current supported workload.

4. Stronger negative validation
   Invalid kernels should fail early and with clear messages.

## Non-Goals

- No real OptiX runtime execution
- No exact/robust arithmetic implementation
- No broad workload expansion beyond the current segment-join path
- No attempt to claim NVCC-compilable correctness beyond current non-GPU checks

## Proposed Implementation Shape

1. Extend the backend plan representation to include stable serialization helpers.
2. Introduce deterministic JSON serialization ordering and possibly structured formatting helpers for codegen.
3. Add golden test fixtures for:
   - `plan.json`
   - `device_kernels.cu`
   - `host_launcher.cpp`
4. Add negative tests for:
   - incomplete kernels
   - unsupported geometry combinations
   - unsupported emit fields
   - unsupported acceleration choices
   - invalid roles or duplicate role declarations if applicable
5. Keep the narrow workload honest: only assert what the current implementation really supports.

## Success Criteria

Goal 1 is complete if:

- The same kernel always produces byte-stable artifact outputs.
- Tests compare against checked-in golden files for the current workload.
- Invalid compiler inputs fail with precise, tested error messages.
- `make test` passes with the new golden and negative tests.
- Gemini and Codex agree that the scope is met and claims are technically honest.

## Review Questions For Gemini

1. Is this goal scoped correctly for the pre-GPU stage?
2. Are there missing validation or determinism requirements?
3. Should the golden tests target raw full-file equality, normalized equality, or both?
4. Are there risks in strengthening `plan.json` now that would create semantic debt later?
