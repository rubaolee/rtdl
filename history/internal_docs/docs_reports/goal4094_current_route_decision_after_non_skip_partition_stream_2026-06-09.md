# Goal4094 Current Route Decision After Non-Skip Partition Stream

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4094 refreshes the current benchmark route registry after Goal4093's
non-skip partition pair stream evidence. It does not change the RT-DBSCAN
default route.

## Route Decision

The current RT-DBSCAN reader-facing route remains:

- RTDL/OptiX fixed-radius grouped stream
- Numba component/signature continuation

The partition-convergence preview remains explicit and unpromoted.

## Why Goal4093 Does Not Change The Default

Goal4093 added an explicit `device_count_then_emit_non_skip` mode that elides
`safe_skip` partition pairs from the materialized stream.

It is a useful memory/materialization option:

| Profile | Row reduction | Build-time improvement |
| --- | ---: | ---: |
| `clustered3d` | 1.795x | 1.136x |
| `road3d` | 1.504x | 1.061x |
| `ngsim_dense` | 2.635x | 1.109x |

But it still does not beat the current grouped-stream Numba route in the
prepared-reuse setting:

| Profile | 5-run speedup vs current route | Break-even |
| --- | ---: | ---: |
| `clustered3d` | 0.815x | 7.42 runs |
| `road3d` | 0.572x | never |

So the registry records Goal4093 as evidence, while keeping non-skip partition
convergence as an explicit unpromoted candidate.

## Updated Registry Metadata

- `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is now
  `rtdl.v2_10.current_benchmark_route_decisions.goal4094.v1`.
- The RT-DBSCAN route now references Goal4093.
- The rejected candidates include
  `partition_convergence_hybrid non-skip default promotion after Goal4093 active-pair stream evidence`.
- The next runtime action now names the remaining work more precisely:
  lower candidate/root/repeated-scan work, avoid full materialization, preserve
  same-contract correctness, avoid `ngsim_dense` regression, and beat the
  current grouped-stream Numba route before reconsidering defaults.

## Boundary

This is advisory route metadata only. It does not authorize release action,
public speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, automatic partner selection,
AMD performance wording, app-specific native-engine logic, or default promotion
of `partition_convergence_hybrid`.
