# RTDL v0.9 HIPRT Backend Full-Support Plan

Date: 2026-04-18
Status: planning, requires 3-AI consensus before execution is called approved

## Objective

`v0.9` is the HIPRT backend release line.

The target is to make HIPRT a first-class RTDL backend with the same public
workload support shape as the current Embree, OptiX, and Vulkan backends, then
produce correctness and performance evidence comparing HIPRT against Embree,
OptiX, and Vulkan on Linux.

This does not mean HIPRT must be faster on every workload. It means:

- the public `run_hiprt(...)` surface should accept the same supported RTDL
  kernel families as `run_optix(...)`, `run_vulkan(...)`, and `run_embree(...)`
  where HIPRT has a technically meaningful implementation;
- each accepted workload must have row-level parity against the CPU/oracle or
  Python reference;
- each accepted workload must have Linux timing results against Embree, OptiX,
  and Vulkan where those backends are available;
- unsupported or technically dishonest mappings must be explicitly rejected,
  documented, and reviewed rather than silently falling back.

## Current State

HIPRT currently supports only:

- `hiprt_version()`
- `hiprt_context_probe()`
- direct `ray_triangle_hit_count_hiprt(...)`
- `prepare_hiprt_ray_triangle_hit_count(...)`
- `run_hiprt(...)` for Ray3D probes and Triangle3D build geometry
- `prepare_hiprt(...)` for the same Ray3D/Triangle3D hit-count shape

Validated current path:

- Linux HIPRT SDK: `/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- HIPRT version: `(2, 2, 15109972)`
- device: `NVIDIA GeForce GTX 1070`
- validated through Goals 540-544

Current gap:

- HIPRT has 2 native run symbols.
- Embree, OptiX, and Vulkan expose the broader workload family:
  - `segment_intersection`
  - `point_in_polygon`
  - `overlay_compose`
  - `ray_triangle_hit_count` 2D
  - `ray_triangle_hit_count` 3D
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `point_nearest_segment`
  - `fixed_radius_neighbors` 2D
  - `fixed_radius_neighbors` 3D
  - `knn_rows` 2D
  - `knn_rows` 3D
  - `bfs_discover`
  - `triangle_match`
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
  - prepared DB dataset reuse for the DB family

## Technical Honesty Constraint

HIPRT is a ray tracing library, not a drop-in clone of CUDA, OptiX, Vulkan, or
Embree. Some RTDL workloads map naturally to triangle or AABB traversal. Others
may need custom primitives, geometry lifting, or HIPRT-managed GPU kernels for
refinement after candidate discovery.

For v0.9, every workload must be classified before implementation:

- `native HIPRT traversal`: real HIPRT geometry traversal is used for candidate
  discovery or hit counting;
- `HIPRT-managed GPU companion`: HIPRT/Orochi context is used, but the workload
  is not fundamentally accelerated by HIPRT traversal; this needs explicit
  review before it can count as HIPRT backend support;
- `not acceptable for v0.9`: the mapping would be dishonest, a CPU fallback, or
  too different from the current RTDL semantics.

No workload may be counted as supported if it silently falls back to CPU/oracle.

## Workload Bring-Up Strategy

### Group A: Existing HIPRT Core

Target:

- Ray3D/Triangle3D `ray_triangle_hit_count`

Work:

- keep current direct and prepared APIs;
- strengthen tests and performance harnesses;
- use this as the template for reporting and backend dispatch.

Expected difficulty: low.

### Group B: 3D Nearest-Neighbor Family

Target:

- `fixed_radius_neighbors_3d`
- `knn_rows_3d`
- `bounded_knn_rows_3d` if public dispatch requires it

Candidate mapping:

- encode search points as small AABB/cube custom primitives or triangle proxies;
- cast query-shaped rays or use HIPRT traversal to discover candidates;
- refine exact distances in a HIPRT/Orochi kernel;
- return the same row schema as OptiX/Vulkan/Embree.

Why this is useful:

- v0.8 apps depend heavily on nearest-neighbor rows;
- 3D point workloads are closer to HIPRT's spatial acceleration model than DB or
  graph workloads.

Expected difficulty: medium.

### Group C: 2D Geometry Family

Target:

- `segment_intersection`
- `point_in_polygon`
- `overlay_compose`
- 2D `ray_triangle_hit_count`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `point_nearest_segment`
- 2D `fixed_radius_neighbors`
- 2D `knn_rows`

Candidate mapping:

- lift 2D geometry into 3D with a documented embedding only if it preserves
  RTDL semantics;
- use HIPRT AABB/triangle traversal for candidate discovery where possible;
- perform exact 2D refinement in HIPRT/Orochi kernels or a documented native
  refinement stage;
- reject any degenerate mapping where a 2D ray lies in a triangle plane and
  HIPRT triangle intersection cannot preserve RTDL semantics.

Why this is useful:

- this is the oldest and most visible RTDL workload family;
- parity here is necessary before HIPRT can be described as a peer backend.

Expected difficulty: high.

### Group D: Graph Family

Target:

- `bfs_discover`
- `triangle_match`

Candidate mapping:

- first study whether the existing graph RT lowering can be expressed as HIPRT
  AABB/user-primitive traversal;
- if the implementation would become ordinary GPU compute without meaningful
  HIPRT traversal, classify it separately and do not call it full HIPRT-native
  graph support without review.

Why this is useful:

- v0.6 graph was a major released RTDL line;
- a full v0.9 backend claim needs graph coverage or a documented reason why
  HIPRT cannot honestly provide equivalent graph support.

Expected difficulty: high.

### Group E: Bounded DB Family

Target:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`
- prepared DB dataset reuse

Candidate mapping:

- follow the v0.7 RT-DB lowering contract: rows/predicate ranges become spatial
  candidate discovery; exact predicate checks and grouping preserve SQL-oracle
  parity;
- use HIPRT custom primitives or AABB proxies for row candidate discovery;
- add prepared dataset support so setup/query timing can be separated like
  Embree/OptiX/Vulkan.

Why this is useful:

- DB operations motivated v0.7 and must not regress;
- PostgreSQL remains the external correctness/performance reference on Linux.

Expected difficulty: high.

## Goal Ladder

### Goal 545: v0.9 HIPRT Requirements And Feasibility Matrix

Deliverables:

- this plan;
- machine-readable workload matrix covering every Embree/OptiX/Vulkan workload
  and the proposed HIPRT mapping;
- 3-AI consensus because this defines the version scope.

Exit criteria:

- Codex, Claude, and Gemini agree the plan is honest and executable;
- any workload that may be impossible is marked as risk, not hidden.

### Goal 546: HIPRT Backend API Parity Skeleton

Deliverables:

- `run_hiprt` accepts the same predicate set as peer backends but rejects
  unimplemented predicates with precise `NotImplementedError` messages;
- `prepare_hiprt` mirrors peer backend shape where possible;
- no CPU fallback;
- tests prove unsupported workloads fail honestly.

Consensus:

- 2 AI minimum.

### Goal 547: HIPRT Correctness Harness Across All Workloads

Deliverables:

- reusable workload fixtures for every target workload;
- CPU/oracle or Python-reference expected rows;
- backend-comparison runner for `cpu_python_reference`, `cpu`, `embree`,
  `optix`, `vulkan`, and `hiprt`;
- initially permits HIPRT `NOT_IMPLEMENTED` for planned later goals, but the
  release gate requires all accepted v0.9 workloads to pass.

Consensus:

- 2 AI minimum.

### Goal 548: HIPRT 3D Geometry And 3D NN Expansion

Deliverables:

- HIPRT implementations for 3D hit-count hardening plus 3D nearest-neighbor
  target subset;
- correctness parity;
- performance smoke against Embree, OptiX, and Vulkan.

Consensus:

- 2 AI minimum.

### Goal 549: HIPRT 2D Geometry Expansion

Deliverables:

- HIPRT implementations for the accepted 2D geometry family or explicit
  consensus rejection of any workload whose 2D semantics cannot be honestly
  mapped to HIPRT traversal;
- correctness parity;
- performance comparison.

Consensus:

- 3 AI required if any workload is rejected or reclassified.

### Goal 550: HIPRT Graph Expansion

Deliverables:

- HIPRT implementations for BFS and triangle counting, or a consensus-backed
  technical reason why HIPRT cannot honestly support them at peer-backend level;
- correctness parity;
- performance comparison.

Consensus:

- 3 AI required if any workload is rejected or reclassified.

### Goal 551: HIPRT DB Expansion

Deliverables:

- HIPRT implementations for `conjunctive_scan`, `grouped_count`, `grouped_sum`;
- prepared HIPRT DB dataset API if accepted as required for peer parity;
- correctness parity against CPU/oracle and PostgreSQL on Linux;
- performance comparison against Embree, OptiX, Vulkan, and PostgreSQL.

Consensus:

- 2 AI minimum for implementation closure;
- 3 AI if prepared DB parity is scoped differently from peer backends.

### Goal 552: HIPRT Cross-Backend Performance Suite

Deliverables:

- one Linux command to run correctness and performance across all v0.9 accepted
  workloads;
- results table for HIPRT, Embree, OptiX, Vulkan, CPU/oracle, and PostgreSQL or
  SciPy where already used as an external baseline;
- setup time and query time separated for prepared-capable workloads.

Consensus:

- 2 AI minimum.

### Goal 553: v0.9 Public Docs, Tutorials, Examples

Deliverables:

- README and docs updated from "HIPRT preview" to accurate v0.9 HIPRT status;
- support matrix added under `docs/release_reports/v0_9/`;
- examples for HIPRT backend flags where supported;
- tutorials updated with HIPRT setup and limitations.

Consensus:

- 3 AI required because this is public release-facing wording.

### Goal 554: v0.9 Pre-Release Test, Doc, Flow Audit

Deliverables:

- full local test;
- Linux full backend test;
- Linux HIPRT/Embree/OptiX/Vulkan performance run;
- doc-link audit;
- flow audit confirming consensus files and release boundaries.

Consensus:

- 3 AI required before release authorization.

## Initial Risks

- HIPRT 2D ray/triangle semantics may not map directly to triangle traversal
  because RTDL's 2D rays/segments can be coplanar with lifted triangles.
- Some graph and DB paths may require HIPRT custom primitives or may become
  ordinary GPU compute if not carefully designed.
- The Linux validation GPU is a GTX 1070, which has no RT cores; performance
  results are still valid timing evidence but cannot be framed as RT-core
  speedup evidence on that host.
- HIPRT is validated only through the NVIDIA CUDA/Orochi path so far; AMD GPU
  validation remains unavailable unless new hardware appears.

## Release Rule

The v0.9 release cannot claim "same support as OptiX/Embree/Vulkan" until every
accepted workload either:

- passes HIPRT row-level correctness and has performance data, or
- has a 3-AI consensus report explaining why HIPRT cannot honestly support that
  workload at peer-backend level and how the public support matrix states that
  limit.
