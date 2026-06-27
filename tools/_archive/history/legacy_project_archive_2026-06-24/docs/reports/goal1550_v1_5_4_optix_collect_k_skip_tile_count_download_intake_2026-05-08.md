# Goal 1550: OptiX COLLECT_K_BOUNDED Skip Tile Count Download Intake

## Verdict

Accepted as a small opt-in experimental improvement layered on Goal 1549.

When `RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1` is enabled, the tile emitted-count array is already consumed on device by the batched merge levels. The runtime no longer needs to download those tile counts to host immediately after sorting. This candidate keeps downloading tile overflow flags, but skips the tile emitted-count download.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `e12719de2b48ac911b5cd8115b6f75e8bb2e948b`
- Evidence type: uncommitted working-tree candidate copied to the pod for measurement
- Comparison baseline: accepted Goal 1549 candidate artifact from the same pod

## Artifacts

- `docs/reports/goal1550_v1_5_4_optix_collect_k_skip_tile_count_download_candidate_probe_2026-05-08.json`
- `docs/reports/goal1550_v1_5_4_optix_collect_k_skip_tile_count_download_candidate_probe_2026-05-08.md`
- `docs/reports/goal1550_v1_5_4_optix_collect_k_skip_tile_count_download_candidate_profile_2026-05-08.jsonl`
- Baseline: `docs/reports/goal1549_v1_5_4_optix_collect_k_device_level_counts_candidate_probe_2026-05-08.json`

## Result

| candidates | Goal 1549 total ms | skip-count total ms | total speedup | Goal 1549 D2H transfers | skip-count D2H transfers | Goal 1549 metadata fields | skip-count metadata fields | skip-count tile metadata ms |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.126209 | 0.118645 | 1.064x | 9 | 6 | 9 | 6 | 0.007334 |
| 65537 | 0.291683 | 0.284469 | 1.025x | 69 | 36 | 69 | 36 | 0.007675 |
| 131072 | 0.320287 | 0.312151 | 1.026x | 131 | 67 | 131 | 67 | 0.007515 |

All candidate cases preserved candidate rows, valid counts, overflow flags, native path, and expected profile topology.

## Implementation Notes

- The behavior is not a new env flag; it is the natural behavior when device-level counts are enabled.
- Host-side `current_counts` is populated with placeholders while device-level counts are active.
- The runtime still downloads tile overflow flags, final two segment counts, and the final emitted count.
- This is reduced metadata transfer, not true zero-copy.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action without the required review and consensus.
