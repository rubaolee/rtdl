# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-27T20:10:55Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2645_raydb_rt_perf_pod_2026-05-27.json`
- build command: `make build-optix`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | copies | rows | triangles | rays | median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---|---|
| cpu_python_reference | count | 1 | 8 | None | None | 0.000059 | False | True |
| cpu_python_reference | sum | 1 | 8 | None | None | 0.000049 | False | True |
| cpu_python_reference | min | 1 | 8 | None | None | 0.000046 | False | True |
| cpu_python_reference | max | 1 | 8 | None | None | 0.000045 | False | True |
| cpu_python_reference | avg_as_sum_count | 1 | 8 | None | None | 0.000047 | False | True |
| paper_rt_cpu_reference | count | 1 | 8 | 8 | 72 | 0.001020 | False | True |
| paper_rt_cpu_reference | sum | 1 | 8 | 8 | 12072 | 0.094048 | False | True |
| paper_rt_cpu_reference | min | 1 | 8 | 8 | 12072 | 0.101445 | False | True |
| paper_rt_cpu_reference | max | 1 | 8 | 8 | 12072 | 0.093642 | False | True |
| paper_rt_cpu_reference | avg_as_sum_count | 1 | 8 | 8 | 12072 | 0.093315 | False | True |
| paper_rt_optix | count | 1 | 8 | 8 | 72 | 0.001109 | True | True |
| paper_rt_optix | sum | 1 | 8 | 8 | 12072 | 0.049492 | True | True |
| paper_rt_optix | min | 1 | 8 | 8 | 12072 | 0.041286 | True | True |
| paper_rt_optix | max | 1 | 8 | 8 | 12072 | 0.053261 | True | True |
| paper_rt_optix | avg_as_sum_count | 1 | 8 | 8 | 12072 | 0.041465 | True | True |
| cpu_python_reference | count | 100 | 800 | None | None | 0.001353 | False | True |
| cpu_python_reference | sum | 100 | 800 | None | None | 0.001354 | False | True |
| cpu_python_reference | min | 100 | 800 | None | None | 0.001431 | False | True |
| cpu_python_reference | max | 100 | 800 | None | None | 0.001437 | False | True |
| cpu_python_reference | avg_as_sum_count | 100 | 800 | None | None | 0.001385 | False | True |
| paper_rt_cpu_reference | all | 100 | - | - | - | skipped | - | - |
| paper_rt_optix | count | 100 | 800 | 800 | 72 | 0.010792 | True | True |
| paper_rt_optix | sum | 100 | 800 | 800 | 12072 | 0.063447 | True | True |
| paper_rt_optix | min | 100 | 800 | 800 | 12072 | 0.051541 | True | True |
| paper_rt_optix | max | 100 | 800 | 800 | 12072 | 0.068737 | True | True |
| paper_rt_optix | avg_as_sum_count | 100 | 800 | 800 | 12072 | 0.051764 | True | True |
| cpu_python_reference | count | 1000 | 8000 | None | None | 0.025142 | False | True |
| cpu_python_reference | sum | 1000 | 8000 | None | None | 0.013474 | False | True |
| cpu_python_reference | min | 1000 | 8000 | None | None | 0.014072 | False | True |
| cpu_python_reference | max | 1000 | 8000 | None | None | 0.014113 | False | True |
| cpu_python_reference | avg_as_sum_count | 1000 | 8000 | None | None | 0.013844 | False | True |
| paper_rt_cpu_reference | all | 1000 | - | - | - | skipped | - | - |
| paper_rt_optix | count | 1000 | 8000 | 8000 | 72 | 0.100551 | True | True |
| paper_rt_optix | sum | 1000 | 8000 | 8000 | 12072 | 0.156716 | True | True |
| paper_rt_optix | min | 1000 | 8000 | 8000 | 12072 | 0.169442 | True | True |
| paper_rt_optix | max | 1000 | 8000 | 8000 | 12072 | 0.144807 | True | True |
| paper_rt_optix | avg_as_sum_count | 1000 | 8000 | 8000 | 12072 | 0.126545 | True | True |
| cpu_python_reference | count | 10000 | 80000 | None | None | 0.111787 | False | True |
| cpu_python_reference | sum | 10000 | 80000 | None | None | 0.119584 | False | True |
| cpu_python_reference | min | 10000 | 80000 | None | None | 0.119455 | False | True |
| cpu_python_reference | max | 10000 | 80000 | None | None | 0.124372 | False | True |
| cpu_python_reference | avg_as_sum_count | 10000 | 80000 | None | None | 0.143255 | False | True |
| paper_rt_cpu_reference | all | 10000 | - | - | - | skipped | - | - |
| paper_rt_optix | count | 10000 | 80000 | 80000 | 72 | 1.128145 | True | True |
| paper_rt_optix | sum | 10000 | 80000 | 80000 | 12072 | 1.158717 | True | True |
| paper_rt_optix | min | 10000 | 80000 | 80000 | 12072 | 0.981402 | True | True |
| paper_rt_optix | max | 10000 | 80000 | 80000 | 12072 | 1.007906 | True | True |
| paper_rt_optix | avg_as_sum_count | 10000 | 80000 | 80000 | 12072 | 1.172984 | True | True |

## Speedup Diagnostics

| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |
|---|---:|---|---:|---:|---:|---|
| count | 1 | cpu_python_reference | 0.000059 | 0.001109 | 0.053x | True |
| count | 1 | paper_rt_cpu_reference | 0.001020 | 0.001109 | 0.920x | True |
| sum | 1 | cpu_python_reference | 0.000049 | 0.049492 | 0.001x | True |
| sum | 1 | paper_rt_cpu_reference | 0.094048 | 0.049492 | 1.900x | True |
| min | 1 | cpu_python_reference | 0.000046 | 0.041286 | 0.001x | True |
| min | 1 | paper_rt_cpu_reference | 0.101445 | 0.041286 | 2.457x | True |
| max | 1 | cpu_python_reference | 0.000045 | 0.053261 | 0.001x | True |
| max | 1 | paper_rt_cpu_reference | 0.093642 | 0.053261 | 1.758x | True |
| avg_as_sum_count | 1 | cpu_python_reference | 0.000047 | 0.041465 | 0.001x | True |
| avg_as_sum_count | 1 | paper_rt_cpu_reference | 0.093315 | 0.041465 | 2.250x | True |
| count | 100 | cpu_python_reference | 0.001353 | 0.010792 | 0.125x | True |
| sum | 100 | cpu_python_reference | 0.001354 | 0.063447 | 0.021x | True |
| min | 100 | cpu_python_reference | 0.001431 | 0.051541 | 0.028x | True |
| max | 100 | cpu_python_reference | 0.001437 | 0.068737 | 0.021x | True |
| avg_as_sum_count | 100 | cpu_python_reference | 0.001385 | 0.051764 | 0.027x | True |
| count | 1000 | cpu_python_reference | 0.025142 | 0.100551 | 0.250x | True |
| sum | 1000 | cpu_python_reference | 0.013474 | 0.156716 | 0.086x | True |
| min | 1000 | cpu_python_reference | 0.014072 | 0.169442 | 0.083x | True |
| max | 1000 | cpu_python_reference | 0.014113 | 0.144807 | 0.097x | True |
| avg_as_sum_count | 1000 | cpu_python_reference | 0.013844 | 0.126545 | 0.109x | True |
| count | 10000 | cpu_python_reference | 0.111787 | 1.128145 | 0.099x | True |
| sum | 10000 | cpu_python_reference | 0.119584 | 1.158717 | 0.103x | True |
| min | 10000 | cpu_python_reference | 0.119455 | 0.981402 | 0.122x | True |
| max | 10000 | cpu_python_reference | 0.124372 | 1.007906 | 0.123x | True |
| avg_as_sum_count | 10000 | cpu_python_reference | 0.143255 | 1.172984 | 0.122x | True |

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
