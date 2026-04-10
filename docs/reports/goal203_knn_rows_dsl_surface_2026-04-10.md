# Goal 203: KNN Rows DSL Surface

Date: 2026-04-10
Status: completed

## Result

The public DSL/Python surface for `knn_rows` is now present.

Users can now write kernels using:

- `rt.knn_rows(k=...)`

and the lowering path now produces an explicit `knn_rows` execution plan for
later runtime goals.

## What changed

### Public API

Added:

- `knn_rows(*, k: int)`

to:

- [api.py](/Users/rl2025/rtdl_python_only/src/rtdsl/api.py)

with bounded validation:

- `k` must be positive

### Package export

Exported the new predicate from:

- [__init__.py](/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py)

so users can write:

```python
import rtdsl as rt
```

and then call:

```python
rt.knn_rows(k=8)
```

### Lowering support

Added explicit lowering in:

- [lowering.py](/Users/rl2025/rtdl_python_only/src/rtdsl/lowering.py)

The new lowered plan now:

- uses workload kind `knn_rows`
- carries the `neighbor_rank` output field explicitly
- preserves the family shape established by `fixed_radius_neighbors`

### Language docs

Updated:

- [llm_authoring_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl/llm_authoring_guide.md)
- [dsl_reference.md](/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md)
- [workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)

The docs now:

- mention the new predicate
- show its planned kernel shape
- keep the runtime-not-yet-implemented boundary explicit

## Verification

Ran:

- `PYTHONPATH=src:. python3 -m unittest tests.test_core_quality tests.rtdsl_language_test`
- `python3 -m compileall src/rtdsl docs/rtdl`

## Acceptance summary

Goal 203 is intentionally narrow and is now complete:

- API surface: yes
- package export: yes
- compile-time kernel authoring: yes
- lowering plan shape: yes
- runtime support: intentionally no
- docs honesty: yes
