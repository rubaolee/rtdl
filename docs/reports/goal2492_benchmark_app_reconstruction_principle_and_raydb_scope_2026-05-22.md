# Goal2492: Benchmark-App Reconstruction Principle and RayDB Scope

Date: 2026-05-22

## Status

Goal2492 defines the next benchmark-app rule after the robot-collision closeout.
The purpose is not to finish every paper application as a full product. The
purpose is to use serious app slices to discover and validate RTDL language and
runtime reconstruction needs while keeping the native engines app-agnostic.

## Core Principle

A benchmark app is acceptable when it creates clear RTDL pressure:

- a missing generic primitive;
- a missing result contract;
- a missing memory/lifetime contract;
- a missing partner handoff boundary;
- a missing prepared-state or repeated-query execution model;
- a missing correctness/performance evidence protocol.

A benchmark app does not need to reproduce a complete external system when a
smaller slice is enough to expose the RTDL design problem. Conversely, an app
should not be added only because it is interesting. It must force a concrete
language/runtime improvement or boundary decision.

## What Recent Apps Already Forced

| Benchmark app | RTDL pressure exposed | Main reconstruction result |
| --- | --- | --- |
| Spatial RayJoin-style app | Row/count distinction, point/polygon and segment/segment relationship rows, same-query fairness, prepared traversal | Generic spatial row contracts and prepared query evidence without RayJoin-specific native code |
| RT-DBSCAN-style app | Fixed-radius grouped continuation, union/component propagation, target/source culling, global atomic pressure | Generic grouped fixed-radius continuation and component-style execution pressure |
| Hausdorff/X-HD-style app | Exact continuation, witness tracking, group min/max reductions, partner-owned columns | Python+partner+RTDL boundary for exact non-RT continuation over RTDL-produced candidate structure |
| Robot-collision-style app | Repeated dynamic query geometry against a prepared static scene, reusable query buffers, compact flags, count-only screening | Generic grouped finite 3D segment query, Embree/OptiX prepared scene reuse, device query buffers, scalar result mode |

These apps are not claims that RTDL is a full GIS engine, full DBSCAN engine,
full Hausdorff product, or full robot collision solver. They are evidence that
specific app slices forced useful app-agnostic RTDL mechanisms.

## RayDB Decision Boundary

RayDB remains a good next candidate only if we scope it differently from the
existing spatial RayJoin work. A RayDB campaign should not repeat the already
covered RayJoin-style PIP/LSI/overlay-seed slice unless doing so reveals a new
RTDL contract.

The useful RayDB pressure is database-shaped ray execution:

- table-like query columns rather than Python lists of ad hoc rays;
- declarative query-result mode selection, such as count, flag, first-hit, or
  bounded witness rows;
- prepared scene or prepared index lifetime separate from query table lifetime;
- columnar memory descriptors that can be CPU-owned, RTDL-owned, or
  partner-owned;
- query-plan lowering in Python while native engines stay app-name-free;
- explicit separation between RT traversal, predicate/filter continuation, and
  row/materialized output.

If local or external RayDB code is used later, it must first be checked for
availability, license, dataset requirements, and comparable output contract.
Until then, no authors-code comparison, paper reproduction, or paper-level
speedup claim is authorized.

## Proposed Minimal RayDB Slice

The first RayDB-style RTDL slice should be intentionally small:

```text
prepared triangle/object scene
+ columnar ray query table
+ declarative result mode
-> grouped scalar counts, flags, or first-hit summaries
```

Python owns the database-like layer:

- schema names;
- query names;
- SQL-like or dataframe-like user API;
- table loading and fixture generation;
- paper-specific interpretation;
- row labels and output formatting.

RTDL owns only the generic execution contracts:

- prepared scene descriptors;
- query column descriptors;
- backend-neutral result-mode descriptors;
- phase timing for prepare, query transfer/packing, traversal, continuation, and
  output materialization;
- Embree/OptiX parity checks for the same contract.

## Candidate Goal Sequence

### Goal2492: Scope and Guard the Benchmark-App Rule

Deliver this report and tests that lock the principle:

- benchmark apps are reconstruction instruments;
- partial app slices are allowed;
- app-specific semantics must not enter native Embree/OptiX;
- RayDB is only justified if it exposes database-shaped ray query contracts not
  already covered by spatial RayJoin.

### Goal2493: RayDB Local/External Code Intake

Find what RayDB code and datasets are locally available or externally usable.
Record license, build requirements, dataset size, and whether the outputs can be
matched by a small RTDL slice. If code is not available or unsuitable, proceed
with a synthetic RayDB-style fixture and do not claim authors-code comparison.

### Goal2494: RayDB Query Contract Design

Define the smallest app-agnostic contract:

- query table column descriptors;
- prepared scene lifetime;
- result modes: count, flags, first-hit, and possibly bounded witness rows;
- CPU/Embree/OptiX parity requirements;
- claim boundaries.

### Goal2495: CPU Reference and Fixture

Implement a deterministic CPU reference for the selected slice. It should be a
database-shaped user program, not a DBMS: table descriptors, query descriptors,
and result summaries are enough.

### Goal2496: Embree Implementation

Implement same-contract Embree support or reuse an existing generic Embree
primitive through a clean Python adapter. The key is to expose whether current
RTDL contracts are sufficient for table-shaped ray queries.

### Goal2497: OptiX Implementation and Pod Evidence

Run the same contract on OptiX only when a pod is available. Record hardware,
CUDA/OptiX layout, commands, correctness, and phase timings. Do not publish a
speedup claim without a separate review gate.

## Exit Criteria For The RayDB Campaign

The campaign should close when it has answered the reconstruction question:

- Do RTDL query primitives need first-class columnar query-table descriptors?
- Do result modes need a stable declaration independent of app names?
- Can Python lower database-like user syntax into app-agnostic RTDL primitives?
- Where should partner-owned memory enter the query-table path?
- Which parts are RTDL responsibility, and which parts are user/database code
  responsibility?

If these are answered with tests, docs, and at least one backend path, the app
slice can be finished even if the full RayDB paper system is not reproduced.

If OptiX pod access is unavailable after the CPU and Embree contract are
implemented, the campaign may still close as a CPU/Embree reconstruction slice.
In that case, the closeout must explicitly mark NVIDIA/OptiX evidence as
deferred and must not make RTX, OptiX, or public speedup claims.

## Non-Goals

Goal2492 and the proposed RayDB campaign do not authorize:

- full RayDB reproduction;
- SQL engine or DBMS claims;
- public performance wording;
- authors-code comparison without verified code and datasets;
- app-specific native engine ABI;
- native `raydb`, `sql`, `table`, or `database` vocabulary inside Embree/OptiX
  primitive implementation paths;
- broad claims that RTDL is a general database engine.

## Consensus Requirement

Goal2492 is a roadmap/scope artifact. If it becomes the project-facing roadmap
for the next campaign, it should receive at least 2-AI consensus as defined in
`/Users/rl2025/refresh.md`: Codex plus one independent external AI review saved
in the repository with an explicit acceptable verdict. Any public claim,
release wording, or broad architecture claim still requires the stronger review
gate specified in `refresh.md`.
