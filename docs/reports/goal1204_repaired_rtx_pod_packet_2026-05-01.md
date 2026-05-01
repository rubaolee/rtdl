# Goal1204 Repaired RTX Pod Packet

Date: 2026-05-01

Valid: `True`

## Archive

- path: `/Users/rl2025/rtdl_python_only/docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
- sha256: `4e1b389db324e6a265be73a20047491fe309d42075563dadeac53efbafd43e0f`
- bytes: `1517157`

## Rows

| Label | App | Purpose |
| --- | --- | --- |
| `db_embree_100000_chunked_repair` | `database_analytics` | Verify the previously failing 100k DB Embree scale now passes with compact-summary chunking. |
| `db_optix_100000_chunked_repair` | `database_analytics` | Verify the previously failing 100k DB OptiX scale now passes with compact-summary chunking. |
| `db_embree_300000_chunked_repair` | `database_analytics` | Collect same-scale 300k DB Embree control for the repaired compact-summary path. |
| `db_optix_300000_chunked_repair` | `database_analytics` | Verify the previous 300k OptiX row-ceiling failure is repaired by chunking. |
| `jaccard_optix_8192_public_safe_chunk_512` | `polygon_set_jaccard` | Collect Jaccard claim-path evidence using the reviewed public-safe chunk policy. |
| `jaccard_optix_8192_diagnostic_chunk_64` | `polygon_set_jaccard` | Confirm the formerly failing chunk-64 shape is classified diagnostic-only, not claim-ready. |
| `road_hazard_embree_control_40000` | `road_hazard_screening` | Collect same-scale Embree control for the larger road-hazard floor repair. |
| `road_hazard_optix_control_40000` | `road_hazard_screening` | Rerun road hazard at larger scale so OptiX query time can clear the 0.1s timing floor. |

## Preconditions

- Run only after local Goal1202 and Goal1203 tests pass.
- Use one RTX-class Linux pod session; do not restart per app.
- Install GEOS/Embree/CUDA/OptiX once, then run all rows.
- Copy back the result tgz and sha256 before interpretation.
- A separate intake/review goal must interpret results after copy-back.

## Run On Pod

```bash
ARCHIVE=/tmp/goal1204_rtdl_source_2026-05-01.tar.gz EXPECTED_SHA256=4e1b389db324e6a265be73a20047491fe309d42075563dadeac53efbafd43e0f WORKDIR=/workspace/rtdl_goal1204 RESULT_TGZ=/tmp/goal1204_repaired_rtx_pod.tgz RESULT_SHA=/tmp/goal1204_repaired_rtx_pod.tgz.sha256 bash /tmp/goal1204_executor.sh
```

## Boundary

Goal1204 prepares a future repaired-path pod batch only. It does not run cloud, authorize public docs, release, or public RTX speedup wording.
