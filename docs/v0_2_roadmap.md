# RTDL v0.2 Roadmap

Date: 2026-04-05
Status: proposed

## v0.2 goal

RTDL v0.2 should move from a bounded RayJoin-centered research release toward a
broader programmable system with clearer product value.

That means v0.2 should not merely add more reports. It should expand what RTDL
can *usefully* do while keeping the project technically honest.

## Primary user and workflow

The primary v0.2 user is:

- an advanced technical user, research engineer, or systems programmer who
  wants to express one non-graphical ray-tracing workload without first
  hand-writing separate backend-specific implementations

The primary workflow is:

- define one kernel once
- run it or generate a starter implementation
- keep backend and correctness boundaries explicit

## Release-defining bet

v0.2 should have one release-defining bet:

- **new-workload-first**

That means the first hard proof for v0.2 is:

- RTDL closes one additional workload family beyond the v0.1 RayJoin-centered
  slice

Everything else is secondary unless it clearly strengthens that proof.

## Two primary pillars plus one supporting track

### 1. Broader workload support

v0.1 proved the project on a RayJoin-heavy slice. v0.2 should broaden RTDL’s
scope, but only across workload families that still fit RTDL’s strengths.

Proposed v0.2 workload groups:

- **Core spatial workload expansion**
  - stronger `lsi`
  - broader distance/filter workloads
  - more candidate-generation + exact-refine workflows
- **Programmable ray-query kernels**
  - ray/path/filter/count workloads beyond joins
  - small graph/geometric counting kernels
  - rank/count style kernels like the sorting demo
- **Keep out of core scope for now**
  - full exact overlay materialization
  - broad distributed execution
  - native AMD/Intel GPU backends without hardware access

### 2. Pure code-generation mode

RTDL v0.2 should support a mode where RTDL generates runnable code without
executing it locally.

This mode is **gated**, not co-equal with workload expansion.

This mode should begin with one constrained MVP that outputs:

- RTDL kernel source
- driver/main program
- one accepted emitted target shape
- a verification stub or golden-example harness

Only after that MVP proves non-toy value should RTDL claim a real second
product surface:

- **execute mode**
- **generate-only mode**

### Supporting track: performance maturation on real RT cores

v0.2 should continue performance work where real evidence is currently possible.

Primary priorities:

1. OptiX / NVIDIA RT cores
2. Embree as strong CPU baseline and production-quality fallback
3. Vulkan as correctness/portability backend

Explicitly deferred for now:

- native AMD GPU backend work without AMD hardware
- native Intel GPU backend work without Intel GPU hardware

## Hard gates and kill criteria

### Gate A: scope discipline

No workload-expansion goal counts unless Goal 108 explicitly classifies it as:

- in scope
- experimental
- out of scope

### Gate B: codegen usefulness

Generate-only mode should be cut or paused if:

- the output is not runnable with a clear handoff contract
- the output is only boilerplate with weak RTDL-specific value
- the verification harness cannot show real user value

### Gate C: performance containment

Performance work should not define v0.2 unless:

- it supports the chosen new workload family directly, or
- it removes a release-blocking runtime limitation

## First-wave v0.2 goals

Recommended order:

### Goal 108: v0.2 workload scope charter

Produce a formal in-scope / experimental / out-of-scope table for RTDL v0.2.

### Goal 109: generate-only mode MVP

Support a first end-to-end generate-only path for one accepted RTDL kernel
family, but only as a constrained experiment with a clear success/failure
decision.

### Goal 110: new workload family closure

Take one additional non-join or non-RayJoin-heavy workload family and close it
with:

- execution
- correctness check
- docs/example

This is the release-defining proof and should not be subordinated to codegen.

### Goal 111: narrow generate-only MVP

Close one narrow generate-only product test and decide whether it is worth
keeping.

### Goal 112: OptiX/Embree performance maturation

Push broader workload performance on real accepted surfaces, especially:

- cold-start behavior
- less manual fast-path dependence
- broader workload competitiveness

### Goal 113: generate-only maturation

If Goal 111 survives, strengthen it carefully without letting it expand into
shallow template sprawl.

## Recommended execution choice

If v0.2 has to choose one aggressive bet, it should choose:

- **new-workload-first**

Codegen should remain a constrained secondary bet until it proves clear user
value.

## What v0.2 should not become

v0.2 should not turn into:

- a vague “support everything” roadmap
- a paper-writing treadmill with weak technical movement
- an AMD/Intel backend promise without hardware access
- a code generator that emits unverified fantasy code

## Success criteria

v0.2 is promising only if it can show all of the following:

- RTDL is useful beyond the narrow RayJoin slice
- generated code is either proven useful or explicitly cut back
- the strongest performance path keeps improving on real hardware
- scope remains disciplined enough that results are believable
