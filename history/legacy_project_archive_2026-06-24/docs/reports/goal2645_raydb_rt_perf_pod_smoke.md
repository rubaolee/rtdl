# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-27T20:03:38Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2645_raydb_rt_perf_pod_smoke.json`
- build command: `make build-optix`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | copies | rows | triangles | rays | median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---|---|
| cpu_python_reference | count | 1 | 8 | None | None | 0.000120 | False | True |
| cpu_python_reference | sum | 1 | 8 | None | None | 0.000221 | False | True |
| cpu_python_reference | min | 1 | 8 | None | None | 0.000048 | False | True |
| cpu_python_reference | max | 1 | 8 | None | None | 0.000042 | False | True |
| cpu_python_reference | avg_as_sum_count | 1 | 8 | None | None | 0.000043 | False | True |
| paper_rt_cpu_reference | count | 1 | 8 | 8 | 72 | 0.000935 | False | True |
| paper_rt_cpu_reference | sum | 1 | 8 | 8 | 12072 | 0.188853 | False | True |
| paper_rt_cpu_reference | min | 1 | 8 | 8 | 12072 | 0.093642 | False | True |
| paper_rt_cpu_reference | max | 1 | 8 | 8 | 12072 | 0.102348 | False | True |
| paper_rt_cpu_reference | avg_as_sum_count | 1 | 8 | 8 | 12072 | 0.096573 | False | True |
| paper_rt_optix | count | 1 | 8 | 8 | 72 | 0.472745 | True | True |
| paper_rt_optix | sum | 1 | 8 | 8 | 12072 | 0.042770 | True | True |
| paper_rt_optix | min | 1 | 8 | 8 | 12072 | 0.041380 | True | True |
| paper_rt_optix | max | 1 | 8 | 8 | 12072 | 0.041529 | True | True |
| paper_rt_optix | avg_as_sum_count | 1 | 8 | 8 | 12072 | 0.052232 | True | True |

## Speedup Diagnostics

| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |
|---|---:|---|---:|---:|---:|---|
| count | 1 | cpu_python_reference | 0.000120 | 0.472745 | 0.000x | True |
| count | 1 | paper_rt_cpu_reference | 0.000935 | 0.472745 | 0.002x | True |
| sum | 1 | cpu_python_reference | 0.000221 | 0.042770 | 0.005x | True |
| sum | 1 | paper_rt_cpu_reference | 0.188853 | 0.042770 | 4.416x | True |
| min | 1 | cpu_python_reference | 0.000048 | 0.041380 | 0.001x | True |
| min | 1 | paper_rt_cpu_reference | 0.093642 | 0.041380 | 2.263x | True |
| max | 1 | cpu_python_reference | 0.000042 | 0.041529 | 0.001x | True |
| max | 1 | paper_rt_cpu_reference | 0.102348 | 0.041529 | 2.464x | True |
| avg_as_sum_count | 1 | cpu_python_reference | 0.000043 | 0.052232 | 0.001x | True |
| avg_as_sum_count | 1 | paper_rt_cpu_reference | 0.096573 | 0.052232 | 1.849x | True |

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
