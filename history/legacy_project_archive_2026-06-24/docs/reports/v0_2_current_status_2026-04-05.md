# RTDL v0.2 Current Status

Date: 2026-04-05
Author: Codex
Status: current snapshot after Goals 107-113

## Executive summary

RTDL v0.2 has started in a disciplined way.

The project is no longer at the roadmap-only stage. It now has:

- a published v0.2 roadmap
- a published workload scope charter
- a frozen archived v0.1 baseline
- one closed new workload family
- one closed narrow generate-only MVP
- one defined next-step maturation goal for the generate-only feature

That means v0.2 has already moved beyond planning-only work and into real
technical movement, but still at an early stage.

## What is closed

### Goal 107: v0.2 roadmap

Published planning layer.

What it established:

- v0.2 is workload-first
- code generation is secondary and gated
- performance is a supporting track, not the release identity

### Goal 108: workload scope charter

Published planning layer.

What it established:

- only one family was allowed to define the first v0.2 expansion
- additional spatial filter/refine workloads were the single in-scope family
- novelty-demo sprawl was explicitly blocked

### Goal 109: archive v0.1 baseline

Closed and published.

What it established:

- v0.1 is frozen at tag `v0.1.0`
- users have a stable archived baseline while `main` moves into v0.2

### Goal 110: `segment_polygon_hitcount`

Closed and published.

What it established:

- first closed v0.2 workload family beyond the RayJoin-heavy v0.1 slice
- parity-clean on accepted authored, fixture-backed, and derived cases across:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
- prepared-path checks included for Embree and OptiX on authored and fixture
  cases

Important honesty boundary:

- Goal 110 closed as:
  - workload-family closure
  - semantic/backend closure
- it did **not** claim RT-backed maturity for this family
- the accepted package remains explicit that this family still sits under the
  current audited `native_loop` honesty boundary

### Goal 111: narrow generate-only MVP

Closed and published.

What it established:

- one structured request contract
- one runnable RTDL Python file generated from that request
- verification built into the generated artifact
- accepted seed family:
  - `segment_polygon_hitcount`

Important honesty boundary:

- Goal 111 closed as a narrow kept MVP
- it did **not** prove broad general code generation
- it remains a constrained second bet, not a co-equal v0.2 pillar

### Goal 113: generate-only maturation

Defined and published.

What it established:

- the generate-only feature should continue only through controlled
  improvement, not shallow template sprawl
- the next step is feature strengthening, not unconstrained expansion

## What v0.2 currently means

At this moment, v0.2 means:

1. RTDL has moved beyond pure RayJoin-centered closure work
2. RTDL has already closed one additional workload family
3. RTDL has already closed one narrow generate-only mode that is worth keeping
   under tight control
4. RTDL still maintains explicit honesty boundaries instead of inflating claims

So the project is in a credible early-v0.2 state:

- enough real movement to justify the roadmap
- still disciplined enough to remain believable

## Current strengths

- scope discipline is strong
- v0.1 remains safely archived
- one real workload-family expansion is already closed
- one narrow product-mode experiment is already closed
- the project has not yet drifted into uncontrolled demo accumulation

## Current limits

- only one new workload family is fully closed so far
- `segment_polygon_hitcount` is not yet claimed as RT-core-matured traversal
- generate-only mode remains narrow and easily over-expandable if not governed
- broader v0.2 performance maturation has not yet been the central focus

## Current best single-sentence status

RTDL v0.2 has started with real but still early progress: the roadmap and
scope gates are in place, v0.1 is archived, one new workload family is closed,
and one narrow generate-only MVP is being kept under explicit honesty
boundaries.

## Recommended immediate interpretation

The correct interpretation is:

- disciplined promising start
- real technical progress
- still early
- still disciplined

This is not yet a mature v0.2 release surface.
It is a credible early-v0.2 position.
