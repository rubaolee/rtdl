# Goal3677 Relation-Status Filtered Exact Count

Date: 2026-06-06

## Purpose

Goal3675 proved that the full-county closed-shape membership path could produce an exact scalar count with RTDL OptiX plus a Numba boundary-contact continuation, but the practical one-shot route still materialized the full candidate row stream. Goal3677 tests a narrower generic runtime contract:

- produce a relation-status filtered candidate stream over already prepared point columns,
- support count-only mode with `max_rows=0`,
- compose all-candidate scalar count with a boundary-contact Numba correction,
- keep the native engine app-agnostic and non-authorizing.

This is not a RayJoin-specific ABI. The new native entry point is a generic closed-shape relation-status candidate-column producer:

`rtdl_optix_prepared_point_closed_shape_membership_relation_status_candidate_device_columns_prepared_points_2d`

The filter values are generic relation-status codes:

| Filter | Meaning |
| ---: | --- |
| `0` | all accepted relation candidates |
| `1` | interior accepted candidates |
| `2` | boundary-contact accepted candidates |

## Implementation

Changed files:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/closed_shape_topology.py`
- `scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py`
- `tests/goal3677_relation_status_filtered_exact_count_test.py`

The native filtered pipeline removes the old count-only payload accumulator from raygen and counts only in any-hit, where `relation_status_filter` is available. The Python front door is:

`PreparedOptixPointClosedShapeMembership2D.relation_status_candidate_device_columns_prepared_points(...)`

The composed exact scalar helper is:

`PreparedClosedShapeMembershipCandidateRefinerCupy.count_relation_status_corrected_prepared_points_numba(...)`

It computes:

`exact_count = all_relation_candidate_count - rejected_boundary_contact_count`

The helper retries the boundary stream once with the native required capacity if the initial boundary capacity overflows.

## A5000 Evidence

Artifact:

`docs/reports/goal3677_relation_status_exact_count_a5000/summary.json`

Pod:

`NVIDIA RTX A5000, driver 580.126.09`

Dataset:

`data/rayjoin_public_cdb/br_county_start0_count16545.cdb`

Rows:

- points: `16545`
- shapes: `15700`
- exact oracle count: `47262`

Hot timings:

| Route | Median seconds | Stable count |
| --- | ---: | ---: |
| all relation candidates, count-only | `0.000462027` | `47264` |
| boundary-status candidate columns | `0.000712674` | `47241` |
| relation-status corrected exact Numba count | `0.003199534` | `47262` |
| exact oracle once | `0.224537700` | `47262` |

Correctness:

- corrected count: `47262`
- exact count: `47262`
- all-match exact count: `true`
- boundary-status candidate rows: `47241`
- rejected boundary-contact rows: `2`

## Interpretation

Goal3677 is a useful improvement, but not the final RayJoin-level leap.

Positive result:

- The count-only relation-status path is correct and fast: `47264` candidates in about `0.00045s`.
- The composed exact count is correct and avoids full candidate row materialization.
- Compared with the Goal3675 one-shot Numba exact count path around `0.0215s`, this route is about `6.7x` faster on the same full-county dataset.

Negative result:

- Relation-status filtering is not sparse on this dataset. Boundary-status rows are `47241 / 47264`, so boundary-only output is almost the full candidate stream.
- This means relation-status filtering alone cannot be the final generic solution for exact scalar counts.

Next design target:

- reusable native output buffers for candidate streams, or
- a generic native/partner scalar correction primitive that avoids materializing dense boundary rows.

## Claim Boundary

This report does not authorize:

- v2.x release,
- public speedup claims,
- RayJoin paper reproduction claims,
- RTDL beats RayJoin claims,
- broad RT-core speedup claims,
- true zero-copy claims,
- default-route promotion.

The result is an internal performance-engineering step showing that prepared relation-status filtered streams can improve the exact scalar count path, while also revealing that dense boundary-status datasets still need a stronger generic continuation contract.
