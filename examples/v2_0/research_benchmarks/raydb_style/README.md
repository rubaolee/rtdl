# RayDB-Style Columnar Aggregate Study

This directory contains the first RayDB-style benchmark slice. It is a
language/runtime reconstruction harness, not a RayDB clone and not a public or
whole-app performance claim.

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

Paper-shaped RayDB RT contract reference:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend paper_rt_cpu_reference --mode all
```

Paper-shaped RayDB RT OptiX path, after rebuilding `librtdl_optix` on a CUDA pod:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=build/librtdl_optix.so python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend paper_rt_optix --mode all
```

Goal2684 full RT hit-stream plus Triton continuation path, after rebuilding
the native libraries and installing a CUDA-capable Triton/PyTorch stack:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=build/librtdl_optix.so python examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend paper_rt_optix_hit_stream_triton --mode all
```

This path follows the authors' `RayDB-i0` execution shape at the contract level:
one row becomes one `Triangle3D`, scan predicates are encoded on `Z`, group ids
are encoded on `Y`, aggregate payloads are encoded on `X`, and query regions are
probed by dense `+Z` rays at `Sx/2` and `Sy/2` spacing. Hits are deduplicated by
primitive id before grouped reduction, matching the any-hit/primitive-flag logic
in the reference implementation.

The corresponding RT-core backend is `paper_rt_optix`. It lowers through the
generic `generic_ray_triangle_primitive_grouped_i64_reduction_3d` primitive and
requires a current rebuilt OptiX library on a CUDA pod. The OptiX implementation
is native and RT-core accelerated, but there is no RayDB-specific native code:
it only knows rays, triangles, primitive ids, group ids, payload values,
deduplication, and grouped integer reductions. Python owns RayDB query encoding
and output interpretation.

The Goal2684 hit-stream backend separates traversal from continuation: Embree
or OptiX emits only generic `(ray_id, primitive_id)` hit rows through
`RAY_TRIANGLE_HIT_STREAM_3D`; Python maps primitive ids to app-owned group/value
columns; Triton performs generic grouped `count`, `sum`, `min`, `max`, or fused
`sum_count` continuation. This is the intended v2.5 boundary: RT traversal stays
in RTDL/Embree/OptiX, continuation moves to Triton, and RayDB/SQL/table
semantics stay in the app.

## Current Scope

- tiny denormalized fixture;
- deterministic generated fixture for RT-vs-Embree stress testing;
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
- paper-shaped RayDB RT CPU contract reference for `count`, `sum`, `min`, `max`,
  and `avg_as_sum_count`;
- paper-shaped RayDB RT OptiX path for `count`, `sum`, `min`, `max`, and
  `avg_as_sum_count` through the generic native
  `generic_ray_triangle_primitive_grouped_i64_reduction_3d` primitive;
- paper-shaped RayDB RT hit-stream path for `count`, `sum`, `min`, `max`, and
  `avg_as_sum_count` through generic `(ray_id, primitive_id)` rows plus Triton
  grouped continuation;
- typed packed host buffers for the paper-shaped OptiX path, avoiding Python
  `Triangle3D`/`Ray3D` object construction on the measured path;
- prepared primitive payloads and prepared ray batches for repeated-query
  timing;
- partner-owned CUDA query-ray columns through Torch or CuPy, packed on device
  into a generic prepared ray batch;
- explicit lowering metadata showing that no path authorizes true zero-copy,
  SQL/DBMS, whole-app, or public speedup wording;
- no authors-code timing, SQL engine, DBMS behavior, or row
  materialization claim.

## Current RT-Core Evidence

Goal2644 reopens the benchmark direction because the earlier closed path was a
partner-resident grouped-reduction study, not the paper's RT-core path. The
contract reference is derived from `RayDB-i0` branch `fin` commit
`a610c00d7334d8907435cc0a124f9ca8392ee456`.

Goal2645 adds the generic native OptiX primitive and pod evidence proving real
GAS/`optixTrace` execution. Goal2646 moves the app lowering onto typed packed
host buffers and vectorized dense-code construction. Goal2648 adds PostgreSQL
correctness for the paper-shaped native paths and prepared ray-batch support.
Goal2649 adds the generated fixture that is appropriate for RT-vs-Embree
comparison. Goal2650 adds same-contract prepared Embree timing and removes an
unnecessary native Embree ray pre-copy. Goal2651 adds an app-owned reusable
table descriptor so dense scan/group encoding can be shared across query modes
without adding RayDB semantics to the engine.
Goal2652 adds 10s-level prepared-query timing for Embree host rays, OptiX host
rays, and OptiX Torch partner-owned query-ray columns.
Goal2684 adds the generic RT hit-stream handoff for the v2.5 Triton partner
direction. It is a boundary and implementation milestone, not a public
performance claim until pod artifacts and external review are recorded.

The main seconds-scale internal evidence is:

- `docs/reports/goal2646_raydb_vectorized_cpu_vs_optix_250k_2026-05-27.md`
- `docs/reports/goal2646_raydb_vectorized_cpu_vs_optix_250k_2026-05-27.json`
- `docs/reports/goal2646_raydb_prepared_payload_query_perf_250k_2026-05-27.md`
- `docs/reports/goal2646_raydb_prepared_payload_query_perf_250k_2026-05-27.json`
- `docs/reports/goal2646_raydb_typed_buffers_perf_update_2026-05-27.md`

The repeated 2M-row fixture is no longer treated as the RT-vs-Embree benchmark
fixture: it repeats only eight base records and creates too few distinct query
rays. On the generated 2M-row fixture, PostgreSQL checks the `count` and `sum`
outputs. The first same-contract full prepared-run comparison showed OptiX
beating Embree on the recorded RTX A5000 pod:

- `count`: 2M triangles, 110,592 rays, Embree 1.403637 s, OptiX 0.983565 s,
  1.427x Embree/OptiX;
- `sum`: 2M triangles, 4,755,456 rays, Embree 1.910426 s, OptiX 1.378547 s,
  1.386x Embree/OptiX.

Those 1.427x/1.386x rows are setup-included whole-run timings for a single
prepared run. They should not be compared directly to the later Goal2652
steady-state prepared-query-only rows.

The main current evidence is:

- `docs/reports/goal2649_raydb_generated_rt_vs_embree_2026-05-27.md`
- `docs/reports/goal2649_raydb_generated_embree_vs_optix_2m_2026-05-27.json`
- `docs/reports/goal2649_raydb_generated_postgres_correctness_100k_2026-05-27.json`
- `docs/reports/goal2649_raydb_generated_prepared_host_2m_2026-05-27.json`
- `docs/reports/goal2649_raydb_generated_prepared_torch_2m_2026-05-27.json`
- `docs/reports/goal2650_raydb_prepared_backend_split_2026-05-27.md`
- `docs/reports/goal2651_raydb_reusable_table_descriptor_2026-05-27.md`
- `docs/reports/goal2652_raydb_10s_prepared_query_configs_2026-05-27.md`

This is still internal evidence only; public speedup wording requires the
project’s review/consensus gate and must cite exact script, artifact, backend,
hardware, commit, and output contract.

The prepared-payload timing artifacts separately report repeated query time
after workload construction and scene/payload preparation. They keep primitive
group ids and primitive values device-resident across runs. The newer prepared
ray-batch path also keeps query rays resident across repeated runs; the Torch
variant accepts partner-owned CUDA query columns and packs them on device. The
Goal2651 table descriptor is deliberately app-owned: it prepares dense
predicate and group encodings once, while RTDL native execution remains limited
to generic rays, triangles, primitive ids, payload values, and reductions.

The current closeout evidence is Goal2652. It uses a duration-driven protocol:
after table descriptor, workload, scene/payload, and ray-batch preparation are
complete, each prepared query is repeated until the measured query phase reaches
about 10 seconds. On the same generated 2M-row fixture, `optix_host` beats
`embree_host` by 27.7x for grouped `count` and 104.0x for grouped `sum`.
This is the supported internal RT-vs-Embree row for RayDB. It is not a
whole-app speedup claim.

## Closeout

As of Goal2520, the earlier benchmark slice was closed as an RTDL
reconstruction harness for the partner-resident grouped-aggregate path. That
closeout did not complete RayDB as an RT-core paper-shaped benchmark. Goal2644
reopened the app specifically for the paper-shaped RT path. Goal2652 is the
current internal RT-vs-Embree prepared-query evidence point, and Goal2653 is
the closeout boundary for the rewritten paper-shaped RayDB benchmark slice.

Final large same-contract evidence is recorded in:

- `docs/reports/goal2527_large_same_contract_performance_matrix_2026-05-23.md`
- `docs/reports/goal2527_large_same_contract_performance_matrix_pod_2026-05-23.json`
- `docs/reports/goal2528_raydb_style_benchmark_app_closeout_2026-05-23.md`

The final Goal2528 RTDL OptiX path used the old
`optix_partner_resident_experimental` columnar payload backend, not the current
paper-shaped `paper_rt_optix` path. It includes a fused generic grouped `stats`
reduction that returns `count`, `sum`, `min`, and `max` in one native launch.
On the recorded pod, the fused full-contract medians were `1.601686 ms`,
`1.986026 ms`, and `2.425149 ms` for 1M, 5M, and 10M rows respectively.

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

Goal2644 reopens the benchmark direction because the earlier closed path was a
partner-resident grouped-reduction study, not the paper's RT-core path. Goal2645
and Goal2646 add the generic native RT-core lowering and typed-buffer measured
path. The remaining RayDB-specific engineering target is not app-specific
native code; it is a generic prepared/device-resident primitive-payload context
for grouped primitive reductions.
