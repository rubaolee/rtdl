# Goal 443: v0.7 Columnar Repeated-Query Performance Gate

Date: 2026-04-16

## Verdict

Goal 443 is implemented and ready for external review.

This goal refreshes the old Goal 437 repeated-query gate after Goals 440, 441,
and 442 added columnar prepared DB dataset transfer to Embree, OptiX, and
Vulkan. Goal 437 remains historical row-transfer evidence; Goal 443 is the
current columnar-transfer evidence.

## Reproducible Artifact

Linux host:

```text
lestat-lx1
```

Command:

```text
PYTHONPATH=src:. python3 scripts/goal443_columnar_repeated_query_perf_gate.py --row-count 200000 --repeats 10 --dsn dbname=postgres
```

Raw JSON:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal443_columnar_repeated_query_perf_linux_2026-04-16.json
```

The command was preceded by `pg_isready`; the resulting readiness banner was
trimmed from the JSON artifact so the checked-in file is valid JSON.

## Repeated-Query Performance

All RTDL measurements use `transfer="columnar"`.

### Conjunctive Scan

| Engine | Prepare/setup once | Median query | Total 10 queries | PostgreSQL setup | PostgreSQL median query | PostgreSQL total | Total speedup vs PG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Embree | 0.868922 s | 0.016723 s | 1.035639 s | 10.095979 s | 0.027527 s | 10.371679 s | 10.01x |
| OptiX | 0.993161 s | 0.011508 s | 1.515499 s | 10.095979 s | 0.027527 s | 10.371679 s | 6.84x |
| Vulkan | 0.990011 s | 0.013537 s | 1.438462 s | 10.095979 s | 0.027527 s | 10.371679 s | 7.21x |

### Grouped Count

| Engine | Prepare/setup once | Median query | Total 10 queries | PostgreSQL setup | PostgreSQL median query | PostgreSQL total | Total speedup vs PG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Embree | 0.845944 s | 0.013675 s | 0.982888 s | 12.140907 s | 0.020374 s | 12.346080 s | 12.56x |
| OptiX | 0.831830 s | 0.004832 s | 0.881182 s | 12.140907 s | 0.020374 s | 12.346080 s | 14.01x |
| Vulkan | 0.821223 s | 0.007231 s | 0.893831 s | 12.140907 s | 0.020374 s | 12.346080 s | 13.81x |

### Grouped Sum

| Engine | Prepare/setup once | Median query | Total 10 queries | PostgreSQL setup | PostgreSQL median query | PostgreSQL total | Total speedup vs PG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Embree | 0.837713 s | 0.030569 s | 1.145093 s | 10.160739 s | 0.035185 s | 10.513986 s | 9.18x |
| OptiX | 0.822961 s | 0.010208 s | 0.924547 s | 10.160739 s | 0.035185 s | 10.513986 s | 11.37x |
| Vulkan | 0.823134 s | 0.013092 s | 0.953144 s | 10.160739 s | 0.035185 s | 10.513986 s | 11.03x |

## Correctness Boundary

The JSON artifact records Python truth, PostgreSQL, and backend row-count/hash
equality for every measured workload:

- `conjunctive_scan`: 22,268 rows, hash `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- `grouped_count`: 8 rows, hash `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- `grouped_sum`: 8 rows, hash `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`

## Interpretation

Columnar prepared dataset transfer removes the old row-struct compatibility
ingestion caveat from the repeated-query performance gate. The setup/prepare
phase is now around 0.82 to 0.99 seconds for the measured 200k-row workloads
across all three RT backends.

The justified v0.7 claim is:

RTDL can express three bounded database-style workload kernels and run them
through native prepared RT backends with columnar table ingestion and reusable
acceleration structures. On the Linux 200k-row synthetic gate, Embree, OptiX,
and Vulkan all beat PostgreSQL fresh setup plus 10 repeated queries for the
measured cases.

The excluded claims remain:

- RTDL is not a full database system.
- This does not replace PostgreSQL.
- This does not prove arbitrary SQL acceleration.
- This does not claim PostgreSQL-level durability, concurrency, query planning,
  indexing, or transaction semantics.
