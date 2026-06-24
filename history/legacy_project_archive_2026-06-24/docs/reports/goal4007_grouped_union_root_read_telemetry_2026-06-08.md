# Goal4007 Grouped-Union Root-Read Telemetry

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal4007 adds root-find telemetry to the existing generic OptiX fixed-radius
grouped-union path. This is diagnostic only: it does not add a native ABI, does
not change the accepted runtime strategy, does not authorize release wording,
and does not claim a performance improvement.

The purpose is to identify whether the remaining RT-DBSCAN grouped-stream cost
is just radius-candidate traversal, or whether repeated parent-root reads are
also large enough to justify the next generic primitive.

## Change

The existing device helper `find_grouped_union_root_readonly` now records:

- `uint64[8]=root_find_invocations`
- `uint64[9]=root_find_parent_link_steps`

The Python runtime still treats a 4-counter buffer as the old ABI-compatible
telemetry shape and an 8-counter buffer as the existing extended candidate
diagnostic shape. A 10-counter buffer opt-ins to the new root-read diagnostics:

- `grouped_union_extended_telemetry_enabled: true`
- `grouped_union_root_read_telemetry_enabled: true`
- `grouped_union_telemetry_counter_count: 10`

The pod sweep runner keeps its old default of `--telemetry-counters 8`; Goal4007
passes `--telemetry-counters 10` explicitly.

## Pod Evidence

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.

Source commit for the code under test: `94bf59a4`.

Command shape:

```bash
python3 scripts/goal3996_grouped_union_extended_telemetry_sweep_pod.py \
  --goal Goal4007 \
  --profile <profile> \
  --radius <actual benchmark radius> \
  --point-counts 65536 \
  --repeats 3 \
  --telemetry-counters 10 \
  --output docs/reports/goal4007_grouped_union_root_read_telemetry_pod/<profile>_65536.json
```

Artifacts:

- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/clustered3d_65536.json`
- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/road3d_65536.json`
- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/ngsim_dense_65536.json`

## Default-Route Telemetry

Rows below use the current accepted route:
`same_root_on_direct_off`.

| Profile | Radius | Median elapsed sec | Candidates | Same-root culled | Reported | Root calls | Parent-link steps | Root calls / candidate | Steps / root call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.055 | 0.214375 | 273,911,978 | 273,833,704 | 78,274 | 548,003,862 | 708,889,367 | 2.001 | 1.294 |
| `road3d` | 0.030 | 0.066684 | 85,627,372 | 85,469,792 | 157,580 | 171,688,664 | 304,914,824 | 2.005 | 1.776 |
| `ngsim_dense` | 0.012 | 0.019155 | 12,299,418 | 12,225,077 | 74,341 | 24,764,290 | 33,227,681 | 2.013 | 1.342 |

## Interpretation

The accepted grouped-union route is not mainly limited by successful unions.
Across the actual 65K benchmark radii:

- candidates dominate the work;
- same-root culling removes 99.4%-99.97% of candidate hits;
- the path performs about two readonly root finds per candidate;
- parent-link walks are nontrivial, especially for `road3d` at 1.776 parent-link
  steps per root call.

This explains why Goal4002's direct side-effect mode did not become a robust
default: bypassing the any-hit report is not enough when the path still performs
massive candidate traversal and root-read traffic.

It also explains why Goal4004's microcell route was the wrong direction:
moving to a cell graph introduced huge partner work while failing to eliminate
the deeper generic requirement.

## Design Consequence

The next performance primitive should not be an app-shaped DBSCAN ABI and should
not revive the rejected microcell route. The evidence points to the
partition-convergence hybrid shape encoded as the
Goal4005 `partition_convergence_hybrid` candidate:

1. device-resident partition AABB/count columns;
2. safe full-partition-pair summary without materializing candidate pairs;
3. RT traversal only for ambiguous boundary partition pairs;
4. deterministic component-root convergence and staleness counters.

Goal4007 narrows that target: the primitive must reduce not only radius
candidate hits, but also repeated root-read traffic.

## Claim Boundary

This report does not authorize:

- a v2.x release claim;
- a DBSCAN-native ABI claim;
- a paper speedup claim;
- a broad RT-core speedup claim;
- a default switch away from `grouped_stream`.

It is root-find telemetry, diagnostic only.
