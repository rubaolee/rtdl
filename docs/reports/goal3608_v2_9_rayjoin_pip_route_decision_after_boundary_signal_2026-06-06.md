# Goal3608 - v2.9 RayJoin PIP Route Decision After Boundary-Signal Evidence

Date: 2026-06-06

Status: internal v2.9 route-decision note. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, RT-core speedup, true zero-copy, or native default-route claims.

## Decision

For the current v2.9 RayJoin public-CDB benchmark app, the recommended PIP scalar-count route is:

- **CuPy dense CUDA-core scalar count** when the user wants the fastest current public-CDB PIP count.
- **Prepared OptiX exact count** when the user wants a no-partner RTDL/OptiX-only count path.
- **Do not promote the boundary-event signal route** as a default route.

The overall RayJoin benchmark should remain mixed-route:

- PIP scalar count: CuPy dense.
- LSI count: RTDL/OptiX.
- Overlay active-count: RTDL/OptiX.

This is consistent with the v2.x design rule: users may choose partners, and RTDL should recommend the fastest honest same-contract route rather than forcing all work through RT cores.

## Why

Goal3604 tested the constructive boundary-event signal route on 512, 1024, and 2048 public-CDB county slices.

It was exact on those slices, but slow:

| Chains | CuPy Dense Sec | Prepared OptiX Exact Sec | Boundary-Event Signal Sec | Boundary Signal / CuPy |
| ---: | ---: | ---: | ---: | ---: |
| 512 | 0.000443555 | 0.000825559 | 0.012200347 | 0.036x |
| 1024 | 0.000464818 | 0.001399391 | 0.016942505 | 0.027x |
| 2048 | 0.000497468 | 0.002284547 | 0.021782851 | 0.023x |

Goal3606 then tested the same signal on a 4096-chain slice across tolerances:

| `crossing_tolerance` | Exact Count | Filtered Count | Missing | Extra | Match |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 11316 | 11311 | 6 | 1 | false |
| 1e-6 | 11316 | 11311 | 6 | 1 | false |
| 1e-5 | 11316 | 11314 | 3 | 1 | false |
| 1e-4 | 11316 | 11317 | 3 | 4 | false |
| 1e-3 | 11316 | 11329 | 3 | 16 | false |

So the route is neither fast enough nor robust enough for default promotion.

## Design Meaning

This does not mean RTDL cannot express RayJoin-like work. It means this particular multi-stage PIP signal is the wrong current performance vehicle.

The useful generic lesson is:

- candidate columns are useful,
- boundary-event columns are useful,
- topology/ownership/tolerance policy matters,
- scalar PIP count should not pay for a large boundary-event row stream when the user only needs a count.

The next serious RTDL-side primitive direction is a fused generic exact closed-shape membership/count continuation with explicit topology/ownership/tolerance contracts. It must stay app-agnostic:

- allowed generic concepts: point id, shape id, boundary id, crossing parameter, topology row, ownership status, deterministic tie-break/tolerance policy;
- not allowed in the engine ABI: RayJoin, CDB, county, GIS assignment semantics, paper-specific ownership policy.

## Reader Guidance

For a user or reviewer asking for one RayJoin v2.9 implementation:

- it is a mixed Python+CuPy+RTDL/OptiX implementation;
- PIP uses CuPy because the current dense CUDA-core scalar-count route wins;
- LSI and overlay use RTDL/OptiX because the RT route wins there;
- a single RayJoin number must define a workload mix/weighting first, otherwise it hides the fact that different contracts have different best routes.

## Boundary

This is a route-decision note, not a release packet and not a public claim packet.
