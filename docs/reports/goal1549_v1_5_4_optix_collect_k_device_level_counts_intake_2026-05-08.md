# Goal 1549: OptiX COLLECT_K_BOUNDED Device-Level Counts Intake

## Verdict

Accepted as an opt-in experimental improvement layered on Goal 1548.

The candidate keeps per-level segment counts on device through the batched compact levels. After tile sorting, the tile emitted-count array is already on GPU. The candidate lets derived materialize/mark kernels read counts from that device array, lets the device prefix kernel write the next level counts, and downloads only the final two segment counts before the last two-segment compact merge.

The path is enabled by adding:

`RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1`

to the accepted Goal 1548 environment:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1`

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `41ae7926f69fdf4bb9c2aa140fa2a583d2d666fc`
- Evidence type: uncommitted working-tree candidate copied to the pod for measurement
- Confirmation shape: same binary, reverse-order A/B, candidate first then control, `21` repeats per case

## Artifacts

- `docs/reports/goal1549_v1_5_4_optix_collect_k_device_level_counts_candidate_probe_2026-05-08.json`
- `docs/reports/goal1549_v1_5_4_optix_collect_k_device_level_counts_candidate_probe_2026-05-08.md`
- `docs/reports/goal1549_v1_5_4_optix_collect_k_device_level_counts_candidate_profile_2026-05-08.jsonl`
- `docs/reports/goal1549_v1_5_4_optix_collect_k_device_level_counts_control_probe_2026-05-08.json`
- `docs/reports/goal1549_v1_5_4_optix_collect_k_device_level_counts_control_probe_2026-05-08.md`
- `docs/reports/goal1549_v1_5_4_optix_collect_k_device_level_counts_control_profile_2026-05-08.jsonl`

## Result

| candidates | Goal 1548 total ms | device-count total ms | total speedup | Goal 1548 H2D transfers | device-count H2D transfers | Goal 1548 D2H transfers | device-count D2H transfers | Goal 1548 merge-launch ms | device-count merge-launch ms |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.130758 | 0.126209 | 1.036x | 3 | 1 | 8 | 9 | 0.048242 | 0.033584 |
| 65537 | 0.358179 | 0.291683 | 1.228x | 63 | 1 | 98 | 69 | 0.214386 | 0.077889 |
| 131072 | 0.406921 | 0.320287 | 1.271x | 125 | 1 | 191 | 131 | 0.249271 | 0.088899 |

All candidate cases preserved candidate rows, valid counts, overflow flags, native path, and expected profile topology.

## Implementation Notes

- `RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS` is effective only with derived level descriptors and device prefix compact enabled.
- New derived count kernels read `current_counts[pair_index * 2]` and `current_counts[pair_index * 2 + 1]` directly on device.
- The existing device prefix kernel writes next-level pair counts into a ping-pong device count buffer.
- Carry segments copy their count device-to-device into the next count buffer.
- Before the final two-segment merge, the runtime downloads the final two segment counts so the existing final compact pair path can remain unchanged.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action without the required review and consensus.
