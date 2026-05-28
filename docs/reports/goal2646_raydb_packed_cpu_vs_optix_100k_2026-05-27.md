# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-27T20:29:38Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2646_raydb_packed_cpu_vs_optix_100k_2026-05-27.json`
- build command: `make build-optix`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | copies | rows | triangles | rays | median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---|---|
| cpu_python_reference | count | 100000 | 800000 | None | None | 1.161058 | False | True |
| cpu_python_reference | sum | 100000 | 800000 | None | None | 1.190861 | False | True |
| cpu_python_reference | min | 100000 | 800000 | None | None | 1.242444 | False | True |
| cpu_python_reference | max | 100000 | 800000 | None | None | 1.288987 | False | True |
| cpu_python_reference | avg_as_sum_count | 100000 | 800000 | None | None | 1.297930 | False | True |
| paper_rt_optix | count | 100000 | 800000 | 800000 | 72 | 1.495852 | True | True |
| paper_rt_optix | sum | 100000 | 800000 | 800000 | 12072 | 1.388112 | True | True |
| paper_rt_optix | min | 100000 | 800000 | 800000 | 12072 | 1.418908 | True | True |
| paper_rt_optix | max | 100000 | 800000 | 800000 | 12072 | 1.360563 | True | True |
| paper_rt_optix | avg_as_sum_count | 100000 | 800000 | 800000 | 12072 | 1.446462 | True | True |

## Speedup Diagnostics

| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |
|---|---:|---|---:|---:|---:|---|
| count | 100000 | cpu_python_reference | 1.161058 | 1.495852 | 0.776x | True |
| sum | 100000 | cpu_python_reference | 1.190861 | 1.388112 | 0.858x | True |
| min | 100000 | cpu_python_reference | 1.242444 | 1.418908 | 0.876x | True |
| max | 100000 | cpu_python_reference | 1.288987 | 1.360563 | 0.947x | True |
| avg_as_sum_count | 100000 | cpu_python_reference | 1.297930 | 1.446462 | 0.897x | True |

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
