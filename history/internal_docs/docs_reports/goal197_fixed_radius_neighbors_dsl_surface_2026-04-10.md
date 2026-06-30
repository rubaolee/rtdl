# Goal 197: Fixed-Radius Neighbors DSL Surface

Date: 2026-04-10
Status: completed

## Result

The public DSL/Python surface for `fixed_radius_neighbors` is now present.

Users can now write kernels using:

- `rt.fixed_radius_neighbors(radius=..., k_max=...)`

but the lowering path still rejects the workload honestly because runtime
support is not part of this goal.

## What changed

### Public API

Added:

- `fixed_radius_neighbors(*, radius: float, k_max: int)`

to:

- [api.py](/Users/rl2025/rtdl_python_only/src/rtdsl/api.py)

with bounded validation:

- radius must be non-negative
- `k_max` must be positive

### Package export

Exported the new predicate from:

- [__init__.py](/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py)

so users can write:

```python
import rtdsl as rt
```

and then call:

```python
rt.fixed_radius_neighbors(radius=0.5, k_max=16)
```

### Honest lowering boundary

Added an explicit rejection in:

- [lowering.py](/Users/rl2025/rtdl_python_only/src/rtdsl/lowering.py)

so `rt.lower_to_execution_plan(...)` now fails with an intentional message:

- the workload is a planned `v0.4` surface
- Goal 197 adds the DSL/Python contract only
- lowering is not implemented yet

### Language docs

Updated:

- [llm_authoring_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl/llm_authoring_guide.md)
- [dsl_reference.md](/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md)
- [workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)

The docs now:

- mention the new predicate
- show its planned kernel shape
- keep the implemented-versus-planned boundary explicit

## Verification

Ran:

- `PYTHONPATH=src:. python3 -m unittest tests.test_core_quality tests.rtdsl_language_test`
  - `Ran 104 tests`
  - `OK`
- `python3 -m compileall src/rtdsl docs/rtdl`
  - `OK`

## Acceptance summary

Goal 197 is intentionally narrow and is now complete:

- API surface: yes
- package export: yes
- compile-time kernel authoring: yes
- lowering/runtime support: intentionally no
- docs honesty: yes
