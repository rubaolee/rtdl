# Future-Version To-Do List

Purpose: catch important ideas that should not distract the current release
lane until they are explicitly promoted by reviewed consensus.

Rules:

- Add new future ideas here instead of scattering them through handoff notes.
- Keep each item tied to a current observation or measurement.
- Mark whether it is a v2.x hardening candidate, v2.5+ optimization lane, or
  v3.0+ architecture idea.
- Do not treat this file as release authorization. Promotion still needs the
  normal report/review/consensus process.

## v2.x Hardening Candidates

### Generic Closed-Shape Membership / Predicate Primitive

Origin: Goal2233/Goal2235 RayJoin-style probes; sharpened by Goal2295 and
Goal2299 current prepared closed-shape telemetry/negative probes, then partly
closed by Goal2301/Goal2303 bounded point-probe evidence.

Observation:

- Prepared ray/segment group count is correct and app-agnostic, but it reduces
  point membership through boundary crossings plus grouped host reduction.
- Compact odd-parity output improves the generic path, but remains slower than
  the old optimized positive-output path because it still traverses boundary
  segments and reduces grouped crossings.
- Goal2295 measured the current prepared closed-shape path and found the
  largest PIP-style cost is RT candidate traversal/write, not Python point
  packing or upload. On the 100,000-point RayJoin-exported probe,
  candidate-write time was about 37.5 ms, while point packing/upload was under
  2 ms and exact refinement was about 10-13 ms.
- Goal2299 compared the accepted closed-shape primitive with the older
  ray/segment odd-parity route on the same 100,000-point stream. The
  ray/segment route was exact, but 56x-74x slower, so it is a rejected fallback
  for this workload shape.
- Goal2301/Goal2303 replaced the infinite upward point probe with a bounded
  vertical point probe and reduced the current RayJoin-exported PIP scalar-count
  median from 37.9 ms to 9.4 ms while preserving the exact expected count.
- Goal2308/Goal2310 added a synthetic single-shape coordinate-magnitude smoke
  pass, but did not prove broad coordinate-system or performance generality.
- Goal2312 added a generic prepared closed-shape `run_raw()` row-view surface,
  reducing the current RayJoin-exported positive-row median from 23.2 ms to
  about 8.9 ms by avoiding Python dictionary materialization when callers only
  need a row view or row count.

Future work:

- Maintain the app-agnostic primitive that receives points plus closed shape
  geometry and emits compact positive membership rows.
- Keep vocabulary generic: point, closed shape, membership, predicate, positive
  rows.
- Avoid RayJoin, PIP, polygon, county, map, or spatial-join names in the public
  ABI.
- Prefer a prepared variant so static closed-shape geometry can be reused across
  query batches.
- Do not reopen boundary ray/segment grouping for this workload shape unless a
  new profile overturns Goal2299.
- Study whether the bounded point-probe half-extent should become configurable
  or derived from prepared-scene metadata before claiming broad
  coordinate-scale generality.
- After the bounded-probe traversal and row-view wins, the next likely work is
  device-resident continuation or partner-side reduction over the closed-shape
  stream, plus broader data-shape validation.
- Do not prioritize Python packing, upload reuse, or replacing GEOS exact
  refinement unless a new profile contradicts the Goal2295/Goal2298 evidence.
- Keep app semantics in Python/partner code: the engine should not know that a
  shape means a county, region, join relation, or GIS layer.

Boundary:

- This is not a v2.0 release authorization by itself.
- If promoted for v2.0, it needs pod evidence and at least 2-AI consensus.

## v2.5+ Optimization Lane

### RayJoin-Style Work After v2.0 Closure

Origin: Goals2192-2314 RayJoin same-query stream adapter, prepared OptiX
segment-pair and closed-shape membership work, bounded point probe, raw row
view, pod timing, and 2-AI reviews.

Current status update, 2026-05-18:

- The user explicitly reopened RayJoin as the top benchmark-app performance
  priority before the final v2.0 decision.
- The reopened work must still preserve app-agnostic native engines.
- The active push is generic: device-resident row streams, generic
  count/parity continuation, stronger closed-shape membership validation,
  many-query batching, phase-separated timing, and disciplined RayJoin
  paper-protocol comparison.
- Do not solve the gap by reintroducing RayJoin-specific native kernels.

v2.0 closure state:

- Treat the RayJoin-style v2.0 project as closed for this release lane.
- Users can implement the scoped RayJoin-style LSI and PIP workloads through
  Python+RTDL prepared generic primitives with exact parity on the
  RayJoin-exported 100,000-query streams.
- The current prepared OptiX route is in the low-millisecond range after
  preparation: about 10.1 ms for LSI witness rows and about 8.7 ms for PIP
  positive row views on the RTX A5000 pod.
- The project does not claim RTDL beats the RayJoin paper implementation, does
  not claim full RayJoin paper reproduction, and does not claim whole-app
  speedup.

Future work:

- Reproduce a broader RayJoin paper matrix only if the project explicitly
  reopens that research lane after v2.0.
- Compare against RayJoin with phase-boundary discipline: paper query phase,
  RTDL prepared query phase, full Python runtime call, and whole-app command
  must be reported as distinct rows.
- Promote device-resident row streams / continuations only as a generic RTDL
  contract, not as a RayJoin-specific native path.
- Keep RayJoin-specific datasets, patches, and query-export infrastructure in
  audit/research reports rather than the learner path.

Boundary:

- Do not block the v2.0 release lane on beating RayJoin RT.
- Do not use the bounded RayJoin closure as a broad RT-core speedup claim.

### Device-Resident Prepared Scene Output Streams

Origin: Goal2249 RayJoin same-query PIP prepared closed-shape pod evidence;
reinforced by Goal2266 prepared closed-shape count scaling and Goal2270
prepared segment-pair count scaling.

Observation:

- Prepared closed-shape membership removes repeated scene upload/build overhead
  and improves the 100,000-query same-query PIP path.
- Generic scalar count APIs help when witness rows are large, but both
  closed-shape membership and segment-pair intersection still pay candidate
  copyback plus host exact refinement.
- Goal2273 showed that sparse RayJoin-exported LSI does not benefit from
  scalar count alone because witness output is already small; the next
  improvement needs to reduce segment-pair candidate/refinement cost itself.
- Goal2276 showed that prepared-scene host metadata caching helps sparse LSI
  modestly, but it does not remove the candidate/refinement boundary.
- Goal2280 showed that direct primitive indices in host exact refinement are
  not enough: same-pod A/B on the RayJoin-exported 100k LSI stream regressed
  raw witness rows and left scalar count effectively neutral.
- Goal2312 removed Python dictionary materialization from the prepared
  closed-shape positive-row timing by exposing a generic raw row view, bringing
  row-output timing near the scalar-count path for the current RayJoin-exported
  PIP stream.
- The remaining gap to RayJoin's paper benchmark is not the predicate itself:
  RTDL still returns host-visible rows through the Python boundary, while the
  RayJoin paper reports a tighter pure GPU query-execution metric.

Future work:

- Study a generic device-resident output stream contract for prepared RTDL
  scenes.
- Keep the primitive vocabulary generic: point, shape, membership, row stream,
  compact positives.
- Include segment-pair predicate/count continuation as a generic stream case,
  not as an LSI or RayJoin-specialized path.
- Avoid further host metadata micro-optimizations unless a profile shows a new
  bottleneck; the next likely win is to remove candidate copyback or host exact
  refinement from the reduction path.
- Let Python/partner code decide whether to materialize rows, reduce them, or
  keep them GPU-resident for a downstream partner primitive.

Boundary:

- This is not part of the Goal2249 claim and does not authorize a RayJoin-beat
  claim.
- Promotion needs a separate report, pod evidence, and external review.

### Device-Resident Grouped Count / Parity Reduction

Origin: Goal2233/Goal2235 output materialization measurements.

Future work:

- Move grouped count/parity accumulation onto the device for generic
  ray/segment workloads.
- Support bounded or streaming output so sparse positives do not require large
  intermediate row materialization.
- Preserve the generic `(ray_id, group_id)` contract.

Boundary:

- Do not reopen the historical collect-k optimization lane before v2.5 unless
  explicitly promoted.

### RayJoin-Style First-Hit / Nearest-Boundary Probe

Origin: Goal2335 RayJoin current-v2.0 basis completion; promoted by
Goal2337 into a measured v2.1 generic primitive.

Observation:

- RayJoin `query=pip` exposes a vertical-ray nearest-boundary support contract,
  not the same contract as RTDL's faster closed-shape membership predicate.
- Current RTDL v2.0 can express that contract by turning each query point into a
  vertical probe segment, running generic prepared segment-pair intersection,
  and reducing by probe id.
- This is correct on the tested RayJoin streams, but slow: the 65,536-point
  pod run emitted 2.32 million generic intersection rows before reduction.

v2.1 status:

- Goal2337 added `rtdl_optix_run_prepared_segment_first_hit` and
  `rtdl_optix_count_prepared_segment_first_hit` as generic prepared segment
  first-hit primitives.
- The contract stays generic: probe id, primitive id, hit point, and hit
  parameter.
- The 65,536-query RayJoin PIP same-query evidence matched the RayJoin positive
  set exactly and reduced the v2.0 vertical-probe route from 734.597 ms to
  10.073 ms including validation, with the native query at 2.654 ms.
- Do not introduce a RayJoin-specific native continuation.

Future work:

- Generalize the same device-resident grouped-continuation pattern to parity,
  grouped counts, and compact positive id streams when a future benchmark needs
  more than one bounded witness per probe.
- Keep full RayJoin paper reproduction, broader spatial-join matrices, and
  user-authored shader injection outside this v2.1 closure unless explicitly
  reopened.

Boundary:

- This belongs in the v2.x primitive/runtime lane. It does not require v3.0
  custom shader injection unless we decide users should author their own
  traversal shaders.

### Hausdorff Beyond Projected Point Sets

Origin: Goal2143 RTDL/X-HD technical report and Goal2340 v2.1 benchmark
refresh.

Observation:

- The current Hausdorff benchmark is exact for 2D projected point sets and uses
  app-level X-HD-style seeding/pruning over generic point-group RTDL
  primitives.
- It intentionally does not implement full 3D surface Hausdorff, MRI/BraTS
  volume workflows, original X-HD WKT-file reproduction, or continuous
  segment/surface Hausdorff semantics.
- Goal2340 made the user default more scale-aware for large point-set rows, but
  did not add a new native Hausdorff kernel or app-shaped engine code.

Future work:

- If promoted, study continuous or surface Hausdorff through generic prepared
  primitives: point groups, segment/surface distance probes, bounded witnesses,
  and device-side max-distance reduction.
- Keep X-HD relationship as inspiration and validation guidance unless exact
  dataset/protocol reproduction is performed.
- Do not introduce native `hausdorff` or `xhd` ABI names.
- Consider whether v2.x generic device-resident reductions are enough before
  moving this to a v3.0 user-defined shader-extension lane.

Boundary:

- Do not block the current v2.x learner/release lane on full X-HD reproduction.
- Promotion needs a separate design report, pod evidence, and external review.

### RTNN-Informed 3D Bounded Neighbor Search

Origin: Goal2353 RTNN pod baseline and Goal2357 uniform-cell neighbor step.

Observation:

- RTNN shows that nearest-neighbor performance comes from spatial organization,
  batching/partitioning, and bounded output policy, not from merely calling
  OptiX once.
- Goal2357 added a generic uniform-cell 3D bounded-neighbor path with a compact
  populated-row stream for the OptiX backend and kept the old all-pairs CUDA
  path plus a simple RT traversal probe as explicit diagnostics.
- The uniform-cell path improved same-protocol warm/raw RTDL rows over the old
  CUDA path, and beat the collected RTNN 65k warm row, but still trailed RTNN at
  262k.

Future work:

- Promote this into an explicit `prepared_bounded_neighbor_search_3d` primitive
  with reusable prepared search-point structures, batch/partition policy, and
  raw/device-resident row continuation. Goal2361 added first-phase telemetry for
  the existing path; use that evidence to choose whether preparation reuse,
  partitioning, row continuation, or exact-normalization removal comes first.
- Goal2363 showed that the packed-column user path removes most Python record
  normalization overhead for the current benchmark rows. Make packed/prepared
  column input policy a first-class part of the eventual primitive so serious
  users do not accidentally benchmark tuple-of-dict normalization.
- Goal2365 added a prepared harness mode so the same packed columns can be
  bound once and executed repeatedly. Future primitive work should expose this
  as a stable API rather than leaving it only as benchmark runner policy.
- Goal2369 pod results showed that current prepared execution reuses Python
  packed inputs but not a native/device-resident 3D neighbor search structure:
  packed `run-optix` and packed `prepared-optix` have similar warm times.
- Goal2371 added the native prepared uniform-cell 3D bounded-neighbor handle,
  so the search-side grid/device buffers are now retained across query runs.
  The remaining 262k bottleneck is row download plus host exact refinement, so
  the next serious RTNN-informed primitive should be a device-resident exact
  filter, row-summary continuation, or bounded output path that avoids sending
  millions of candidate rows back to the CPU for final reduction.
- Goal2373 tested naive `std::thread` parallelization of the host exact-refine
  materialization loop and rejected it as a noisy optimization: one large run
  improved, but smaller rows regressed and worker-count/NUMA sensitivity made
  the result unsuitable for a runtime primitive. Prefer a device-resident
  continuation/summary contract over more host-thread tuning.
- Goal2375 added the first prepared exact-count summary for the 3D
  fixed-radius neighbor primitive. This validated the continuation idea: when
  users need only a count, RTDL can skip row materialization and host
  exact-refine. Future work should generalize the same pattern to device-side
  min/max/sum reductions while preserving a clear distinction between summary
  contracts and witness-row contracts.
- Goal2391 showed that Python-level density-aware partitioning over many
  prepared RTDL handles is not the right clustered-data optimization: it
  preserves exactness but adds halo duplication, handle preparation, and launch
  overhead. The next RTDL-side fix should be a lower-level generic runtime
  primitive: adaptive/density-aware fixed-radius scheduling or a generic CUDA-grid partner backend that keeps the same `fixed_radius_neighbors_3d` contract without adding RTNN-specific ABI.
- Goal2391 also added a CuPy RawKernel uniform-grid baseline. That stronger
  CUDA-core opponent beats current RTDL on dense clustered rows, which is a
  useful benchmark pressure signal rather than a failure of the app-agnostic
  design.
- Study whether a real RT-core prepared variant can beat the uniform-cell path
  only after the prepared contract exists; do not treat naked OptiX traversal as
  sufficient.
- Keep names generic: no native `rtnn` ABI names and no benchmark-specific
  continuation.

Boundary:

- This is v2.x runtime/primitive work. It does not require v3.0 user-defined
  shader injection unless users must author custom neighbor predicates.

## RT-DBSCAN-Informed Fixed-Radius Component Continuation

Origin: Goal2405 true OptiX RT count-threshold device columns.

Observation:

- Goal2405 added a generic true-RT `fixed_radius_count_threshold_3d` prepared
  device-column path. It writes threshold-capped counts and core flags into
  partner CUDA columns without neighbor-row materialization.
- The path is faster than the earlier OptiX-backend uniform-cell summary bridge
  and wins on a dense clustered 131k probe, but sparse road-like rows still
  favor the pure CuPy grid continuation.
- The remaining cost is not the core-flag threshold alone. The full DBSCAN
  composition still runs a separate partner radius-graph component continuation,
  which redoes candidate-pair traversal after RT thresholding.

Future work:

- Design a generic device-resident radius-graph component continuation contract
  that can consume RT traversal hits or compact edge streams without returning
  to host row materialization.
- Goal2407 tried the most direct version of this idea: an OptiX any-hit
  core-graph union over a device parent array. It compiled and matched
  signatures, but it was slower than the Goal2405 RT-count plus CuPy-grid
  continuation on the measured A5000 rows. Do not promote raw any-hit atomic
  union as the continuation primitive without a better scheduling/aggregation
  design.
- Goal2415 tested the corrected clique-safe microcell continuation after the
  Goal2411/Goal2412 safety correction. It preserved correctness and activated
  on several pod rows, but it was slower than the existing RT-count plus CuPy
  grid continuation because `radius / sqrt(3)` microcells require more cells,
  a `5 x 5 x 5` neighbor stencil, and exact cross-microcell pair checks. Do not
  treat microcell graph compression as the next performance path for RT-DBSCAN.
  Pivot to prepared CuPy grid continuation hardening first: cache/reuse point
  columns, cell ids, sorted order, unique cells, starts/counts, and output
  buffers under the same generic fixed-radius component-label contract.
- Goal2418 completed that prepared-grid hardening and validated it on an RTX
  A5000 pod. Prepared RT-count plus prepared CuPy-grid continuation beat the
  older fresh-grid RT bridge on every measured row and beat pure CuPy on larger
  clustered rows. Road-shaped sparse data remained the boundary: near parity at
  131k, still slower at smaller sizes. The next leap should therefore be a
  generic device-resident radius-graph edge stream or grouped union
  continuation that avoids redoing radius traversal after RT thresholding,
  rather than another DBSCAN-specific native shortcut.
- Goal2420 extended the pod profile. At 262k points, the prepared RT bridge also
  beat pure CuPy on `road3d`, so sparse-road data has a scale crossover. Compact
  `ngsim_dense` still favored pure CuPy through 131k. This argues for an
  explicit plan/explain path that reports the selected backend, partner,
  preparation/reuse state, RT phase timing, continuation timing, and claim
  boundary. Do not hide this behind an invisible dispatcher.
- Goal2423 turned the proven prepared RT-count plus prepared CuPy-grid path
  into a public generic composite runtime:
  `prepare_optix_cupy_radius_graph_components_3d`. This is now the baseline
  user-facing contract for current RT-DBSCAN-style experiments while deeper
  device-resident edge-stream or grouped-union continuations are designed.
- Keep the primitive generic: fixed-radius graph/component labels, grouped
  union/find continuation, or row-stream continuation. Do not add
  DBSCAN-specific native ABI.
- Preserve explicit claim metadata for RT-core phase, partner continuation
  phase, row materialization policy, and zero-copy/direct-device handoff policy.

Boundary:

- This belongs in v2.x runtime/primitive work. It is not a v3.0 shader-injection
  feature unless users need to define custom hit predicates.

## v3.0+ Architecture Ideas

### User-Defined Predicate Extension Surface

Origin: v3.0 custom-engine-extension discussions and RayJoin predicate needs.

Future work:

- Study a safe user predicate ABI for prepared scenes.
- Separate device-side payload schema from host-side dataset descriptors.
- Treat shader injection/JIT as its own architecture stream with independent
  conformance and safety review.
