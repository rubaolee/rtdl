# Goal3300 RayJoin Boundary-Event Count Route

Date: 2026-06-04

Status: complete with RTX A5000 pod evidence; negative for PIP performance.

## Purpose

Goals3297-3299 added a generic closed-shape boundary-event stream:

- host rows for first boundary crossing;
- device-resident boundary-event columns;
- grouped count continuation over the boundary-event `point_id` column.

Goal3300 wires that stream into the RayJoin same-slice benchmark as an explicit
PIP count mode:

`boundary_event_point_id_count_device_columns`

This is intentionally not a RayJoin PIP positive-membership count. It is a
generic first closed-shape boundary-event count grouped by point id. The runner
records that distinction as:

`rtdl_boundary_event_count_not_pip_membership`

## Implementation

- Added the new PIP count mode to
  `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`.
- Kept native code unchanged. The route composes existing generic OptiX runtime
  primitives:
  - `first_boundary_crossing_device_columns(...)`;
  - `grouped_count_by_point_id_device_columns(...)`.
- Added a runner-level validation helper so both warmup and measured samples
  fail closed if the app forgets to disclose that the route is not a positive
  membership contract.
- Split route timing in the repeated runner:
  - `boundary_event_device_columns_ms`;
  - `boundary_event_grouped_count_ms`;
  - `prepared_query_ms` remains their compatibility sum for existing tables.
- Moved typed-stream metadata construction out of the timed `prepared_query_sec`
  lane.

## External Review Intake

Claude reviewed the initial Goal3300 route in
`docs/reviews/goal3301_claude_review_goal3300_boundary_event_count_route_2026-06-04.md`
with verdict `accept-with-boundary`.

The review found two required fixes before using the route as a benchmark data
point:

- validate the non-membership disclosure during warmup too;
- split boundary-event production timing from grouped-count continuation timing.

Both findings were implemented before the final pod artifact below.

## Pod Evidence

Artifact:

- `docs/reports/goal3300_boundary_event_same_slice_pod_2026-06-04.json`

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- RTDL commit: `56a91c8955985acd2ef98964c776444797b7bce9`
- Focused tests on pod: 29 passed
- Status: `pass_with_optimization_gap`

Inputs:

- LSI: `br_county_start256_count512.cdb + br_soil_start256_count512.cdb`
- PIP: `br_county_start0_count512.cdb`

Median same-slice query/count timings:

| workload | RTDL route | RayJoin query median | RTDL prepared query median | RTDL / RayJoin | count contract |
| --- | --- | ---: | ---: | ---: | --- |
| LSI | `left_id_dense_count` | 0.231 ms | 0.294 ms | 1.28x | matching visible count, 269 |
| PIP | `boundary_event_point_id_count_device_columns` | 0.222 ms | 3.894 ms | 17.52x | boundary-event count, not PIP membership |

PIP split timing:

| phase | median |
| --- | ---: |
| boundary-event device columns | 3.763 ms |
| grouped count by point id | 0.133 ms |

The route produced 3961 boundary-event rows on the 512-feature PIP slice.

## Interpretation

This is a useful contract probe and a poor PIP performance route.

The grouped-count continuation is not the bottleneck. It is about 0.13 ms
median on the A5000 pod. The bottleneck is producing a large boundary-event
stream: about 3.76 ms median, with 3961 emitted event rows and no candidate
download. The previous tuned PIP membership-count route from Goal3294 was much
faster, about 0.361 ms median, because it counts inside the closed-shape
membership path instead of materializing boundary-event columns.

The lesson is precise: for RayJoin-style PIP performance, RTDL should not use
boundary-event materialization as the count path. The next useful primitive is
a fused generic closed-shape first-hit or predicate-count path that can stop or
reduce inside traversal without writing a boundary-event row stream.

## Boundary

This packet does not authorize:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RT-core speedup claims;
- RTDL-beats-RayJoin claims;
- true-zero-copy claims.

The native engine remains app-agnostic. RayJoin interpretation stays in the
benchmark app and runner.
