# Goal2646 RayDB Prepared Payload Query Timing

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-28T01:02:19Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- output JSON: `docs/reports/goal2650_raydb_generated_prepared_embree_host_2m_no_precopy_2026-05-27.json`

## Matrix

| mode | fixture | copies | ray batch | rows | triangles | rays | workload build s | prepare scene/payload s | partner ray cols s | prepare rays s | query median s | RT core | correct |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| count | generated_deterministic | 1 | host | 2000000 | 2000000 | 110592 | 0.500848 | 0.431815 | 0.000000 | 0.000010 | 0.006101 | False | True |
| sum | generated_deterministic | 1 | host | 2000000 | 2000000 | 4755456 | 0.753227 | 0.426226 | 0.000000 | 0.000046 | 0.095588 | False | True |

## Boundary

- This runner measures prepared query time after workload construction and prepared scene/payload creation.
- The prepared primitive payload keeps primitive group ids and primitive values device-resident across repeated runs.
- `ray_batch=host` prepares the generic 3-D ray batch once from host packed rays.
- `ray_batch=cupy` and `ray_batch=torch` create partner-owned CUDA ray columns, then pack them on device into a prepared generic 3-D ray batch.
- Both prepared-ray modes avoid query-ray upload on each repeated run.
