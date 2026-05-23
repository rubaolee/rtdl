# Goal2551 3-AI Consensus: Benchmark-App Wave Rethinking

Date: 2026-05-23

Participants:

- Codex: `docs/reports/goal2551_codex_rethinking_benchmark_app_wave_2026-05-23.md`
- Gemini: `docs/reports/goal2551_gemini_rethinking_benchmark_app_wave_2026-05-23.md`
- Claude: `docs/reports/goal2551_claude_rethinking_benchmark_app_wave_2026-05-23.md`

## Consensus Verdict

The benchmark-app wave is successful as an internal RTDL research snapshot, but
it is not clean enough for public release wording or external ABI
stabilization.

All three reviews agree:

- the four benchmark apps are useful reconstruction instruments;
- the claim boundaries are mostly disciplined;
- Barnes-Hut Goal2549 correctly rejected app-specific inverse-square native
  engine math;
- the next work should not be another benchmark-app optimization loop;
- the next work should be engine-purity and primitive-consolidation.

The appropriate internal snapshot label is:

`internal-benchmark-apps-2026-05-23`

This label is suitable for git/tag review because it explicitly says internal.
It must not be described as a public RTDL release.

## Main Shared Findings

### 1. Native Engine Is Not Yet Fully App-Independent

The strongest agreed issue is DB/RayDB/DBSCAN vocabulary and structure in the
OptiX native layer.

Concrete examples:

- `RtdlDb*` structs and constants in `src/native/optix/rtdl_optix_prelude.h`
- `DbScanPipeline`, `g_dbscan`, `kDbScanKernelSrc`, and `db_scan_*` kernel names
  in `src/native/optix/rtdl_optix_core.cpp` and
  `src/native/optix/rtdl_optix_workloads.cpp`
- runtime/report wording such as "DB lowering" where the implementation is
  really a generic encoded-column predicate scan / grouped aggregate path

Consensus: this is the most important engine-purity target.

### 2. Capacity/Overflow Contract Is Inconsistent

Claude identified a concrete ABI safety gap that Codex and Gemini did not
initially emphasize: grouped-reduction `_with_capacity` variants have a
capacity argument but do not expose an `overflowed_out` signal like other
bounded primitives.

Consensus: this should be fixed before treating the grouped-reduction ABI as
stable. Silent truncation or ambiguous capacity-hit behavior is not acceptable.

### 3. Common Grouped-Reduction Machinery Is Fragmented

Grouped operations now appear independently in:

- RT-DBSCAN grouped union / component paths;
- RayDB-style columnar grouped aggregates;
- robot collision group-any pose flags;
- Barnes-Hut grouped/vector/scalar accumulation;
- Torch/CuPy partner reductions;
- native OptiX grouped i64 reduction paths.

Consensus: RTDL needs one grouped-reduction substrate with shared semantics,
capacity reporting, backend lowering, and tests.

### 4. Device Column Descriptors Need One Stable ABI

Device/partner-resident column descriptors are split across
`columnar_partner.py`, `columnar_aggregate_reference.py`,
`partner_adapters.py`, and `optix_runtime.py`.

Consensus: introduce one `DeviceColumnDescriptor` / device-column ABI contract
before claiming partner-resident columnar execution is stable.

### 5. App-Specific Python Adapters Should Move Out Of Shared Adapter Core

`robot_collision_pose_flags_optix_prepared_partner_device_columns` is not
native-engine leakage, but it is app-specific inside `partner_adapters.py`.

Consensus: keep generic group-any and any-hit flag operations in
`partner_adapters.py`; move app-specific wrappers to benchmark/app modules or a
clearly named `rtdsl.app_adapters` namespace.

### 6. Barnes-Hut Aggregate Frontier Must Stay Math-Agnostic In Native Engine

All three reviews accept Goal2549's correction: inverse-square force math must
not be fused into native OptiX as an engine primitive.

Consensus: native work may produce generic frontier/range/traversal outputs.
Fused app math requires a reviewed operator plug-in or partner mechanism.

## Prioritized Next Work

### P0. Native Naming And ABI Purity

Rename DB/RayDB/DBSCAN-shaped native concepts before external ABI
stabilization:

- `RtdlDbField` -> `RtdlPayloadField` or `RtdlColumnarField`
- `RtdlDbScalar` -> `RtdlPayloadScalar` or `RtdlColumnarScalar`
- `RtdlDbClause` -> `RtdlPredicateClause`
- `RtdlDbGrouped*Row` -> `RtdlGrouped*Row`
- `DbScanPipeline` / `db_scan_*` -> `ColumnarPredicateScan*` /
  `columnar_scan_*`

Add a native source purity gate that scans `src/native/embree` and
`src/native/optix` for benchmark/app terms such as:

`dbscan`, `raydb`, `robot`, `collision`, `barnes`, `force`, `inverse_square`

Use an explicit allowlist only for intentionally grandfathered compatibility
symbols.

### P0. Capacity/Overflow Contract Fix

Add `overflowed_out` or an equivalent status/result structure to grouped
`*_with_capacity` APIs. Every capacity-bounded primitive must expose:

- status;
- written count;
- required or observed capacity;
- overflow flag.

### P1. Unified Columnar Device ABI

Create one reusable descriptor contract covering:

- dtype token;
- device pointer;
- element count;
- shape/stride/contiguity;
- CUDA device id;
- ownership/lifetime;
- host materialization boundary;
- output-buffer descriptors.

Then lower RayDB-style columnar aggregates through this generic ABI.

### P1. Shared Grouped-Reduction Substrate

Define one grouped reduction primitive family:

- `GROUP_ANY`
- `GROUP_COUNT`
- `GROUP_SUM_I64`
- `GROUP_SUM_F32/F64`
- `GROUP_MIN/MAX`
- fused `SUM_COUNT`
- grouped `STATS`

Then migrate RT-DBSCAN, RayDB-style, robot collision, and Barnes-Hut paths onto
that substrate where applicable.

### P1. Move App-Specific Partner Convenience Wrappers

Move app-specific wrappers such as robot pose-flag adapters out of the shared
partner core. Keep only generic any-hit flags, group-any, grouped reductions,
and device-column utilities in `partner_adapters.py`.

### P2. Aggregate-Frontier Traversal Primitive

For Barnes-Hut and future hierarchical apps, design a math-agnostic
aggregate-frontier primitive:

- accepted aggregate IDs;
- exact member IDs or ranges;
- per-source counts/ranges;
- traversal diagnostics;
- no inverse-square or timestep-specific math in native engine.

### P2. Evidence Manifest

Create a single machine-readable benchmark-app evidence manifest with:

- benchmark app;
- primitive contracts used;
- backend support;
- correctness oracle;
- performance artifact paths;
- claim boundary;
- external review status;
- internal snapshot id.

## Release / Snapshot Boundary

Approved:

- commit and push the current benchmark-app wave as an internal snapshot;
- optionally tag it `internal-benchmark-apps-2026-05-23`;
- use it as review material for the next engine-purity phase.

Not approved:

- public release wording;
- broad speedup wording;
- external ABI stability claims;
- claiming the native engine is fully app-independent.

## Final Consensus

Proceed by syncing the current cleaned repository state to git as an internal
snapshot, then start the next goal on P0 engine-purity and capacity/overflow
fixes. The benchmark-app work should be considered complete enough for review,
but not complete enough for public release.
