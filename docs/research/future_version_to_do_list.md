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

Origin: Goal2233/Goal2235 RayJoin-style probes.

Observation:

- Prepared ray/segment group count is correct and app-agnostic, but it reduces
  point membership through boundary crossings plus grouped host reduction.
- Compact odd-parity output improves the generic path, but remains slower than
  the old optimized positive-output path because it still traverses boundary
  segments and reduces grouped crossings.

Future work:

- Add an app-agnostic primitive that receives points plus closed shape geometry
  and emits compact positive membership rows.
- Keep vocabulary generic: point, closed shape, membership, predicate, positive
  rows.
- Avoid RayJoin, PIP, polygon, county, map, or spatial-join names in the public
  ABI.
- Prefer a prepared variant so static closed-shape geometry can be reused across
  query batches.
- Keep app semantics in Python/partner code: the engine should not know that a
  shape means a county, region, join relation, or GIS layer.

Boundary:

- This is not a v2.0 release authorization by itself.
- If promoted for v2.0, it needs pod evidence and at least 2-AI consensus.

## v2.5+ Optimization Lane

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
