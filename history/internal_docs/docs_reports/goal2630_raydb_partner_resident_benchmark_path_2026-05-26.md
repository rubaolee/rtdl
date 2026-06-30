# Goal2630 RayDB Partner-Resident Benchmark Path

Date: 2026-05-26

This internal report closes the immediate RayDB-style data-movement/reduction
gap found in Goal2628. It does not make a public speedup claim and it does not
claim RayDB SQL/DBMS behavior.

## Problem

Goal2628 measured RayDB-style grouped count/sum through the first-wave OptiX
columnar payload path. That path copied host columns into an OptiX payload and
reported:

- `true_zero_copy_authorized=false`
- `all_numeric_columns_use_typed_host_buffers=false`
- `typed_host_buffer_column_count=0`
- `transfer_path=direct_columnar_record_set_to_columnar_payload`

At 960K rows, that path was slower than Embree:

- count: Embree `0.189s`, OptiX `0.736s`
- sum: Embree `0.190s`, OptiX `0.652s`

This was a real data movement / reduction path problem, not evidence that the
partner-resident grouped-reduction mechanism was slow.

## Change

The benchmark runner now uses the existing generic OptiX partner-resident
grouped-i64 dispatcher for the RayDB-style OptiX row:

```text
optix_partner_resident_experimental
run_optix_partner_resident_columnar_grouped_i64_reduction
```

The app now supports `--warmup` and `--repeat` so the benchmark can measure a
warm prepared-device query inside one process rather than a cold one-shot path.

Important boundary: this path avoids host table copy/materialization and uses
CUDA device-resident columns, but it still reports `true_zero_copy_authorized=false`
and `rt_core_accelerated=false`. It is a Python+partner+RTDL data-resident
grouped-reduction path, not an RT-core traversal claim.

## Pod Evidence

Pod:

```text
ssh root@203.57.40.101 -p 10165 -i ~/.ssh/id_ed25519
```

Actual local key used on this Mac:

```text
/Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Commit:

```text
0005a05193920fe1b6a66e91d0108ce41d2f1ce8
```

Artifact:

```text
docs/reports/goal2630_raydb_partner_resident_matrix_pod/summary.json
docs/reports/goal2630_raydb_partner_resident_matrix_pod/summary.md
```

## Result

Workload: synthetic RayDB-style grouped aggregate, `120000` fixture copies,
`960000` rows, warmup `2`, repeat `12`.

| Mode | Embree query sec | OptiX partner-resident warm query median sec | Speedup vs Embree |
| --- | ---: | ---: | ---: |
| grouped count | `0.211074` | `0.000732717` | `288x` |
| grouped sum | `0.198884` | `0.000954303` | `208x` |

Both OptiX rows matched the CPU reference.

## Interpretation

RayDB is no longer a generic "OptiX slower than Embree" case when we use the
partner-resident path we already built. The old loss came from the wrong
benchmark front door: cold/copy columnar payload timing instead of warm
device-resident grouped reduction.

What remains unsolved:

- This still is not a true-zero-copy public claim.
- This still is not RT-core accelerated.
- The row remains a synthetic RayDB-style grouped aggregate, not a full RayDB
  reproduction or DBMS benchmark.

