# Goal2646 RayDB Prepared Payload Query Timing

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-28T00:08:07Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- output JSON: `docs/reports/goal2648_raydb_prepared_ray_batch_host_2m_2026-05-27.json`

## Matrix

| mode | copies | ray batch | rows | triangles | rays | workload build s | prepare scene/payload s | partner ray cols s | prepare rays s | query median s | RT core | correct |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| count | 250000 | host | 2000000 | 2000000 | 72 | 1.054018 | 0.565819 | 0.000000 | 0.000328 | 0.471004 | True | True |
| sum | 250000 | host | 2000000 | 2000000 | 12072 | 0.812500 | 0.106687 | 0.000000 | 0.000220 | 0.357715 | True | True |

## Boundary

- This runner measures prepared query time after workload construction and prepared scene/payload creation.
- The prepared primitive payload keeps primitive group ids and primitive values device-resident across repeated runs.
- `ray_batch=host` prepares the generic 3-D ray batch once from host packed rays.
- `ray_batch=cupy` and `ray_batch=torch` create partner-owned CUDA ray columns, then pack them on device into a prepared generic 3-D ray batch.
- Both prepared-ray modes avoid query-ray upload on each repeated run.
