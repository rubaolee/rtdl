# Goal3862 - Generic AABB Multi-Operation Count Probe

Date: 2026-06-08

Status: internal generic-runtime probe, accepted with boundary.

## Purpose

Goal3861 showed that the LibRTS-style `operation=all` row is dominated by cold scene/query preparation, while the prepared hot query is already much smaller. Goal3862 tests whether a generic multi-operation AABB count primitive can reduce the hot query cost by running the independent supported counts through one prepared-query-set API.

The new generic native symbol is:

```text
rtdl_optix_count_prepared_aabb_index_2d_multi_operation_packed_queries
```

It is not LibRTS-specific. It accepts a prepared AABB index plus prepared point-query and box-query buffers, then returns:

- `point_contains`
- `range_contains`
- `range_intersects`

The Python binding exposes this as:

```text
PreparedOptixAabbIndex2D.count_prepared_query_set(...)
```

The LibRTS benchmark app uses the new path only for `--operation all` with prepared queries.

## Evidence

Pod:

```text
ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519
```

Artifact directory:

```text
docs/reports/goal3862_librts_aabb_multi_operation_streams_a5000/
```

Comparison baseline:

```text
docs/reports/goal3861_librts_aabb_prepared_probe_a5000/
```

## Result

The counts match Goal3861 exactly.

| Row | Goal3861 query median sec | Goal3862 query median sec | Hot speedup | Payload speedup |
| --- | ---: | ---: | ---: | ---: |
| `all_32768_repeat20` | 0.030255 | 0.030031 | 1.007x | 1.100x |
| `all_65536_repeat10` | 0.125268 | 0.121693 | 1.029x | 0.995x |

The hot-query improvement is real but small. It is not a major performance direction by itself.

The current LibRTS scale-profile row was also rerun after the native rebuild:

```text
all_pass: true
row: librts_spatial_index_optix_scale_default_32768
multi_operation_native_used: true
claim_flag_violations: []
payload elapsed_sec: 0.678777
prepared query median sec: 0.030449
```

## Interpretation

This goal gives RTDL a cleaner generic AABB query-set API, but it also proves that multi-operation bundling alone does not solve the LibRTS performance story. The expensive pieces remain:

- cold scene construction;
- prepared query-buffer construction;
- the inherent RT traversal for the four underlying count passes, especially the two-pass `range_intersects` contract.

The next major LibRTS direction should not be another Python wrapper tweak. It should be either:

1. a prepared-session benchmark/accounting contract that reports cold prepare and hot query consistently across apps; or
2. a deeper generic AABB predicate-count primitive that changes the number or nature of underlying traversals.

## Boundary

This goal does not authorize:

- release action;
- public speedup wording;
- whole-app acceleration claims;
- broad RT-core claims;
- paper reproduction claims;
- true zero-copy claims;
- automatic partner selection claims;
- app-specific native-engine logic.

The accepted claim is narrower: the generic multi-operation prepared AABB query-set path is correct and app-agnostic, but its measured hot speedup is only modest on the A5000 probe.
