# Phoenix V3 RayJoin Point-Location Runner Focused POD A/B

Status: `rayjoin_point_location_runner_pod_ab_collected_not_release`.

- dataset: `data/rayjoin_public_cdb/br_county.cdb`
- point order: `y_then_x`
- repeat/warmup/samples: `50` / `5` / `7`
- row count: `47262`
- output contract: `point_to_shape_positive_hit_count_relation_status_corrected_executor_validated`
- median per-call speedup, legacy over runner: `0.9734650006717721`
- median total-repeat speedup, legacy over runner: `0.9737541084926657`
- material Set-A candidate: `False`

This packet compares the productized Phoenix V3 prepared-execution runner
against the current OptiX relation-status corrected executor, not against Embree.
It authorizes no release, broad V3-over-V2 wording, true-zero-copy wording,
or all-app rerun.
