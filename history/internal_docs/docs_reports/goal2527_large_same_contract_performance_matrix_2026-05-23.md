# Goal2527 Large Same-Contract Performance Matrix

Date: 2026-05-23

## Verdict

Yes: we can run serious large tests that clearly compare PostgreSQL, DuckDB,
cuDF, and RTDL on the same deterministic RayDB-style grouped aggregate
contract, assuming the recorded correctness checks are accepted.

This goal also exposed and fixed one runtime scale blocker: the RTDL OptiX
partner-resident grouped reduction path had a conservative 1,000,000-row guard.
The guard is now raised to 100,000,000 rows for this device-column grouped path
only; the older first-wave RT AABB DB lowering cap remains unchanged.

This is still internal diagnostic evidence. It does not authorize public
speedup, whole-DBMS, authors-code, RayDB reproduction, SQL-engine, or
true-zero-copy claims.

## Pod And Boundary

Pod:

```text
ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519_rtdl_codex
hostname: 57449dd4f93c
GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
CUDA toolkit: /usr/local/cuda-12.8
RTDL OptiX env: RTDL_OPTIX_PTX_ARCH=compute_89
LD_LIBRARY_PATH prefix: /usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64
```

Artifacts:

- `docs/reports/goal2527_large_same_contract_external_pod_2026-05-23.json`
- `docs/reports/goal2527_large_same_contract_rtdl_optix_pod_2026-05-23.json`
- `docs/reports/goal2527_large_same_contract_performance_matrix_pod_2026-05-23.json`

Benchmark contract:

- deterministic i64 columns: `row_id`, `region_id`, `ship_year`, `discount`,
  `quantity`, `revenue`;
- row counts: 1,000,000; 5,000,000; 10,000,000;
- groups: 1,024 dense `region_id` groups;
- predicate: `ship_year BETWEEN 1994 AND 1995`, `discount BETWEEN 4 AND 6`,
  `quantity < 25`;
- result: grouped `count`, `sum`, `min`, `max`, and
  `avg_as_sum_count` as `sum+count`.

Timing boundary:

- setup, deterministic data generation, table/DataFrame/tensor creation, index
  construction, and RTDL descriptor preparation are excluded;
- timed loops include query execution and compact grouped result
  materialization;
- warmup: 2;
- timed repeats: 5;
- all available results matched the shared expected rows.

## Indexing

PostgreSQL was given serious query-specific indexing:

```sql
CREATE INDEX rtdl_goal2527_predicate_group_cover_idx
ON rtdl_goal2527 (ship_year, discount, quantity, region_id) INCLUDE (revenue);

CREATE INDEX rtdl_goal2527_partial_group_cover_idx
ON rtdl_goal2527 (region_id) INCLUDE (revenue)
WHERE ship_year BETWEEN 1994 AND 1995
  AND discount BETWEEN 4 AND 6
  AND quantity < 25;
```

The 10M PostgreSQL plan used:

```text
Parallel Index Only Scan using rtdl_goal2527_partial_group_cover_idx
```

DuckDB was given its supported ART index on
`(ship_year, discount, quantity, region_id, revenue)`. Its optimizer still
preferred the analytic scan plus perfect-hash group-by path. That is an
important result: DuckDB's serious baseline for this workload is its columnar
analytic execution, not an index-only OLTP-style path.

## Performance Matrix

Median milliseconds, setup excluded:

| Rows | PostgreSQL indexed | DuckDB indexed setup | cuDF GPU dataframe | RTDL sum_count only | RTDL full contract |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1,000,000 | 6.241950 | 4.087197 | 42.533734 | 1.027780 | 1.601686 |
| 5,000,000 | 43.007387 | 11.630014 | 51.043358 | 1.382040 | 1.986026 |
| 10,000,000 | 66.663138 | 19.248983 | 52.286274 | 1.819912 | 2.425149 |

The final RTDL full contract uses one fused native `stats` launch that computes
`count`, `sum`, `min`, and `max` together. The older three-launch comparison
path remains recorded in the RTDL artifact:

| Rows | RTDL fused full contract | RTDL three-launch full contract | Fused / three-launch improvement |
| ---: | ---: | ---: | ---: |
| 1,000,000 | 1.601686 | 3.763097 | 2.35x |
| 5,000,000 | 1.986026 | 4.831247 | 2.43x |
| 10,000,000 | 2.425149 | 6.138255 | 2.53x |

Internal diagnostic ratios versus RTDL full contract:

| Rows | PostgreSQL / RTDL | DuckDB / RTDL | cuDF / RTDL |
| ---: | ---: | ---: | ---: |
| 1,000,000 | 3.90x | 2.55x | 26.56x |
| 5,000,000 | 21.65x | 5.86x | 25.70x |
| 10,000,000 | 27.49x | 7.94x | 21.56x |

Interpretation:

- RTDL full-contract is the fastest recorded full result path at all three
  large sizes, even against PostgreSQL with a partial covering index.
- DuckDB is very strong for this workload, but the fused RTDL full-contract
  path is now clearly faster at every measured size.
- cuDF is a valid lightweight GPU dataframe baseline, but this group-by path
  has higher dataframe/runtime overhead than RTDL's specialized partner-resident
  reductions.
- RTDL `sum_count` alone remains the fastest subpath, but full-contract now
  also uses one fused native launch rather than three launches.

## Engineering Consequences

Goal2527 gives us a better benchmark shape than the tiny fixture:

1. We now have a same-contract large matrix across SQL DBMS, embedded analytical
   SQL, GPU dataframe, and RTDL.
2. We confirmed serious PostgreSQL indexing matters and should be documented by
   plan evidence, not assumed.
3. We learned DuckDB indexing is not the core mechanism for this analytic
   grouped aggregate; its scan/group-by engine is the meaningful baseline.
4. We removed an RTDL scale blocker by raising the partner-resident grouped-row
   guard.
5. The app-driven runtime optimization target is complete: a fused
   full-contract grouped reduction now computes count/sum/min/max in one native
   launch instead of three.

## Claim Boundary

Allowed:

- On the recorded pod, for this deterministic grouped aggregate contract, all
  available implementations matched the expected compact grouped rows.
- On the recorded pod, RTDL fused full-contract median was `1.601686 ms`,
  `1.986026 ms`, and `2.425149 ms` for 1M, 5M, and 10M rows respectively.
- PostgreSQL used a partial covering index and an index-only scan in the 10M
  plan.

Blocked:

- public speedup wording;
- whole RayDB or authors-code comparison;
- SQL-engine claim for RTDL;
- true-zero-copy claim;
- claim that DuckDB used the created index for this analytic query;
- claim that user Python code performance is RTDL's responsibility.
