# Goal3592: RayJoin Explicit Mixed-Route Reference Packet

Date: 2026-06-06

## Purpose

Goal3589 showed that the current RayJoin promoted RTDL/OptiX routes are not the
best path for every simple authored contract when a warmed dense CuPy CUDA-core
baseline is available.

Goal3592 translates that into a user-facing v2.x design rule:

**Do not hide this behind automatic dispatch. Let the user choose explicit
routes, and document the recommended high-performance packet for the benchmark
contract.**

The recommended packet is still RTDL+Python+partner code over generic
app-agnostic primitives. It does not put RayJoin logic into the native engine.

## Inputs

Goal3592 recomputes from:

- `docs/reports/goal3583_rayjoin_hot_promoted_routes_a5000/summary.json`
- `docs/reports/goal3583_rayjoin_hot_promoted_routes_stress_a5000/summary.json`
- `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_a5000/summary.json`
- `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_stress_a5000/summary.json`

## Standard Packet

Dataset tier: `x512`

| Contract | Recommended route | Recommended sec | Embree sec | Speedup vs Embree |
| --- | --- | ---: | ---: | ---: |
| PIP positive assignment count/refinement | CuPy dense CUDA-core count | 0.000071101 | 0.010831083 | 152.334x |
| LSI dense left-id count | CuPy dense CUDA-core count | 0.000071960 | 0.012941647 | 179.846x |
| Overlay active pair-dependency count | CuPy dense CUDA-core active count | 0.000061321 | 0.349695023 | 5702.689x |
| **Composite summed wall-time** | explicit mixed packet | **0.000204382** | **0.373467754** | **1827.307x** |

Route-balanced geometric mean vs Embree: **538.591x**.

## Stress Packet

Dataset tier: `x2048`

| Contract | Recommended route | Recommended sec | Embree sec | Speedup vs Embree |
| --- | --- | ---: | ---: | ---: |
| PIP positive assignment count/refinement | CuPy dense CUDA-core count | 0.000302662 | 0.034963941 | 115.521x |
| LSI dense left-id count | RTDL/OptiX dense left-id count | 0.000122694 | 0.019551154 | 159.349x |
| Overlay active pair-dependency count | CuPy dense CUDA-core active count | 0.000112117 | 5.392689579 | 48098.653x |
| **Composite summed wall-time** | explicit mixed packet | **0.000537474** | **5.447204675** | **10134.830x** |

Route-balanced geometric mean vs Embree: **960.243x**.

## Interpretation

This is the clean v2.x answer to "which partner should I choose?"

- For simple dense PIP and overlay active-count fixtures, choose CuPy.
- For stress LSI, choose RTDL/OptiX.
- Do not claim one universal partner/backend is best.
- Do not let the runtime silently auto-switch unless a future version adds a
  reviewed planner/explain contract.

This reconciles the two facts that looked contradictory:

1. Goal3586: RTDL/OptiX is a huge improvement over Embree for the promoted
   RayJoin-style rows.
2. Goal3589: warmed CuPy is the stronger non-RT CUDA-core baseline for simple
   PIP and overlay active-count.

The practical reference implementation is therefore an explicit mixed packet.
That is how a user should write a high-performance RTDL+Python+partner program:
use RTDL/OptiX where RT traversal pays, use partner CUDA code where the contract
is a cheap dense reduction, and keep the choice visible in the code/report.

## Design Consequence

The native engine still stays generic. The missing system feature is not
"RayJoin inside the engine." The missing system feature is a clearer
primitive/partner menu for:

- dense same-contract CUDA-core baselines;
- RTDL/OptiX prepared traversal routes;
- explicit route selection and `explain` metadata;
- benchmark packets that report route choice rather than hiding it.

This supports the v2.9 performance direction without waiting for v3.0
user-defined shader injection.

## Boundaries

Goal3592 does not authorize:

- automatic partner/backend selection;
- a RayJoin paper reproduction claim;
- a claim that RTDL beats the original RayJoin implementation;
- a public RT-core speedup claim for the full RayJoin app;
- a release authorization;
- a true zero-copy claim.

It authorizes an internal benchmark recommendation: for the current simple
authored RayJoin packet, the best v2.x reference implementation is an explicit
mixed route, not pure RTDL/OptiX and not pure CuPy.

## Validation

Validation test:
`tests/goal3592_rayjoin_explicit_mixed_route_reference_packet_test.py`

The test recomputes all recommended-route choices, summed wall-time speedups,
and route-balanced geometric means directly from the Goal3583 and Goal3589
artifacts.
