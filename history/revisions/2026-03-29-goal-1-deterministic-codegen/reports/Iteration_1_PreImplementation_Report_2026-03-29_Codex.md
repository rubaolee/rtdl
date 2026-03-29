# Iteration 1 Pre-Implementation Report

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-1-deterministic-codegen
Status: awaiting Gemini review

## Summary

I propose Goal 1 as the first compiler-quality milestone before GPU/runtime integration:

- strengthen the backend plan contract
- make generated artifacts deterministic
- add golden tests for the supported narrow workload
- add stronger negative validation tests

## Why This Goal Is First

The project already has a real compiler shape. Before moving to a GPU environment, the main risk is semantic drift between frontend intent, lowering, and generated artifacts. Goal 1 addresses that risk directly and creates a stable base for later runtime integration.

## Expected Deliverables

- stronger and more explicit serialized backend plan
- deterministic generation of `plan.json`, `device_kernels.cu`, and `host_launcher.cpp`
- checked-in golden fixtures for the current segment-join workload
- expanded validation and negative tests
- updated documentation only if the strengthened contract changes what the project claims

## Constraints

- no runtime integration
- no advanced precision work
- no expansion beyond the current narrow supported workload unless needed for validation honesty

## Risks Already Visible

- some future fields may not yet be mature enough for a stable plan contract
- snapshot tests can become brittle if formatting is not consciously stabilized
- invalid-input coverage may expose structural API ambiguities, not just missing tests

## Requested Gemini Action

Review the scope, identify missing requirements, and say whether this is the right first pre-GPU goal. If you recommend changes, be specific enough that the implementation target can be revised before any code changes are made.
