# Iteration 3 Implementation Report

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-6-python-simulator
Repo: /Users/rl2025/rtdl_python_only
Baseline Commit: 3569438d984d695795eb9c1903f728b03a065dd1

## Implemented

### New Runtime Entry Point

Added a CPU execution layer in:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/runtime.py`

Exposed publicly as:

- `rt.run_cpu(...)`

Updated exports in:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`

### Execution Model

`rt.run_cpu(kernel_fn, **inputs)` now:

1. compiles the RTDL kernel
2. validates required and unexpected input names
3. normalizes Python-side records into RTDL reference dataclasses
4. dispatches by predicate to the current CPU reference semantics
5. projects output rows to the kernel's `emit` fields

### Geometry Input Support

Supported simulator inputs:

- `segments`: mappings or `rt.Segment`
- `points`: mappings or `rt.Point`
- `triangles`: mappings or `rt.Triangle`
- `rays`: mappings or `rt.Ray2D`
- `polygons`: mappings with `id` + inline `vertices`, or `rt.Polygon`

Extra bookkeeping fields in mappings are ignored when the required logical
fields are present.

### Tests

Added simulator tests in:

- `/Users/rl2025/rtdl_python_only/tests/rtdsl_simulator_test.py`

Coverage includes:

- all 4 workload happy paths
- equivalence to `reference.py`
- missing input failure
- unexpected input failure
- polygon normalization failure
- precision rejection for non-`float_approx`

### Docs / Examples

Added:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_simulator_demo.py`

Updated:

- `/Users/rl2025/rtdl_python_only/docs/rtdl/programming_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/README.md`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/Makefile`
- `/Users/rl2025/rtdl_python_only/apps/rtdsl_python_demo.py`

## Evidence

- `make test`: pass
- `make build`: pass
- `make run-rtdsl-sim`: pass

### Simulator Demo Output

Observed local execution rows:

- LSI rows with materialized intersections
- PIP rows with `contains` results
- overlay rows with `requires_lsi` / `requires_pip`
- ray-query rows with per-ray hit counts

## Design Choice Recorded

Simulator-mode polygons intentionally use logical polygon records with inline
`vertices`. This is a deliberate convenience boundary for local CPU execution,
because the existing `Polygon2DLayout` encodes polygon references rather than
direct executable geometry.
