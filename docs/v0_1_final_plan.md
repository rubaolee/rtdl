# RTDL v0.1 Final Plan

## Purpose

This document separates the project into two layers of goals:

- a **baseline Embree goal** that can be completed before NVIDIA hardware is available, and
- a **final NVIDIA/OptiX goal** that defines RTDL v0.1 completion.

The reason for this split is practical: the Embree path is the staging ground for the final RayJoin-on-RT-cores result.

## Final v0.1 Goal

RTDL v0.1 should be able to express selected RayJoin workloads in the DSL, lower them into a real OptiX/CUDA backend, run them on NVIDIA RT cores, and regenerate the performance-figure workflow from the RayJoin paper.

The reproduced figures do not need to match the paper numerically. The requirement is to regenerate the same style of experiment structure:

- same workload families,
- same or equivalent datasets,
- same measurement categories,
- same comparison layout,
- same figure-generation workflow.

In short:

> RTDL v0.1 should execute RayJoin-style workloads on NVIDIA RT cores and reproduce the paper's benchmark/figure pipeline with RTDL-generated implementations.

## Baseline Goal Before NVIDIA Hardware

Before the NVIDIA machine is available, RTDL should become a complete executable system on top of Embree.

That baseline goal is:

> RTDL should support the current RayJoin-aligned workload surface through the DSL, IR, dataset pipeline, CPU reference runtime, and Embree backend, with correctness checks and a benchmarkable harness.

This baseline is not a side project. It is the precondition for a stable OptiX bring-up.

## Current Progress Snapshot

As of March 31, 2026:

- the Embree baseline is complete and published,
- the current RTDL feature surface includes six executable workload families,
- the first Embree evaluation report has already been generated,
- and the active next layer is Goal 13: reproducing as much of the RayJoin paper structure as possible on the Embree baseline before NVIDIA hardware is available.

Goal 13 is explicitly an Embree-phase reproduction effort. It should be read as:

- a workload-and-dataset expansion of the current local baseline,
- not the final OptiX/RT-core reproduction,
- and not a claim that all paper datasets are already ingested.

## Why the Embree Baseline Matters

- It proves RTDL is more than a frontend sketch.
- It forces stable input/layout/output contracts.
- It gives the project a real native backend before GPU-specific debugging begins.
- It provides a correctness cross-check against future OptiX execution.
- It lets the benchmark harness, dataset flow, and workload semantics mature early.

## Goal Structure

### Goal A: Embree Baseline

RTDL should run the selected workload surface locally through:

- `rt.run_cpu(...)` as semantic reference,
- `rt.run_embree(...)` as real native backend execution,
- shared workload and dataset contracts,
- shared output schemas,
- shared validation rules.

### Goal B: NVIDIA Finalization

RTDL should then add:

- real OptiX runtime execution,
- generated host/device integration,
- RT-core execution on NVIDIA hardware,
- benchmark automation,
- figure regeneration.

## What the Embree Baseline Must Deliver

The Embree baseline should deliver the following before NVIDIA bring-up:

1. Stable workload surface
   RTDL can express the selected v0.1 workload set with documented source-level patterns.

2. Stable IR and lowering boundary
   Each workload compiles into a well-defined IR and lowering contract.

3. Stable dataset pipeline
   The project can load representative RayJoin-aligned datasets and normalize them for execution.

4. Stable runtime ABI
   Layouts, IDs, geometry roles, and emitted records are frozen enough to reuse in OptiX.

5. CPU vs Embree correctness checks
   Each supported workload has automated comparison between `run_cpu(...)` and `run_embree(...)`.

6. Local benchmark harness
   The repository can run repeatable local measurements on the Embree backend even if those numbers are not part of the final paper reproduction.

7. Documentation and examples
   Human and agent users can write RTDL programs and understand the supported execution modes.

## What the Final NVIDIA Goal Must Deliver

After the hardware is available, the final phase should deliver:

1. Real OptiX runtime integration
   Replace the current skeleton-only path with a runnable generated backend.

2. Workload execution on NVIDIA RT cores
   Execute the target RTDL workloads through OptiX/CUDA on the cloud GPU machine.

3. Correctness validation
   Cross-check GPU results against `run_cpu(...)` and, where appropriate, `run_embree(...)`.

4. Benchmark harness
   A stable scriptable pipeline for running workload/dataset experiments and saving results.

5. Figure regeneration
   Scripts that regenerate the selected RayJoin paper figures from fresh benchmark outputs.

6. Final packaging
   Docs, commands, plots, and limitations needed to present RTDL v0.1 clearly.

## Dependency Order

The dependency order should be explicit:

1. Finish the Embree baseline.
2. Freeze the workload and dataset scope for v0.1.
3. Freeze the runtime ABI shared by Embree and OptiX.
4. Bring up the first real OptiX workload on NVIDIA.
5. Validate correctness against CPU and Embree.
6. Expand to the full in-scope workload set.
7. Run benchmarks and regenerate figures.

This ordering matters because backend debugging is much easier once the language and runtime contracts are already stable.

## Suggested Phases

### Phase 1: Complete Embree Baseline

Deliverables:

- all selected pre-GPU workloads runnable on CPU and Embree,
- correctness comparisons,
- local benchmark scripts,
- stable docs and examples.

Success condition:

- RTDL is a reliable executable system before any NVIDIA-specific work starts.

### Phase 2: Freeze Final v0.1 Scope

Deliverables:

- selected RayJoin workloads,
- selected datasets,
- selected figures to regenerate,
- explicit out-of-scope items.

Success condition:

- no ambiguity remains about what counts as v0.1 completion.

### Phase 3: First OptiX Bring-Up

Deliverables:

- one workload running end to end through generated OptiX/CUDA code.

Success condition:

- RTDL executes one real workload on NVIDIA RT cores.

### Phase 4: Full Workload Coverage on NVIDIA

Deliverables:

- all in-scope workloads executable on the NVIDIA backend.

Success condition:

- RTDL covers the selected RayJoin workload set on RT cores.

### Phase 5: Benchmark and Figure Reproduction

Deliverables:

- raw benchmark outputs,
- plotting scripts,
- regenerated figure set.

Success condition:

- the RayJoin paper's experiment structure has been reproduced with RTDL-generated implementations.

## Acceptance Criteria

### Embree Baseline Acceptance

The baseline is complete when:

- the selected workload set executes through `run_cpu(...)`,
- the same workload set executes through `run_embree(...)`,
- dataset loading and normalization are stable,
- tests cover correctness on representative inputs,
- docs explain how to author and run the workloads.

### Final v0.1 Acceptance

v0.1 is complete when:

- the selected workload set executes through the NVIDIA/OptiX backend,
- the benchmark harness runs the selected datasets,
- figure-generation scripts reproduce the selected paper-style plots,
- results and limitations are documented honestly.

## Immediate Next Steps

Before the NVIDIA machine arrives:

1. finish the Embree baseline as the main active goal,
2. choose the exact workload and figure scope for final v0.1,
3. make the benchmark harness and dataset pipeline reusable across backends,
4. lock the runtime ABI that OptiX will inherit.

When the NVIDIA machine is ready:

1. install CUDA/OptiX toolchain,
2. run the first generated OptiX workload,
3. compare outputs against CPU and Embree,
4. expand to the remaining in-scope workloads,
5. regenerate figures.

## Positioning Statement

The clearest way to describe the project now is:

> RTDL is currently in an Embree-backed baseline phase. The final v0.1 milestone is RayJoin-style execution on NVIDIA RT cores with paper-style benchmark figure regeneration.
