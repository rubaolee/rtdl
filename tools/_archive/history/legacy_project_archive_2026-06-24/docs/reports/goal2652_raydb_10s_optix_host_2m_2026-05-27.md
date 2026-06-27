# Goal2646 RayDB Prepared Payload Query Timing

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-28T01:33:02Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- output JSON: `docs/reports/goal2652_raydb_10s_optix_host_2m_2026-05-27.json`

## Matrix

| mode | fixture | copies | ray batch | rows | triangles | rays | table descriptor s | workload build s | prepare scene/payload s | partner ray cols s | prepare rays s | query iterations | query total s | query median s | query mean s | RT core | correct |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| count | generated_deterministic | 1 | host | 2000000 | 2000000 | 110592 | 0.327047 | 0.179084 | 0.498844 | 0.000000 | 0.001765 | 56418 | 10.000055 | 0.000170 | 0.000177 | True | True |
| sum | generated_deterministic | 1 | host | 2000000 | 2000000 | 4755456 | 0.327047 | 0.474939 | 0.121286 | 0.000000 | 0.115330 | 10499 | 10.000406 | 0.000948 | 0.000953 | True | True |

## Boundary

- This runner measures prepared query time after workload construction and prepared scene/payload creation.
- With table descriptor reuse enabled, dense predicate/group encoding is prepared once per fixture and reused across modes.
- The prepared primitive payload keeps primitive group ids and primitive values device-resident across repeated runs.
- `ray_batch=host` prepares the generic 3-D ray batch once from host packed rays.
- `ray_batch=cupy` and `ray_batch=torch` create partner-owned CUDA ray columns, then pack them on device into a prepared generic 3-D ray batch.
- Both prepared-ray modes avoid query-ray upload on each repeated run.
