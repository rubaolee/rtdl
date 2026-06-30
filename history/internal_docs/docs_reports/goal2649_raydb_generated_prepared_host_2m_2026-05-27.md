# Goal2646 RayDB Prepared Payload Query Timing

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-28T00:33:49Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- output JSON: `docs/reports/goal2649_raydb_generated_prepared_host_2m_2026-05-27.json`

## Matrix

| mode | fixture | copies | ray batch | rows | triangles | rays | workload build s | prepare scene/payload s | partner ray cols s | prepare rays s | query median s | RT core | correct |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| count | generated_deterministic | 1 | host | 2000000 | 2000000 | 110592 | 0.528242 | 0.498125 | 0.000000 | 0.002238 | 0.000233 | True | True |
| sum | generated_deterministic | 1 | host | 2000000 | 2000000 | 4755456 | 0.813706 | 0.123695 | 0.000000 | 0.126912 | 0.001108 | True | True |

## Boundary

- This runner measures prepared query time after workload construction and prepared scene/payload creation.
- The prepared primitive payload keeps primitive group ids and primitive values device-resident across repeated runs.
- `ray_batch=host` prepares the generic 3-D ray batch once from host packed rays.
- `ray_batch=cupy` and `ray_batch=torch` create partner-owned CUDA ray columns, then pack them on device into a prepared generic 3-D ray batch.
- Both prepared-ray modes avoid query-ray upload on each repeated run.
