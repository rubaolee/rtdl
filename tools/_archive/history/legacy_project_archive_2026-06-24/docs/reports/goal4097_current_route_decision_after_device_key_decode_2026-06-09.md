# Goal4097 Current Route Decision After Device Key Decode

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4097 refreshes the current benchmark route registry after Goal4096's
device partition-key decode optimization.

The RT-DBSCAN route improves, but the default route still does not change.

## Current Route

The current reader-facing RT-DBSCAN route remains:

- RTDL/OptiX fixed-radius grouped stream
- Numba component/signature continuation

The partition-convergence preview remains explicit and unpromoted.

## New Evidence

Goal4096 removes unnecessary host partition-key reconstruction from device pair
enumeration. In the non-skip partition-convergence preview, build medians improve
over Goal4093:

| Profile | Goal4093 build median | Goal4096 build median | Speedup |
| --- | ---: | ---: | ---: |
| `clustered3d` | 0.090940 | 0.076903 | 1.183x |
| `road3d` | 0.082980 | 0.067624 | 1.227x |
| `ngsim_dense` | 0.201882 | 0.136991 | 1.474x |

Prepared reuse also improves but remains below the current route for five runs:

| Profile | Goal4096 5-run speedup vs current route | Break-even |
| --- | ---: | ---: |
| `clustered3d` | 0.849x | 6.87 runs |
| `road3d` | 0.602x | never |

## Registry Changes

- `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is now
  `rtdl.v2_10.current_benchmark_route_decisions.goal4097.v1`.
- The RT-DBSCAN route now references Goal4096.
- The unpromoted candidate list records
  `partition_convergence_hybrid default promotion after Goal4096 device key decode improvement`.

## Boundary

This is advisory route metadata only. It does not authorize release action,
public speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, automatic partner selection,
AMD performance wording, app-specific native-engine logic, or default promotion
of `partition_convergence_hybrid`.
