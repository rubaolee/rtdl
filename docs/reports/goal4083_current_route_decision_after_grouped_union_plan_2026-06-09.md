# Goal4083 Current Route Decision After Grouped-Union Plan

Date: 2026-06-09

## Status

Implemented, local tests pass.

## Purpose

Goal4083 refreshes the machine-readable current benchmark route registry after
the RT-DBSCAN grouped-union bottleneck chain:

- Goal4074: native grouped-union traversal is the production bottleneck;
- Goal4075: Numba reset fusion is useful cleanup but not a material speedup;
- Goal4078: root path-compression probe was rejected and reverted;
- Goal4079: current-head root/candidate telemetry shows candidate enumeration
  and root-read work must be reduced together;
- Goal4080: the next candidate primitive is a generic fixed-radius
  grouped-union work-reduction route, not app tuning.

## Registry Update

`src/rtdsl/current_benchmark_route_decisions.py` now reports version:

`rtdl.v2_10.current_benchmark_route_decisions.goal4083.v1`

The RT-DBSCAN row still recommends the current accepted route:

`RTDL/OptiX fixed-radius grouped stream with Numba component/signature continuation`

The row now explicitly says that existing partition-convergence previews remain
unpromoted, and that the next serious direction is the Goal4080 generic
work-reduction primitive with correctness, production-timing, and work-counter
acceptance bars.

## Boundary

This is advisory metadata only. It does not authorize release, public speedup,
broad RT-core, whole-app acceleration, paper-reproduction, true-zero-copy,
automatic partner/backend selection, AMD performance, or app-specific native
engine logic.
