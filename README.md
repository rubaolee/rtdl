# RTDL

RTDL is a research project for making non-graphics ray tracing programming substantially easier. The **whole-project goal** is to build a Python-hosted DSL and runtime/compiler stack for non-graphical, re-purposed RT-based applications across multiple underlying RT libraries, hardware targets, and software ecosystems.

The long-term backend picture includes:

- CPU RT libraries such as Intel Embree,
- NVIDIA OptiX / CUDA,
- AMD HIP RT,
- Intel RT hardware/software stacks,
- Apple RT ecosystems,
- Qualcomm/mobile RT ecosystems,
- and other practical RT backends over time.

The **current v0.1 goal** is narrower: prove that vision on one concrete application family, RayJoin-style workloads. Right now, this repository therefore focuses on a RayJoin-oriented vertical slice, using a Python-hosted DSL with a compiler IR underneath it: users stay in Python, describe geometry, traversal, refinement, and outputs, while the compiler and runtime handle BVH construction, ray formulation, payload packing, shader wiring, and backend-specific launch details.

This repository now contains:

- design notes for the first version of the project,
- a Python-hosted RT DSL prototype,
- an initial compiler IR for RT kernels,
- a RayJoin backend plan, OptiX/CUDA code generator, and now a controlled runnable OptiX runtime,
- multi-workload compiler coverage for `lsi`, `pip`, compositional `overlay`, `ray_tri_hitcount`, `segment_polygon_hitcount`, and `point_nearest_segment`,
- a Python dataset pipeline for RayJoin-style CDB inputs, and
- Python tests to keep the seed implementation executable.

Current status:

- Whole-project framing: multi-backend DSL for non-graphical RT applications.
- Current v0.1 framing: RayJoin-focused vertical slice.
- The Embree baseline is complete and checked in to this repository.
- Goal 13, "RayJoin paper reproduction on Embree," is canceled as superseded by Goal 15; its checklist, target matrix, dataset provenance note, and accepted Section 5.6 analogue remain valid reference artifacts.
- RayJoin Section 5.6 scalability is now supported as a scaled synthetic Embree analogue for `lsi` and `pip`, with generated Figure 13 / Figure 14 analogue artifacts and a dedicated report.
- Goal 15 is complete as an audited native C++ + Embree versus RTDL + Embree comparison slice for deterministic `lsi` and `pip` fixtures.
- Goal 18 is complete as the current low-overhead runtime continuation slice; `run_embree(..., result_mode="raw")` is now first-class and the packed/prepared Embree path covers all six current local Embree workloads.
- Goal 19 is now measured locally for `lsi` and `pip`: the ordinary dict-return path remains far slower than the current native wrapper baseline, while the raw and prepared-raw RTDL Embree paths are close to that baseline on matched deterministic and larger-profile runs.
- Goal 23 is complete as the current bounded Embree reproduction package: Figure 13 / Figure 14 bounded analogues, partial Table 3 bounded rows, Table 4 overlay-seed analogue, Figure 15 overlay speedup analogue, and a final report with explicit missing-family labeling.
- Goal 31 is complete as the current exact-source `lsi` correctness-restoration round: the broken local BVH candidate path was removed from active use, and the local `lsi` backend now closes the known Mac/Linux reproducers through an audited `native_loop` implementation.
- Goal 32 is complete as the current local `lsi` optimization follow-up: the Goal 31 brute-force `native_loop` was replaced with a parity-safe double-precision sort-sweep candidate pass, improving local native performance while keeping the same exact-source correctness boundary.
- Goal 40 is complete as the native C/C++ oracle replacement round: `run_cpu(...)` now routes through a native oracle while `run_cpu_python_reference(...)` preserves the old Python semantics for regression checks.
- Goal 41 is complete as the cross-host oracle correctness round: Python oracle, native oracle, and Embree match on small cases across Mac/Linux, and native oracle matches Embree on larger validated cases.
- Goal 43 is complete as the first OptiX GPU validation ladder on `192.168.1.20`; the current OptiX path is parity-clean across the bounded validation suite.
- Goal 44 is complete as the first bounded OptiX large-scale synthetic performance round, establishing a GPU baseline on the GTX 1070 host for deterministic PIP workloads.
- A checked-in status PDF summarizes the current RTDL state and the paper-reference figures used for the reproduction phase.

Current top-level interpretation:

- the project vision is broader than RayJoin and broader than Embree,
- but the current v0.1 slice is intentionally centered on RayJoin workloads,
- and the currently validated executable backends are Embree on this Mac and OptiX on the Linux GPU host `192.168.1.20`.

Current semantic/runtime boundaries:

- `point_in_polygon(..., boundary_mode="inclusive")` is the only supported PIP boundary mode in the audited baseline.
- `lsi`, `segment_polygon_hitcount`, and `point_nearest_segment` are valid RTDL workloads, but the current local backend lowers them to audited `native_loop` execution rather than BVH-backed traversal.
- Precision remains `float_approx`; RTDL does not yet claim robust or exact computational geometry.
- The current automated verification story is still local-only; this repo does not yet have a CI pipeline or a cross-platform test matrix.

Current execution-mode guidance:

- `run_embree(...)` returns Python dict rows and is the convenience path.
- `run_embree(..., result_mode="raw")` returns a thin native row view and is the main low-overhead path.
- `prepare_embree(kernel).bind(...).run_raw()` is the preferred repeated-execution path when performance matters.
- For the current matched `lsi` and `pip` comparisons, the raw and prepared-raw paths are close to the current native Embree wrapper baseline while the dict path is still much slower.
- That native baseline uses the same compiled Embree shared library as RTDL, so the measured gap is mainly Python/ctypes host-path overhead rather than two independent native geometry engines.
- In the current low-overhead slice, `lsi`, `segment_polygon_hitcount`, and `point_nearest_segment` still use audited `native_loop` execution rather than BVH-backed traversal.

Current OptiX/codegen caveat:

- The current local Embree runtime does not appear to silently truncate output rows.
- The controlled OptiX runtime is now real and GPU-validated on a GTX 1070 host, but the generated OptiX/CUDA skeleton path still carries an `output_capacity` plus `atomicAdd` overflow pattern that should not be treated as the trusted runtime path.

## Why RayJoin First

RayJoin is the right **first application target** for RTDL because it already proves that non-graphics workloads can benefit from RT cores, but it also exposes the current programming cost:

- developers still have to reason about OptiX program stages,
- problem formulation is expressed indirectly through rays and hit programs,
- precision handling is tightly coupled to backend details,
- BVH and launch configuration decisions leak into application logic, and
- debugging requires understanding CUDA, OptiX, and the application domain at once.

RTDL aims to raise the abstraction level without hiding the performance model.

So the intended hierarchy is:

- **whole project**: general DSL for non-graphical RT applications across many backends
- **v0.1**: first serious RayJoin-style vertical slice
- **current local phase**: Embree-backed baseline and reproduction work on this Mac

Current precision note:

- the implemented backend path is currently `float_approx`, not exact or robust geometric arithmetic,
- `precision="exact"` is intentionally rejected by the current RTDL lowering path,
- advanced precision work remains future roadmap work.

## Repository Layout

- `src/rtdsl/`: Python-hosted RT DSL prototype and IR.
- `apps/rtdsl_python_demo.py`: multi-workload RTDL and RayJoin-sample-data demo.
- `tests/rtdsl_py_test.py`: Python DSL regression test.
- `tests/fixtures/rayjoin/`: tiny CDB fixtures extracted from the public RayJoin sample data.
- `generated/`: emitted backend skeletons from the Python DSL pipeline.
- `docs/vision.md`: whole-project vision and how v0.1 fits inside it.
- `docs/rayjoin_target.md`: how RTDL maps onto RayJoin-specific concerns.
- `docs/v0_1_roadmap.md`: concrete scope and milestones for the first RTDL release.
- `docs/v0_1_final_plan.md`: staged plan for the RayJoin-focused v0.1 slice, from Embree baseline to final NVIDIA/OptiX completion.
- `docs/embree_baseline_plan.md`: step plan for the pre-GPU Embree baseline.
- `docs/embree_baseline_contracts.md`: frozen workload, ABI, precision, and dataset contracts for the Embree baseline.
- `docs/embree_evaluation_plan.md`: Goal 9 plan for reproducing the Embree baseline evaluation.
- `docs/embree_evaluation_matrix.md`: frozen evaluation matrix for the Embree reproduction phase.
- `docs/goal_13_rayjoin_paper_embree_plan.md`: preserved Goal 13 plan, now canceled as superseded by Goal 15 while retaining its completed artifacts.
- `docs/rayjoin_paper_reproduction_checklist.md`: checklist for re-testing RayJoin workloads through RTDL.
- `docs/rayjoin_paper_reproduction_matrix.md`: frozen paper-target matrix for Table 3 / Table 4 / Figure 13 / Figure 14 / Figure 15 analogues.
- `docs/rayjoin_paper_dataset_provenance.md`: provenance mapping for RayJoin paper datasets and RTDL substitutions.
- `docs/rtdl_feature_guide.md`: English overview of the currently supported RTDL feature surface and example kernels.
- `docs/development_reliability_process.md`: the review, revision, validation, and archival workflow used to keep RTDL reliable.
- `docs/ai_collaboration_workflow.md`: how Codex, Gemini, and Claude collaborate on goals, reviews, revisions, and closure decisions.
- `docs/reports/`: generated high-level Goal 9 evaluation summaries and PDF report snapshots.
- `docs/reports/rtdl_status_report_2026-03-31.pdf`: current project status PDF with RayJoin reference figures.
- `docs/reports/section_5_6_scalability_report_2026-03-31.md`: current Section 5.6 Embree analogue report.
- `docs/reports/section_5_6_scalability_report_2026-03-31.pdf`: PDF summary of the current Section 5.6 Embree analogue.
- `docs/reports/rtdl_embree_paper_report_2026-03-31.md`: paper-style consolidated report for the current Embree-phase reproduction effort.
- `docs/reports/rtdl_embree_paper_report_2026-03-31.pdf`: paper-style consolidated PDF with RTDL figures and corresponding RayJoin reference figures.
- `docs/goal_14_section_5_6_exact_scale_plan.md`: Goal 14 plan for five-minute local Section 5.6 profiles on the current Mac.
- `docs/reports/goal_14_section_5_6_exact_scale_estimation_2026-03-31.md`: exact-scale feasibility and runtime estimate for Section 5.6 on the current Mac.
- `docs/reports/goal15_cpp_embree_comparison_2026-03-31.md`: Goal 15 native C++ + Embree versus RTDL + Embree comparison report.
- `docs/reports/goal17_low_overhead_runtime_2026-03-31.md`: Goal 17 first low-overhead runtime slice report.
- `docs/goal_18_low_overhead_runtime_continuation.md`: Goal 18 plan for turning the low-overhead path into a more first-class runtime mode.
- `docs/reports/goal18_low_overhead_runtime_continuation_2026-04-01.md`: Goal 18 continuation report for raw-result mode and extended prepared/runtime coverage.
- `docs/goal_19_embree_performance_comparison_plan.md`: Goal 19 plan for RTDL vs pure C/C++ Embree performance comparison under a 5–10 minute local runtime budget.
- `docs/reports/goal19_embree_performance_comparison_2026-04-01.md`: Goal 19 report comparing RTDL dict/raw/prepared paths against native Embree for `lsi` and `pip`.
- `docs/runtime_overhead_architecture.md`: architecture note describing the current host-path overhead and the redesign target.
- `docs/embree_rayjoin_reproduction_program.md`: staged program for the current RayJoin-on-Embree reproduction effort.
- `docs/goal_21_rayjoin_matrix_dataset_setup.md`: Goal 21 setup and frozen matrix/provenance handoff.
- `docs/goal_21_rayjoin_matrix_dataset_frozen.md`: frozen paper-target matrix, bounded local profile policy, and Goal 22 blocker list.
- `docs/goal_22_rayjoin_gap_closure.md`: Goal 22 scope for dataset/provenance/reporting blockers ahead of bounded local runs.
- `docs/rayjoin_public_dataset_sources.md`: current public-source acquisition and bounded-preparation picture for the remaining RayJoin dataset families.
- `docs/goal_23_bounded_embree_reproduction.md`: Goal 23 scope for the executable bounded local reproduction slice.
- `docs/reports/goal23_embree_reproduction_report_2026-04-01.md`: final bounded Embree reproduction report for the current runnable RayJoin slice.
- `docs/reports/goal23_embree_reproduction_report_2026-04-01.pdf`: PDF version of the final bounded Embree reproduction report.
- `docs/rtdl/`: language reference, programming guide, cookbook, and LLM authoring guide.
- `examples/`: canonical language examples plus authored example programs.

## Build

Prepare the compiler/runtime workspace:

```sh
make build
```

Run the test suite:

```sh
make test
```

Run the stronger local verification package:

```sh
make verify
```

The default `build` and `test` targets do not require Embree. They validate the
current compiler surface and skip Embree-only checks automatically when Embree is
not installed.

Install Embree before using the native local backend:

```sh
brew install embree
```

Run the Python RTDL example:

```sh
make run-rtdsl-py
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

Generate the current project status PDF with RayJoin reference figures:

```sh
python3 scripts/generate_status_report_pdf.py
```

Run the default local Section 5.6 smoke analogue and generate the report plus Figure 13 / Figure 14 analogue SVGs:

```sh
make eval-section-5-6
```

Reproduce the checked-in 2026-03-31 published large LSI-only analogue report:

```sh
make eval-section-5-6-publish-2026-03-31
```

Generate the consolidated paper-style Embree report:

```sh
make report-rtdsl-paper
```

Generate the Goal 14 Section 5.6 estimation report and five-minute local profile recommendation:

```sh
make report-goal14-section-5-6-estimate
```

Run the Goal 15 native C++ + Embree versus RTDL + Embree comparison harness:

```sh
make run-goal15-compare
```

Run the Goal 17 low-overhead prepared Embree comparison harness:

```sh
PYTHONPATH=src:. python3 scripts/goal17_compare_prepared_embree.py
```

Run the Goal 18 low-overhead result-mode comparison harness:

```sh
make run-goal18-compare
```

Run the Goal 19 RTDL vs native Embree performance comparison harness:

```sh
make run-goal19-compare
```

Run the Goal 23 bounded Embree reproduction package:

```sh
make run-goal23-reproduction
```

If Embree or TBB live outside the default Homebrew prefixes, set:

```sh
export RTDL_EMBREE_PREFIX=/custom/embree/prefix
export RTDL_TBB_PREFIX=/custom/tbb/prefix
```

## Python Example

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
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

Current low-overhead runtime slice:

- `prepare_embree(kernel)` for compiled-once execution setup
- `run_embree(..., result_mode="raw")` for thin native row views from the main runtime entry point
- packed/prepared Embree coverage for:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`
  - `segment_polygon_hitcount`
  - `point_nearest_segment`
- packed native-ready helpers:
  - `pack_segments(...)`
  - `pack_points(...)`
  - `pack_polygons(...)`
  - `pack_rays(...)`
  - `pack_triangles(...)`
- `EmbreeRowView` as the thin raw-row result type

Current measured performance conclusion:

- the ordinary dict-return `run_embree(...)` path is still not performance-comparable to native C++ + Embree
- the first-class raw path and the prepared raw path are close to the current native wrapper baseline on the matched `lsi` and `pip` comparisons
- that native baseline uses the same compiled Embree shared library as RTDL, so the remaining gap is mainly Python/ctypes host overhead
- larger-profile Goal 19 comparison:
  - `lsi`: raw `0.98x` and prepared raw `0.89x` gap vs native
  - `pip`: raw `0.87x` and prepared raw `0.83x` gap vs native

Current dataset support in the prototype:

- parsing RayJoin-style CDB chain files,
- deriving segment, point-probe, and polygon-ref views in Python, and
- using tiny fixtures extracted from the public RayJoin sample data for non-GPU validation.

The current Python pipeline is:

1. `@rt.kernel` compiles Python syntax into an RT kernel IR.
2. `rt.lower_to_execution_plan(...)` lowers that IR into an RTDL backend plan for the current v0.1 slice.
3. `rt.generate_optix_project(...)` emits OptiX/CUDA skeleton files for inspection and backend experimentation.

RTDL now also has a local CPU execution path for the currently supported
workloads:

4. `rt.run_cpu(kernel_fn, **inputs)` executes the kernel through the Python
   host stack using the native C/C++ oracle semantics and returns result rows on non-GPU machines.

RTDL now also has a native local Embree execution path for the currently
supported workloads:

5. `rt.run_embree(kernel_fn, **inputs)` executes the kernel through an
   Embree-backed runtime and returns result rows on this Mac.

RTDL now also has a controlled OptiX execution path for the current workload
surface on the first NVIDIA host:

6. `rt.run_optix(kernel_fn, **inputs)` executes the kernel through the OptiX
   runtime on supported NVIDIA machines. The currently trusted bring-up path is
   the Linux GTX 1070 host `192.168.1.20` using the `nvcc` PTX fallback.

RTDL now also has a frozen Embree-baseline integration layer:

7. `python -m rtdsl.baseline_runner <workload>` runs a representative baseline
   workload case through CPU and/or Embree.
8. `python -m rtdsl.baseline_benchmark` records warmup-aware timing artifacts
   under `build/`.
9. `python -m rtdsl.baseline_summary <json>` prints a human-readable summary of
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
