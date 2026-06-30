# Goal1205 Repaired RTX Pod Intake

Date: 2026-05-01

Goal1205 intakes Goal1204 pod artifacts only. It does not authorize public docs, release, or public RTX speedup wording without a separate review decision.

## Status

- valid: `True`
- failed count: `3`
- failed labels: `db_embree_100000_chunked_repair, db_embree_300000_chunked_repair, road_hazard_embree_control_40000`

## Database Analytics

| Copies | Embree status | OptiX status | Embree sec | OptiX sec | Ratio | Repair passed |
| --- | --- | --- | --- | --- | --- | --- |
| 100000 | ok | ok | 0.338303 | 0.301344 | 1.12265 | True |
| 300000 | ok | ok | 1.05533 | 0.906979 | 1.16357 | True |

## Polygon Jaccard

| Chunk | Status | Public safe | Diagnostic only | Parity | OptiX candidate sec |
| --- | --- | --- | --- | --- | --- |
| 512 | ok | True | False | True | 1.19001 |
| 64 | ok | False | True | False | 1.2714 |

## Road Hazard

- embree status: `ok`
- optix status: `ok`
- embree sec: `0.814722`
- optix sec: `0.230652`
- ratio embree/optix: `3.53225`
- timing floor met: `True`
- same-scale public positive candidate: `True`

## Decisions

- `database_analytics`: `repair_passed`
- `polygon_set_jaccard`: `public_safe_chunk_ready`
- `road_hazard_screening`: `same_scale_public_positive_candidate`


## Recovery Merge

Goal1206 merges the original Goal1204 pod evidence with Embree4 /usr recovery controls. It is an evidence intake only and does not authorize public wording without review.

- original input: `/Users/rl2025/rtdl_python_only/docs/reports/goal1204_live_pod_2026-05-01/extracted/docs/reports/goal1204_repaired_rtx_pod`
- recovery input: `/Users/rl2025/rtdl_python_only/docs/reports/goal1204_embree4_usr_recovery_live_pod_2026-05-01/extracted/docs/reports/goal1204_embree4_usr_recovery`
- recovery copied files: `9`
