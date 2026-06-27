# Goal2528 RayDB-Style Benchmark App Closeout

Date: 2026-05-23

## Verdict

The RayDB-style benchmark app is complete as an RTDL language/runtime
reconstruction benchmark.

It is not a RayDB paper reproduction, not an authors-code comparison, not a SQL
engine, and not a DBMS implementation. Its final scope is a deterministic
RayDB-style grouped aggregate contract used to force and validate app-agnostic
RTDL runtime capabilities.

## Final App Scope

The closed app covers:

- deterministic columnar i64 input;
- predicate filtering over `ship_year`, `discount`, and `quantity`;
- dense grouped aggregation by `region_id`;
- grouped `count`, `sum`, `min`, `max`, and decomposed
  `avg_as_sum_count`;
- CPU reference correctness;
- PostgreSQL correctness and indexed timing;
- DuckDB analytical timing;
- cuDF GPU dataframe timing;
- RTDL OptiX partner-resident CUDA tensor timing;
- final fused RTDL full-contract grouped stats path.

The app intentionally does not cover:

- SSB SF=20 reproduction;
- RayDB authors-code build or timing;
- Crystal/HeavyDB/MonetDB reproduction;
- SQL parsing or query optimization;
- DBMS storage/index management inside RTDL;
- public speedup claims.

## Runtime Work Completed

This benchmark drove the following app-agnostic RTDL improvements:

- partner-resident columnar descriptors for CUDA tensor inputs;
- generic grouped i64 dispatcher;
- fused grouped `sum_count`;
- grouped `min` and `max`;
- raised device-column grouped-row validation cap from 1M to 100M rows for the
  partner-resident grouped path only;
- fused grouped `stats` reduction returning `count`, `sum`, `min`, and `max` in
  one native launch.

The native engine remains app-name-free for this path. The new fused operation
is generic grouped integer statistics, not a RayDB-specific ABI.

## Final Performance Evidence

Final pod:

```text
ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519_rtdl_codex
hostname: 57449dd4f93c
GPU: NVIDIA RTX 4000 Ada Generation
```

Final large same-contract artifact:

- `docs/reports/goal2527_large_same_contract_performance_matrix_pod_2026-05-23.json`

Median milliseconds, setup/index/descriptor preparation excluded:

| Rows | PostgreSQL indexed | DuckDB | cuDF | RTDL fused full contract |
| ---: | ---: | ---: | ---: | ---: |
| 1,000,000 | 6.241950 | 4.087197 | 42.533734 | 1.601686 |
| 5,000,000 | 43.007387 | 11.630014 | 51.043358 | 1.986026 |
| 10,000,000 | 66.663138 | 19.248983 | 52.286274 | 2.425149 |

All available results matched the shared expected compact grouped rows.

## What Remains Deferred

Further work is optional and should be a new goal, not a blocker for this app:

- authors-code RayDB build/data/same-contract adapter;
- Crystal or another GPU database baseline;
- SSB-scale paper reproduction;
- broader SQL/DBMS semantics;
- public speedup wording with external review.

## Closeout Decision

No more work is required for this benchmark app before moving on. The app has
already served its purpose: it exposed runtime gaps, forced app-agnostic
partner-resident grouped reductions, produced large same-contract external
baseline evidence, and closed with a fused full-contract RTDL path.
