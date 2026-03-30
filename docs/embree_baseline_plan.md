# Embree Baseline Plan

## Goal

The Embree baseline goal is to make RTDL a complete executable system on this Mac for the current RayJoin-aligned workload surface.

That means:

- `rt.run_cpu(...)` remains the semantic reference runtime,
- `rt.run_embree(...)` is the real native backend runtime,
- the workload, dataset, and ABI contracts are stable enough to carry forward into the future OptiX backend.

This is the pre-GPU foundation for RTDL v0.1.

## Baseline Scope

The current baseline workload scope is:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`

These workloads should all be:

- expressible in RTDL,
- runnable through `run_cpu(...)`,
- runnable through `run_embree(...)`,
- testable on shared inputs,
- documented for human and agent authoring.

## Steps

### 1. Freeze the baseline workload scope

Decide and record the exact workload set required for the Embree baseline.

Current proposed scope:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`

Success condition:

- the baseline workload set is explicit and no longer ambiguous.

### 2. Freeze the input and output contracts

For each workload, lock:

- geometry types,
- required record fields,
- layout expectations,
- emitted record schema,
- allowed precision mode,
- result interpretation.

Success condition:

- every baseline workload has a stable contract visible in code and docs.

### 3. Freeze the runtime ABI

Make sure normalized records, IDs, roles, and output mapping are consistent across:

- `run_cpu(...)`,
- `run_embree(...)`,
- future OptiX backend work.

Success condition:

- there is one shared execution contract instead of backend-specific ad hoc behavior.

### 4. Finish CPU vs Embree correctness coverage

For every baseline workload, add or strengthen tests that compare:

- CPU results,
- Embree results,
- identical inputs.

Success condition:

- backend agreement is covered by automated tests on representative cases.

### 5. Expand dataset coverage

Move beyond tiny fixtures where needed and prepare representative RayJoin-aligned datasets for:

- local validation,
- local benchmarking,
- future OptiX reuse.

Success condition:

- the dataset path is stable and useful beyond unit-sized examples.

### 6. Build the baseline benchmark harness

Add scripts that can:

- run workloads repeatedly,
- record timings,
- save raw results,
- label backend, workload, dataset, and configuration.

Success condition:

- the Embree baseline can be measured reproducibly.

### 7. Add reproducible workload runners

Each workload should have a clean runnable entry point for:

- authored examples,
- fixture-based runs,
- benchmark runs.

Success condition:

- a contributor can execute each workload without reverse-engineering the repo.

### 8. Tighten documentation

Document:

- how to write RTDL kernels,
- how to run CPU and Embree backends,
- what is guaranteed,
- what is still approximate,
- what belongs to the baseline versus the future OptiX phase.

Success condition:

- the baseline is teachable and operationally clear.

### 9. Validate authored programs

Continue checking that:

- humans can write valid RTDL kernels,
- Codex can write valid RTDL kernels,
- Gemini can write valid RTDL kernels,
- those programs can execute through Embree.

Success condition:

- the language is usable in practice, not just internally by the repo authors.

### 10. Archive and lock the baseline

When the above steps are complete:

- update history,
- define the Embree baseline as the locked pre-GPU foundation,
- treat later OptiX work as backend expansion rather than language redesign.

Success condition:

- the project has a stable baseline before NVIDIA bring-up begins.

## Recommended Execution Order

1. freeze workload and ABI contracts
2. strengthen CPU vs Embree tests
3. add benchmark harness
4. enlarge dataset coverage
5. improve examples and docs
6. declare baseline complete

## Acceptance Criteria

The Embree baseline is complete when:

- all baseline workloads run through `run_cpu(...)`,
- all baseline workloads run through `run_embree(...)`,
- CPU and Embree agree on representative inputs,
- dataset handling is stable,
- examples and docs are usable,
- local benchmarking infrastructure exists.

## Relationship To The Final v0.1 Goal

The Embree baseline is not the final project goal.

The final v0.1 goal remains:

- RTDL workloads running on NVIDIA RT cores through OptiX/CUDA,
- plus reproduction of the RayJoin paper's benchmark and figure workflow.

The Embree baseline exists so that the language, runtime contract, datasets, and validation story are already mature before OptiX bring-up.
