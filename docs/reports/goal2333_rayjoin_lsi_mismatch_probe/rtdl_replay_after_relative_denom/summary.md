# Goal2327 RayJoin Pod Artifact Summary

Input directory: `docs/reports/goal2333_rayjoin_lsi_mismatch_probe/rtdl_replay_after_relative_denom`

## Hardware

- GPU: `NVIDIA RTX A5000, 570.211.01`

## Fixture Prepared OptiX Route

| workload | mode | rows/count | query_pack_sec | shape_pack_sec | prepare_sec | query_sec |
| --- | --- | --- | --- | --- | --- | --- |
| lsi | count | 1 | 0.000087 | n/a | 0.493448 | 0.000213 |
| pip | rows | 6 | 0.000013 | 0.000062 | 0.703029 | 0.000328 |

## Same-Query Stream Replay

| route | queries | left/items | right/shapes | prepare_sec | median_query_sec | parity |
| --- | --- | --- | --- | --- | --- | --- |
| lsi/raw_rows | 65536 | 65536 | 326193 | 1.009976 | 0.004948 | true |
| lsi/scalar_count | 65536 | 65536 | 326193 | 1.009976 | 0.004929 | true |
| pip/positive_rows | 65536 | 65536 | 15700 | 0.368727 | 0.005061 | true |
| pip/scalar_count | 65536 | 65536 | 15700 | 0.368727 | 0.005038 | true |

## Claim Boundary

- `full_rayjoin_reproduction`: `false`
- `paper_scale_perf_claim_authorized`: `false`
- `requires_external_review_before_public_claim`: `true`
- `rtdl_beats_rayjoin_claim_authorized`: `false`
- `v2_0_release_authorized`: `false`
- `whole_app_speedup_claim_authorized`: `false`

This summary is descriptive evidence only. It does not authorize a RayJoin paper-speedup claim or a v2.0 release claim.
