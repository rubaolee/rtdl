# Goal2037 v2.0 Embree CPU Partner All-Thread Plan

Date: 2026-05-14

Status: proposed-for-review, then implementation/test.

## Purpose

The next v2.0 goal is to fully test the Embree engine on local Linux using all available CPU threads. This is the CPU sibling of the OptiX+CuPy pod evidence: Embree remains the app-agnostic native candidate producer, while the v2 partner continuation runs in CPU memory instead of GPU memory.

This goal exists because v2.0 must not be understood as "only NVIDIA GPU." If the user runs Embree, the architecture should still be Python+partner+RTDL:

- Native engine: Embree, CPU ray/candidate traversal.
- Partner layer: NumPy or Torch-CPU first; Numba-CPU when custom scalar loops dominate.
- Memory target: host zero-copy or minimal-copy host array handoff.
- Thread target: all available CPU cores, with thread counts recorded.

## Architecture Decision

For Embree v2.0, the default partner stack should be:

1. **NumPy** for vectorized reductions, grouping, masks, and summary outputs.
2. **Torch-CPU** when API parity with Torch-GPU matters.
3. **Numba-CPU** for user-defined continuation kernels that would otherwise become slow Python loops.
4. **Python C extension** only as an interoperability demonstration, not the default RTDL partner path.

Rationale:

- CuPy RawKernel is the right GPU continuation escape hatch, but it is not useful on CPU-only Embree machines.
- A C extension proves Python can call arbitrary native code, but it weakens the v2.0 teaching story if used as the primary Embree answer.
- Numba keeps the "Python-authored compiled continuation" story without moving app customization into the RTDL native engine.
- NumPy/Torch-CPU provide the cleanest first proof for data-science users and are easiest to audit for correctness.

## Required Evidence

Goal2037 should produce a local Linux artifact packet containing:

- CPU model, core/thread count, OS, Python version, NumPy/Torch/Numba availability.
- Embree library build/probe status.
- Environment thread settings:
  - `OMP_NUM_THREADS`
  - `TBB_NUM_THREADS`
  - `MKL_NUM_THREADS`
  - `OPENBLAS_NUM_THREADS`
  - `NUMEXPR_NUM_THREADS`
  - `RTDL_EMBREE_THREADS` if supported by the local runtime.
- A full app matrix covering the same v2.0 rows used in the all-app comparison.
- For each app:
  - v1.8 Python+RTDL/Embree baseline where available.
  - v2.0 Embree+CPU-partner row.
  - correctness parity or explicit reason parity is not applicable.
  - wall-clock timing with repeats, medians, min, max.
  - note whether continuation is NumPy, Torch-CPU, Numba-CPU, or legacy Python fallback.

## App Continuation Policy

| App family | Embree v2.0 CPU partner target | Notes |
| --- | --- | --- |
| Fixed-radius threshold rows | NumPy or Torch-CPU threshold/count reductions | Covers service coverage, hotspots, facility threshold, Hausdorff threshold proxy, ANN coverage, outlier, DBSCAN core, Barnes-Hut node coverage. |
| Segment/polygon count/flag rows | NumPy grouped counts over generic witness pairs | Avoid Python row loops when output is compact. |
| Segment/polygon any-hit row materialization | NumPy compact row arrays; bounded output policy required | May remain slower when the app really needs materialized rows. |
| Database analytics | NumPy columnar predicates and grouped reductions; Numba if loops remain | Do not put DB semantics back into Embree. |
| Graph analytics | NumPy/Numba graph continuation | Current GPU v2 graph row is closed-form for the authored app; Embree CPU testing should expose whether a reusable graph primitive is still missing. |
| Polygon exact metrics | NumPy tiled candidate continuation first; Numba optional for exact loops | CPU equivalent of Goal2032 bounded candidate lesson. |
| Robot collision | NumPy compact flags/counts from generic any-hit rows | Full pose flag parity is required. |

## Threading Policy

The local Linux run must use all available threads unless the runner records a reason not to. The test harness should:

1. Detect logical CPU count with `nproc`.
2. Export thread environment variables to that count.
3. Print progress before every app row and every repeat.
4. Use per-row timeouts.
5. Save partial artifacts even when a row fails or times out.

This is important because silent long-running tests are not acceptable for this project.

## Claim Boundaries

This goal may claim:

- Embree v2.0 CPU-partner evidence exists for tested rows.
- Host-side partner continuation works without GPU/CuPy.
- All-thread local Linux testing was attempted and recorded.

This goal must not claim without further evidence:

- v2.0 release readiness.
- True host zero-copy for every Embree row.
- Broad all-app speedup over v1.8.
- Equivalence between CPU Embree and GPU OptiX performance.
- Triton/Numba first-class public backend support.

## Relationship To Goal2025 And Goal2026

Goal2025 proposes Triton/Numba as future user-select partners. Goal2037 uses only the safe subset needed now: Numba-CPU may be used as an implementation technique for CPU continuation, but Triton/Numba should not become a v2.0 release requirement.

Goal2026 describes the desired Embree CPU partner architecture. Goal2037 converts that Q&A into testable evidence: it must verify whether the current code actually uses host arrays efficiently, and it must mark any copied or Python-loop fallback honestly.

## Immediate Execution Plan

1. Write a local Linux runner for Embree+CPU-partner all-app testing with progress logging and per-row timeouts.
2. Start with a smoke scale to validate dependencies and parity.
3. Increase to order-of-seconds rows where feasible.
4. Produce a JSON+Markdown evidence report.
5. Seek at least one external AI review before treating this as accepted v2.0 evidence.

## Initial Verdict

`needs-implementation`

The architecture is sound, but the release-relevant question is empirical: which rows already have a true CPU partner continuation, which are still Python fallback, and where Embree all-thread performance is actually useful.
