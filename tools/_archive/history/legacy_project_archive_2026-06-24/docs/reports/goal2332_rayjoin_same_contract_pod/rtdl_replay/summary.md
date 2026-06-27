# Goal2327 RayJoin Pod Artifact Summary

Input directory: `docs/reports/goal2332_rayjoin_same_contract_pod/rtdl_replay`

## Hardware

- GPU: `NVIDIA RTX A5000, 570.211.01`

## Fixture Prepared OptiX Route

| workload | mode | rows/count | query_pack_sec | shape_pack_sec | prepare_sec | query_sec |
| --- | --- | --- | --- | --- | --- | --- |
| lsi | count | 1 | 0.000074 | n/a | 0.535221 | 0.000192 |
| pip | rows | 6 | 0.000012 | 0.000061 | 0.845513 | 0.000278 |

## Same-Query Stream Replay

| route | queries | left/items | right/shapes | prepare_sec | median_query_sec | parity |
| --- | --- | --- | --- | --- | --- | --- |
| lsi/raw_rows | 65536 | 65536 | 326193 | 1.022088 | 0.004808 | true |
| lsi/scalar_count | 65536 | 65536 | 326193 | 1.022088 | 0.004807 | true |
| pip/positive_rows | 65536 | 65536 | 15700 | 0.368436 | 0.005798 | true |
| pip/scalar_count | 65536 | 65536 | 15700 | 0.368436 | 0.005737 | true |

## Claim Boundary

- `full_rayjoin_reproduction`: `false`
- `paper_scale_perf_claim_authorized`: `false`
- `requires_external_review_before_public_claim`: `true`
- `rtdl_beats_rayjoin_claim_authorized`: `false`
- `v2_0_release_authorized`: `false`
- `whole_app_speedup_claim_authorized`: `false`

This summary is descriptive evidence only. It does not authorize a RayJoin paper-speedup claim or a v2.0 release claim.
