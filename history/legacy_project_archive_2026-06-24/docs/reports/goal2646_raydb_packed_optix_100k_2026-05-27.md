# Goal2645 RayDB Paper-RT Perf Pod Evidence

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-27T20:27:41Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2645_raydb_rt_perf_pod.py`
- output JSON: `docs/reports/goal2646_raydb_packed_optix_100k_2026-05-27.json`
- build command: `make build-optix`

## Contract

- App-owned Python lowering encodes RayDB rows as triangles and predicate queries as +Z rays.
- Native runtime sees only generic 3-D rays, triangles, primitive group ids, i64 values, primitive-id deduplication, and grouped reductions.
- The engine does not contain RayDB, SQL, table, SSB, database, or query-plan vocabulary.

## Matrix

| backend | mode | copies | rows | triangles | rays | median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---|---|
| paper_rt_optix | count | 100000 | 800000 | 800000 | 72 | 1.382133 | True | True |
| paper_rt_optix | sum | 100000 | 800000 | 800000 | 12072 | 1.318847 | True | True |
| paper_rt_optix | min | 100000 | 800000 | 800000 | 12072 | 1.326231 | True | True |
| paper_rt_optix | max | 100000 | 800000 | 800000 | 12072 | 1.329833 | True | True |
| paper_rt_optix | avg_as_sum_count | 100000 | 800000 | 800000 | 12072 | 1.574640 | True | True |

## Speedup Diagnostics

No successful paper RT OptiX comparison rows were produced.

## Claim Boundary

- performance claim authorized: `False`
- These rows are for internal engineering and review. Public docs must cite this script, JSON artifact, backend, hardware, commit, and output contract if any later statement uses the data.
