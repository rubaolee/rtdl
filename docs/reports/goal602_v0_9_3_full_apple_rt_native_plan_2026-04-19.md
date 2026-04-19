# Goal602: v0.9.3 Full Apple RT Native Coverage Plan

Date: 2026-04-19

Status: proposed plan; requires 3-AI consensus before implementation

## Objective

`v0.9.3` is the Apple RT native-completion line.

The goal is to move the remaining `run_apple_rt` compatibility predicates from
`cpu_reference_compat` to Apple Metal/MPS RT hardware-backed execution wherever
the workload can honestly be lowered to ray/triangle or ray/segment traversal.

The target public statement after v0.9.3 is:

> All current RTDL workloads are callable through `run_apple_rt`, and every
> workload has an Apple RT hardware-backed candidate-discovery path where the
> heavy traversal/search step uses Apple Metal/MPS RT. CPU code may still do
> exact refinement, grouping, dedupe, or final reduction where that is the
> documented RTDL contract.

This is stricter than v0.9.2. In v0.9.2, many workloads are callable through
`run_apple_rt` but still execute through CPU-reference compatibility. In v0.9.3,
that compatibility fallback should be removed from the default support matrix
for accepted workloads.

## Definition Of Hardware-Backed

A workload counts as Apple RT hardware-backed only if:

- the backend calls Apple Metal/MPS RT traversal through the native Apple RT
  library for candidate discovery or nearest/intersection search
- the CPU does not perform the full candidate search as a substitute for MPS
  traversal
- CPU postprocessing is limited to exact refinement, row sorting, dedupe,
  grouping, aggregation, or application-level semantics after MPS candidate
  discovery
- `run_apple_rt(..., native_only=True)` succeeds for that workload
- correctness is proven against `cpu_python_reference`

A workload does not count as hardware-backed if:

- `run_apple_rt` directly calls `_run_cpu_python_reference_from_normalized`
- the only native work is a trivial probe/version call
- MPS traversal is used only for an unrelated dummy operation

## Current v0.9.2 State

Native Apple RT today:

- 3D `ray_triangle_closest_hit`
- 3D `ray_triangle_hit_count`
- 2D `segment_intersection`

Compatibility today:

- `bfs_discover`
- `bounded_knn_rows`
- `conjunctive_scan`
- `fixed_radius_neighbors`
- `grouped_count`
- `grouped_sum`
- `knn_rows`
- `overlay_compose`
- `point_in_polygon`
- `point_nearest_segment`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`
- 2D `ray_triangle_hit_count`
- `segment_polygon_anyhit_rows`
- `segment_polygon_hitcount`
- `triangle_match`

## Technical Strategy

Apple MPS RT is not a general compute API. It is strongest at ray/triangle
intersection and nearest-hit queries. Therefore v0.9.3 should not try to turn
every workload into a monolithic Apple shader. Instead, it should lower each
workload into a small number of MPS-backed candidate-discovery primitives plus
existing exact RTDL refinement.

### Geometry And Polygon Workloads

First priority because they map most directly to MPS:

- 2D `ray_triangle_hit_count`
- `point_in_polygon`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `overlay_compose`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Implementation direction:

- encode 2D triangles/segments/polygon edges as thin 3D triangles or segment
  slabs
- reuse the existing masked segment-intersection path where possible
- add grouped row assembly in the Python Apple RT dispatcher only after native
  candidate discovery
- keep exact area/Jaccard arithmetic on CPU if MPS only identifies candidate
  polygon pairs

Expected difficulty:

- low to medium for 2D ray-triangle and PIP candidate discovery
- medium for segment-polygon hitcount/anyhit because inside-segment cases must
  be handled honestly
- high for polygon overlap/Jaccard if exact area is required; MPS can discover
  candidate pairs, but exact overlap area remains CPU refinement

### Nearest-Neighbor Workloads

Second priority:

- `point_nearest_segment`
- `fixed_radius_neighbors`
- `knn_rows`
- `bounded_knn_rows`

Implementation direction:

- for point-nearest-segment, use MPS candidate discovery over segment slabs or
  bounded search rays, then CPU exact distance refinement
- for point-point neighbor workloads, encode points as tiny geometric
  primitives and use MPS to generate bounded candidate neighborhoods; CPU
  performs exact distance, rank, radius, and tie-breaking
- if direct point primitives are not available in MPS, use small triangles or
  degenerate boxes encoded as triangle geometry

Expected difficulty:

- medium for `point_nearest_segment`
- high for KNN/radius because correct candidate completeness is the hard part;
  the lowering must avoid missing true neighbors

### Graph Workloads

Third priority:

- `bfs_discover`
- `triangle_match`

Implementation direction:

- encode CSR adjacency relationships into geometric interval primitives
- use MPS rays to discover edge/neighbor candidates
- CPU retains deterministic dedupe, ordering, and triangle uniqueness rules

Expected difficulty:

- high. The graph workloads are not naturally geometric, but v0.6 already
  established an RT-style traversal model. Apple RT can follow the same spirit
  if the adjacency search is lowered to MPS candidate traversal.

### DB Workloads

Fourth priority:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Implementation direction:

- follow the v0.7 RT-DB idea: rows become geometric primitives in predicate
  space, predicates become probe rays/volumes, MPS returns candidate row IDs
- CPU performs exact predicate checking and grouping/sum aggregation
- support the existing bounded integer/text-like test cases first; do not claim
  arbitrary SQL or a DBMS

Expected difficulty:

- high. It is implementable in bounded form, but it requires careful row/field
  encoding and honest setup-vs-query timing.

## Proposed v0.9.3 Goal Ladder

### Goal603: Apple RT Native-Coverage Contract

Deliverables:

- update `apple_rt_support_matrix()` with fields:
  - `predicate`
  - `mode`
  - `native_candidate_discovery`
  - `cpu_refinement`
  - `notes`
- add tests proving `native_only=True` rejects only genuinely unsupported
  workloads
- add a report that defines exact v0.9.3 native-coverage semantics

Consensus:

- 3-AI planning consensus required before implementation.

### Goal604: Geometry Native Coverage

Deliverables:

- native Apple RT candidate discovery for:
  - 2D `ray_triangle_hit_count`
  - `point_in_polygon`
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `overlay_compose`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- correctness tests against CPU reference
- perf report vs Embree

Consensus:

- 2-AI finish consensus.

### Goal605: Nearest-Neighbor Native Coverage

Deliverables:

- native Apple RT candidate discovery for:
  - `point_nearest_segment`
  - `fixed_radius_neighbors`
  - `knn_rows`
  - `bounded_knn_rows`
- completeness tests for adversarial nearest/radius cases
- perf report vs Embree

Consensus:

- 2-AI finish consensus.

### Goal606: Graph Native Coverage

Deliverables:

- native Apple RT candidate discovery for:
  - `bfs_discover`
  - `triangle_match`
- deterministic parity tests
- perf report vs Embree

Consensus:

- 2-AI finish consensus.

### Goal607: DB Native Coverage

Deliverables:

- native Apple RT candidate discovery for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- correctness against CPU reference and PostgreSQL-style expected rows where
  available
- setup/query timing vs Embree

Consensus:

- 2-AI finish consensus.

### Goal608: v0.9.3 Full-Surface Performance Report

Deliverables:

- repeatable full-surface Apple RT-vs-Embree harness
- native-only performance table
- compatibility-fallback table should be empty for accepted workloads
- clear setup/query split where relevant

Consensus:

- 2-AI finish consensus.

### Goal609: Public Docs And Tutorials Refresh

Deliverables:

- front page
- docs index
- backend maturity
- capability boundaries
- quick tutorial
- release-facing examples
- v0.9.3 release package

Consensus:

- 2-AI finish consensus.

### Goal610: v0.9.3 Pre-Release Test/Doc/Audit Gate

Deliverables:

- full local test suite
- Apple RT native-only suite
- public command audit
- docs audit
- performance report audit
- external AI review

Consensus:

- 3-AI final release consensus.

## Risks And Non-Negotiable Honesty Boundaries

- Some workloads may be hardware-backed only for candidate discovery, not for
  final exact semantics. That is acceptable if documented.
- If a workload cannot be lowered to complete MPS candidate discovery without
  missing true results, it must remain unsupported in `native_only=True` until
  the lowering is fixed.
- Performance may be worse than Embree. Correctness and native candidate
  discovery come first; speed claims require separate evidence.
- Do not call CPU-reference compatibility "Apple RT hardware."
- Do not claim Apple RT is a DBMS, graph database, ANN index, renderer, or
  general GPU compute framework.

## Initial Recommendation

Proceed in this order:

1. Goal603 contract first.
2. Goal604 geometry native coverage next.
3. Only after Goal604 passes, move to nearest-neighbor, graph, and DB groups.

This order maximizes reusable infrastructure and minimizes the risk of
inventing dishonest native coverage labels.
