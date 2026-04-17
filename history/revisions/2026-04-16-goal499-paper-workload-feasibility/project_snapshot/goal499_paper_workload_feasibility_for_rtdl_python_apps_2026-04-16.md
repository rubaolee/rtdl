# Goal 499: Paper Workload Feasibility For RTDL + Python Apps

Date: 2026-04-16

Status: accepted planning report with AI consensus

## Source PDFs

The user supplied four local papers:

- `/Users/rl2025/Downloads/2026-xhd.pdf`
- `/Users/rl2025/Downloads/3620665.3640360.pdf`
- `/Users/rl2025/Downloads/3710848.3710885.pdf`
- `/Users/rl2025/Downloads/2409.09918v2.pdf`

Local text extraction was done with `pypdf` in a temporary build venv under
`build/pdf_extract_venv`; extracted text was written under `build/paper_text/`
for analysis only and is not a source artifact.

## Framing

These workloads are not being used to attack the RTDL language design. The
release question is:

Can an RTDL + Python application finish the workload, with RTDL owning the
accelerated query/kernel core and Python owning orchestration, data loading,
domain logic, and reporting?

If a workload cannot be finished with RTDL + Python, the result should identify
the exact missing layer:

- missing input/output data type
- missing RTDL kernel primitive
- missing backend lowering
- missing reduction/aggregation pattern
- missing prepared dataset reuse pattern
- performance-only gap rather than expressiveness gap
- domain code that correctly belongs in Python or an external library

## Executive Summary

| Paper | Workload | Current RTDL + Python feasibility | Recommended next-release status |
| --- | --- | --- | --- |
| X-HD | directed Hausdorff distance over large 2D/3D point sets | feasible as a bounded app using nearest-neighbor rows plus Python reduction; paper-level performance needs new prepared point-set and HD pruning primitives | strong first app candidate |
| Juno | high-dimensional ANN with IVF/PQ, sparse codebook selection, RT/Tensor pipeline | not feasible as a faithful RTDL app today; requires high-dimensional vector/PQ data model and sparse subspace selection primitive | roadmap/research candidate, not first app |
| RT-BarnesHut | Barnes-Hut force approximation via RT traversal over tree nodes | feasible only as a simplified app if Python builds the tree and RTDL filters/compacts candidate nodes; faithful version needs hierarchical node primitives and force-reduction support | medium/high-risk language-growth candidate |
| RT collision detection | discrete and continuous robot collision detection | bounded discrete-pose collision screening is a strong app candidate; continuous swept sphere/B-spline CCD needs new curve/sphere/swept-volume primitives | strong app candidate for DCD, defer CCD |

## Workload 1: X-HD Hausdorff Distance

Source: `/Users/rl2025/Downloads/2026-xhd.pdf`

### Paper Workload

X-HD computes directed Hausdorff distance between two point sets. For each point
in set `A`, it finds the nearest point in set `B`; the directed Hausdorff
distance is the maximum of those nearest-neighbor distances.

The paper maps HD to RT acceleration through nearest-neighbor style search, then
adds domain-specific optimizations:

- group spatially close points in a uniform grid
- build BVH objects from non-empty grid cells / AABBs
- use HD lower/upper-bound estimators to prune non-contributing points/cells
- selectively offload heavy-cell distance computation to a CUDA kernel for load
  balance

### What Data Becomes What Data

| Input | Output |
| --- | --- |
| point set `A`, point set `B` | one directed HD scalar |
| optionally both directions `A -> B` and `B -> A` | undirected HD scalar |
| per-point nearest distances | max-reduced HD result and optional witness pair |

### RTDL Should Own

- point-set candidate search
- nearest-neighbor or nearest-distance rows
- optional prepared point-set dataset for repeated HD queries
- emitted rows such as `point_id`, `neighbor_id`, `distance`

### Python Should Own

- reading image/geospatial/point-cloud data
- converting to RTDL point rows
- invoking one or two directed passes
- reducing nearest-distance rows into `max(distance)`
- reporting witness points and final scalar
- optional comparison against NumPy/SciPy/sklearn brute-force truth on small
  cases

### Current RTDL Fit

Current RTDL already has nearest-neighbor concepts (`fixed_radius_neighbors`,
`knn_rows`) and app-style Python composition. Therefore, a bounded HD app is
feasible now if it uses RTDL to generate nearest-neighbor rows and Python to
reduce them.

However, a faithful X-HD-style performance implementation needs more than the
current public language:

- direct `nearest_distance_rows(k=1)` or equivalent app-facing helper
- prepared point-set reuse for repeated directed passes
- grid-cell/AABB point grouping
- HD-specific pruning / estimator controls
- load-balance escape path for heavy cells on GPU

### Recommendation

Implement first as an app example, not as a new built-in workload:

- `examples/rtdl_hausdorff_distance_app.py`
- Python builds small point sets and calls RTDL nearest-neighbor kernel(s)
- Python computes directed and undirected HD
- correctness oracle: brute-force Python/NumPy for small point sets

Add a standard-library helper only if the app pattern repeats:

- `rtdsl.apps.directed_hausdorff(...)`
- later: native prepared dataset and RT backend specialization

## Workload 2: Juno High-Dimensional ANN

Source: `/Users/rl2025/Downloads/3620665.3640360.pdf`

### Paper Workload

Juno accelerates approximate nearest-neighbor search for high-dimensional vector
databases using IVF/PQ-style indexing. It reduces unnecessary distance
calculation by exploiting sparsity and locality in product-quantized subspaces,
then maps selective subspace entry lookup to RT cores. The paper also pipelines
RT-core selection with tensor-core computation.

### What Data Becomes What Data

| Input | Output |
| --- | --- |
| high-dimensional vectors, query vectors, IVF/PQ codebooks | top-k approximate neighbors |
| query projections plus subspace thresholds | selected codebook entries |
| selected entries plus encoded vectors | approximate distance scores |

### RTDL Should Own

Only if this becomes a real target:

- subspace threshold candidate selection
- RT-mapped sparse codebook entry lookup
- emitted candidate IDs / codebook-entry hits

### Python Should Own

- dataset ingestion
- IVF/PQ training or import from FAISS-like tooling
- codebook construction
- regression/threshold model training
- final top-k ranking and recall evaluation

### Current RTDL Fit

This is not a natural fit for current RTDL. Current RTDL is strongest on
2D/3D spatial geometry, nearest-neighbor rows, graph steps, and bounded DB-style
analytical kernels. Juno needs high-dimensional vector types, product
quantization, subspace codebooks, sparse LUT construction, and tensor-core
pipeline awareness.

RTDL + Python could build a toy ANN demo today, but it would not be faithful to
the paper's core contribution unless the language/runtime adds new vector/PQ
abstractions.

### Minimal Missing RTDL Additions

- `VectorBatch` / high-dimensional vector input type
- `PQCodebook` / encoded-vector data model
- `SubspaceQuery` / thresholded subspace probe type
- `subspace_radius_candidates` or `selective_codebook_entries` primitive
- top-k candidate scoring helper or emitted score rows

### Recommendation

Do not choose Juno as the first next-release app workload. Keep it as a roadmap
candidate for an RTDL vector-search line after the app-composition release proves
the easier spatial/graph/DB app pattern.

## Workload 3: RT-BarnesHut

Source: `/Users/rl2025/Downloads/3710848.3710885.pdf`

### Paper Workload

RT-BarnesHut accelerates Barnes-Hut `n`-body simulation by mapping tree nodes to
RT scene geometry and query bodies to rays. Unlike leaf-only nearest-neighbor
mappings, internal tree nodes contribute approximate force when accepted by the
Barnes-Hut opening criterion.

### What Data Becomes What Data

| Input | Output |
| --- | --- |
| bodies with position/mass | force or acceleration vector per body |
| quadtree/octree nodes with center-of-mass metadata | accepted force-contribution rows |
| timestep state | updated body positions/velocities after Python integration |

### RTDL Should Own

- candidate/accepted tree-node discovery for each body
- emitted contribution rows such as `body_id`, `node_id`, `mass`, `center`,
  `acceptance_kind`
- optionally force contribution calculation if a primitive exists

### Python Should Own

- building and updating the quadtree/octree
- storing body state
- timestep loop
- numerical integration
- validation against brute-force `O(n^2)` on small cases
- visualization/reporting

### Current RTDL Fit

A simplified RTDL + Python app is possible if Python builds tree nodes as
geometry-like records and RTDL is used only for candidate filtering. But a
faithful RT-BarnesHut workload requires current RTDL to grow:

- RTDL does not currently expose a public hierarchical tree-node input type.
- RTDL does not have a built-in Barnes-Hut opening predicate.
- RTDL does not have a force-vector reduction primitive.
- Current emitted rows are good for candidate discovery but not yet a full
  simulation-reduction model.

### Minimal Missing RTDL Additions

- `TreeNodes2D` / `TreeNodes3D` build input type
- `Bodies` probe input type if current point types are insufficient
- `barnes_hut_accept(theta=...)` predicate
- emitted force-contribution rows
- optional grouped vector-sum helper

### Recommendation

Use RT-BarnesHut as a medium-risk app-composition workload:

- start with 2D bodies
- Python builds quadtree and integrates timesteps
- RTDL emits accepted node/body contribution rows
- Python computes final force vectors initially
- only later move vector force reduction into RTDL if repeated app needs justify
  it

## Workload 4: RT Collision Detection

Source: `/Users/rl2025/Downloads/2409.09918v2.pdf`

### Paper Workload

The paper presents ray-traced robot collision detection:

- RT-DCD: discrete-pose mesh-to-mesh collision detection using rays along mesh
  triangle edges against the target mesh, with broad-phase OBB filtering and
  bidirectional checks for missed cases
- RT-CCD: continuous collision detection by tracing swept sphere-approximated
  robot volumes along piecewise-linear or B-spline trajectories against mesh
  obstacles

### What Data Becomes What Data

| Input | Output |
| --- | --- |
| robot link meshes, obstacle meshes, pose batch | collision boolean or hit rows per pose/link |
| transformed link edge rays and obstacle triangles | ray/triangle hit rows |
| sphere robot model plus path segments/curves | continuous path collision flags |

### RTDL Should Own

- ray/triangle candidate search and hit rows
- batched pose/link query core if the input type exists
- possibly mesh edge-ray generation if standardized
- emitted rows such as `pose_id`, `link_id`, `triangle_id`, `hit`

### Python Should Own

- robot model loading
- obstacle mesh loading
- forward kinematics
- pose/path batch construction
- OBB broad phase, at least initially
- bidirectional checking policy
- motion-planning integration
- output/visualization

### Current RTDL Fit

Bounded discrete-pose collision screening is a strong RTDL + Python app
candidate because it uses the same general shape as existing ray/triangle and
visual-demo work:

- Python prepares meshes and pose batches.
- Python emits rays along transformed mesh edges.
- RTDL performs ray/triangle hit detection.
- Python aggregates hits into collision booleans.

The faithful paper version still needs additions:

- public 3D mesh/triangle/ray tutorial surface if current public examples remain
  mostly 2D
- `ray_triangle_anyhit_rows` or boolean hit rows, not only hit counts
- batch IDs for pose/link rows
- optional OBB broad-phase helper
- for CCD: sphere/curve/swept-volume primitives

### Recommendation

Choose RT-DCD first and defer RT-CCD:

- next-release app: `rtdl_robot_collision_screening.py`
- bounded input: small mesh fixtures, small pose batch
- RTDL kernel: edge rays against obstacle triangles
- Python: FK/pose transform and collision aggregation
- correctness oracle: brute-force ray/triangle or simple mesh intersection on
  small fixtures

Do not attempt continuous swept sphere/B-spline CCD until RTDL has a clear
primitive story for spheres, curves, and swept volumes.

## Recommended Next-Release App Set

The next release should use three app workloads:

1. **Hausdorff Distance App**
   - low risk
   - mostly current RTDL nearest-neighbor + Python reduction
   - demonstrates RTDL as a spatial metric kernel inside Python

2. **Discrete Robot Collision Screening App**
   - medium risk
   - likely requires small public 3D ray/triangle row improvements
   - demonstrates RTDL as a batched geometry query core inside robotics-style
     Python orchestration

3. **2D Barnes-Hut Force Contribution App**
   - medium/high risk
   - likely requires new tree-node / contribution-row primitive
   - demonstrates RTDL + Python on hierarchical simulation, not just joins

Keep **Juno ANN** as a later vector-search roadmap item unless the next release
explicitly chooses to open a high-dimensional vector/PQ language line.

## Review Follow-Up

Claude review accepted the classification and specifically asked for one
pre-commit check: verify that the nearest-neighbor public surface used by the
X-HD recommendation exists. That check passed:

- `src/rtdsl/api.py` defines `fixed_radius_neighbors`, `knn_rows`, and
  `bounded_knn_rows` as public predicates.
- `src/rtdsl/__init__.py` exports all three predicates.
- `docs/tutorials/nearest_neighbor_workloads.md`,
  `docs/tutorials/feature_quickstart_cookbook.md`, and the public examples
  `examples/rtdl_fixed_radius_neighbors.py` and `examples/rtdl_knn_rows.py`
  already exercise the app-facing nearest-neighbor surface.

Claude also noted that RT-BarnesHut is better treated as medium/high risk rather
than medium risk because faithful support requires heterogeneous internal-node
geometry and reduction semantics that RTDL does not yet expose.

## Language Growth Rule For These Apps

When an app cannot be finished cleanly, add the smallest RTDL surface that
preserves the RTDL + Python boundary:

- prefer emitted candidate/contribution rows over hidden full-system behavior
- keep app orchestration in Python
- add reusable types/predicates only when at least one app proves the need
- do not add one-off paper-specific shortcuts that cannot become standard RTDL
  feature or library surfaces

## Immediate Implementation Plan

1. Build `rtdl_hausdorff_distance_app.py` using current nearest-neighbor rows
   and Python reduction.
2. Build a bounded `rtdl_collision_screening_app.py` prototype with small
   triangle/ray fixtures and decide whether a new `ray_triangle_anyhit_rows`
   primitive is required.
3. Prototype `rtdl_barnes_hut_2d_app.py` with Python-built quadtree and
   RTDL-emitted candidate/contribution rows.
4. Write correctness oracles for all three apps before any performance claims.
5. Only after app correctness is proven, decide which new RTDL primitives belong
   in the language/standard library.

## Verdict

The four uploaded papers are useful for next-release planning, but they are not
equally ready for immediate RTDL + Python implementation. X-HD and RT-DCD are
the best near-term app workloads. RT-BarnesHut is a good controlled language
growth workload. Juno requires a larger vector/PQ direction and should not be
the first implementation target unless the release scope changes.
