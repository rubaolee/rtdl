# Goal3586: RayJoin Composite Score From Hot Promoted Routes

Date: 2026-06-06

## Purpose

Goal3583 closed the measurement-contract bug for RayJoin promoted routes by
measuring hot prepared-query medians for three RayJoin-style contracts:

- PIP positive assignment count/refinement
- LSI dense left-id count
- overlay active pair-dependency count

Goal3586 turns those three per-contract measurements into a single RayJoin-style
app score, while still preserving the per-contract detail. This addresses the
reader/reviewer question: "What is RayJoin as one benchmark app, not three
separate rows?"

## Score Definitions

Two scores are reported.

1. **Primary app packet score: summed wall-time ratio.**
   Sum the three Embree contract times and divide by the sum of the three OptiX
   hot prepared-query times. This answers: "If this fixed RayJoin-style packet
   runs PIP, LSI, and overlay active-count once each, what is the app-level
   speedup?"

2. **Secondary route-balanced score: geometric mean.**
   Compute the geometric mean of the three per-contract speedups. This answers:
   "How strong is the improvement if each contract has equal narrative weight?"
   It prevents the very large overlay active-count row from hiding the smaller
   but still positive PIP row.

Both scores are internal benchmark engineering evidence. They are not a full
RayJoin paper reproduction and do not authorize public speedup wording.

## Standard Composite

Source artifact:
`docs/reports/goal3583_rayjoin_hot_promoted_routes_a5000/summary.json`

| Contract | Embree sec | OptiX hot query sec | Speedup |
| --- | ---: | ---: | ---: |
| PIP positive assignment count/refinement | 0.010831083 | 0.002115869 | 5.119x |
| LSI dense left-id count | 0.012941647 | 0.000102108 | 126.744x |
| Overlay active pair-dependency count | 0.349695023 | 0.000357255 | 978.838x |
| **Composite summed wall-time** | **0.373467754** | **0.002575233** | **145.023x** |

Route-balanced geometric mean: **85.956x**.

## Stress Composite

Source artifact:
`docs/reports/goal3583_rayjoin_hot_promoted_routes_stress_a5000/summary.json`

| Contract | Embree sec | OptiX hot query sec | Speedup |
| --- | ---: | ---: | ---: |
| PIP positive assignment count/refinement | 0.034963941 | 0.005896886 | 5.929x |
| LSI dense left-id count | 0.019551154 | 0.000131294 | 148.911x |
| Overlay active pair-dependency count | 5.392689579 | 0.001166145 | 4624.372x |
| **Composite summed wall-time** | **5.447204675** | **0.007194325** | **757.153x** |

Route-balanced geometric mean: **159.830x**.

## Interpretation

The single app-level RayJoin-style result is now strong and legible:

- standard fixed packet: **145.023x** summed wall-time speedup;
- stress fixed packet: **757.153x** summed wall-time speedup.

The route-balanced geometric means are also strong:

- standard: **85.956x**;
- stress: **159.830x**.

The stress app-packet score is larger because overlay active-count scales into a
multi-second Embree workload while the prepared OptiX active-count continuation
stays near millisecond scale. This is a real benefit for this active-count
contract, but it is not full polygon overlay materialization.

The PIP row remains the weakest route because exact simple-ring refinement is
performed by CuPy in the app layer after RT candidate generation. That is still a
valid partner-assisted v2.x route, but it explains why PIP is a 5-6x row rather
than a 100x+ row.

## Boundaries

This composite score is not:

- a full RayJoin paper reproduction;
- a paper-scale RayJoin claim;
- a claim that RTDL beats the original RayJoin implementation;
- a full polygon overlay materialization result;
- a true zero-copy claim;
- a release authorization.

It is a same-project Embree-vs-OptiX comparison over derived tiled fixtures and
hot prepared-query contracts.

## Validation

Validation test:
`tests/goal3586_rayjoin_composite_score_from_hot_promoted_routes_test.py`

The test recomputes all composite totals and geometric means directly from the
Goal3583 standard and stress JSON artifacts and checks that the report keeps the
claim boundaries visible.
