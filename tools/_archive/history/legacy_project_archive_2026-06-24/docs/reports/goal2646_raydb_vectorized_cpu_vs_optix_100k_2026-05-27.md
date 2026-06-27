# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-27T20:35:26Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2646_raydb_vectorized_cpu_vs_optix_100k_2026-05-27.json`
- build command: `make build-optix`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | copies | rows | triangles | rays | median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---|---|
| cpu_python_reference | count | 100000 | 800000 | None | None | 1.239575 | False | True |
| cpu_python_reference | sum | 100000 | 800000 | None | None | 1.225437 | False | True |
| cpu_python_reference | min | 100000 | 800000 | None | None | 1.272574 | False | True |
| cpu_python_reference | max | 100000 | 800000 | None | None | 1.294969 | False | True |
| cpu_python_reference | avg_as_sum_count | 100000 | 800000 | None | None | 1.246759 | False | True |
| paper_rt_optix | count | 100000 | 800000 | 800000 | 72 | 0.702730 | True | True |
| paper_rt_optix | sum | 100000 | 800000 | 800000 | 12072 | 0.666197 | True | True |
| paper_rt_optix | min | 100000 | 800000 | 800000 | 12072 | 0.680978 | True | True |
| paper_rt_optix | max | 100000 | 800000 | 800000 | 12072 | 0.657970 | True | True |
| paper_rt_optix | avg_as_sum_count | 100000 | 800000 | 800000 | 12072 | 0.693491 | True | True |

## Speedup Diagnostics

| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |
|---|---:|---|---:|---:|---:|---|
| count | 100000 | cpu_python_reference | 1.239575 | 0.702730 | 1.764x | True |
| sum | 100000 | cpu_python_reference | 1.225437 | 0.666197 | 1.839x | True |
| min | 100000 | cpu_python_reference | 1.272574 | 0.680978 | 1.869x | True |
| max | 100000 | cpu_python_reference | 1.294969 | 0.657970 | 1.968x | True |
| avg_as_sum_count | 100000 | cpu_python_reference | 1.246759 | 0.693491 | 1.798x | True |

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
