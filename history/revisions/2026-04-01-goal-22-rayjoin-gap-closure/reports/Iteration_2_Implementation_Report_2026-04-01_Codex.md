# Goal 22 Iteration 2 Implementation Report

## Summary

This first Goal 22 slice closes the machine-readable registry and analogue-generator part of the blocker list.

It does **not** claim that the missing public RayJoin datasets are acquired yet. Instead, it makes the current reproduction state explicit and generates the current Table 3 / Table 4 / Figure 15 analogue artifacts with honest status labels.

## Changes Made

### 1. Extended paper-reproduction registries

Updated [paper_reproduction.py](/Users/rl2025/rtdl_python_only/src/rtdsl/paper_reproduction.py) to add:

- `DatasetFamily`
- `LocalProfile`
- `dataset_families(...)`
- `local_profiles(...)`

These registries now encode:

- paper dataset-family status
- preferred provenance
- frozen local profile policies

while preserving the existing `paper_targets(...)` API.

### 2. Added Goal 22 analogue-artifact generator

Added [rayjoin_artifacts.py](/Users/rl2025/rtdl_python_only/src/rtdsl/rayjoin_artifacts.py) and [goal22_generate_reproduction_artifacts.py](/Users/rl2025/rtdl_python_only/scripts/goal22_generate_reproduction_artifacts.py).

The generator now produces:

- `goal22_reproduction_registry.json`
- `table3_analogue.md`
- `table4_overlay_analogue.md`
- `figure15_overlay_speedup_analogue.md`

These are intentionally status-aware outputs:

- available families are marked explicitly
- missing families are marked explicitly
- the `overlay-seed analogue` boundary is encoded directly in the generated artifacts

### 3. Added tests

Added [goal22_reproduction_test.py](/Users/rl2025/rtdl_python_only/tests/goal22_reproduction_test.py) to verify:

- dataset-family coverage for all current Table 3 handles
- presence of the frozen local profiles
- generator output content, including the `overlay-seed analogue` label

## Verification

Ran:

```sh
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal22_reproduction_test tests.paper_reproduction_test
PYTHONPATH=src:. python3 scripts/goal22_generate_reproduction_artifacts.py
```

Result:

- tests passed
- analogue artifacts generated under:
  - [build/goal22_reproduction](/Users/rl2025/rtdl_python_only/build/goal22_reproduction)

## Scope Boundary

This slice resolves the registry / reporting / generator part of Goal 22 only.

Still deferred to later Goal 22 work:

- actual public dataset acquisition and conversion for the missing families
- bounded per-pair local profiles once those datasets exist
- population of the generated analogue artifacts with real bounded run results
