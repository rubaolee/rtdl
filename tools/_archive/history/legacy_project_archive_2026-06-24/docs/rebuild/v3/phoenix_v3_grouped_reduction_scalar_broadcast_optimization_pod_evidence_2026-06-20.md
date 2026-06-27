# Phoenix V3 Grouped-Reduction Scalar-Broadcast Optimization Pod Evidence

Status: `grouped_reduction_scalar_broadcast_optimization_pod_evidence_not_release`.

This packet records a V3-only generic packing optimization for the current
grouped_sum candidate path. It is not release authorization.

## What Changed

The RayDB-style grouped_sum lowering creates a large fixed-direction ray batch.
Before this patch it allocated full-length `dx`, `dy`, `dz`, and `tmax` arrays
even though those fields are constants for every ray.

The V3 change lets the generic 3-D ray packer validate and broadcast scalar
fields, then updates the RayDB lowering to pass scalar direction/tmax values.
This reduces cold workload-build cost without changing the native grouped
reduction primitive or adding an app-specific native engine.

Modified sources:

```text
src/rtdsl/optix_runtime.py
examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
```

## Artifact Sources

Probe:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_probe_20260620
```

Actual repeat100 rerun:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620
```

Machine-readable packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.json
```

## Current Results

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
current_packet_external_review_status: blocked_current_packet
current_packet_2ai_consensus_status: not_recorded_for_this_packet
```

| Row | Hot OptiX/Embree | Actual repeat100 loop | Actual cold plus loop | Embree workload build | OptiX workload build | Classification |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 262,144 rows / 1,024 groups | 203.022x | 200.353x | 27.917x | 1.620s | 1.644s | candidate, not M7 |
| 524,288 rows / 2,048 groups | 158.970x | 157.642x | 2.983x | 84.916s | 94.866s | large cold prepare cost, not M7 |

All rows matched the CPU reference and kept public/release flags false.

## Before And After

| Row | Before cold plus loop | After cold plus loop | Before Embree workload build | After Embree workload build | Before OptiX workload build | After OptiX workload build |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 262,144 rows / 1,024 groups | 27.012x | 27.917x | 1.909s | 1.620s | 3.304s | 1.644s |
| 524,288 rows / 2,048 groups | 2.062x | 2.983x | 180.525s | 84.916s | 184.104s | 94.866s |

The optimization is real and useful, but it does not make the 524,288-row case
a clean public row. Cold prepare remains large and must stay visible.

## Claim Boundary

Allowed:

```text
The V3 grouped_sum candidate now uses a generic scalar-broadcast ray-packer
optimization that reduced 524,288-row workload-build time materially while
preserving correctness in the actual repeat100 pod rerun.
```

Forbidden:

```text
Do not claim grouped_sum is released.
Do not claim V3 is broadly faster than V2.x.
Do not claim a whole-app or whole-database speedup.
Do not hide the 524,288-row cold prepare cost.
Do not call either row M7-qualified before external review closes.
```

## External Review

Fresh external review is blocked:

```text
docs/reviews/external_review_blocked_phoenix_v3_grouped_reduction_scalar_broadcast_optimization_2026-06-20.md
```

## Goal-Level Decision Audit

Decision: promote scalar-broadcast repeat100 artifacts to current local
grouped_sum candidate evidence.

1. Did I make a foolish decision?

   No. The probe showed the constant ray direction/tmax arrays were a fixable
   generic packer cost, and the repeat100 rerun preserved correctness.

2. If yes, what actions made the decision foolish?

   It would be foolish to keep quoting pre-optimization cold-plus-loop values
   after the generic packer rerun succeeded, or to turn the result into a
   release claim without external review.

3. Was there another path?

   Yes. Skip optimization and move to another app. That would leave the
   clearest grouped_sum cold-start blocker partially self-inflicted.

4. Can I now try a different path that truly solves the problem?

   Yes. Use scalar-broadcast repeat100 artifacts as current local evidence,
   keep release authorization false, and request external review when
   available.
