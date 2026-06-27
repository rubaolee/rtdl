# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-28T00:31:34Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2649_raydb_generated_embree_vs_optix_2m_2026-05-27.json`
- build command: `make build-optix`
- Embree build/probe command: `make build-embree`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | fixture | copies | rows | triangles | rays | median s | RT core | correct |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| paper_rt_embree | count |  | 1 | 2000000 | 2000000 | 110592 | 1.403637 | False | True |
| paper_rt_embree | sum |  | 1 | 2000000 | 2000000 | 4755456 | 1.910426 | False | True |
| paper_rt_optix | count |  | 1 | 2000000 | 2000000 | 110592 | 0.983565 | True | True |
| paper_rt_optix | sum |  | 1 | 2000000 | 2000000 | 4755456 | 1.378547 | True | True |

## Speedup Diagnostics

| mode | copies | baseline | baseline median s | paper RT OptiX median s | baseline / OptiX | correct |
|---|---:|---|---:|---:|---:|---|
| count | 1 | paper_rt_embree | 1.403637 | 0.983565 | 1.427x | True |
| sum | 1 | paper_rt_embree | 1.910426 | 1.378547 | 1.386x | True |

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
