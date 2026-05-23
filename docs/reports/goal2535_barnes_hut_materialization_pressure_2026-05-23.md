# Goal2535 Barnes-Hut Materialization Pressure Guard

Date: 2026-05-23

## Decision

Added a generic materialization-pressure contract:

- `generic_vector_sum_materialization_pressure_2d_v1`

This estimates the intermediate contribution-row count and approximate memory
cost for vector-sum execution. It is a planning guard: it tells the benchmark
when materialized Python rows are acceptable for reference/debug and when
streamed or native fused execution should be preferred.

## What Changed

Implemented in `src/rtdsl/aggregate_tree_reference.py`:

- `estimate_vector_sum_materialization_pressure_2d(...)`
- `VECTOR_SUM_MATERIALIZATION_PRESSURE_2D_CONTRACT`

Updated the Barnes-Hut benchmark wrapper:

- added `materialization_pressure_bucketized_cpu`

## Local Evidence

Timing and pressure artifact:

- `docs/reports/goal2535_barnes_hut_materialization_pressure_local_2026-05-23.json`

At 2,048 bodies:

- contribution rows: 258,495
- estimated native intermediate bytes: 16,543,680
- estimated Python intermediate bytes: 82,718,400
- recommendation: `materialized_reference_allowed`

At 8,192 bodies:

- contribution rows: 1,188,963
- estimated native intermediate bytes: 76,093,632
- estimated Python intermediate bytes: 380,468,160
- recommendation: `streamed_or_native_fused`

The default Python warning threshold is 256 MiB. The byte estimates are
deliberately approximate because Python object overhead varies; the point is to
make the row-materialization boundary explicit and testable.

## Main Insight

The benchmark has crossed from "row contracts are enough to explain behavior"
to "row contracts must have a fused execution plan." At 8,192 bodies the
contribution rows alone are estimated above the warning threshold, before
counting the opening-frontier rows themselves.

This is now a concrete RTDL runtime requirement, not just an app observation:
generic aggregate-frontier programs need a way to stream/fuse vector
contributions and grouped reductions.

## Remaining Work

Local:

- write the fused native/partner lowering design packet;
- optionally add a 3-D reference variant for closer paper alignment;
- add a hard fail/warn policy for very large Python materialization runs.

Pod-required:

- build/run the authors' OWL sample;
- collect OptiX timings;
- validate a native RTDL fused frontier-to-vector-sum implementation.

## Claim Boundary

- Not native timing.
- Not authors-code timing.
- Not paper reproduction.
- Not public speedup wording.
- Native engines remain app-name-free.
