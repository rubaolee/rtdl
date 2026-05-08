# Goal 1552: OptiX COLLECT_K_BOUNDED Device Final Counts Intake

## Verdict

Accepted as a small opt-in experimental improvement layered on Goal 1550.

The candidate lets the final two-segment compact pair read its two input segment counts directly from the device count buffer. It avoids the final host download of those two input counts while keeping the existing three-kernel final compact shape: materialize, mark counts, compact.

The path is enabled by adding:

`RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1`

to the accepted Goal 1550 environment:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1 RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1`

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `a3db1d1ae1d5628b6cfd73655807e1dadc60bf3a`
- Evidence type: uncommitted working-tree candidate copied to the pod for measurement
- Confirmation shape: same binary, reverse-order A/B, candidate first then control, `31` repeats per case

## Artifacts

- `docs/reports/goal1552_v1_5_4_optix_collect_k_device_final_counts_candidate_probe_2026-05-08.json`
- `docs/reports/goal1552_v1_5_4_optix_collect_k_device_final_counts_candidate_probe_2026-05-08.md`
- `docs/reports/goal1552_v1_5_4_optix_collect_k_device_final_counts_candidate_profile_2026-05-08.jsonl`
- `docs/reports/goal1552_v1_5_4_optix_collect_k_device_final_counts_control_probe_2026-05-08.json`
- `docs/reports/goal1552_v1_5_4_optix_collect_k_device_final_counts_control_probe_2026-05-08.md`
- `docs/reports/goal1552_v1_5_4_optix_collect_k_device_final_counts_control_profile_2026-05-08.jsonl`

## Result

| candidates | Goal 1550 total ms | device-final-count total ms | total speedup | Goal 1550 D2H transfers | device-final-count D2H transfers | Goal 1550 metadata fields | device-final-count metadata fields |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.119326 | 0.112293 | 1.063x | 6 | 4 | 6 | 4 |
| 65537 | 0.285521 | 0.281163 | 1.016x | 36 | 34 | 36 | 34 |
| 131072 | 0.312833 | 0.306882 | 1.019x | 67 | 65 | 67 | 65 |

All candidate cases preserved candidate rows, valid counts, overflow flags, native path, and expected profile topology.

## Implementation Notes

- `RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS` is effective only with device-level counts enabled.
- New final-pair count kernels read `counts[0]` and `counts[1]` from device memory.
- The runtime still computes the final output count from block counts on host, preserving existing deterministic compact behavior and return semantics.
- This is reduced metadata transfer, not true zero-copy.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action without the required review and consensus.
