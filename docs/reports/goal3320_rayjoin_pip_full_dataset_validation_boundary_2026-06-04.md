# Goal3320 - RayJoin PIP Full-Dataset Validation Boundary

Date: 2026-06-04

## Purpose

Goal3318 made the prepared point / closed-shape scalar-count batch executor reusable and fast on the validated 512-row RayJoin county slice. Goal3320 checks whether that route can be broadened to larger CDB inputs without changing the v2.8 engine contract.

The answer is bounded: the route is fast on another validated slice, but it is not yet generally correct for county-style CDB topology.

## Pod Validation Context

- GPU: NVIDIA RTX A5000, driver 580.126.09
- Commit: `c037f510b89a2effd4eff32d025da1a3c053a0b1`
- RTDL library: `/root/rtdl_goal3293/build/librtdl_optix.so`
- Query axis: `z_point`
- Validation probe: exact Python/CDB scalar count versus the device-filtered prepared-points scalar count and point-id grouped device count.

The validation matrix is saved at:

- `docs/reports/goal3320_rayjoin_pip_device_count_validation_matrix_2026-06-04.json`

The successful soil-slice executor artifact is saved at:

- `docs/reports/goal3320_rayjoin_pip_batch_executor_auto_stream_br_soil_start256_count512_2026-06-04.json`

## Validation Results

| Dataset | Points | Shapes | Exact count | Device scalar count | Point-id grouped count | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `br_county.cdb` | 16545 | 15700 | 47262 | 47554 | 47554 | mismatch |
| `br_county_start256_count512.cdb` | 512 | 478 | 1417 | 1429 | 1429 | mismatch |
| `br_soil_start256_count512.cdb` | 512 | 501 | 1471 | 1471 | 1471 | match |

The soil slice also validates the Goal3318 executor on a second CDB family:

| Request count | Effective streams | Executor ms/request | Native ms/request | Count |
| ---: | ---: | ---: | ---: | ---: |
| 8 | 4 | 0.025973 | 0.023892 | 1471 |
| 16 | 8 | 0.015696 | 0.014447 | 1471 |
| 32 | 8 | 0.013224 | 0.012552 | 1471 |
| 64 | 16 | 0.012868 | 0.012359 | 1471 |

## Interpretation

This is a correctness boundary, not a timing failure.

The current generic fast route is a point-to-closed-shape membership count over prepared point columns and closed-shape geometry. It works on validated simple-chain slices. The full county CDB and the county start256 slice expose topology or degeneracy behavior that is not represented by this current primitive contract.

The important design conclusion is that broad RayJoin-level CDB support needs a richer generic closed-shape topology contract. That contract should remain app-agnostic, but it likely needs to represent face/ring/chain identity, deterministic boundary degeneracy handling, and duplicate ownership policy instead of treating every accelerated candidate as a simple closed-shape membership event.

The benchmark app's validated route is doing the right thing by failing closed when the fast route cannot match exact CDB semantics. We should not broaden the Goal3318 executor as release evidence for full CDB workloads until such validation passes or a richer primitive exists.

## Required Follow-Up

1. Add a validated-domain preflight for the device-filtered prepared-points count route, including the batch executor, so it only engages when exact validation passes on the intended input domain.
2. Design a generic face/topology-aware closed-shape membership primitive for CDB-style workloads.
3. Keep the exact fallback route available for county-style inputs until the richer primitive is validated.
4. Treat the soil-slice result as useful repeated-query throughput evidence, not a whole RayJoin workload claim.

## Claim Boundary

- `release_authorized`: false
- `public_speedup_claim_authorized`: false
- `rt_core_speedup_claim_authorized`: false
- `true_zero_copy_claim_authorized`: false
- `rtdl_beats_rayjoin_claim_authorized`: false
- `rayjoin_paper_reproduction_claim_authorized`: false

