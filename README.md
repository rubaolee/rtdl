# RTDL

RTDL is a research project for making non-graphics ray tracing programming substantially easier. The initial target is RayJoin, an OptiX/CUDA system for spatial joins on NVIDIA RT cores. The project is now framed as a Python-hosted DSL with a compiler IR underneath it: users stay in Python, describe geometry, traversal, refinement, and outputs, while the compiler and runtime handle BVH construction, ray formulation, payload packing, shader wiring, and backend-specific launch details.

This repository now contains:

- design notes for the first version of the project,
- a Python-hosted RT DSL prototype,
- an initial compiler IR for RT kernels,
- a RayJoin backend plan and OptiX/CUDA skeleton generator,
- multi-workload compiler coverage for `lsi`, `pip`, compositional `overlay`, and 2D ray-vs-triangle hit counts,
- a Python dataset pipeline for RayJoin-style CDB inputs, and
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
- `apps/rtdsl_python_demo.py`: multi-workload RTDL and RayJoin-sample-data demo.
- `tests/rtdsl_py_test.py`: Python DSL regression test.
- `tests/fixtures/rayjoin/`: tiny CDB fixtures extracted from the public RayJoin sample data.
- `generated/`: emitted backend skeletons from the Python DSL pipeline.
- `docs/vision.md`: project scope and research framing.
- `docs/rayjoin_target.md`: how RTDL maps onto RayJoin-specific concerns.
- `docs/v0_1_roadmap.md`: concrete scope and milestones for the first RTDL release.
- `docs/v0_1_final_plan.md`: staged plan from Embree baseline to final NVIDIA/OptiX v0.1 completion.
- `docs/embree_baseline_plan.md`: step plan for the pre-GPU Embree baseline.
- `docs/embree_baseline_contracts.md`: frozen workload, ABI, precision, and dataset contracts for the Embree baseline.
- `docs/embree_evaluation_plan.md`: Goal 9 plan for reproducing the Embree baseline evaluation.
- `docs/embree_evaluation_matrix.md`: frozen evaluation matrix for the Embree reproduction phase.
- `docs/reports/`: generated high-level Goal 9 evaluation summaries and PDF report snapshots.
- `docs/rtdl/`: language reference, programming guide, cookbook, and LLM authoring guide.
- `examples/`: canonical language examples plus authored example programs.

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

Run the local CPU simulator demo:

```sh
make run-rtdsl-sim
```

Run the Embree backend demo:

```sh
make run-rtdsl-embree
```

Run the frozen Embree baseline workloads through both CPU and Embree:

```sh
make run-rtdsl-baseline
```

Run the local Embree baseline benchmark harness and summary:

```sh
make bench-rtdsl-baseline
```

Run the Embree evaluation pipeline and generate tables, figures, and the PDF report:

```sh
make eval-rtdsl-embree
```

Embree setup on this Mac:

```sh
brew install embree
```

If Embree or TBB live outside the default Homebrew prefixes, set:

```sh
export RTDL_EMBREE_PREFIX=/custom/embree/prefix
export RTDL_TBB_PREFIX=/custom/tbb/prefix
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

Current workload coverage in the prototype:

- `lsi`: segment-vs-segment intersection
- `pip`: point-in-polygon as a workload-specific backend skeleton
- `overlay`: compositional overlay seed generation over polygon inputs
- `ray_tri_hitcount`: finite 2D rays against triangles with per-ray hit counts
- `segment_polygon_hitcount`: per-segment polygon hit counts
- `point_nearest_segment`: nearest segment id plus distance per point

Current dataset support in the prototype:

- parsing RayJoin-style CDB chain files,
- deriving segment, point-probe, and polygon-ref views in Python, and
- using tiny fixtures extracted from the public RayJoin sample data for non-GPU validation.

The current Python pipeline is:

1. `@rt.kernel` compiles Python syntax into an RT kernel IR.
2. `rt.lower_to_rayjoin(...)` lowers that IR into a RayJoin-oriented backend plan.
3. `rt.generate_optix_project(...)` emits OptiX/CUDA skeleton files for inspection and further backend work.

RTDL now also has a local CPU execution path for the currently supported
workloads:

4. `rt.run_cpu(kernel_fn, **inputs)` executes the kernel through the Python
   reference semantics and returns result rows on non-GPU machines.

RTDL now also has a native local Embree execution path for the currently
supported workloads:

5. `rt.run_embree(kernel_fn, **inputs)` executes the kernel through an
   Embree-backed runtime and returns result rows on this Mac.

RTDL now also has a frozen Embree-baseline integration layer:

6. `python -m rtdsl.baseline_runner <workload>` runs a representative baseline
   workload case through CPU and/or Embree.
7. `python -m rtdsl.baseline_benchmark` records warmup-aware timing artifacts
   under `build/`.
8. `python -m rtdsl.baseline_summary <json>` prints a human-readable summary of
   those benchmark results.

## Language Docs

RTDL now has a language-facing docs set for the currently implemented surface:

- `docs/rtdl/dsl_reference.md`
- `docs/rtdl/programming_guide.md`
- `docs/rtdl/workload_cookbook.md`
- `docs/rtdl/llm_authoring_guide.md`

These documents describe the supported RTDL language for the current six
workloads and are intended to be strong enough for both human and agent authoring.

## Example Library

The repository now keeps authored RTDL programs under `examples/`:

- `examples/rtdl_language_reference.py`: canonical reference kernels
- `examples/rtdl_codex_authored.py`: Codex-authored kernels
- `examples/rtdl_gemini_authored.py`: Gemini-authored kernels
- `examples/rtdl_ray_tri_hitcount.py`: canonical ray-query kernel plus random-data helpers
- `examples/rtdl_goal10_reference.py`: Goal 10 reference kernels for mixed-geometry hit counts and nearest-segment queries
- `examples/rtdl_codex_ray_query.py`: Codex-authored ray-query kernel
- `examples/rtdl_simulator_demo.py`: local CPU execution demo using `rt.run_cpu(...)`
- `examples/rtdl_embree_demo.py`: local native execution demo using `rt.run_embree(...)`

Additional agent-authored kernels can be validated against the same compiler path.
