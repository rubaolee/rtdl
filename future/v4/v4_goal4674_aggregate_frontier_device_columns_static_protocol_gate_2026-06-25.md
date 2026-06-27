# V4 Goal4674 Aggregate-Frontier Device Columns Static/Protocol Gate

Date: 2026-06-25

Status:

```text
goal4674_static_protocol_gate_complete_pod_not_authorized
```

Decision label:

```text
aggregate_frontier_device_columns_static_protocol_gate_pass__goal4675_local_runner_authorized__pod_not_authorized
```

Machine evidence:

```text
future/v4/evidence/v4_goal4674_aggregate_frontier_device_columns_static_protocol_gate_2026-06-25.json
```

## Decision

Goal4674 passes the local static/protocol gate for
`AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D`.

This authorizes only Goal4675 local runner productization:

```text
v4_aggregate_frontier_device_columns_2d_prepared_runner
```

It does not authorize POD benchmarking, V4 release, public speedup wording, or
whole-app high-performance wording.

## What Was Checked

The current source contains a real device-column contract and native ABI:

- `src/rtdsl/aggregate_tree_reference.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`

The required current symbols are present:

```text
AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D
rtdl_optix_prepare_aggregate_frontier_device_columns_2d
rtdl_optix_run_aggregate_frontier_device_columns_2d
rtdl_optix_destroy_aggregate_frontier_device_columns_2d
```

The native device-column path is not a Python-side or native-side wrapper around
the old host-row collector. The native API loads the device-column kernels:

```text
rtdl_aggregate_frontier_count_2d
rtdl_aggregate_frontier_prefix_2d
rtdl_aggregate_frontier_write_2d
```

and does not call:

```text
rtdl_optix_collect_aggregate_frontier_2d(
```

The run body launches the prepared count/prefix/write functions through
`cuLaunchKernel` and writes `row_offsets` plus device column pointers.

The runtime metadata also keeps the intended boundary:

```text
frontier_columns_materialized_on_host: false
row_offsets_materialized_on_host: false
```

Only small scalar host outputs are allowed before downstream continuation:

```text
row_count
attempted_count
overflow
phase_timings
```

## V2.14 / V3.0.2 / V4 Denominators

The denominator is now frozen enough for Goal4675 local work.

| Version | Classification | Route meaning |
| --- | --- | --- |
| V2.14 | logical family present; device-column primitive absent | RTDL/OptiX aggregate-frontier host/native row collection plus explicit CuPy or Numba weighted-vector continuation |
| V3.0.2 | device-column primitive present | same family already exists; V4/V3.0.2 same-route parity cannot be sold as a new V4 speed win |
| Current V4 | target selected; static gate passed | local runner productization may proceed; not a catalog/release surface yet |

This distinction matters. The clean-new-lever claim is only against V2.14. If a
later audit finds an equivalent V2.14 device-column route under another name,
this target must be reclassified as same-primitive improvement before any POD
run.

## Correctness Contract

Goal4675 and any later Goal4676 POD run must verify:

- aggregate-frontier row parity;
- row-offset parity;
- overflow fail-closed behavior;
- downstream weighted-vector summary parity against
  `sum_aggregate_frontier_weighted_vectors_2d_cpu_reference`;
- no host frontier rows before partner continuation.

Frozen row schema:

```text
source_id
frontier_kind_code
item_id
owner_aggregate_id
dfs_index
resume_index
metadata_flags
```

Forbidden hot-path outputs before partner continuation:

```text
frontier_i64_rows_host_tuple
frontier_rows_host_dicts
per_source_summary_host_dict
```

## Frozen Later POD Bars

These bars apply only if Goal4676 is separately authorized after Goal4675:

| Metric | Bar |
| --- | ---: |
| V4 aggregate-frontier hot over V2.14 | `>= 1.20x` |
| V4 aggregate-frontier wall over V2.14 | `>= 1.10x` |
| V4 app-probe hot over V2.14 | `>= 1.20x` |
| Correctness parity | required |
| Host frontier materialization in hot path | forbidden |
| Partner migration counts as speed | false |

## Goal4675 Authorization

Goal4675 may proceed locally with these restrictions:

- no POD run;
- no public claim;
- no app-identity public or native symbols;
- no Barnes-Hut force-law engine;
- no wrapping `rtdl_optix_collect_aggregate_frontier_2d` as the hot
  device-column route;
- no promotion of the old aggregate-tree fused weighted-vector sum as-is.

Goal4675 output must be a generic prepared runner with phase/residency telemetry
and local correctness fixtures.

## Kill Conditions

Stop and reclassify if any of these happens:

- V2.14 is found to have an equivalent device-column aggregate-frontier route.
- Goal4675 cannot run without host frontier row materialization before partner
  continuation.
- Goal4675 requires Barnes-Hut, force-law, or app-specific engine semantics.
- Goal4675 can only reuse the rejected aggregate-tree fused weighted-vector
  implementation as-is.
- Correctness parity against the frozen row and summary contracts fails.
- Phase telemetry cannot distinguish aggregate-frontier traversal from
  downstream continuation.

## Review State

This goal is complete as a local static/protocol gate. It is not an external
release authorization.

- Codex: self-audit complete.
- Claude: weekly limit is known until 2026-06-28 19:00 America/New_York; review
  debt is recorded instead of probing repeatedly.
- Antigravity: review request/debt is required before treating this as full
  external consensus.

The allowed next work is Goal4675 local implementation only.

## Goal-Level Decision Audit

1. Was I being stupid?
   - Yes, the dangerous path was available.
2. If yes, what action would have made it stupid?
   - Counting the existing aggregate-frontier family as a V4 speed win without
     freezing the V2.14 denominator and without proving the device-column route
     avoids host frontier materialization.
3. Is there another path that avoids getting stuck on that premise?
   - Yes. Treat this as a static/protocol gate only, authorize only local runner
     work, and keep POD plus public claims blocked.
4. Can I now try the different path that actually solves the problem?
   - Yes. Proceed to Goal4675 local runner productization; do not run POD until
     Goal4676 is separately authorized.

## Non-Authorization

This goal does not authorize V4 release, public speedup wording, whole-app
high-performance wording, POD spend, RT-core speedup wording, true-zero-copy
wording, C ABI, embedding, non-Python hosts, arbitrary callback claims, or any
Barnes-Hut/DBSCAN/RayJoin app-identity native kernel.
