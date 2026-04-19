# RTDL Capability Boundaries

This page explains what RTDL can do today, what it can technically be used for
but is not intended to become, and what it cannot do yet.

RTDL is a language/runtime for expressing non-graphical spatial,
geometric-query, graph, and bounded analytical workloads that can be lowered to
ray-tracing-style traversal and refinement. Python remains the application
host: it loads data, calls RTDL kernels, checks results, reduces rows, and
connects the kernel result to the rest of an application.

## Short Version

| Category | Meaning | Examples |
| --- | --- | --- |
| Can do and intended | Released or directly aligned with the RTDL design | spatial joins, nearest-neighbor rows, graph BFS/triangle counting, bounded DB-style scans/groups |
| Can do but not intended as RTDL's role | Possible when RTDL is used as a kernel inside a larger Python app, but RTDL should not become the whole system | rendering demos, robotics app orchestration, database-style workflows, full simulations |
| Cannot do yet | Missing language types, predicates, reductions, or backend lowering | full SQL DBMS behavior, general rendering, high-dimensional ANN/PQ, continuous swept-volume collision detection, general HIPRT or Apple RT backend coverage |

## What RTDL Can Do And Intends To Do

RTDL is intended to express workloads where the hard part is structured
candidate discovery and refinement over geometric, spatial, graph, or bounded
analytical data.

### Geometry And Spatial Query Kernels

RTDL can express and run released geometry workloads such as:

- line-segment intersection
- point-in-polygon
- segment/polygon hit counting
- segment/polygon any-hit rows
- polygon overlap seed rows
- polygon-set Jaccard under the documented bounded contract
- point-nearest-segment rows
- ray/triangle hit-count style kernels

The intended use is not to replace a GIS system. The intended use is to make
the ray-tracing-style candidate/refine kernel easier to write and run across
supported backends.

### Nearest-Neighbor Kernels

RTDL can express nearest-neighbor style workloads such as:

- `fixed_radius_neighbors`
- `knn_rows`
- `bounded_knn_rows`

These are suitable for applications that need neighbor rows, ranked neighbor
rows, or radius-bounded candidate rows. Python can then reduce, aggregate, or
post-process those rows into application answers such as assignment decisions,
Hausdorff-distance summaries, or local neighborhood metrics.

The current v0.8 ANN candidate app is inside this nearest-neighbor boundary:
Python selects a bounded candidate subset, RTDL ranks that subset with
`knn_rows(k=1)`, and Python reports recall and distance-ratio metrics. This is
candidate-subset reranking, not a full ANN index.

### Graph Kernels

RTDL can express the released graph workload family:

- BFS frontier expansion
- triangle counting / triangle matching

The graph line is intended to show that the RTDL traversal/refine model can
cover graph workloads whose core step can be mapped into RT-style candidate
discovery or intersection-like work. RTDL is not trying to become a full graph
database or graph-processing framework.

### Bounded DB-Style Analytical Kernels

RTDL `v0.7.0` can express a bounded database-style analytical family:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

These are RTDL kernels over bounded row data. They are useful for exploring how
selection and simple grouping can be converted into ray-tracing-style traversal
and candidate filtering.

RTDL is not a DBMS. It does not provide transactions, SQL parsing, query
optimization, storage management, concurrency control, indexes as a database
would define them, or durability. PostgreSQL is used as an external correctness
and timing baseline, not as an RTDL backend.

### RTDL + Python Applications

RTDL is intended to be used inside Python applications:

- Python loads and normalizes data.
- Python declares or calls RTDL kernels.
- RTDL owns the heavy traversal/refine kernel.
- Python reduces rows and implements domain-specific application logic.

This is the expected model for new app workloads from papers: if the workload's
core query can become RTDL rows, Python should own the rest.

Current accepted v0.8 examples of this model are Hausdorff distance, ANN
candidate search, outlier detection, DBSCAN clustering, robot collision
screening, and Barnes-Hut force approximation. Their backend and performance
boundaries are recorded in Goal507, Goal509, and Goal524.

The released `v0.9.0` HIPRT backend also fits this intended direction.
`run_hiprt` now covers the 18-workload Linux HIPRT matrix, while
repeated-query `prepare_hiprt` currently covers prepared 3D ray/triangle
hit-count, prepared 3D fixed-radius nearest-neighbor, prepared graph CSR paths,
and prepared bounded DB table reuse.

The released `v0.9.1` Apple RT slice also fits this direction. It began with
3D `ray_triangle_closest_hit` through Apple Metal/MPS on macOS Apple Silicon.
Current v0.9.2 candidate work expands the native Apple slices to 3D hit-count
and 2D segment-intersection and adds prepared/masked performance work, while the
rest of the current Apple dispatcher remains compatibility mode.

## What RTDL Can Do But Is Not Intended To Become

Some things are possible with RTDL as a component, but they should not become
RTDL's job.

### Rendering And Visual Demos

RTDL can power visual demos when the RTDL part is the geometric/ray query core.
For example, a Python demo may use RTDL to compute ray/triangle or hit-count
results and then use Python to create frames or videos.

RTDL is not intended to become:

- a renderer
- a graphics engine
- a shader language
- a material system
- an animation system
- a scene editor

Visual demos are valid only when RTDL remains the compute/query kernel and
Python owns scene setup, shading, animation, and media output.

### Database-Like Applications

RTDL can run bounded DB-style kernels and can be compared against PostgreSQL.
It can be embedded in apps that load table-like rows, prepare an RT dataset,
run bounded predicates, and emit result rows.

RTDL is not intended to become:

- PostgreSQL
- SQLite
- a transactional database
- a SQL optimizer
- a storage engine
- a general BI system

If an application needs a real DBMS, use a real DBMS and use RTDL only for the
specific kernel where RT traversal is the point.

### Robotics Or Simulation Applications

RTDL can be used inside robotics or simulation apps when the core operation is
a geometric query, such as discrete collision screening or ray/triangle checks.

RTDL is not intended to own:

- robot model loading
- forward kinematics
- planning loops
- timestep integration
- physics state management
- visualization

Those belong in Python or domain libraries. RTDL should own the kernel rows
that are worth lowering to a ray-tracing-style backend.

### End-To-End Application Frameworks

RTDL can help build applications, but it is not intended to become an
application framework. It should not grow paper-specific one-off shortcuts that
hide the domain application inside RTDL. New primitives should become part of
the language or standard-library surface only when they are reusable across
workloads.

## What RTDL Cannot Do Yet

This section is intentionally direct. A user should not need to infer these
limits from old reports.

### Full SQL Or Full Database Systems

RTDL cannot run arbitrary SQL. It cannot currently support joins, nested
queries, transactions, indexes, persistence, query planning, or full database
administration. The current DB-style line is a bounded analytical kernel
surface, not a database product.

### General High-Dimensional Vector Search

RTDL does not yet have the language surface for faithful high-dimensional ANN
systems such as IVF/PQ pipelines, product-quantized codebooks, sparse subspace
selection, or tensor-core scoring pipelines. A toy vector-search demo may be
possible in Python, but it would not be faithful RTDL support for that class.

The v0.8 ANN candidate app does not contradict this limit. It is a bounded
candidate-subset reranking example over existing nearest-neighbor rows, not
FAISS, HNSW, IVF, PQ, or learned/vector-index support.

### Continuous Swept-Volume Collision Detection

RTDL can support bounded discrete ray/triangle-style collision screening more
naturally than continuous collision detection. Continuous swept sphere,
B-spline, curve, or swept-volume collision detection needs new primitives and
backend lowering before it can be claimed as an RTDL capability.

The current v0.8 robot screening app is inside the bounded discrete case:
CPU/Embree/OptiX are correctness-gated in Goal509, while Vulkan is not exposed
for that app until its per-edge hit-count mismatch is fixed.

### Full Barnes-Hut Or General N-Body Simulation

RTDL can potentially help discover candidate tree-node/body contribution rows,
but it does not yet expose a full hierarchical tree-node input type,
Barnes-Hut opening predicate, force-vector reduction primitive, or timestep
simulation model. Python can build a simplified app around RTDL rows, but RTDL
cannot honestly claim faithful Barnes-Hut acceleration yet.

Goal509 measures that simplified app by separating RTDL candidate generation
from Python opening-rule and force-reduction work. That evidence supports
candidate-row generation, not full N-body solver acceleration.

### Arbitrary Data Types And Arbitrary Predicates

RTDL does not support arbitrary Python objects or arbitrary user predicates in
accelerated backends. Current kernels depend on bounded, typed inputs and
predicates that the runtime knows how to lower. New data types such as strings,
dates, curves, spheres, meshes with rich metadata, or high-dimensional vectors
need explicit language and backend support before performance claims are valid.

### Closest-Hit / RTXRMQ Coverage

The released `v0.9.0` line includes a bounded `ray_triangle_closest_hit`
primitive for 3D ray/triangle workloads on the CPU Python reference, `run_cpu`,
and Embree backend. Goal573 uses it to express an exact RTXRMQ-style
range-minimum query gate from `/Users/rl2025/Downloads/2306.03282v1.pdf`.

The current boundary is backend coverage, not language shape: OptiX, Vulkan,
and HIPRT still need native closest-hit kernels before RTDL can claim full
four-backend RTXRMQ support.

The released `v0.9.1` Apple RT slice adds one native closest-hit path through
Apple Metal/MPS, and current v0.9.2 candidate work adds prepared closest-hit
reuse. That does not change the remaining OptiX, Vulkan, and HIPRT closest-hit
gaps.

### HIPRT Backend Coverage

The released `v0.9.0` HIPRT backend can use `run_hiprt` for the 18-workload
Linux HIPRT matrix on a HIPRT-SDK setup. It cannot yet claim AMD GPU hardware
validation, HIPRT CPU fallback, RT-core speedup evidence from the tested GTX
1070 path, OptiX/Vulkan/HIPRT native closest-hit support, or broader prepared
HIPRT reuse beyond the prepared 3D ray/triangle, 3D fixed-radius
nearest-neighbor, graph CSR, and bounded DB table paths.

### Apple RT Backend Coverage

The released `v0.9.1` Apple RT slice can use `run_apple_rt` for 3D
`ray_triangle_closest_hit` on Apple Silicon macOS after `make build-apple-rt`.
Goal582 extends the dispatcher so all 18 current RTDL predicates are callable
through `run_apple_rt` on Apple Silicon macOS. Goal583 adds native Apple MPS RT
for 3D `ray_triangle_hit_count`. Goal590 adds native Apple MPS RT for 2D
`segment_intersection` by tracing left segments against extruded right-segment
quadrilaterals and then applying analytic intersection refinement. The current
native modes are therefore 3D closest-hit, 3D hit-count, and 2D
segment-intersection. Current v0.9.2 candidate performance work adds prepared
closest-hit reuse and masked chunked nearest-hit traversal for hit-count and
segment-intersection. The broader 2D geometry, nearest-neighbor, graph, and DB
paths are currently `cpu_reference_compat`.

It cannot yet claim broad native Apple RT parity, Apple hardware speedup
evidence, non-macOS support, or hardware-backed Apple RT support for the
broader workload matrices.

### Automatic Speedups For Every Workload

RTDL does not promise that every RTDL kernel is faster than every CPU or
database baseline. Some current paths are correctness-credible but not
performance-leading. Performance claims must name:

- workload
- backend
- dataset size
- host machine
- setup/preparation cost
- query cost
- baseline used for comparison

The strongest RTDL claim is about making RT-style workloads easier and more
portable to write while preserving an honest path to backend acceleration.

## How To Decide If A New Workload Belongs In RTDL

A workload is a good RTDL target if most answers are "yes":

- Does it have a candidate-discovery step that resembles traversal,
  intersection, containment, nearest-neighbor search, or bounded scan?
- Can the heavy part emit rows that Python can reduce or post-process?
- Can its inputs be represented as bounded typed records?
- Can it benefit from prepared data reuse or backend acceleration?
- Can correctness be checked against a simple oracle on small cases?

A workload should stay mostly in Python or an external system if most answers
are "yes":

- Is the hard part orchestration, I/O, training, scheduling, optimization, or
  domain policy rather than traversal/refinement?
- Does it require arbitrary SQL, arbitrary Python predicates, or mutable system
  state?
- Would implementing it require RTDL to become a renderer, DBMS, robotics
  stack, graph database, or full simulation engine?

## Design Rule

When RTDL grows, it should grow by adding reusable language or standard-library
surfaces:

- new input types
- new predicates
- new emitted row shapes
- new reduction helpers
- new prepared-dataset patterns
- new backend lowering paths

It should not grow by hiding complete applications inside special-case
primitives. RTDL should make the kernel 10x easier to write; Python should keep
the application understandable.
