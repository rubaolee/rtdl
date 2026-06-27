# Goal 519: RT Workload Universe From arXiv 2603.28771v1

Date: 2026-04-17

Status: accepted after Claude/Gemini/Codex consensus

Source paper:

- `/Users/rl2025/Downloads/2603.28771v1.pdf`
- Title: *Ray Tracing Cores for General-Purpose Computing: A Literature Review*
- arXiv ID in PDF metadata: `2603.28771v1`

## Purpose

This goal converts the paper's comprehensive RT-accelerated workload list into
an RTDL project roadmap.

The project direction is:

**RTDL should eventually attempt all workload families from the paper unless
there is a fundamental reason not to.**

For each family, the required lifecycle is:

1. propose the bounded RTDL formulation
2. plan the feature/app boundary
3. implement an app or primitive
4. test correctness
5. verify performance honestly
6. document public usage and limits
7. run whole-system release audit before release

## Paper Takeaways Relevant To RTDL

The paper identifies 32 distinct non-graphics RT-core problems. Its broad
guidance aligns strongly with RTDL's current design:

- RT mappings usually have three parts:
  - represent data as geometric objects
  - map queries to ray launches
  - interpret intersections as operations or query results
- The best candidates exploit BVH pruning and work reduction.
- Nearest-neighbor and proximity variants are the strongest broad family.
- Heuristic/approximate workloads can benefit because they reduce work.
- Latency-bound graph-style workloads are weaker performance candidates.
- Future RTDL kernels should prefer many short rays over a few long rays when
  the workload can be formulated either way, because the paper identifies this
  as a practical RT-core design principle.
- The rigid RT-core model, lack of internal BVH-node access, FP32 geometry, 3D
  coordinate limits, and context switching between RT/CUDA are real limits.

This is consistent with our ITRE boundary:

- RTDL owns the `input -> traverse -> refine -> emit` kernel.
- Python owns orchestration, construction, reductions, and output.

## Current RTDL Coverage Against The Paper

| Paper workload | RTDL status | Readout |
| --- | --- | --- |
| Line-Segment Intersection | covered | RTDL has segment/polygon and line/segment-style spatial join surfaces from earlier releases. |
| Point in Polygon | covered | RTDL has point/polygon and spatial join surfaces. |
| FRNN | covered | `fixed_radius_neighbors`. |
| kNN | covered | `knn_rows`; Hausdorff app uses `k=1`. |
| BFS | covered but performance-weak | v0.6 graph line supports BFS; paper also warns BFS is often latency-bound and weak for RT. |
| Triangle Counting | covered | v0.6 graph line supports triangle counting. |
| Set Intersection | partially covered | triangle-count graph intersections and spatial joins cover some forms; generic set intersection should be a future bounded primitive/app; paper evidence includes slow cases, so performance claims must be re-proven. |
| Range Queries | partially covered | v0.7 DB predicates and spatial filters cover bounded forms; standalone index/range-query workload remains future work. |
| Point Queries | partially covered | point/location/query-style workloads exist, but dedicated database/index point-query app should be added. |
| Index Scan | partially covered | v0.7 DB scan/aggregation line covers bounded scans; paper-style index scan deserves separate app/benchmark. |
| Barnes-Hut | app-level partial | v0.8 has bounded one-level candidate-generation app; full RT-BarnesHut requires language growth. |
| Discrete Collision Detection | app-level partial | v0.8 robot collision screening covers bounded discrete ray/triangle hit-count screening. |
| Continuous Collision Detection | not yet | requires swept-volume/time-interval collision semantics. |
| ANN | not yet | likely near-term app over approximate/proximity rows. |
| Non-euclidean kNN | not yet | likely future metric/plugin work; exact formulation depends on embeddability. |
| Outlier Detection | not yet | likely app over FRNN/kNN density rows. |
| DBSCAN | not yet | likely app over FRNN neighborhood rows plus Python clustering. |
| Graph Drawing | not yet | likely app over proximity/collision/force-style rows; heuristic family. |
| Point Location | not yet | likely geometric primitive/app over spatial cell/mesh containment. |
| Penetration Depth | not yet | collision/geometry primitive; may require robust closest-feature queries. |
| SpMM | not yet | abstract indexing/matrix mapping; possible but needs careful proof of value; paper evidence is modest and includes near-break-even cases. |
| Binary Search | not yet | abstract indexing mapping; paper suggests mixed results. |
| RMQ | not yet | abstract index structure; likely language/reduction/indexing growth. |
| Particle Simulation | not yet | simulation app; may use neighbor/collision kernels first. |
| Particle Tracking | not yet | direct ray/path style app candidate. |
| Particle-Mesh Coupling | not yet | simulation app requiring mesh/particle interaction semantics. |
| Particle Transport | not yet | direct ray/path simulation app candidate. |
| Radio Wave Propagation | not yet | direct ray/path simulation app candidate. |
| Infrared Radiation | not yet | direct ray/path simulation app candidate. |
| Space Skipping | not yet | visualization/acceleration helper; may be support infrastructure rather than public app. |
| Segmentation | not yet | grid/visualization-style app; needs clear non-computer-vision boundary. |
| Voxelization | not yet | strong geometric app candidate. |

## Fundamental Out-Of-Scope Boundaries

The project should attempt all workload families except where the target would
contradict RTDL's scope. Current fundamental boundaries are:

- **Hardware modification papers**: extending RT cores or changing GPU
  architecture is out of scope. RTDL targets available Embree/OptiX/Vulkan/CPU
  software surfaces.
- **Full systems**: RTDL should not become a DBMS, renderer, robotics stack,
  particle simulator, or clustering framework. It can provide kernels/apps
  inside those systems.
- **Arbitrary high-dimensional exact geometry**: RT cores expose 3D-ish spatial
  traversal. Higher-dimensional exact problems need bounded embeddings,
  approximations, or clear rejection.
- **Algorithms requiring internal BVH-node programmability**: current RT cores
  do not expose internal traversal-node hooks. RTDL can approximate by encoding
  nodes as leaves, but must not claim the same capability as hypothetical
  hardware changes.
- **Performance-impossible claims**: latency-bound workloads such as BFS may be
  supported for language completeness without claiming RT acceleration wins.

## Proposed Roadmap

### Stage 0: Close v0.8 As App-Building Foundation

Current v0.8 should remain focused:

- app-building proof using existing RTDL features
- ITRE boundary documented
- public command surface validated
- Linux full public command validation complete

Do not overload v0.8 with the whole paper taxonomy.

### Stage 1: v0.9 Proximity And Heuristic Apps

These best match the paper's strongest categories and current RTDL surface:

- ANN app
- Outlier detection app
- DBSCAN app
- Graph drawing / force-layout screening app
- fuller Hausdorff variants if needed

Expected RTDL growth:

- reusable neighborhood-row schemas
- optional approximate result contracts
- app-level repeated-query/prepared dataset patterns

### Stage 2: v1.0 Indexing And DB-Style Query Apps

This extends the v0.7 DB work toward the paper's indexing family:

- point query app
- range query app
- index scan app
- generic set intersection app
- binary search / RMQ feasibility studies

Expected RTDL growth:

- index-key encodings
- multi-predicate bundles
- prepared-index dataset lifecycle
- PostgreSQL and CPU baselines as mandatory correctness/performance anchors

### Stage 3: v1.1 Collision And Geometry Apps

These connect the robot app to broader geometry/collision workloads:

- penetration depth
- discrete collision detection beyond the current bounded robot screening app
- continuous collision detection
- point location
- voxelization

Expected RTDL growth:

- robust closest-feature rows
- swept/time-interval predicates
- mesh-cell containment rows
- stronger geometric precision boundaries

### Stage 4: v1.2 Simulation And Wave/Particle Apps

These are direct ray/path style candidates but require domain-specific app
orchestration:

- particle tracking
- particle transport
- particle simulation
- particle-mesh coupling
- radio wave propagation
- infrared radiation

Expected RTDL growth:

- path-step kernels
- material/interaction records
- multi-stage iteration orchestration
- energy/weight accumulation rows

### Stage 5: Support/Infrastructure Workloads

These may become internal capabilities before public apps:

- space skipping
- segmentation-like grid filtering
- dexelization/voxel-like intermediate formats

Expected RTDL growth:

- grid/voxel input families
- occupancy rows
- acceleration-helper APIs

## Per-Workload Lifecycle Template

Every new workload family should use this gate sequence:

1. **Proposal**: paper source, RT mapping, what data becomes what data.
2. **Plan**: app-only vs language primitive vs backend runtime work.
3. **Implementation**: Python app first if ITRE can express the kernel; language
   growth only when repeated apps prove the gap.
4. **Correctness**: Python reference plus domain baseline; PostgreSQL/PostGIS or
   SciPy/NetworkX/FAISS/etc. where appropriate.
5. **Performance**: Linux first; compare against serious non-RT baselines.
6. **Docs**: examples, tutorial, capability boundary, release-facing command.
7. **Verification**: Claude/Gemini/Codex consensus.
8. **Whole-system audit**: public docs, command truth, history, release wording,
   full/targeted tests before release.

## Immediate Recommendation

After the current v0.8 release package is closed, start the paper-driven app
program with **ANN / outlier detection / DBSCAN** because:

- they belong to the paper's strongest proximity family
- they can likely be built with existing `fixed_radius_neighbors` / `knn_rows`
  plus Python orchestration
- they directly test whether ITRE remains sufficient for app-level growth
- they avoid prematurely growing DB/index or simulation primitives

The second near-term package should be **point query / range query / index scan**
because it extends v0.7 DB work and can use PostgreSQL as the correctness and
performance baseline.

## AI Consensus

- Claude review: `docs/reports/goal519_claude_review_2026-04-17.md`, verdict
  `PASS`.
- Gemini Flash review:
  `docs/reports/goal519_gemini_review_2026-04-17.md`, verdict `ACCEPT`.
- Codex review: accepted after incorporating Claude's non-blocking design notes
  about short-ray preference and Set Intersection / SpMM performance risk.
