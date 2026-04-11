# Goal 245: Code Surface Audit Pass

## Objective

Record the next system-audit pass for the public code-facing surface after the
front page, tutorials, docs, and examples tiers.

## Scope

This pass covers the main public package and runtime entrypoints:

- `src/rtdsl/__init__.py`
- `src/rtdsl/api.py`
- `src/rtdsl/runtime.py`
- `src/rtdsl/oracle_runtime.py`
- `src/rtdsl/types.py`
- `src/rtdsl/baseline_runner.py`
- `src/rtdsl/reference.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/vulkan_runtime.py`

## Required Checks

- package import behaves correctly
- DSL surface and workload predicates still match the released `v0.4.0` contract
- runtime entrypoints expose backend boundaries honestly
- no maintainer-local paths or host leakage remain in these public code-facing files
- quality follow-up items are recorded explicitly rather than hidden under pass-only language
