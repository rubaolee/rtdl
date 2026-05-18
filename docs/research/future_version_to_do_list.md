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

## v3.0+ Architecture Ideas

### User-Defined Predicate Extension Surface

Origin: v3.0 custom-engine-extension discussions and RayJoin predicate needs.

Future work:

- Study a safe user predicate ABI for prepared scenes.
- Separate device-side payload schema from host-side dataset descriptors.
- Treat shader injection/JIT as its own architecture stream with independent
  conformance and safety review.
