# Goal 521: Claude Review — v0.8 Workload Scope Decision Matrix

Date: 2026-04-17

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **PASS**

## Coverage Check

Goal519 lists 32 distinct non-graphics RT-core workloads. Goal521's decision matrix accounts for all 32. No workload is missing or double-counted.

## Decision-by-Decision Assessment

**already-covered (8 workloads)**

All eight are consistent with Goal519's "covered" or "covered but performance-weak" readouts:

- kNN, FRNN: released primitives; reused by the new v0.8 apps.
- Line-Segment Intersection, Point in Polygon: released geometry surface.
- BFS: released v0.6 graph line; Goal521 correctly preserves the performance-weak boundary.
- Triangle Counting: released v0.6 graph line.
- Discrete CD: robot collision screening is the correct representative app for bounded discrete hit-count screening.
- Barnes-Hut: existing v0.8 app is the correct representative; gap to full RT-BarnesHut is honestly documented.

No already-covered label overstates what RTDL has actually shipped.

**do-now-v0.8 (3 workloads)**

ANN, Outlier Detection, DBSCAN are all expressible with `knn_rows` / `fixed_radius_neighbors` plus Python orchestration, which matches Goal519's "not yet — likely near-term app" assessment. The ANN entry explicitly disclaims a full ANN index, which is the critical honesty gate. The acceleration of these three from Goal519's "Stage 1 / v0.9" into v0.8 is justified because they need no new language internals and Goal521's v0.8 scope rule permits exactly this. This is not scope creep; it is the correct reading of what the current surface can support.

**defer-version (19 workloads)**

Every deferral cites a concrete missing requirement (language primitive, output contract, domain baseline, backend package, or value-proof). The groupings are rational:

- DB/indexing cluster (Set Intersection, Point Queries, Range Queries, Index Scan, Binary Search, RMQ): correctly deferred together pending PostgreSQL-baseline methodology.
- Geometry/collision cluster (Penetration Depth, Continuous CD, Point Location, Voxelization, Non-euclidean kNN): correctly deferred pending geometry/metric primitives.
- Simulation/wave/particle cluster (Particle Simulation, Particle Tracking, Particle Transport, Particle-Mesh Coupling, Radio Wave Propagation, Infrared Radiation): correctly deferred pending path-step and domain-semantics design.
- SpMM, Graph Drawing: correctly deferred with honest performance-risk and design-gap reasons.

No deferral looks like avoidance of a workload that could actually be done today with existing RTDL primitives.

**out-of-scope-until-reframed (2 workloads)**

- Space Skipping: correct; it is support infrastructure, not a user-facing kernel.
- Segmentation: correct; the label is too broad and requires a bounded grid/filtering formulation before it can be an RTDL app.

## v0.8 App List

The proposed list — Hausdorff, ANN candidate, outlier detection, DBSCAN, robot collision screening, Barnes-Hut — is coherent. All six are expressible without changing RTDL language internals. The list matches Goal519's immediate recommendation (ANN / outlier / DBSCAN) and the earlier v0.8 app boundary (Hausdorff, robot, Barnes-Hut). It is neither under-scoped nor inflated.

## Honesty Assessment

The matrix does not hide partial coverage behind full-coverage labels. Every "partially covered" workload in Goal519 maps to defer-version, not already-covered. Performance-weak and break-even risks (BFS, SpMM, Set Intersection) are preserved or explicitly noted. No app in the do-now list claims capabilities it cannot deliver with the current surface.

## Non-Blocking Notes

1. The ANN entry should carry a short public-docs note distinguishing "candidate-subset kNN reranking" from "approximate nearest neighbor indexing with recall guarantees." This is implied by the matrix but should be stated explicitly in the app documentation when written.
2. The Set Intersection deferral reason mentions "performance-risk disclosure." Goal519 flags this as a case where paper evidence includes slow cases. The performance-risk disclosure requirement should survive into the eventual v1.0 implementation gate, not just the deferral note.

Neither note blocks acceptance. The matrix is complete, honest, and sufficient to close the v0.8 app list.
