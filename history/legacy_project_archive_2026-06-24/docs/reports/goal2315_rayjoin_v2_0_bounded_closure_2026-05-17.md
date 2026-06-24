# Goal2315 RayJoin v2.0 Bounded Closure

## Purpose

Close the RayJoin-style project for the v2.0 release lane without pretending
that RTDL beats the original RayJoin system. The goal is to state what a user
can do with RTDL v2.0 today, what the systems-research evidence shows, and what
work is deliberately deferred to the future-version to-do list.

## User-Level Closure

For a user of the RTDL language, the scoped RayJoin-style workloads are
implementable in v2.0:

| Workload | RTDL v2.0 route | Status |
| --- | --- | --- |
| LSI / segment intersection join | prepared generic segment-pair intersection on OptiX | exact parity on the RayJoin-exported 100k stream |
| PIP / point-in-shape membership join | prepared generic point/closed-shape membership on OptiX | exact parity on the RayJoin-exported 100k stream |

The user writes Python orchestration around generic RTDL prepared primitives.
No RayJoin-specific native engine mode is required.

## Current Prepared Performance Position

Current scoped pod evidence on RTX A5000 after Goal2312/Goal2314:

| Row | RTDL v2.0 median seconds | Exact rows |
| --- | ---: | ---: |
| LSI raw witness rows | 0.010123 | 8,921 |
| LSI scalar count | 0.009986 | 8,921 |
| PIP positive raw row view | 0.008657 | 8,686 |
| PIP scalar count | 0.008476 | 8,686 |

This is a low-millisecond prepared-query result for the current RTDL route.
It is strong enough to close the v2.0 RayJoin-style language/runtime milestone.

## Comparison To Original RayJoin

The original RayJoin RT query-phase numbers imported in Goal2209 remain faster
than RTDL's generic prepared route:

| Workload | RayJoin RT query phase | RTDL v2.0 prepared route | Ratio |
| --- | ---: | ---: | ---: |
| LSI | 0.000612 s | 0.010123 s | RTDL is about 16.6x slower |
| PIP | 0.000575 s | 0.008657 s | RTDL is about 15.1x slower |

The phase boundaries differ: RayJoin reports a specialized C++/CUDA/OptiX
query phase, while RTDL reports a generic Python-hosted prepared primitive
route. The comparison is useful as research pressure, not as a public
win/loss benchmark.

## Systems-Research Closure

The RayJoin project taught RTDL the right next abstraction:

- prepared scene reuse matters;
- prepacked query inputs matter;
- app-specific PIP/LSI engine code should not be reintroduced;
- closed-shape membership is the right generic primitive for PIP-style joins;
- bounded point probes remove major traversal waste for this data shape;
- raw row views remove Python dictionary materialization from row-output
  timings;
- the remaining gap to raw RayJoin-style C++/CUDA/OptiX is device-resident
  continuation, not another app-specific native shortcut.

## Deferred To-Do

The following items were written to `docs/research/future_version_to_do_list.md`
instead of blocking v2.0:

- broader RayJoin paper-matrix reproduction, if explicitly reopened;
- phase-boundary disciplined comparisons between RayJoin and RTDL;
- generic device-resident row streams / continuations;
- downstream partner-side reductions over prepared row streams;
- broader coordinate/data-shape validation for bounded closed-shape membership.

## Claim Boundary

Closed for v2.0:

- RTDL can express and execute the scoped RayJoin-style LSI/PIP workloads.
- The engine route remains app-agnostic.
- Exact parity is preserved on the imported 100k RayJoin-exported streams.
- Current prepared OptiX timings are low-millisecond after preparation.

Not claimed:

- RTDL beats RayJoin.
- RTDL reproduces the full RayJoin paper.
- RTDL has whole-app RayJoin speedup.
- RTDL provides broad RT-core acceleration for arbitrary programs.
- RTDL has true zero-copy or generic device-resident continuation for these
  rows.
- v2.0 is released.

## Verdict

`closed-for-v2.0-with-boundary`

The RayJoin project should not block v2.0 release preparation. Future RayJoin
work belongs in the v2.5+/research lane unless the user explicitly reopens it.
