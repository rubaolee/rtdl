# Goal 521: v0.8 Workload Scope Decision Matrix

Date: 2026-04-17

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal519 accepted the principle that RTDL should eventually attempt every
RT-accelerated workload family listed in arXiv `2603.28771v1` unless there is a
fundamental reason not to.

That does **not** mean every workload belongs in `v0.8`.

This goal defines the `v0.8` app-building scope before more implementation
continues. Every paper-listed workload gets one of four decisions:

- **do-now-v0.8**: implement as an app using the existing RTDL + Python model.
- **already-covered**: the workload family is already represented by an earlier
  released RTDL workload or existing v0.8 app; v0.8 may document it but should
  not reimplement it.
- **defer-version**: feasible, but needs a later focused version because it
  requires new language/runtime design, serious external baselines, or domain
  validation.
- **out-of-scope-until-reframed**: not appropriate as a direct RTDL app unless
  reframed into a bounded kernel role.

Every decision below requires 2+ AI consensus before it is considered closed.

## v0.8 Scope Rule

`v0.8` is for apps that can be written with the current released RTDL surface
plus Python orchestration:

- use existing ITRE kernels first
- no new language internals unless an app proves a reusable gap
- no full external systems
- correctness-first local fixtures are acceptable
- Linux performance closure is required only before making backend/performance
  claims for the new app
- public docs must state what RTDL owns and what Python owns

## Decision Matrix

| Paper workload | v0.8 decision | Reason |
| --- | --- | --- |
| kNN | already-covered | `knn_rows` is a released workload; Hausdorff and ANN candidate apps reuse it. No need to reimplement in v0.8. |
| FRNN | already-covered | `fixed_radius_neighbors` is a released workload; outlier and DBSCAN apps reuse it. |
| ANN | do-now-v0.8 | Current RTDL can express the query kernel as candidate-subset kNN reranking with `knn_rows` over a Python-selected candidate subset; app must honestly avoid claiming a full ANN index or recall-guaranteed ANN system. |
| Outlier Detection | do-now-v0.8 | Current RTDL can emit fixed-radius neighbor rows; Python can compute density counts and outlier labels. |
| DBSCAN | do-now-v0.8 | Current RTDL can emit fixed-radius neighbor rows; Python can perform core/border/noise expansion. |
| Graph Drawing | defer-version | Feasible as a force/proximity app, but needs a clear layout objective, iteration policy, and visual/output boundary; not needed before closing the first proximity package. |
| Line-Segment Intersection | already-covered | Released geometry surface already covers segment/segment and segment/polygon intersection-style rows. |
| Point in Polygon | already-covered | Released geometry surface already covers containment rows. |
| Discrete CD | already-covered | Robot collision screening represents bounded discrete collision screening over ray/triangle hit counts. Broader mesh CD can be a later geometry package. |
| Barnes-Hut | already-covered | Existing v0.8 app covers bounded one-level candidate generation and documents language gaps for full RT-BarnesHut. |
| BFS | already-covered | Released v0.6 graph line covers BFS; paper and RTDL docs both preserve performance-weak boundary. |
| Triangle Counting | already-covered | Released v0.6 graph line covers triangle counting. |
| Set Intersection | defer-version | Partially represented by graph triangle intersections, but generic set intersection needs separate semantics and performance-risk disclosure; Goal519's slow-case warning must survive into the eventual implementation gate. |
| Point Queries | defer-version | v0.7 DB/index work partially covers this, but paper-style point-query apps should be grouped with the future indexing package and PostgreSQL baselines. |
| Range Queries | defer-version | v0.7 DB predicates partially cover this, but standalone range-query apps need the future indexing package and serious baselines. |
| Index Scan | defer-version | v0.7 DB scan line partially covers this, but paper-style index scan deserves a separate PostgreSQL-inclusive correctness/performance gate. |
| Binary Search | defer-version | Feasible as abstract indexing, but paper results are mixed and the RT mapping needs careful value proof. |
| RMQ | defer-version | Requires reduction/index semantics not currently exposed as a first-class RTDL primitive. |
| Penetration Depth | defer-version | Needs robust closest-feature/contact semantics beyond current hit-count and neighbor rows. |
| Continuous CD | defer-version | Requires swept-volume/time-interval semantics beyond current discrete screening. |
| Point Location | defer-version | Feasible geometry/indexing app, but needs mesh/cell containment semantics and correctness baselines. |
| Voxelization | defer-version | Strong geometry candidate, but needs grid/voxel output contracts and likely backend-specific validation. |
| Non-euclidean kNN | defer-version | Needs a metric/embedding contract; exact high-dimensional/non-Euclidean claims would overreach current 2D/3D RT mappings. |
| SpMM | defer-version | Abstract sparse-matrix mapping has modest/mixed paper performance evidence and needs proof that RTDL adds value. |
| Particle Simulation | defer-version | Full simulation is a system; RTDL may provide neighbor/path kernels later after app boundary is designed. |
| Particle Tracking | defer-version | Direct ray/path candidate, but needs domain-specific path-step records and validation data. |
| Particle Transport | defer-version | Direct ray/path candidate, but needs material/interaction semantics and domain baselines. |
| Particle-Mesh Coupling | defer-version | Needs mesh/particle interaction records and multi-stage simulation orchestration. |
| Radio Wave Propagation | defer-version | Direct ray/path candidate, but needs material/reflection/attenuation semantics and validation data. |
| Infrared Radiation | defer-version | Direct ray/path candidate, but needs energy/material semantics and domain validation. |
| Space Skipping | out-of-scope-until-reframed | More likely internal acceleration infrastructure than a standalone user app; should be reframed as support for another workload. |
| Segmentation | out-of-scope-until-reframed | Too broad as stated; needs a bounded grid/filtering formulation before it is an RTDL app. |

## v0.8 App List Proposed For Closure

The proposed `v0.8` app list is:

- Hausdorff distance
- ANN candidate search
- outlier detection
- DBSCAN clustering
- robot collision screening
- Barnes-Hut force approximation

This list covers the workloads that are currently supportable without changing
the RTDL language internals and without pretending RTDL is a full external
system.

## Why Not Implement More In v0.8?

The deferred workloads are not rejected permanently. They are deferred because
they need one of:

- a new language/runtime primitive
- a new output contract
- a new domain baseline
- a new performance methodology
- a significant backend implementation package
- clearer reframing from a full system into an RTDL-owned kernel

Pushing those into `v0.8` would weaken the release by mixing app proof,
language design, backend engineering, and domain validation in one version.

## Consensus Requirement

Before this matrix is accepted:

- at least one Claude or Gemini review must judge whether the decisions are
  reasonable and honest
- Codex must write a consensus note
- any changed decision must carry a reason

After acceptance, `v0.8` app implementation should focus on finishing,
validating, documenting, and auditing the proposed app list, not expanding scope
without a new consensus gate.

## AI Consensus

- Claude review: `docs/reports/goal521_claude_review_2026-04-17.md`, verdict
  `PASS`.
- Gemini Flash review:
  `docs/reports/goal521_gemini_review_2026-04-17.md`, verdict `ACCEPT`.
- Codex review: accepted after incorporating Claude's non-blocking notes about
  ANN candidate-subset kNN reranking wording and future Set Intersection
  performance-risk disclosure.
