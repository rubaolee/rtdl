# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-27T20:40:24Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2646_raydb_vectorized_cpu_vs_optix_250k_2026-05-27.json`
- build command: `make build-optix`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | copies | rows | triangles | rays | median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---|---|
| cpu_python_reference | count | 250000 | 2000000 | None | None | 3.085382 | False | True |
| cpu_python_reference | sum | 250000 | 2000000 | None | None | 2.997176 | False | True |
| cpu_python_reference | min | 250000 | 2000000 | None | None | 3.223301 | False | True |
| cpu_python_reference | max | 250000 | 2000000 | None | None | 3.177053 | False | True |
| cpu_python_reference | avg_as_sum_count | 250000 | 2000000 | None | None | 3.083927 | False | True |
| paper_rt_optix | count | 250000 | 2000000 | 2000000 | 72 | 1.874128 | True | True |
| paper_rt_optix | sum | 250000 | 2000000 | 2000000 | 12072 | 1.780184 | True | True |
| paper_rt_optix | min | 250000 | 2000000 | 2000000 | 12072 | 1.745981 | True | True |
| paper_rt_optix | max | 250000 | 2000000 | 2000000 | 12072 | 1.765843 | True | True |
| paper_rt_optix | avg_as_sum_count | 250000 | 2000000 | 2000000 | 12072 | 1.793880 | True | True |

## Speedup Diagnostics

| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |
|---|---:|---|---:|---:|---:|---|
| count | 250000 | cpu_python_reference | 3.085382 | 1.874128 | 1.646x | True |
| sum | 250000 | cpu_python_reference | 2.997176 | 1.780184 | 1.684x | True |
| min | 250000 | cpu_python_reference | 3.223301 | 1.745981 | 1.846x | True |
| max | 250000 | cpu_python_reference | 3.177053 | 1.765843 | 1.799x | True |
| avg_as_sum_count | 250000 | cpu_python_reference | 3.083927 | 1.793880 | 1.719x | True |

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
