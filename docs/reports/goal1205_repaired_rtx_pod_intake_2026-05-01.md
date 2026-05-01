# Goal1205 Repaired RTX Pod Intake

Date: 2026-05-01

Goal1205 intakes Goal1204 pod artifacts only. It does not authorize public docs, release, or public RTX speedup wording without a separate review decision.

## Status

- valid: `False`
- failed count: `None`
- failed labels: `none`

## Database Analytics

| Copies | Embree status | OptiX status | Embree sec | OptiX sec | Ratio | Repair passed |
| --- | --- | --- | --- | --- | --- | --- |
| 100000 | n/a | n/a | n/a | n/a | n/a | False |
| 300000 | n/a | n/a | n/a | n/a | n/a | False |

## Polygon Jaccard

| Chunk | Status | Public safe | Diagnostic only | Parity | OptiX candidate sec |
| --- | --- | --- | --- | --- | --- |
| 512 | n/a | False | False | n/a | n/a |
| 64 | n/a | False | False | n/a | n/a |

## Road Hazard

- embree status: `n/a`
- optix status: `n/a`
- embree sec: `n/a`
- optix sec: `n/a`
- ratio embree/optix: `n/a`
- timing floor met: `False`
- same-scale public positive candidate: `False`

## Decisions

- `database_analytics`: `blocked_or_incomplete`
- `polygon_set_jaccard`: `blocked_or_incomplete`
- `road_hazard_screening`: `blocked_or_floor_not_met`
