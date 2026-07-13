# Goal5503: LibRTS Author Range-Intersects Contract Audit

## Status

`implemented__author_gpu_contract_audited__review_pending`

The audit is source-backed and does not change RTDL. It records the pinned
author commits and hashes the source files used to determine the benchmark's
range-intersects execution contract.

## Finding

The benchmark input and the author GPU path must be described separately:

```text
benchmark coordinates       float32 (`coord_t = float`)
float OptiX AABB conversion direct float-to-OptixAabb assignment
CPU reference predicate     inclusive min/max AABB overlap
GPU predicate               RayParams<float,2>::IsHit slab test
GPU query shape             forward query diagonal, then reverse envelope diagonal
GPU interval                t0 = 0; t1 = nextafterf(1.0, FLT_MAX)
GPU robustness adjustment   tFar *= 1 + 2 * FLT_GAMMA(3)
```

The shader source calls `RayParams::IsHit` for both directions. Therefore the
CPU inclusive predicate used by Goal5502 is a named independent oracle, not a
proven transcription of the author's GPU predicate. The audit deliberately
records `cpu_reference_and_gpu_predicate_equivalence_proven=false`.

## Evidence

The audit was run on the POD author checkout `/workspace/librts-ae` and
produced:

`Paper-reproduction-apps/librts-paper/results/goal5503_author_contract_audit.json`

Pinned commits:

```text
RTSpatial              7c54c181b1058c87768767998c00e225cc58666e
SpatialQueryBenchmark  9140ad997519713bb5fdceba639a357afa4609ad
```

The evidence includes source hashes for `ray_params.h` and
`shaders_intersects_envelope_query_2d.cu`, in addition to the benchmark
configuration, geometry, WKT loader, envelope, point, and helper sources.
All source checks pass.

## What This Resolves

- It resolves the missing author-source contract audit.
- It shows why an independent CPU FP32 oracle cannot by itself adjudicate the
  two count disagreements.
- It preserves the generic-system boundary: no author-specific behavior is
  authorized in `src/rtdsl` or `src/native`.

## What This Does Not Resolve

- It does not prove the author is wrong or RTDL is right on full inputs.
- It does not prove CPU inclusive overlap and the GPU `RayParams` predicate
  are equivalent on boundary-sensitive cases.
- It does not authorize a full-input RTDL fix, performance comparison, paper
  reproduction, relation-row claim, or Embree work.

## Next Decision Gate

Goal5504 must use discriminating fixtures that exercise the CPU inclusive
predicate and the GPU RayParams boundary behavior. Only if a verified author
contract and an independent generic contract agree on the relevant cases may
the full-input campaign proceed. Otherwise the correct outcome is a bounded
closeout or a separately authorized generic execution-contract decision, not
an author-specific core change.

## Claim Boundary

```json
{
  "author_contract_source_audited": true,
  "author_validity_proven_for_full_inputs": false,
  "full_input_root_cause_resolved": false,
  "rtdl_core_change_authorized": false,
  "author_specific_rtdl_core_behavior_authorized": false,
  "performance_ratio_authorized": false
}
```
