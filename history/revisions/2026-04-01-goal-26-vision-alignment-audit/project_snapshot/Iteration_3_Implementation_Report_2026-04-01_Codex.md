# Iteration 3 Implementation Report

## Scope of This Slice

This first Goal 26 implementation slice addresses the most structural vision-alignment issue identified in pre-review:

- the live repository surface encoded RayJoin as the core backend/plan identity rather than as the current v0.1 application slice

This slice focuses on:

- canonical live API naming
- canonical live schema naming
- canonical live docs/examples/tests
- compatibility preservation for existing RayJoin-named aliases

## Main Revisions

### 1. Canonical generic plan naming

Files:

- `src/rtdsl/ir.py`
- `src/rtdsl/lowering.py`
- `src/rtdsl/codegen.py`
- `src/rtdsl/plan_schema.py`
- `src/rtdsl/__init__.py`
- `schemas/rtdl_plan.schema.json`

Changes:

- introduced `RTExecutionPlan` as the canonical generic plan class
- changed the schema ID to `https://rtdl.dev/schemas/rtdl-plan-v1alpha1.json`
- changed default schema loading to `schemas/rtdl_plan.schema.json`
- introduced canonical lowering entry point:
  - `lower_to_execution_plan(...)`
- preserved compatibility aliases:
  - `RayJoinPlan = RTExecutionPlan`
  - `lower_to_rayjoin(...)` delegates to `lower_to_execution_plan(...)`

### 2. Canonical live backend spelling

Files:

- examples under `examples/`
- tests under `tests/`
- `src/rtdsl/baseline_contracts.py`
- active docs under `docs/rtdl/`
- `README.md`
- `Makefile`

Changes:

- switched live examples/tests/docs from `backend="rayjoin"` to `backend="rtdl"`
- changed live docs to describe `backend="rtdl"` as the canonical spelling
- documented `backend="rayjoin"` as a legacy compatibility spelling inside the current v0.1 slice
- switched the live lowering command references from `rt.lower_to_rayjoin(...)` to `rt.lower_to_execution_plan(...)`

### 3. Compatibility guarantee

Files:

- `tests/rtdsl_py_test.py`

Changes:

- added an explicit regression test proving that the legacy `backend="rayjoin"` spelling and `lower_to_rayjoin(...)` alias still work
- the compatibility test also verifies that the lowered plan normalizes to `backend="rtdl"`

## Verification

Executed:

- `PYTHONPATH=src:. python3 -m unittest tests.rtdsl_py_test tests.rtdsl_language_test tests.goal10_workloads_test tests.rtdsl_ray_query_test`
- `make build`
- `python3 -m py_compile src/rtdsl/ir.py src/rtdsl/lowering.py src/rtdsl/plan_schema.py src/rtdsl/codegen.py src/rtdsl/__init__.py`

Results:

- focused suite passed
- build passed
- modified Python modules compile cleanly

## Expected Review Focus

Claude and Gemini should now judge:

1. whether the canonical naming shift is strong enough
2. whether compatibility handling is honest and technically clean
3. whether remaining vision misalignment still exists elsewhere in the repo
4. whether Goal 26 should continue with a second revision slice after this pass
