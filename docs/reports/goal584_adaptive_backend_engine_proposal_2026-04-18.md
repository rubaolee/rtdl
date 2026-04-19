# Goal584: Adaptive Backend Engine Proposal

Status: accepted, 3-AI planning consensus reached

Date: 2026-04-18 local EDT

Consensus:

- Codex: ACCEPT, proceed as a new adaptive backend/version track.
- Gemini Flash: ACCEPT, proposal is coherent and honest for the 18-workload
  matrix.
- Claude: ACCEPT, proceed to Goal585 with minor refinements recorded below.

## User Requirement

Build a new RTDL backend engine for the existing 18-workload matrix, with
performance advancements in multiple dimensions:

- lower branch-prediction sensitivity
- better multi-level cache behavior
- workload-specific data layout and scheduling
- support for diverse workload requirements that cannot be satisfied by one
  fixed record format or one fixed traversal encoding

## Working Name

`run_adaptive`

This is a placeholder API name. It means a new RTDL backend family, not a
replacement for Embree, OptiX, Vulkan, HIPRT, or Apple RT.

## Baseline Matrix

The target matrix is the current 18-workload RTDL matrix already tracked for the
main cross-backend line:

1. `segment_intersection`
2. `point_in_polygon`
3. `overlay_compose`
4. `ray_triangle_hit_count_2d`
5. `ray_triangle_hit_count_3d`
6. `segment_polygon_hitcount`
7. `segment_polygon_anyhit_rows`
8. `point_nearest_segment`
9. `fixed_radius_neighbors_2d`
10. `fixed_radius_neighbors_3d`
11. `bounded_knn_rows_3d`
12. `knn_rows_2d`
13. `knn_rows_3d`
14. `bfs_discover`
15. `triangle_match`
16. `conjunctive_scan`
17. `grouped_count`
18. `grouped_sum`

## Core Design

The adaptive backend should be a workload-dispatching engine with multiple
specialized kernels behind one RTDL runtime entry point.

It should not force all workloads into one fixed data format.

Instead, each workload family gets:

- an input normalizer
- a layout planner
- a prepared dataset representation where useful
- a branch-reduction strategy
- a cache-level strategy
- a correctness oracle comparison
- a performance benchmark against existing backends

## Performance Ideas

### Branch Behavior

Use branch-reduced or branchless kernels where possible:

- predicate masks instead of nested `if` ladders
- sorted/bucketed inputs to improve predictable control flow
- separate hot paths from rare slow paths
- precompute classification flags for DB predicates and graph rows
- avoid per-row dynamic type checks inside hot loops

### Cache Hierarchy

Use multi-level cache design explicitly:

- L1-friendly tiles for point/ray/segment batches
- L2-sized build-side blocks for triangle, segment, point, graph, and DB data
- prepared reusable columnar or SoA layouts for repeated queries
- compact ID arrays separated from large payload arrays
- contiguous output buffers with stable post-sort only when required

### Workload-Specific Layouts

Use different layouts by family:

- geometry: SoA endpoints, packed bounding boxes, optional tile grids
- ray/triangle: SoA rays, triangle vertex blocks, hit-count/closest-hit modes
- nearest neighbor: point SoA, cell bins or Morton-order buckets
- graph: CSR plus frontier/visited bitsets and sorted seed batches
- DB: columnar numeric/text dictionaries, predicate bytecode, group hash/slot
  arrays

## Backend Positioning

`run_adaptive` should be measured as an RTDL backend, but it is not necessarily
one specific vendor RT API. It is a performance backend with explicit RTDL
kernel ownership. It may use:

- native C/C++ CPU kernels first
- SIMD where available
- prepared datasets
- optional platform-specific acceleration later

This is useful because some RTDL workloads are not naturally expressible as a
single vendor ray query without inefficient encodings.

## Non-Goals

The adaptive backend is not:

- a DBMS
- a renderer
- a replacement for Apple RT / HIPRT / Vulkan / OptiX / Embree
- a claim that every workload can be accelerated by one fixed BVH shape
- a claim of performance win before measurement

## Implementation Sequence

### Goal585: Contract And Runtime Skeleton

Deliver:

- `run_adaptive(...)` public runtime entry point
- decide whether `run_adaptive` remains the stable API name or is replaced by a
  final public name before Goal591
- support matrix API
- explicit per-predicate mode strings
- no fake performance claims
- all 18 predicates callable through the dispatcher
- initial implementation may route to existing CPU reference while preserving
  mode visibility
- thread-safety and scratch/allocation rules for later SIMD/native kernels
- clear lifetime rules for prepared adaptive contexts

Closure:

- tests prove all 18 predicates are accepted by `run_adaptive`
- docs say which paths are native adaptive and which are compatibility
- docs and tests prove compatibility dispatch cannot be mistaken for native
  adaptive acceleration

### Goal586: First Native Family, Ray/Triangle

Deliver native adaptive kernels for:

- `ray_triangle_hit_count_3d`
- `ray_triangle_closest_hit`

Rationale:

- already central to RTDL
- clear comparison to Embree, HIPRT, and Apple RT
- good testbed for branch and cache decisions

Closure:

- correctness parity against CPU reference
- performance compared to Embree and Apple RT on this Mac
- performance compared to HIPRT / OptiX / Vulkan on Linux if synced there
- `ray_triangle_closest_hit` must be compared against Apple RT on macOS, because
  Apple RT already has native closest-hit capability and regression risk should
  be explicit

### Goal587: Geometry 2D Family

Deliver native adaptive kernels for:

- `segment_intersection`
- `point_in_polygon`
- `overlay_compose`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

Rationale:

- branch-heavy control flow
- benefits from tiling, bounding boxes, and layout planning

Closure:

- correctness parity against CPU reference
- compare with Embree/OptiX/Vulkan/HIPRT where available

### Goal588: Nearest-Neighbor Family

Deliver native adaptive kernels for:

- `fixed_radius_neighbors_2d`
- `fixed_radius_neighbors_3d`
- `knn_rows_2d`
- `knn_rows_3d`
- `bounded_knn_rows_3d`
- `point_nearest_segment`

Rationale:

- likely strong cache-layout wins through tiling/binning/Morton ordering
- repeated-query prepared data matters

### Goal589: Graph Family

Deliver native adaptive kernels for:

- `bfs_discover`
- `triangle_match`

Rationale:

- graph workloads are memory-bound and branch-sensitive
- CSR layout and frontier/visited bitsets need a dedicated strategy

### Goal590: DB Analytical Family

Deliver native adaptive kernels for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Rationale:

- columnar layout, predicate bytecode, and group aggregation can reduce branch
  and cache penalties
- PostgreSQL remains a correctness/performance comparison on Linux

### Goal591: Full-Matrix Benchmark And Audit

Deliver:

- 18-workload correctness matrix
- repeated-query performance matrix
- comparison against Embree, OptiX, Vulkan, HIPRT, Apple RT where applicable
- honest report identifying wins, losses, and unsupported dimensions

## Risk Register

- Some workloads may not outperform mature backends.
- Some workloads need different data structures and should not share one layout.
- Performance must separate prepare time from query time.
- On macOS, Apple RT and Embree are available, but OptiX/Vulkan/HIPRT comparisons
  require Linux.
- A compatibility dispatcher alone is not a performance backend.
- CPU SIMD/native paths need explicit thread-safety and allocation discipline
  before they are used as reusable prepared contexts.
- The placeholder API name must be resolved before full-matrix release closure.

## Current Recommendation

Proceed, but do not call it complete until every workload has one of:

- native adaptive implementation with correctness and performance evidence
- documented technical blocker with 2+ AI consensus

The first implementation goal should be Goal585: `run_adaptive` skeleton and
support matrix, followed by Goal586 ray/triangle native kernels.
