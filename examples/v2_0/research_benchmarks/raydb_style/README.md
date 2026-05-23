# RayDB-Style Columnar Aggregate Study

This directory contains the first RayDB-style benchmark slice. It is a
language/runtime reconstruction harness, not a RayDB clone and not a performance
claim.

The app keeps database-shaped semantics in Python. The reusable RTDL code is the
generic columnar grouped aggregate oracle in `src/rtdsl/columnar_aggregate_reference.py`.
That module also exposes `plan_columnar_aggregate_lowering(...)`, which records
the current backend support matrix and the next direct-columnar engine target.

## Run

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --mode all
```

Embree count/sum parity, when `librtdl_embree` is available:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend embree --mode all
```

OptiX count/sum parity, when `librtdl_optix` and a CUDA-capable NVIDIA runtime
are available:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend optix --mode all
```

Experimental partner-resident OptiX count/sum/min/max parity plus composite
avg-as-sum-count lowering, when PyTorch CUDA tensors and the current OptiX
backend are available:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=build/librtdl_optix.so python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend optix_partner_resident_experimental --mode all
```

## Current Scope

- tiny denormalized fixture;
- integer-coded group and predicate columns;
- CPU reference grouped `count`, `sum`, `min`, `max`, and `avg_as_sum_count`;
- Embree parity for grouped `count` and `sum` through existing generic columnar
  payload support;
- OptiX parity for grouped `count` and `sum` through existing generic columnar
  payload support;
- experimental OptiX partner-resident parity for grouped `count`, `sum`, `min`,
  `max`, and composite `avg_as_sum_count` using CUDA tensor descriptors and
  compact grouped output materialization;
- composite `avg_as_sum_count` lowers to a generic fused native `sum_count`
  grouped reduction; there is no native average ABI;
- explicit lowering metadata showing that no path authorizes true zero-copy,
  SQL/DBMS, whole-app, or public speedup wording;
- no authors-code timing, SQL engine, DBMS behavior, or row
  materialization claim.

## Closeout

As of Goal2520, this benchmark slice is closed as an RTDL reconstruction
harness for the partner-resident grouped-aggregate path. Goals2527 and 2528 add
the final large same-contract performance matrix and full-contract closeout.
The final partner-resident path uses one runtime dispatcher for generic grouped
i64 reductions, so the app no longer selects low-level native symbols directly.

Final large same-contract evidence is recorded in:

- `docs/reports/goal2527_large_same_contract_performance_matrix_2026-05-23.md`
- `docs/reports/goal2527_large_same_contract_performance_matrix_pod_2026-05-23.json`
- `docs/reports/goal2528_raydb_style_benchmark_app_closeout_2026-05-23.md`

The final RTDL OptiX path includes a fused generic grouped `stats` reduction
that returns `count`, `sum`, `min`, and `max` in one native launch. On the
recorded pod, the fused full-contract medians were `1.601686 ms`, `1.986026 ms`,
and `2.425149 ms` for 1M, 5M, and 10M rows respectively.

Authors-code performance comparison is intentionally separate. It requires a
new feasibility gate proving that the authors' code is available, buildable,
and comparable under the same input/query/result contract.

## External Correctness Oracles

Goal2522 adds a PostgreSQL correctness-oracle runner for the same tiny fixture:

```bash
PYTHONPATH=src:. python3 scripts/goal2522_postgresql_correctness_oracle.py \
  --dsn "$RTDL_POSTGRES_DSN" \
  --output docs/reports/goal2522_postgresql_correctness_oracle_2026-05-23.json
```

This checks SQL semantics for grouped `count`, `sum`, `min`, `max`, and
`avg_as_sum_count` on the exact synthetic contract. It is not a PostgreSQL
performance comparison and does not authorize SQL-engine, DBMS, authors-code,
RayDB reproduction, true zero-copy, or speedup claims.

Goal2523 and Goal2524 add pod-backed diagnostic timing for PostgreSQL and
DuckDB on the same tiny contract. Goal2525 records that the tested pod had an
NVIDIA GPU but no quick GPU database stack installed, so RAPIDS/cuDF is deferred
to a separate install-and-contract goal if we decide a GPU DB-like baseline is
worth the setup cost.

Goal2526 performs that lightweight GPU baseline with RAPIDS/cuDF. It loads the
fixture once into a cuDF GPU DataFrame, runs the same filter/groupby reductions,
and records exact correctness parity plus diagnostic timing. This remains a GPU
dataframe baseline, a GPU dataframe boundary check, not a SQL-engine or DBMS
claim.

Goal2527 promotes the external baseline shape from tiny fixture to large
same-contract testing. PostgreSQL is tested with query-specific serious
indexing, DuckDB is tested with its supported index setup while its optimizer
uses analytical scan/group-by, cuDF remains the lightweight GPU dataframe
baseline, and RTDL uses partner-resident CUDA tensors.

Goal2528 closes the app after the final fused RTDL full-contract reduction. Any
authors-code RayDB comparison, SSB paper reproduction, or Crystal/GPU-DBMS
comparison is deferred to a separate goal.
