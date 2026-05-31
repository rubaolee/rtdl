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

### Hit-Stream Continuation Promotion Gates After Goal2744

Origin: Goals2685-2744 device-resident hit-stream handoff, native OptiX
device-column output, owner lifecycle guards, stream-ordering metadata,
cross-partner transfer planning, Triton group-id validation boundary, and native
release-entrypoint audit.

Observation:

- RTDL now has a generic OptiX hit-stream device-column path for
  `ray_ids:int64` and `primitive_ids:int64`, plus a Python owner guard and a
  native release entrypoint audit.
- Goal2740 made partner transfer semantics explicit: Triton is a preview
  executable carrier path, CuPy is descriptor-only for the current generic
  hit-stream slice, Numba is a narrow preview where supported, and silent copies
  are forbidden.
- Goal2743 made the current Triton group-id bounds check honest: it is a Torch
  CUDA precheck with a host scalar sync, not a device-resident error-flag
  primitive.
- Goal2744 reduces the release-entrypoint risk from "unknown" to
  "present/audited", but native lifetime still needs broader hardware and
  failure-path validation.
- Goal2748 added the first Triton device-resident group-id invalid-count flag
  and an opt-in host-raise mode, but default grouped-operation enforcement still
  preserves the conservative host-scalar exception boundary.
- Goal2750 added a transfer-planner safety gate: device partners now fail
  closed with `stream_ordering_proof_required` when hit-stream columns are
  device-resident but producer/consumer stream ordering is not proven.
- Goal2752 separated host-synchronized safety from event/same-stream
  zero-copy-compatible ordering metadata, so host sync is no longer easy to
  mistake for a future no-sync zero-copy proof.
- Goal2754 pod evidence showed current generic hit-stream + Triton continuation
  is 29.5x-147.9x slower than the fused prepared grouped primitive on the
  low-hit-count scalar grouped-reduction RayDB-style fixture, while preserving
  correctness and same-pointer adapter evidence. This supports primitive-first
  selection for scalar reductions and reserves hit streams for unfused
  continuations or future lower-overhead handoff work.
- Goal2756 added caller-owned reusable CUDA output buffers for the generic
  OptiX ray/triangle hit-stream column path. This removes the per-run native
  output-column `cuMemAlloc`/release from the reusable path and records the
  caller-owned lifetime in the handoff metadata, but it remains
  host-synchronized before partner consumption and does not authorize a true
  zero-copy or public speedup claim.
- Goal2758 measured that reusable output buffers do reduce the narrow
  output-allocation overhead on the RTX A5000 pod: total median reusable/native
  ratios were about `0.90x`, `0.97x`, `0.95x`, `0.73x`, and `0.90x` for
  1,024 through 524,288 generic hit rows. This is an internal primitive/runtime
  probe, not a public speedup claim, and it does not close the larger
  hit-stream-continuation gap from Goal2754.

Future work:

- Integrate device-resident group-id validation/error flags into a larger
  no-host-read continuation plan; Goal2748 supplies the flag primitive, but
  Python exception enforcement still reads a host scalar by design.
- Add stream/event evidence that proves the OptiX producer and Triton consumer
  are ordered on real hardware without relying on device-wide synchronization.
- Reduce generic hit-stream continuation overhead only through generic runtime
  work: event/same-stream ordering, fused gather+continuation, and
  device-resident row-count/overflow handling. Reusable output buffers are now
  available as a Goal2756 building block and need broader scale/perf validation.
- Run multi-GPU and multi-driver same-pointer/lifetime validation before any
  public true-zero-copy wording is considered.
- Extend cross-partner transfer plans only when CuPy or Numba has a real
  executable generic kernel path; until then, keep descriptor-only and preview
  labels explicit.
- Keep app logic out of the native engine: hit streams carry generic ray and
  primitive ids; app grouping, values, and semantics remain in Python/partner
  payload columns.

Boundary:

- This is v2.x runtime hardening, not v3.0 shader injection.
- None of these items authorizes public speedup, true zero-copy, or release
  promotion without the normal report/review/consensus process.

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
- Goal2425 added the missing fair prepared-CuPy baseline and corrected the
  planner thresholds: prepared RT wins clustered rows at 65k and above, road
  rows only at the measured 524k crossover, and compact dense rows still favor
  prepared pure CuPy through 262k. Goal2427 then smoked the updated explicit
  plan on the pod. The planning/correctness issue is closed for this stage; the
  remaining performance issue is the generic continuation itself.
- Goal2430 prototyped a prepared CuPy directed adjacency stream. It showed the
  generic continuation idea is real: after stream preparation, grouped
  union/find continuation was about 5.6x to 28x faster than the prepared CuPy
  grid continuation on the measured pod rows. The boundary is memory: dense
  rows can materialize very large directed streams, for example 136345976 edges
  at 32768 clustered points. Next work should add a bounded/chunked adjacency
  stream and then a generic prepared OptiX fixed-radius adjacency writer that
  feeds the same partner continuation.
- Goal2431 added the generic prepared OptiX fixed-radius adjacency writer. The
  first pod evidence confirms that OptiX can fill the same caller-owned CuPy
  `edge_offsets` / `neighbor_indices` stream and preserve exact labels. The
  result is a correctness and architecture closure rather than a big speedup:
  steady-state component labeling is near parity with the prepared pure-CuPy
  adjacency stream, while stream preparation is heavier. The next performance
  step is still bounded/chunked or grouped continuation, not DBSCAN-native
  engine code.
- Goal2433 added the bounded/chunked OptiX adjacency continuation. It preserves
  exact labels and cuts peak adjacency storage from one full dense stream to a
  per-chunk stream, but is slower when the full stream fits because it currently
  fills chunks twice: once for union and once for border/core labeling. The next
  performance step is to fuse or cache enough per-chunk continuation state to
  avoid the second RT fill, or to add a generic grouped stream-reduction
  primitive.
- Goal2435 removed that second RT fill by capturing one core-neighbor candidate
  per border point during the chunked union pass. This improved the chunked path
  while preserving exact labels, but it remains slower than full adjacency when
  the full stream fits. The next step is a lower-overhead grouped stream
  continuation or a planner policy that selects full adjacency, chunked
  adjacency, or prepared grid according to memory and data-shape evidence.
- Goal2437 added the explicit app-level continuation planner for the adjacency
  family. It records the selected mode, reason, edge estimate, edge budget, and
  claim boundaries, and it intentionally stays outside the native engine.
  Goal2439 pod-smoked both planner branches: full OptiX adjacency when the
  stream fits the budget, and chunked OptiX adjacency when it does not.
- Goal2441/2442 made the chunked path degree-budget-aware. A requested
  `max_directed_edges_per_chunk` now splits adjacency chunks after exact degree
  counts are known; the pod smoke enforced an 8,000,000 directed-edge cap on the
  32,768-point clustered row with a maximum chunk of 7,999,889 edges. This is a
  memory-control improvement, not a speedup claim.
- Goal2444/2445 prepared each chunk's prefix offset column once and reused it
  across repeated chunked runs. The 32,768-point clustered pod smoke showed the
  second prepared run using `prepared_chunk_edge_offsets_reused=true`, with
  matching component signatures.
- Goal2447/2449/2450 tested the remaining small workspace-reuse idea. A single
  reused neighbor-index workspace was correct but 1.044x slower than default;
  bounded pools of 4, 8, and 18 workspaces were also slower or only parity on
  the RTX A5000 smoke. Keep per-chunk allocation as the performance default.
- Goal2452 found a better immediate policy win: the explicit continuation
  planner was too conservative. On the RTX A5000, full OptiX directed adjacency
  for the 32,768-point clustered row was about 6.4x faster than chunking and
  fit memory, so the default directed-edge budget was raised to 160,000,000.
  Chunking remains the memory-bounded branch above that explicit budget.
- Keep the primitive generic: fixed-radius graph/component labels, grouped
  union/find continuation, or row-stream continuation. Do not add
  DBSCAN-specific native ABI.
- Preserve explicit claim metadata for RT-core phase, partner continuation
  phase, row materialization policy, and zero-copy/direct-device handoff policy.
- The remaining RT-DBSCAN performance leap is a lower-overhead generic grouped
  stream continuation that can consume RT traversal hits or bounded edge chunks
  with fewer launches and less intermediate storage. Do not solve it with a
  DBSCAN-specific kernel. Goal2455 captured the design target and recommends a
  generic fixed-radius grouped component continuation as the first concrete
  proof.
- Goal2457 implemented that first concrete proof for OptiX fixed-radius
  grouped union workspaces. It improves the dense over-budget branch versus
  chunked adjacency, but full adjacency remains faster when the whole stream
  fits. Future v2.x work should keep this as a generic predicate/grouped
  continuation family and look for lower-overhead atomics or segmented
  reductions, not DBSCAN-native ABI.
- Goal2459 removed unnecessary exact-degree work from the grouped-stream core
  predicate by using threshold-capped count flags at `min_neighbors`. The count
  phase is no longer the main bottleneck; the remaining hard target is the
  grouped-union pass and its global atomic pressure.
- Goal2461 removed the grouped-stream self-query host repack/upload by adding a
  generic prepared-search self-query device path. On the RTX A5000 pod, the
  steady-state grouped continuation improved by about 2.3x-2.5x versus
  Goal2459. The remaining RT-DBSCAN runtime work is now deeper: reduce
  grouped-union global atomic pressure with a generic segmented/blocked
  continuation design, not a DBSCAN-specific native endpoint.
- Goal2463 added a generic all-items-eligible grouped-union mode for prepared
  fixed-radius self-query continuations. It helps dense rows where the
  count-threshold pass proves every item is predicate-true, improving the
  65,536-point clustered RT-DBSCAN row by about 1.13x on the RTX A5000 pod. It
  does not help mixed predicate rows; the next large step is still a generic
  blocked/segmented continuation that reduces global atomic pressure.
- Goal2465 moved the all-items `target > source` condition into the OptiX
  intersection program, so hits that anyhit would ignore are not reported. This
  improves the dense 65,536-point clustered row by another about 1.08x on the
  same RTX A5000 pod. The deeper remaining work is unchanged: reduce global
  atomic pressure for generic grouped continuations.
- Goal2467 opened the next Mac-local design step for a generic
  blocked/segmented grouped continuation. The design target is
  `generic_fixed_radius_blocked_grouped_component_continuation_3d`, recorded as
  non-executable and `needs-more-evidence` until native implementation, pod
  timing, and external review exist. A Mac-local CPU simulator now fixes the
  semantic and telemetry contract for segment count, fixed capacity,
  proposal-rejection rate, atomic-attempt counters, and fail-closed fallback.
  Keep this app-independent; RT-DBSCAN is only the benchmark stressor.
- Goal2468 added local overhead-breakdown instrumentation for the grouped
  stream benchmark path and replayable pod runner. The next pod run should
  attribute the gap between full warm elapsed time and native grouped RT time
  before choosing label-materialization, Python/CuPy orchestration, or native
  grouped-continuation work. This is diagnostic plumbing only; it is not a
  performance claim.
- Goal2468 pod evidence on RTX PRO 4500 Blackwell attributed the current
  grouped-stream full-vs-native gap mostly to Python row materialization,
  label densification, and benchmark signature construction. At 65,536
  clustered points, native grouped RT was about 58.9 ms while row
  materialization plus densification plus signature was about 66.4 ms.
  Before deeper native work, add a raw column/label benchmark mode or
  device/partner-column signature path that avoids Python dictionary rows when
  users do not ask for row output.
- Goal2469 added the first local version of that path:
  `optix_rt_core_grouped_stream_cupy_column_signature_3d`. It keeps the
  row-returning grouped-stream mode intact but computes the benchmark signature
  from partner column arrays without Python row dictionaries. RTX 2000 Ada pod
  timing showed the no-row consumer path reduced measured benchmark tail time
  from 0.091646 s to 0.068829 s at 32,768 clustered points and from 0.236771 s
  to 0.196566 s at 65,536 clustered points. The stable attribution is
  host-side gap reduction: removing Python row dictionaries and label
  densification, partially offset by the column-signature computation. This is
  not a faster native RT primitive claim. Gemini review accepted this narrow
  boundary, and the Codex/Gemini consensus records Goal2469 as closed for the
  benchmark-consumer row-materialization issue.
- Goal2470 ran a Mac-local segment-sensitivity sweep over the Goal2467
  simulator. It found that naive tiny fixed-hit segments are unlikely to reduce
  global atomic pressure enough: at 2,048 clustered points, 64-hit segments
  reject only about 0.06% of global parent attempts and 256-hit segments reject
  only about 1.35%. Larger 2,048-hit segments reject about 46%, but require
  larger fixed buffers. The first native prototype should therefore use large
  enough segment buffers or spatial/Morton/query-local grouping, not a naive
  many-tiny-query-chunks launch plan.
- Goal2471 starts the telemetry-first native slice by adding optional
  caller-owned `uint64[4]` grouped-union atomic counters to the generic prepared
  OptiX fixed-radius grouped-union self-query path. This is instrumentation,
  not an optimization: the default non-telemetry symbol remains unchanged.
  Goal2471 pod validation on an RTX A5000 confirmed all-items parent counters
  and predicated fallback counters execute correctly, so the counters can now be
  used as evidence for later optimization studies.
- Goal2472 adds the first concrete blocked-continuation runtime scaffold: a
  generic prepared fixed-radius grouped-union self-query range symbol and an
  explicit RT-DBSCAN benchmark mode that can run grouped continuation over
  contiguous prepared-search query blocks. This is still a candidate path, not
  a default dispatcher or speed claim. RTX A5000 pod evidence showed query
  range blocking is correct but slower than the unblocked path: `8192`-item
  blocks were 2.39x-2.84x slower end-to-end and `32768`-item blocks were still
  1.06x-1.09x slower end-to-end. Keep the range symbol as a generic scaffold,
  but do not promote query chunking as the next optimization. The next useful
  work is a true segmented/proposal-reduction path that reduces global parent
  atomic attempts inside a launch.
- Goal2473 used Goal2471 telemetry at benchmark scale on the RTX A5000. The
  current optimized grouped-union path records only about 1.19x-1.23x parent
  atomic attempts per point at 32,768 and 65,536 clustered points, while native
  grouped time is still about 31 ms and 83 ms respectively. This weakens the
  hypothesis that duplicate global parent atomics alone dominate. The next
  optimization should also target RT hit reporting/anyhit work or a generic
  connectivity-proposal contract that produces fewer useful callbacks, not just
  local deduplication of already-small atomic counts.
- Goal2474 starts that direction by moving generic predicated grouped-union
  no-op filtering into the OptiX intersection program. In predicated mode, hits
  that cannot affect parent union or fallback candidates are rejected before
  `optixReportIntersection`; anyhit keeps the same checks as a safety net. This
  is pod-validated as part of Goal2475 and mostly affects mixed-predicate rows.
- Goal2475 adds a stronger generic culling candidate for dense parent-union
  rows: after the exact radius test, the OptiX intersection program reads the
  current union-find roots and skips `optixReportIntersection` when source and
  target are already connected. This targets anyhit callback overhead rather
  than atomic count alone. RTX A5000 pod evidence was positive: grouped-native
  median improved by about 19.1% at 32,768 clustered points and 19.9% at 65,536
  clustered points; total column-signature benchmark median improved by about
  3.9% and 10.8% respectively, with signatures matching. Treat this as an
  internal engineering win accepted by Codex/Gemini consensus; public wording
  still requires the normal release-claim process.
- Do not spend more v2.2 time on neighbor-index workspace reuse unless a new
  stream-ordered event mechanism avoids device-wide synchronization. The
  current evidence says the next useful work is the grouped continuation leap.

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
