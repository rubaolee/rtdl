# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-28T00:10:50Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2648_raydb_embree_vs_optix_2m_after_prepared_ray_2026-05-27.json`
- build command: `make build-optix`
- Embree build/probe command: `make build-embree`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | copies | rows | triangles | rays | median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---|---|
| paper_rt_embree | count | 250000 | 2000000 | 2000000 | 72 | 1.962543 | False | True |
| paper_rt_embree | sum | 250000 | 2000000 | 2000000 | 12072 | 2.083110 | False | True |
| paper_rt_optix | count | 250000 | 2000000 | 2000000 | 72 | 1.950381 | True | True |
| paper_rt_optix | sum | 250000 | 2000000 | 2000000 | 12072 | 1.839847 | True | True |

## Speedup Diagnostics

| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |
|---|---:|---|---:|---:|---:|---|
| count | 250000 | paper_rt_embree | 1.962543 | 1.950381 | 1.006x | True |
| sum | 250000 | paper_rt_embree | 2.083110 | 1.839847 | 1.132x | True |

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
