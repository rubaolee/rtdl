# Goal 19: RTDL vs Native Embree Performance Comparison

Goal 19 focuses on one question:

Can the current RTDL runtime paths achieve performance comparable to a pure C/C++ + Embree implementation on the same workloads?

This round is a measurement and comparison round, not a language-feature round.

## Goal

Compare the current RTDL Embree execution paths against pure native C/C++ + Embree programs on matched workloads and matched datasets.

## Compared Paths

For workloads where native baselines exist or can be added, compare:

1. RTDL ordinary dict-return path
2. RTDL first-class raw path:
   - `run_embree(..., result_mode="raw")`
3. RTDL prepared raw path:
   - `prepare_embree(...).bind(...).run_raw()`
4. pure C/C++ + Embree executable path

## Required Scope

Goal 19 should include:

- `lsi`
- `pip`

If practical in the same round, extend native baselines to:

- `overlay`
- `ray_tri_hitcount`
- `segment_polygon_hitcount`
- `point_nearest_segment`

But the minimum acceptable slice is `lsi` + `pip`.

## Required Evidence

The round should report two kinds of evidence:

### 1. Deterministic fixture comparison

Use the same small deterministic fixtures for:

- correctness parity
- host-path overhead comparison
- near-native gap measurement

### 2. Scalability-profile comparison

Use matched larger profiles for `lsi` and `pip` so the project can answer:

- how the latest RTDL low-overhead path compares to pure native Embree under larger workloads
- whether the current host/runtime gap remains acceptable as data size grows

## Runtime Budget

This round should stay practical on the current Mac.

The comparison package should be designed to finish in roughly:

- at least `5 minutes`
- at most about `10 minutes`

for the default local run.

That budget includes:

- deterministic fixture comparisons
- larger matched profile comparisons
- all measured RTDL/native modes included in the round

`lsi` and `pip` do not need to use the same larger-profile sizes. They should use different sizes if that is what is needed to keep the total comparison run inside the 5–10 minute window.

## Acceptance Criteria

Goal 19 is acceptable only if:

1. workload inputs are matched between RTDL and native paths
2. correctness parity is verified before timing claims are accepted
3. the report clearly distinguishes:
   - deterministic fixture comparisons
   - larger scalability-profile comparisons
4. the default benchmark package finishes within the intended 5–10 minute local window
5. native baselines are reported only for workloads that actually have native executables
6. the report states clearly whether RTDL is:
   - still materially slower
   - close enough for the current goal
   - or still in need of another runtime redesign slice

## Non-Goals

This round does not require:

- NVIDIA / OptiX work
- new DSL syntax
- new workloads unless needed for native-comparison completeness
- paper-reproduction claims beyond the measured Embree comparisons

## Main Deliverables

- updated native comparison executables if needed
- comparison harness for current RTDL runtime modes vs native
- benchmark JSON artifacts
- markdown comparison report
- final conclusion on whether the current RTDL runtime is performance-comparable enough to proceed
