# Goal1413 Roadmap To An App-Independent RTDL Engine

Date: 2026-05-06

Status: pre-release roadmap note for v1.5 and post-v1.5 planning.

## Purpose

This document records the roadmap from the v1.5 release candidate to a future
RTDL engine whose native execution core has no application-specific knowledge.
It also clarifies the intended two-stage programming model:

1. Python + RTDL
2. Python + partner + RTDL

The distinction matters because RTDL should own the performance and correctness
contract of the RTDL language and engine, but it should not pretend to own or
optimize arbitrary user Python code.

## Current v1.5 Boundary

v1.5 is a standalone RTDL language/runtime completion release candidate for the
supported Embree+OptiX surface. It is not yet a fully app-independent native
engine release.

The stable v1.5 primitive layer is app-name-free:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`

However, the native Embree/OptiX implementation still contains some
workload-shaped compatibility/proof entry points. Those entry points are
bounded and honestly documented, but they mean v1.5 must not be described as a
zero-app-knowledge engine release.

## Target Engine

The target app-independent RTDL engine has these properties:

- Native execution accepts primitive packets, typed layouts, buffers, predicates,
  reductions, and bounded output contracts.
- Native execution does not contain application names, application-specific
  branches, or workload-specific public entry points.
- Application lowering lives outside the engine, initially in Python and later
  optionally in partner integrations.
- Backend implementations preserve the same RTDL contract across Embree and
  OptiX.
- Public performance claims remain tied to measured RTDL subpaths, not arbitrary
  end-to-end user programs.

This target is an app-independent RTDL engine, not a general-purpose computing
engine and not a promise that arbitrary Python code becomes fast.

## Stage 1: Python + RTDL

In the first stage, users write Python code and call RTDL directly.

This is a deliberate boundary:

- The user chooses how much ordinary Python code to write.
- RTDL does not take responsibility for the performance of arbitrary user
  Python loops, object construction, JSON materialization, plotting, I/O,
  dataframe work, or postprocessing.
- RTDL does take responsibility for the RTDL language surface and engine
  execution once data and operations enter RTDL-owned contracts.
- RTDL should still avoid unnecessary overhead at the RTDL boundary.

v1.5 already reflects this direction through scalar summary and reduction work.
Instead of forcing apps to materialize large row outputs and then reduce them in
Python, the v1.5 primitive layer supports native-style summary contracts such
as hit counts and numeric reductions. That is not a guarantee that all user
Python becomes fast; it is RTDL reducing avoidable RTDL-side overhead.

Likely next work in this stage:

- promote `COLLECT_K_BOUNDED` in v1.5.1 with fail-closed semantics and native
  Embree/OptiX parity;
- reduce compatibility wrappers that expose workload-shaped native entry
  points;
- add stricter primitive-packet lowering tests;
- investigate zero-copy or reduced-copy data exchange for RTDL-owned buffers;
- keep Python-side app lowering explicit and outside the native engine.

The performance principle for Stage 1 is:

> RTDL should minimize overhead it introduces or controls, but it does not own
> arbitrary Python code written around RTDL calls.

## Stage 2: Python + Partner + RTDL

In the second stage, users can let RTDL cooperate with a partner system that
also has a performance contract. Examples may include Numba, CuTile Python, or
other array/kernel/dataframe/runtime partners.

The purpose of the partner mechanism is not to make RTDL a general-purpose
compiler. The purpose is to define a safe boundary where:

- RTDL owns ray-tracing-style primitive packets, traversal, hit tests,
  reductions, and bounded collection;
- the partner owns its own compute regions, Python acceleration model, memory
  model, or data layout;
- both sides exchange typed buffers, ownership/lifetime metadata, and execution
  dependencies through explicit contracts;
- neither side silently assumes responsibility for code it does not control.

This stage is the route toward broader end-to-end performance because it gives
ordinary Python-adjacent code a performance-aware partner instead of asking RTDL
to absorb arbitrary Python semantics.

Likely work in this stage:

- define the partner API boundary in v1.6;
- build a first partner prototype in v1.7;
- add conformance tests for buffer ownership, synchronization, failure modes,
  and backend parity in v1.8;
- harden partner interoperability and documentation in v1.9;
- make partner-ready RTDL a public v2.0 capability.

## Responsibility Split

| Layer | Responsibility | Not Responsible For |
| --- | --- | --- |
| User Python | Application control, data preparation, orchestration, postprocessing | RTDL engine internals |
| RTDL language | Primitive contracts, layouts, predicates, reductions, bounded collection | Arbitrary Python performance |
| RTDL native engine | App-independent primitive execution on Embree/OptiX | App-specific business logic or app names |
| Partner runtime | Its own accelerated Python-adjacent compute and memory model | RTDL traversal semantics |
| Integration boundary | Typed exchange, lifetime, synchronization, error contracts | Hidden ownership or unbounded implicit copies |

## Roadmap

### v1.5

Release standalone RTDL for the supported Embree+OptiX surface. Preserve the
honest boundary that native internals are not yet fully app-independent.

### v1.5.1

Promote `COLLECT_K_BOUNDED` only if it has fail-closed semantics, backend
parity, correctness tests, benchmark evidence, and external review. Use this as
the first serious cleanup point for row-returning app-shaped paths.

### v1.6

Define the app-independent engine boundary and the partner API specification.
Identify which remaining native entry points must be removed, generalized, or
kept only as private compatibility shims.

### v1.7

Implement the first partner prototype and prove that RTDL can cooperate with a
partner without absorbing arbitrary Python performance responsibility.

### v1.8

Add conformance tests for partner memory exchange, zero-copy or reduced-copy
paths, synchronization, errors, and backend parity.

### v1.9

Harden the partner mechanism and remove or quarantine remaining workload-shaped
native surfaces.

### v2.0

Publish RTDL as partner-ready with an app-independent native engine boundary:
RTDL owns primitive execution, partners own their accelerated regions, and user
Python remains user code.

## Public Wording Boundary

Allowed:

- RTDL v1.5 starts the transition toward an app-independent native engine by
  stabilizing app-name-free primitive and reduction contracts.
- RTDL intends to support both Python+RTDL and Python+partner+RTDL workflows.
- RTDL minimizes overhead it controls, including reductions and future
  reduced-copy or zero-copy mechanisms where safe.

Not allowed:

- claiming v1.5 already has a zero-app-knowledge native engine;
- claiming RTDL owns arbitrary Python performance;
- claiming partner integrations exist before they are implemented and tested;
- claiming whole-app speedups without measured, reviewed, subpath-specific
  evidence.

## Conclusion

The correct roadmap is not to make RTDL responsible for all Python code. The
correct roadmap is to make RTDL app-independent inside its own language and
engine boundary, then add partner mechanisms for users who want coordinated
performance beyond direct Python+RTDL calls.
