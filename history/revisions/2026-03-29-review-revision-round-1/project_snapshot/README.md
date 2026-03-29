# RTDL

RTDL is a research project for making non-graphics ray tracing programming substantially easier. The initial target is RayJoin, an OptiX/CUDA system for spatial joins on NVIDIA RT cores. The project is now framed as a Python-hosted DSL with a compiler IR underneath it: users stay in Python, describe geometry, traversal, refinement, and outputs, while the compiler and runtime handle BVH construction, ray formulation, payload packing, shader wiring, and backend-specific launch details.

This repository now contains:

- design notes for the first version of the project,
- a Python-hosted RT DSL prototype,
- an initial compiler IR for RT kernels,
- a RayJoin backend plan and OptiX/CUDA skeleton generator,
- Python tests to keep the seed implementation executable.

## Why RayJoin First

RayJoin is a strong first backend target because it already proves that non-graphics workloads can benefit from RT cores, but it also exposes the current programming cost:

- developers still have to reason about OptiX program stages,
- problem formulation is expressed indirectly through rays and hit programs,
- precision handling is tightly coupled to backend details,
- BVH and launch configuration decisions leak into application logic, and
- debugging requires understanding CUDA, OptiX, and the application domain at once.

RTDL aims to raise the abstraction level without hiding the performance model.

Current precision note:

- the implemented backend path is currently `float_approx`, not exact or robust geometric arithmetic,
- `precision="exact"` is intentionally rejected by the current RayJoin lowering path,
- advanced precision work remains future roadmap work.

## Repository Layout

- `src/rtdsl/`: Python-hosted RT DSL prototype and IR.
- `apps/rtdsl_python_demo.py`: RayJoin-flavored Python kernel example.
- `tests/rtdsl_py_test.py`: Python DSL regression test.
- `generated/`: emitted backend skeletons from the Python DSL pipeline.
- `docs/vision.md`: project scope and research framing.
- `docs/rayjoin_target.md`: how RTDL maps onto RayJoin-specific concerns.
- `docs/v0_1_roadmap.md`: concrete scope and milestones for the first RTDL release.

## Build

Prepare the workspace:

```sh
make build
```

Run the Python RTDSL example:

```sh
make run-rtdsl-py
```

Run the test suite:

```sh
make test
```

## Python Example

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join():
    left = rt.input("left", rt.Segments)
    right = rt.input("right", rt.Segments)
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])
```

This is intentionally small. The immediate goal is to stabilize the Python frontend, the RT kernel IR, and the lowering boundary before introducing richer operators, scheduling controls, backend specialization, and code generation. The currently implemented backend should be read as a float-based prototype path, not as an exact geometric kernel.

The current Python pipeline is:

1. `@rt.kernel` compiles Python syntax into an RT kernel IR.
2. `rt.lower_to_rayjoin(...)` lowers that IR into a RayJoin-oriented backend plan.
3. `rt.generate_optix_project(...)` emits OptiX/CUDA skeleton files for inspection and further backend work.
