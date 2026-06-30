# Goal2551 Codex Rethinking: Benchmark-App Wave

Date: 2026-05-23

Scope: RT-DBSCAN, robot collision, RayDB-style columnar aggregate, and
Barnes-Hut benchmark-app work through Goal2550.

## Executive Judgment

The benchmark-app wave succeeded at its main purpose: it exposed real language
and runtime pressure points instead of merely adding demos. The core RTDL
direction is still sound:

- app/domain policy belongs in Python examples, benchmark adapters, and partner
  code;
- native engines should provide app-independent traversal, hit-stream,
  grouped-continuation, columnar, and reduction primitives;
- public performance claims remain blocked unless exact subpath evidence and
  external consensus exist.

However, the current tree is not yet clean enough to call the native engine
fully app-independent. It is good enough for an internal benchmark-app snapshot,
but the next work should be an engine-purity and primitive-consolidation pass.

## App-Specific Or Workload-Specific Items Still Near Engine Boundaries

### Native OptiX DB/RayDB Vocabulary

`src/native/optix/rtdl_optix_workloads.cpp` still contains `DbScanPipeline`,
`g_dbscan`, `kDbScanKernelSrc`, `db_scan_kernel.cu`, and error strings such as
"first-wave OptiX DB lowering".

This is the most concrete app/domain-specific leakage in the native engine. The
functionality is really a generic encoded-column predicate scan / compact
candidate-set primitive. It should be renamed and documented that way.

Recommended action:

- rename `DbScan*` / `db_scan*` to generic columnar predicate-scan names;
- rename public/runtime wording from DB/RayDB to columnar predicate/aggregate
  where the code is not actually a DBMS;
- add a source scanner that fails on benchmark app names in `src/native/embree`
  and `src/native/optix`, with a short allowlist for historical compatibility
  reports only.

### Partner Adapters Contain App-Specific Convenience Wrappers

`src/rtdsl/partner_adapters.py` contains
`robot_collision_pose_flags_optix_prepared_partner_device_columns`. This is not
native-engine leakage, because it wraps generic any-hit ray flags and performs a
partner-side group-any reduction. Still, the name and metadata are app-specific
inside a central adapter module.

Recommended action:

- keep the generic operations in `partner_adapters.py`;
- move benchmark-specific wrappers into benchmark/app modules, or expose them
  under an explicit `rtdsl.app_adapters` namespace so the boundary is visible.

### RayDB-Style Wording In Core Columnar Partner Planning

`src/rtdsl/columnar_partner.py` describes the first executable slice as
"numeric RayDB-style columns only". The actual design should be a generic
numeric columnar aggregate contract.

Recommended action:

- rename this wording to "numeric columnar aggregate columns";
- keep RayDB only in benchmark docs and examples.

### Weighted Inverse-Square References In Core RTDSL

`src/rtdsl/aggregate_tree_reference.py` contains weighted inverse-square
contribution and vector-sum contracts. These are not in the native engine, and
Goal2549 correctly rejected moving the inverse-square math into native OptiX.
Still, inverse-square is a force-law shape, so it should not become the only
aggregate-frontier reduction model.

Recommended action:

- split aggregate-frontier traversal/frontier production from math;
- treat inverse-square as one app/partner operator over a generic frontier;
- design a reviewed operator plug-in mechanism before native fused math.

## Common Features Implemented Multiple Times

### Grouped Reductions

Grouped count/sum/min/max/avg-like behavior now appears in:

- RT-DBSCAN grouped union / grouped continuation paths;
- RayDB-style columnar grouped aggregates;
- robot collision pose flag group-any;
- Barnes-Hut vector/scalar grouped accumulation;
- partner-side Torch/CuPy reductions;
- native OptiX grouped int64 paths.

This should become a shared grouped-reduction substrate with explicit
operations:

- `GROUP_ANY`
- `GROUP_COUNT`
- `GROUP_SUM_I64`
- `GROUP_SUM_F32/F64`
- `GROUP_MIN/MAX`
- fused `SUM_COUNT`
- segmented/blocked output compaction and overflow reporting

### Device Column Descriptors

Device column and partner-resident handoff logic is split between
`columnar_partner.py`, `columnar_aggregate_reference.py`,
`partner_adapters.py`, and `optix_runtime.py`.

This should become one reusable descriptor/ABI layer:

- dtype token;
- device pointer;
- shape/stride/contiguity;
- device id;
- ownership/lifetime;
- row count;
- optional output buffer descriptor;
- explicit host-materialization boundary.

### Capacity And Overflow Contracts

Several paths have one-off capacity limits, output capacities, row-count caps,
or fail-closed overflow behavior. This must be normalized.

Recommended shared model:

- every primitive returns `status`, `required_capacity`, `written_count`, and
  `overflowed`;
- fail-closed default;
- benchmark apps may choose retry/chunking policy, but native engines should
  report capacity needs in one common shape.

### Prepared-State Lifetime

RT-DBSCAN, robot collision, RayDB-style columnar aggregates, and Barnes-Hut all
show that prepared state must be first-class:

- prepared search points / scene geometry;
- prepared triangle scenes;
- prepared columnar payloads;
- prepared aggregate trees/frontiers;
- partner-resident buffers.

This deserves a unified prepared-object lifecycle and metadata contract across
Embree, OptiX, and partner adapters.

## Suggested Next Work

### Goal A: Engine-Purity Gate

Write and pass a source-level guard that scans native engines for benchmark or
app vocabulary:

- `dbscan`, `raydb`, `robot`, `collision`, `barnes`, `force`,
  `inverse_square`, and similar names;
- allow only generic primitive terms or explicitly grandfathered legacy rows.

Then rename the concrete OptiX DB scan pipeline to a generic columnar predicate
scan.

### Goal B: Unified Columnar Device ABI

Promote partner-resident column descriptors into a stable internal ABI:

- one descriptor struct;
- one Python validation layer;
- one OptiX native intake path;
- one set of dtype/layout rules.

This is the prerequisite for RayDB-style work to become an RTDL primitive
instead of a benchmark-specific adapter.

### Goal C: Shared Grouped-Reduction Substrate

Implement one grouped-reduction abstraction and lower RT-DBSCAN, RayDB-style
aggregates, robot pose flags, and Barnes-Hut accumulation onto it where
possible.

This should reduce duplicated Torch/CuPy/native code and make performance work
portable across apps.

### Goal D: Aggregate-Frontier Primitive Without App Math

For Barnes-Hut, native work should first produce generic frontier/range outputs
or traversal diagnostics. Fused inverse-square accumulation is not allowed in
native engine until a generic operator plug-in or partner mechanism is designed.

### Goal E: Evidence Manifest

Create a single machine-readable benchmark-app evidence manifest:

- app name;
- primitive contracts used;
- backends tested;
- correctness oracle;
- performance artifact paths;
- claim boundary;
- external-review status;
- internal-version snapshot id.

This will make external reviews much easier than scanning hundreds of
goal-numbered reports.

## Internal-Version Recommendation

Create an internal git snapshot after cleanup and validation, but do not publish
it as a public release.

Suggested label:

`internal-benchmark-apps-2026-05-23`

This snapshot is suitable for external review because it includes:

- benchmark apps and scripts;
- evidence reports;
- claim-boundary tests;
- Barnes-Hut Goal2549 rejection guard;
- final Barnes-Hut Goal2550 closeout.

It is not suitable for public release wording because the native engine still
has naming/purity debt and the benchmark-app performance claims remain bounded
or internal-only.
