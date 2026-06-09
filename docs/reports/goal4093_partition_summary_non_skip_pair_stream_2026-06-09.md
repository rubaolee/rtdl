# Goal4093 Partition Summary Non-Skip Pair Stream

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4093 adds an explicit device partition-summary enumeration mode:

`device_count_then_emit_non_skip`

This mode emits only actionable partition pairs:

- `safe_full`
- `ambiguous`

It elides `safe_skip` rows from the materialized pair stream. The old
`device_count_then_emit` mode remains unchanged and still emits all partition
pairs.

## Why This Matters

After Goal4088, the remaining partition-summary producer debt is not host AABB
rebuild. It is the cost of complete visible partition-pair materialization. The
component-union continuation does not need rows whose status is `safe_skip`, so
Goal4093 adds a generic explicit mode that does not materialize those rows.

This is not DBSCAN-specific. It is a generic fixed-radius partition-summary
stream option.

## Implementation

Files changed:

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`

The RawKernel helper now accepts `emit_status_filter` with values:

- `all`
- `non_skip`

When `non_skip` is selected, the kernel returns before appending rows with
status `0` (`safe_skip`). Metadata records:

- `pair_stream_filter: non_skip_actionable_pairs`
- `safe_skip_pairs_elided: true`
- `pair_capacity_source: device_exact_active_count`

The option is exposed through the RT-DBSCAN benchmark CLI as an explicit
`--partition-pair-enumeration device_count_then_emit_non_skip` choice.

## Pod Evidence

Artifacts:

- `docs/reports/goal4093_partition_summary_non_skip_pair_stream_pod.json`
- `docs/reports/goal4093_partition_summary_non_skip_pair_stream_pod.stdout.txt`
- `docs/reports/goal4093_partition_non_skip_reuse_pod.json`
- `docs/reports/goal4093_partition_non_skip_reuse_pod.stdout.txt`

Hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.05

Source commit:

- `28291d111588440e14c11f08657a8088fb7619f6`

## Build-Time Result

Comparison is against Goal4088 all-pair device count-then-emit after the host
AABB skip.

| Profile | All-pair rows | Non-skip rows | Row reduction | Goal4088 median sec | Goal4093 median sec | Time improvement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 19,668,778 | 10,960,581 | 1.795x | 0.103282 | 0.090940 | 1.136x |
| `road3d` | 10,271,711 | 6,830,362 | 1.504x | 0.088037 | 0.082980 | 1.061x |
| `ngsim_dense` | 30,525,629 | 11,585,223 | 2.635x | 0.223795 | 0.201882 | 1.109x |

The row-count reduction is large. The time improvement is smaller because the
kernel still scans the same partition-neighborhood search space twice: once for
counting and once for emitting.

## Reuse Result

| Profile | Prepare sec | Replay median sec | 5-run speedup vs current route reference | Break-even runs |
| --- | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.326070 | 0.049348 | 0.815x | 7.42 |
| `road3d` | 0.112484 | 0.040841 | 0.572x | never |

Clustered repeated-signature reuse improves again, from an 8.48-run break-even
after Goal4088 to 7.42 runs after Goal4093. Road still never breaks even
because replay remains slower than the current recommended route.

## Policy

Keep `device_count_then_emit_non_skip` as an explicit memory/materialization
option. Do not promote it as the RT-DBSCAN default route.

The next larger step remains a fused/native producer that avoids scanning the
same partition-neighborhood space twice and can feed safe-full/ambiguous
continuations without materializing a full pair table.

## Boundary

This report does not promote `partition_convergence_hybrid`, change the default
route, add a native ABI, authorize release wording, public speedup wording,
broad RT-core wording, whole-app acceleration wording, paper-reproduction
wording, hidden dispatch, automatic partner selection, app-specific engine
logic, or true-zero-copy wording.
