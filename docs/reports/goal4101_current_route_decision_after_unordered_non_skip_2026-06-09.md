# Goal4101 - Current Route Decision After Unordered Non-Skip Partition Stream

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4100 added and measured `device_count_then_emit_non_skip_unordered`, an explicit order-insensitive partition-pair stream for the RT-DBSCAN partition-convergence preview. This report refreshes the current benchmark route registry so readers see that evidence without mistaking it for a default-route promotion.

## Route Registry Change

The registry version is now:

`rtdl.v2_10.current_benchmark_route_decisions.goal4101.v1`

The RT-DBSCAN route remains:

`RTDL/OptiX fixed-radius grouped stream with Numba component/signature continuation`

Goal4100 is recorded as an unpromoted candidate because:

- unordered non-skip build medians improve by 1.13x-1.17x over the Goal4096 sorted non-skip path;
- unordered pair emit medians improve by 1.38x-2.32x;
- clustered five-run prepared reuse is still 0.851x versus the current recommended route;
- road five-run prepared reuse is still 0.605x and does not break even;
- the unordered stream has `pair_order = device_atomic_append_unordered`, so it is not the same contract as sorted pair rows for order-sensitive consumers.

## Interpretation

The new path is useful as an explicit option for order-insensitive continuations. It is not a replacement for the current route. It also clarifies the next runtime target: not another small cleanup of the emitted row table, but a fused/native fixed-radius grouped-union primitive that can consume device status directly and avoid the double pass plus full partition-pair materialization.

## Boundary

This is advisory route metadata only. Users choose partners explicitly. It does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, AMD performance wording, or app-specific native-engine logic.
