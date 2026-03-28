# RTDL v0.1 Roadmap

## v0.1 Goal

RTDL v0.1 should be able to re-implement all RayJoin workloads through the new Python-hosted DSL and generated RayJoin-style backend path, without yet reproducing RayJoin's most advanced precision machinery such as 64-bit precision extension.

This means v0.1 is:

- an initial version of RayJoin through RTDL,
- functionally capable across the RayJoin workload surface,
- backend-driven through generated OptiX/CUDA code, and
- explicit about simplified precision limitations.

This does **not** mean v0.1 must already:

- match every optimization in the RayJoin paper,
- achieve the same strongest robustness guarantees,
- support all future RT workloads beyond RayJoin, or
- provide a fully mature production runtime.

## What v0.1 Should Deliver

At the end of v0.1, the system should provide:

- a Python-hosted DSL that can express every workload RayJoin supports,
- a compiler IR that represents those workloads cleanly,
- a RayJoin-oriented lowering path for each workload,
- generated OptiX/CUDA backend code for each workload,
- a runnable execution path for each workload, and
- validation against reference outputs on representative datasets.

The right interpretation is:

> RTDL v0.1 should cover the RayJoin workload family with a simplified precision model.

## v0.1 Precision Policy

The project should make this limitation explicit from the start:

- v0.1 does not attempt to reproduce RayJoin's precision extension to 64 bits,
- v0.1 may use float-based or otherwise simplified precision handling,
- v0.1 must document where the simplified model is acceptable, and
- v0.1 must identify numerical edge cases that are deferred to later releases.

So the promise of v0.1 is **workload coverage**, not **full numerical parity with the research paper**.

## Scope Breakdown

### In Scope

- all RayJoin workloads at the query level,
- Python DSL support for those workloads,
- IR support for those workloads,
- RayJoin-specific lowering logic,
- generated backend code for those workloads,
- end-to-end execution for those workloads,
- correctness validation on representative inputs.

### Out of Scope

- advanced precision extension mechanisms,
- fully generalized multi-backend support,
- full optimization parity with handwritten RayJoin,
- comprehensive performance tuning beyond functional viability,
- research-complete robustness guarantees.

## Required Workstreams

### 1. Workload Enumeration

The first requirement is to create a precise list of RayJoin workloads and pin down:

- input geometry types,
- output schemas,
- semantics,
- expected candidate-generation behavior, and
- expected refinement behavior.

Without this list, v0.1 scope is too ambiguous to implement or test.

### 2. DSL Surface Expansion

The Python API must move beyond the current single segment-join path and support:

- each RayJoin workload family,
- richer predicate descriptions,
- more geometry kinds,
- configurable output policies, and
- reusable workload templates.

The frontend should stay compact, but it must no longer be effectively hard-coded to one example.

### 3. IR Generalization

The IR needs to become the stable semantic core for v0.1. It must represent:

- geometry roles,
- layouts,
- traversal strategy,
- predicate family,
- refinement mode,
- emit schema,
- precision mode,
- batching or scheduling hints when needed.

This is the main boundary that will keep the DSL from collapsing into backend-specific templates.

### 4. Backend Lowering Coverage

For each RayJoin workload, add a lowering path that decides:

- build side vs probe side,
- acceleration structure strategy,
- payload contract,
- launch parameter schema,
- ray formulation,
- refinement stage, and
- output materialization.

The existing segment path is the seed pattern for this work.

### 5. Real Runtime Integration

The generated host/device skeletons must be connected to a real execution path:

- OptiX module creation,
- program group creation,
- shader binding table setup,
- launch parameter upload,
- BVH build,
- kernel launch,
- output retrieval.

Until this exists, the compiler is only partially complete.

### 6. Validation Harness

For each workload, prepare:

- input datasets,
- expected outputs or trusted baselines,
- automated correctness checks,
- clear statements of allowed precision limitations.

Validation must become part of the definition of v0.1, not an afterthought.

## Recommended Milestones

### Milestone A: Scope Freeze

Deliverables:

- explicit list of RayJoin workloads,
- per-workload semantics notes,
- v0.1 precision policy note.

Success condition:

- no ambiguity remains about what v0.1 must support.

### Milestone B: Frontend and IR Coverage

Deliverables:

- Python DSL constructs for all RayJoin workloads,
- generalized IR to represent them.

Success condition:

- every RayJoin workload can be expressed at the RTDL source level and compiled into IR.

### Milestone C: Lowering and Codegen Coverage

Deliverables:

- backend lowering for every RayJoin workload,
- generated host/device artifacts for each one.

Success condition:

- every supported workload produces a backend plan and emitted code.

### Milestone D: Runtime Execution

Deliverables:

- real OptiX/CUDA execution path wired to generated artifacts.

Success condition:

- generated workloads actually run, not just compile into skeletons.

### Milestone E: Validation and Positioning

Deliverables:

- correctness suite,
- representative datasets,
- precision limitations document,
- baseline comparisons.

Success condition:

- RTDL v0.1 is defensible as an initial RayJoin re-implementation through DSL and code generation.

## Success Criteria

RTDL v0.1 is complete when:

- each RayJoin workload can be written in RTDL,
- each workload lowers into a RayJoin-oriented backend plan,
- each workload generates backend code,
- each workload can execute through the runtime path,
- outputs are functionally correct on representative test cases, and
- precision limitations are documented honestly and explicitly.

## Immediate Next Steps

The next concrete sequence should be:

1. enumerate all RayJoin workloads and write them down in this repository,
2. map each workload to the DSL and IR concepts that are still missing,
3. prioritize them in implementation order,
4. build the next workload after segment join,
5. begin wiring the generated backend to a real OptiX execution path.

## Positioning Statement

The right way to describe v0.1 is:

> RTDL v0.1 re-implements the RayJoin workload surface through a Python-hosted DSL and generated RayJoin-style backend, using a simplified precision model.

That framing is ambitious enough to matter, but constrained enough to execute.
