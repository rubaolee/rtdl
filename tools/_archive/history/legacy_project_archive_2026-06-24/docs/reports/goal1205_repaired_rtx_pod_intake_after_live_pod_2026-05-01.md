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
| 100000 | failed | ok | n/a | 0.301344 | n/a | False |
| 300000 | failed | ok | n/a | 0.906979 | n/a | False |

## Polygon Jaccard

| Chunk | Status | Public safe | Diagnostic only | Parity | OptiX candidate sec |
| --- | --- | --- | --- | --- | --- |
| 512 | ok | True | False | True | 1.19001 |
| 64 | ok | False | True | False | 1.2714 |

## Road Hazard

- embree status: `failed`
- optix status: `ok`
- embree sec: `n/a`
- optix sec: `0.230652`
- ratio embree/optix: `n/a`
- timing floor met: `True`
- same-scale public positive candidate: `False`

## Decisions

- `database_analytics`: `blocked_or_incomplete`
- `polygon_set_jaccard`: `public_safe_chunk_ready`
- `road_hazard_screening`: `blocked_or_floor_not_met`
