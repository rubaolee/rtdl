# Goal2646 RayDB Prepared Payload Query Timing

Status: internal evidence only; public speedup wording remains unauthorized pending review.

## Provenance

- timestamp UTC: `2026-05-27T21:02:15Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2646_raydb_prepared_payload_perf_pod.py`
- output JSON: `docs/reports/goal2646_raydb_prepared_payload_query_perf_250k_2026-05-27.json`

## Matrix

| mode | copies | rows | triangles | rays | workload build s | prepare s | prepared query median s | RT core | correct |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| count | 250000 | 2000000 | 2000000 | 72 | 0.887277 | 0.512687 | 0.471953 | True | True |
| sum | 250000 | 2000000 | 2000000 | 12072 | 1.012094 | 0.122992 | 0.358819 | True | True |
| min | 250000 | 2000000 | 2000000 | 12072 | 0.893524 | 0.108545 | 0.357411 | True | True |
| max | 250000 | 2000000 | 2000000 | 12072 | 0.885291 | 0.106278 | 0.359761 | True | True |
| avg_as_sum_count | 250000 | 2000000 | 2000000 | 12072 | 0.883030 | 0.108919 | 0.370539 | True | True |

## Boundary

- This runner measures prepared query time after workload construction and prepared scene/payload creation.
- The prepared primitive payload keeps primitive group ids and primitive values device-resident across repeated runs.
- Query rays are still uploaded each run; prepared ray batches are future work.
