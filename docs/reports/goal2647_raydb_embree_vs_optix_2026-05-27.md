# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-27T23:28:20Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2647_raydb_embree_vs_optix_2026-05-27.json`
- build command: `make build-optix`
- Embree build/probe command: `make build-embree`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | copies | rows | triangles | rays | median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---|---|
| paper_rt_embree | count | 10000 | 80000 | 80000 | 72 | 0.081036 | False | True |
| paper_rt_embree | sum | 10000 | 80000 | 80000 | 12072 | 0.081263 | False | True |
| paper_rt_optix | count | 10000 | 80000 | 80000 | 72 | 0.073858 | True | True |
| paper_rt_optix | sum | 10000 | 80000 | 80000 | 12072 | 0.071271 | True | True |
| paper_rt_embree | count | 100000 | 800000 | 800000 | 72 | 0.888326 | False | True |
| paper_rt_embree | sum | 100000 | 800000 | 800000 | 12072 | 0.856369 | False | True |
| paper_rt_optix | count | 100000 | 800000 | 800000 | 72 | 0.723177 | True | True |
| paper_rt_optix | sum | 100000 | 800000 | 800000 | 12072 | 0.667174 | True | True |
| paper_rt_embree | count | 250000 | 2000000 | 2000000 | 72 | 1.994661 | False | True |
| paper_rt_embree | sum | 250000 | 2000000 | 2000000 | 12072 | 2.122789 | False | True |
| paper_rt_optix | count | 250000 | 2000000 | 2000000 | 72 | 1.821685 | True | True |
| paper_rt_optix | sum | 250000 | 2000000 | 2000000 | 12072 | 1.721987 | True | True |

## Speedup Diagnostics

| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |
|---|---:|---|---:|---:|---:|---|
| count | 10000 | paper_rt_embree | 0.081036 | 0.073858 | 1.097x | True |
| sum | 10000 | paper_rt_embree | 0.081263 | 0.071271 | 1.140x | True |
| count | 100000 | paper_rt_embree | 0.888326 | 0.723177 | 1.228x | True |
| sum | 100000 | paper_rt_embree | 0.856369 | 0.667174 | 1.284x | True |
| count | 250000 | paper_rt_embree | 1.994661 | 1.821685 | 1.095x | True |
| sum | 250000 | paper_rt_embree | 2.122789 | 1.721987 | 1.233x | True |

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
