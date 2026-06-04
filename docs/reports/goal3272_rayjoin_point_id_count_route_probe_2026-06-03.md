# Goal3272 RayJoin Point-ID Count Route Probe

Date: 2026-06-03

Status: implemented and pod-measured on NVIDIA A40; accepted as a reusable
device-column continuation substrate. It is not the fastest RayJoin PIP
scalar-count path for this benchmark.

Short verdict: this is not the fastest RayJoin PIP scalar-count path.

## Purpose

Goal3271 added a generic closed-shape membership continuation that counts
positive memberships by caller point ID into a dense device-resident count
column. Goal3272 wires that primitive into the RayJoin same-slice PIP benchmark
as an experimental RayJoin PIP count route.

The new app count mode is:

- `point_id_count_device_columns_validated`

It is validated against exact prepared count before the timed lane is accepted.

## What Changed

The RayJoin benchmark app now accepts a third PIP count mode:

- `exact`
- `device_filtered_validated`
- `point_id_count_device_columns_validated`

The same-slice runner also accepts the new mode through:

```text
--rtdl-pip-count-mode point_id_count_device_columns_validated
```

## Boundary

This is a point-id grouped-count device column route. It is an app-level
benchmark route over a generic RTDL primitive. It does not add RayJoin-specific
native engine logic.

Claim flags:

- not a release claim
- not a public speedup claim
- not a RayJoin paper reproduction claim
- not a true zero-copy claim
- not an RTDL-beats-RayJoin claim

## Pod Measurement

The same-slice runner measured three PIP lanes on the NVIDIA A40 pod at commit
`20dcdb7a2c071c88e445d1c874591edde1912775`:

1. RayJoin upstream `query_exec` PIP reported query timing.
2. RTDL current best validated `device_filtered_validated` count mode.
3. RTDL experimental `point_id_count_device_columns_validated` mode.

The comparison keeps the existing count boundary: RayJoin PIP still does not
expose the positive assignment count in the unpatched upstream binary, while
RTDL validates its device-side count against exact prepared count.

| Lane | PIP count | Median prepared/query ms | Ratio vs RayJoin reported query | Evidence |
| --- | ---: | ---: | ---: | --- |
| RayJoin upstream `query_exec` | not exposed | 0.194263 | 1.000x | `device_filtered_validated_same_slice.json` |
| RTDL `device_filtered_validated` | 1430 | 0.330849 | 1.703x | `device_filtered_validated_same_slice.json` |
| RayJoin upstream `query_exec` | not exposed | 0.205326 | 1.000x | `point_id_count_device_columns_same_slice.json` |
| RTDL `point_id_count_device_columns_validated` | 1430 | 0.448119 | 2.182x | `point_id_count_device_columns_same_slice.json` |

The point-id grouped-count route also validates against exact prepared count in
the same run:

| Lane | Timed device-side median ms | Exact validation median ms | Device-side / exact |
| --- | ---: | ---: | ---: |
| `device_filtered_validated` | 0.330849 | 0.459384 | 0.720x |
| `point_id_count_device_columns_validated` | 0.448119 | 0.554271 | 0.809x |

## Interpretation

The new point-id device-column path is correct and useful, but it is not the
fastest RayJoin PIP scalar-count path for this benchmark. The likely reason is
contract shape: this same-slice probe only needs one scalar count, while the new
primitive pays for a richer dense `point_id -> count` output column. That richer
output is the right substrate for downstream per-point continuation and grouped
partner consumers, but for a single scalar count the older
`device_filtered_validated` path remains the better route.

Goal3272 therefore closes as a route/provenance probe, not a performance win.
The next performance target is to use the point-id count columns only when a
caller actually consumes per-point grouped results, and keep the scalar
device-filtered path as the benchmark default for current RayJoin PIP count.
