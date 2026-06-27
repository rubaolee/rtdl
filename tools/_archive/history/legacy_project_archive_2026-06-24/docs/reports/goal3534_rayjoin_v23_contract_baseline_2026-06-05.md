# Goal3534 RayJoin v2.3 Contract Baselines

Date: 2026-06-05

Status: internal A5000 evidence. This report does not authorize release, public speedup wording, RayJoin paper reproduction claims, broad RT-core speedup claims, true zero-copy claims, or app-specific native-engine shortcuts.

## Purpose

After Goal3532 split RayJoin into promoted v2.8 contract rows, the missing question was: "RayJoin v2.8 vs v2.3, contract by contract, anyway?"

Goal3534 answers the part that can be answered honestly:

1. Measure the old common `prepared_optix` scalar count contracts in both the v2.3 evidence checkout and current v2.8.
2. Record which v2.8 promoted contracts have no matching v2.3 surface, rather than manufacturing fake ratios.

## Evidence

Artifact:

`docs/reports/goal3534_rayjoin_v23_contract_baseline_a5000/summary.json`

Run facts:

- Pod: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
- v2.3 evidence commit: `2a28365d0246d51f3e3322b546f8a68c58632db4`
- v2.8 current commit: `c237b0db296c890455661b16e6066c1c71ee2e97`
- Dataset pair: `tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_county_subset.cdb`
- Repeats: 7 per workload per checkout
- Metric: median `phases_sec.prepared_query_sec`

## Common v2.3/v2.8 Scalar Contracts

These are the only direct contract-level v2.3 vs v2.8 RayJoin baselines currently available from the v2.3 evidence checkout.

| Common contract row | v2.3 sec | v2.8 sec | v2.8 / v2.3 | Reading |
| --- | ---: | ---: | ---: | --- |
| `rayjoin_common_pip_prepared_optix_count` | 0.000254 | 0.000247 | 1.032x | small win / noise |
| `rayjoin_common_lsi_prepared_optix_scalar_count` | 0.000245 | 0.000244 | 1.004x | parity |
| `rayjoin_common_overlay_seed_prepared_optix_active_count` | 0.000248 | 0.000238 | 1.040x | small win / noise |

This replaces the earlier single old-runner RayJoin number (`1.096x`) with a more precise statement: the old scalar count contracts are basically parity-to-small-win on this checked-in CDB pair.

## v2.8 Promoted Contracts vs v2.3 Surface

| v2.8 promoted row | v2.8 sec | v2.3 status |
| --- | ---: | --- |
| `rayjoin_count_parity_pip_prepared_optix` | 0.000275 | common scalar contract measured via `rayjoin_common_pip_prepared_optix_count` |
| `rayjoin_count_parity_lsi_left_id_dense_count` | 0.059606 | no same contract; v2.3 has scalar total LSI count only |
| `rayjoin_count_parity_overlay_seed_active_count` | 0.345494 | common scalar output measured, but v2.8 row is a newer device-continuation route |
| `rayjoin_relation_columns_cdb_pair` | 0.000532 | no equivalent contract in v2.3 evidence checkout |
| `rayjoin_relation_grouped_count_cdb_pair` | 0.000177 | no equivalent contract in v2.3 evidence checkout |
| `rayjoin_shape_pair_payload_bounds_cdb_pair` | 0.000936 | no equivalent contract in v2.3 evidence checkout |
| `rayjoin_shape_pair_payload_witness_cdb_pair` | 0.000721 | no equivalent contract in v2.3 evidence checkout |
| `rayjoin_overlay_area_relation_stream_cdb_pair` | 0.000454 | no equivalent contract in v2.3 evidence checkout |
| `rayjoin_overlay_area_device_tile_planner_cdb_pair` | 0.001283 | no equivalent contract in v2.3 evidence checkout |
| `rayjoin_overlay_area_tile_executor_cdb_pair` | 0.001268 | no equivalent contract in v2.3 evidence checkout |

## Interpretation

RayJoin has two different stories:

- The old v2.3-compatible scalar contracts are not meaningfully faster in v2.8. They are around parity, with small wins that are too tiny to headline.
- The interesting v2.8 work is not a faster copy of old v2.3 RayJoin. It is new promoted machinery: dense left-id columns, relation columns, grouped relation continuations, shape-pair payloads, witnesses, and overlay tile-task execution. Most of those did not exist in the v2.3 evidence checkout.

So the honest answer to "RayJoin v2.8 vs v2.3?" is:

- common old scalar contracts: about `1.00x` to `1.04x`;
- old blended same-runner full route: `1.096x`;
- v2.8 promoted contracts: mostly v2.8-only evidence, not ratio-able against v2.3 without backporting or writing an artificial v2.3 baseline.

## Next Step

The remaining serious RayJoin performance question is not "re-run v2.3 harder." It is a larger-scale v2.8 promoted packet, preferably with RayJoin-exported streams or larger non-empty CDB data, so the new relation/payload/overlay continuations are measured outside tiny-fixture launch overhead.

## Verdict

`accept-with-boundary`

Goal3534 gives the requested v2.3 baselines where they really exist and refuses fake comparisons where v2.3 lacks the contract.
