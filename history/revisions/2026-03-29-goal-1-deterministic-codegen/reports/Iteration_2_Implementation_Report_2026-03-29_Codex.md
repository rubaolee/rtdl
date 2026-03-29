# Iteration 2 Implementation Report

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-1-deterministic-codegen
Status: implemented, awaiting Gemini review

## Goal Implemented

Goal 1: strengthen RTDL backend planning and code generation as deterministic, testable compiler artifacts.

## Changes Made

### 1. Stable backend plan serialization

- added `RayJoinPlan.to_dict()` in `src/rtdsl/ir.py`
- added explicit schema markers:
  - `$schema`
  - `schema_version`
- moved serialization responsibility into IR-layer objects instead of ad hoc codegen-only assembly

### 2. Explicit deterministic JSON output

- changed `src/rtdsl/codegen.py` to serialize `plan.json` with:
  - `plan.to_dict()`
  - `json.dumps(..., indent=2, sort_keys=True)`

This makes the metadata artifact byte-stable for the same input.

### 3. Formal plan schema

- added `schemas/rayjoin_plan.schema.json`
- added `src/rtdsl/plan_schema.py`
- implemented a lightweight local validator that supports the schema features used here:
  - `type`
  - `required`
  - `const`
  - `enum`
  - `items`
  - `additionalProperties`
  - local `#/definitions/...` references

This keeps validation dependency-free while still making the contract explicit.

### 4. Stronger frontend/lowering validation

- `rt.input(...)` now rejects invalid roles
- `rt.input(...)` now rejects duplicate input names within a kernel
- RayJoin lowering now rejects:
  - unsupported acceleration choices
  - duplicate explicit roles across candidate inputs

### 5. Golden artifact tests

- added exact golden fixtures under `tests/golden/county_zip_join/`:
  - `plan.json`
  - `device_kernels.cu`
  - `host_launcher.cpp`

### 6. Expanded test coverage

- replaced the earlier substring-heavy generated-output checks with:
  - exact golden comparison
  - schema validation for `plan.json`
- added negative tests for:
  - missing required segment fields
  - unsupported precision claim
  - unsupported acceleration
  - unsupported emit field
  - unsupported geometry pair
  - invalid input role
  - duplicate input names
  - duplicate explicit roles
  - kernel without `rt.emit(...)`

## Local Verification

Executed successfully:

- `make test`
- `make build`
- `make run-rtdsl-py`

Current unit test count:

- 14 tests passing

## Notes

- This round does not add runtime execution.
- This round does not change the narrow workload scope.
- The generated OptiX/CUDA output remains a semantically meaningful skeleton, not a fully integrated runtime.

## Review Request For Gemini

Review the implementation for:

1. correctness of the deterministic codegen contract
2. soundness of the schema and schema validator
3. adequacy of golden-file coverage
4. missing negative tests or invalid assumptions
5. any places where the code or tests still overclaim what RTDL can do
