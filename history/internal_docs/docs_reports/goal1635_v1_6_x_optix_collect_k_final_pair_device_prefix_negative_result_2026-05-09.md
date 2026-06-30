# Goal1635 v1.6.x OptiX Collect-K Final-Pair Device-Prefix Negative Result

## Verdict

`final_pair_device_prefix_rejected`

An opt-in prototype that moved final-pair block prefix/count handling onto the device was measured and rejected. It preserved parity, but it made the 262144-candidate collect-k path slower.

The prototype runtime flag is intentionally not retained in production code.

## Scope

- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Shared environment:
  - `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`
- Control artifact: `docs/reports/goal1635_final_pair_device_prefix_control_262144_repeats5.json`
- Candidate artifact: `docs/reports/goal1635_final_pair_device_prefix_candidate_262144_repeats5.json`

## Result

| mode | total_ms | wrapper_median_ms | final_pair_mark_sync_ms | final_pair_prefix_host_ms | final_pair_prefix_device_ms | final_pair_final_sync_ms | parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| control | 0.648121 | 0.704855 | 0.323850 | 0.016921 | 0.000000 | 0.000000 | pass |
| candidate | 0.675452 | 0.720702 | 0.003580 | 0.000000 | 0.003440 | 0.370261 | pass |

The prototype removed the host prefix step and shifted the mark wait into a later final synchronization, but the total path became slower. This means the host-side block-prefix scan/upload is not the main bottleneck. The dominant cost is still waiting for the final mark/compact chain to complete.

## Next Work

Do not retain or promote the final-pair device-prefix prototype.

The next collect-k optimization should target final mark/compact algorithmic work or a different final-output strategy, not merely moving the small prefix calculation from host to device.

## Claim Boundary

This is internal negative diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
