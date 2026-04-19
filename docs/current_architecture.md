# RTDL Current Architecture

This is the current public architecture page for users evaluating RTDL.
Historical architecture reports are preserved elsewhere, but this page explains
the released `v0.7.0` design, the released `v0.8.0` app-building layer, the
released `v0.9.0` HIPRT / closest-hit expansion, and the released `v0.9.1`
Apple RT closest-hit slice on top of it.

For a direct capability boundary, including what RTDL can do, can help with but
should not become, and cannot do yet, read
[RTDL Capability Boundaries](capability_boundaries.md).

## The User Contract

RTDL is a Python-hosted language/runtime for workloads that can be expressed as
ray-tracing-style search:

1. declare probe-side data
2. declare build-side data
3. traverse an acceleration structure
4. refine candidate hits with workload semantics
5. emit rows for the surrounding application

The intended benefit is a **10x reduction in authoring burden** for modern
ray-tracing workloads. Instead of hand-writing separate Embree, OptiX, Vulkan,
HIPRT, Apple RT, and CPU code paths, the user writes one RTDL kernel shape and
chooses a backend when running it.

This is not a blanket performance claim. Performance depends on workload,
backend, host hardware, data shape, and preparation strategy. The release
reports define the exact current performance evidence.

## What RTDL Owns

RTDL owns the workload core:

- kernel declaration
- typed inputs
- traversal intent
- refinement predicates
- emitted row shape
- backend dispatch
- native prepared datasets where supported
- correctness comparison against oracle and external baselines

For released workload families, RTDL also owns the backend-specific lowering
needed to reach CPU/oracle, Embree, OptiX, and Vulkan surfaces where those
backends are supported.

The released `v0.9.0` HIPRT work provides `run_hiprt` Linux parity coverage for
the current 18-workload HIPRT matrix. It does not claim AMD GPU validation,
RT-core speedup evidence, CPU fallback, or OptiX/Vulkan/HIPRT support for the
new closest-hit primitive.

The released `v0.9.1` Apple RT work provides `run_apple_rt` for 3D
`ray_triangle_closest_hit` through Apple Metal/MPS on macOS Apple Silicon. It
does not claim full Apple backend parity or performance speedup yet.

The post-`v0.9.1` Goal582 development line makes `run_apple_rt` callable for
all 18 current RTDL predicates on Apple Silicon macOS. That is a dispatch
coverage step, not full hardware parity: 3D closest-hit is `native_mps_rt`, 3D
hit-count is `native_mps_rt_3d_else_cpu_reference_compat`, and other predicates
are currently `cpu_reference_compat` and are rejected when `native_only=True`.

## What Python Owns

Python remains the application layer:

- data loading
- fixture construction
- app control flow
- multi-step orchestration
- presentation, files, plots, and videos
- post-processing around emitted rows

The design goal is that Python should be thin during heavy work. Heavy
candidate search, traversal, and backend-specific execution belong in RTDL
kernels and native backend paths, not in Python loops.

## Backend Roles

| Backend or system | Role |
| --- | --- |
| `cpu_python_reference` | slowest, clearest truth path that should run broadly |
| `cpu` / oracle | compiled C/C++ correctness baseline |
| Embree | CPU ray-tracing backend |
| OptiX | NVIDIA GPU ray-tracing backend on supported Linux/GPU hosts |
| Vulkan | portable GPU ray-tracing backend on supported Linux/GPU hosts |
| HIPRT | released Linux HIPRT-SDK path for the v0.9 18-workload `run_hiprt` matrix |
| Apple RT | released macOS Apple Silicon Metal/MPS slice for 3D closest-hit; post-v0.9.1 compatibility dispatch for the broader 18-predicate surface |
| PostGIS / PostgreSQL | external correctness and timing baselines, not RTDL backends |

## Workload Families

Current released public workload families include:

- geometry: segment/polygon, overlap, Jaccard-boundary cases, ray/triangle
  hit-count style kernels
- nearest neighbor: fixed-radius neighbors and KNN rows
- graph: bounded BFS expansion and triangle-count probe kernels
- DB-style analytics: bounded conjunctive scan, grouped count, and grouped sum
- closest-hit: exact bounded RTXRMQ-style range-minimum query on CPU reference,
  `run_cpu`, and Embree

The released HIPRT backend covers the v0.9 18-workload `run_hiprt` matrix.
The prepared HIPRT API is narrower: `prepare_hiprt` currently covers Ray3D
probes against Triangle3D build geometry emitting per-ray hit-count rows, plus
Point3D probe batches against prepared Point3D build sets for fixed-radius
nearest-neighbor rows, prepared graph CSR build data for BFS discovery and
triangle-match query batches, and prepared bounded DB table reuse for
conjunctive scan, grouped count, and grouped sum.

The released Apple RT native slice started with 3D `ray_triangle_closest_hit`
over Ray3D/Triangle3D data. Goal582 adds broad callable dispatch through CPU
reference compatibility for the other current predicates, and Goal583 adds
native Apple MPS RT execution for 3D `ray_triangle_hit_count`.

Each family is documented with its own current support boundary. Not every
backend/workload/platform combination has the same maturity.

The current `v0.8.0` app-building release demonstrates how those released
features can be used inside Python applications without changing language
internals first. Current examples include Hausdorff distance over `knn_rows`,
ANN candidate search over `knn_rows`, outlier detection and DBSCAN over
`fixed_radius_neighbors`, robot collision screening over `ray_triangle_hit_count`,
and Barnes-Hut force
approximation over `fixed_radius_neighbors`.

The programming-model claim is intentionally bounded: the accepted
`input -> traverse -> refine -> emit` shape is sufficient for the RTDL-owned
query/traversal kernel in those apps, while Python remains responsible for app
orchestration, construction, reductions, and output. See
[ITRE App Programming Model](rtdl/itre_app_model.md).

The current performance evidence for that app-building line is intentionally
phase-specific: Hausdorff reports nearest-neighbor app performance, robot
collision accepts CPU/Embree/OptiX and rejects Vulkan for hit-count mismatch,
Barnes-Hut separates RTDL candidate-generation timing from Python opening-rule
and force-reduction timing, and the Stage-1 proximity apps have bounded Linux
CPU/oracle, Embree, OptiX, and Vulkan timing characterization through Goal524.
Goal524 is not an external-baseline speedup claim; SciPy was absent in that
validation checkout, and no claim is made against SciPy, scikit-learn, FAISS,
or production ANN/clustering systems.

## How A Workload Becomes RT Work

RTDL lowers a user-level workload into a backend-specific ray-tracing search
problem:

- build-side records become acceleration-structure primitives or encoded
  searchable geometry
- probe-side records become rays, query boxes, or workload-specific probe
  records
- traversal finds candidate row pairs or row IDs
- refinement applies the exact workload rule for the bounded release contract
- emission returns stable rows to the Python application

For DB-style workloads, this means bounded predicates and grouped aggregations
are mapped into RT-style candidate discovery plus exact post-traversal checks.
RTDL is still not a DBMS and does not execute arbitrary SQL.

## Current Boundaries

Use RTDL today when you want a compact language/runtime surface for released
ray-tracing-style workloads and you are willing to stay inside documented
release bounds.

Do not read the current system as:

- a general-purpose renderer
- a database management system
- an arbitrary SQL engine
- a proof that every backend is faster for every workload
- a claim that every platform has identical backend coverage
- a claim that HIPRT is AMD-validated, RT-core-accelerated on the tested GTX
  1070 path, a CPU fallback backend, or a native closest-hit backend today
- a claim that Apple RT has full native workload parity or measured speedup
  beyond the current 3D closest-hit slice

For exact release claims, read:

- [RTDL Capability Boundaries](capability_boundaries.md)
- [v0.8 App Building](tutorials/v0_8_app_building.md)
- [ITRE App Programming Model](rtdl/itre_app_model.md)
- [v0.9 Support Matrix](release_reports/v0_9/support_matrix.md)
- [v0.9 Release Package](release_reports/v0_9/README.md)
- [v0.8 Release Statement](release_reports/v0_8/release_statement.md)
- [v0.8 Support Matrix](release_reports/v0_8/support_matrix.md)
- [v0.7 Release Statement](release_reports/v0_7/release_statement.md)
- [v0.7 Support Matrix](release_reports/v0_7/support_matrix.md)
- [Release-Facing Examples](release_facing_examples.md)
