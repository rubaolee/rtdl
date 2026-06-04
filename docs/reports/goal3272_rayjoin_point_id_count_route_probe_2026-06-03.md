# Goal3272 RayJoin Point-ID Count Route Probe

Date: 2026-06-03

Status: implemented locally; performance verdict pending pod measurement.

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

## Measurement Plan

Measure three same-slice PIP lanes on the pod:

1. RayJoin upstream `query_exec` PIP reported query timing.
2. RTDL current best validated `device_filtered_validated` count mode.
3. RTDL experimental `point_id_count_device_columns_validated` mode.

The comparison must keep the existing count boundary: RayJoin PIP still does not
expose the positive assignment count in the unpatched upstream binary, while
RTDL validates its device-side count against exact prepared count.

Performance verdict pending pod measurement.
