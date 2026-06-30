# Goal2327 RayJoin Pod Artifact Summary

Input directory: `docs/reports/goal2327_rayjoin_local_linux_smoke`

## Hardware

- GPU: `NVIDIA GeForce GTX 1070, 580.126.09`

## Fixture Prepared OptiX Route

| workload | mode | rows/count | query_pack_sec | shape_pack_sec | prepare_sec | query_sec |
| --- | --- | --- | --- | --- | --- | --- |
| lsi | count | 1 | 0.000074 | n/a | 0.404530 | 0.000185 |
| pip | rows | 6 | 0.000011 | 0.000055 | 0.738646 | 0.000307 |

## Same-Query Stream Replay

| route | queries | left/items | right/shapes | prepare_sec | median_query_sec | parity |
| --- | --- | --- | --- | --- | --- | --- |
| same-query stream replay | skipped | n/a | n/a | n/a | n/a | n/a |

## Claim Boundary

- `full_rayjoin_reproduction`: `false`
- `paper_scale_perf_claim_authorized`: `false`
- `requires_external_review_before_public_claim`: `true`
- `rtdl_beats_rayjoin_claim_authorized`: `false`
- `v2_0_release_authorized`: `false`
- `whole_app_speedup_claim_authorized`: `false`

This summary is descriptive evidence only. It does not authorize a RayJoin paper-speedup claim or a v2.0 release claim.
