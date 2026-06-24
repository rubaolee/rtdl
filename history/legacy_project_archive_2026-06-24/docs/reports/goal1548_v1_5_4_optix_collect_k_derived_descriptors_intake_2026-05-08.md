# Goal 1548: OptiX COLLECT_K_BOUNDED Derived Level Descriptors Intake

## Verdict

Accepted as an opt-in experimental improvement for the OptiX `COLLECT_K_BOUNDED` row-width-2 batched compact path.

The candidate keeps the accepted Goal 1545 device-prefix compact path, but removes three host-uploaded descriptor arrays from each batched compact level. Instead of uploading first-row pointers, second-row pointers, and output-row pointers, the level materialize and compact kernels derive those addresses from the current level base pointer, output base pointer, segment capacity, output capacity, and pair index.

The path is enabled by adding:

`RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1`

to the accepted Goal 1545 environment:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `cfae0a74bf4bf188b47640ba16770ca1e8505e55`
- Evidence type: uncommitted working-tree candidate copied to the pod for measurement
- Confirmation shape: same binary, reverse-order A/B, candidate first then control, `21` repeats per case

## Artifacts

- `docs/reports/goal1548_v1_5_4_optix_collect_k_derived_descriptors_candidate_probe_2026-05-08.json`
- `docs/reports/goal1548_v1_5_4_optix_collect_k_derived_descriptors_candidate_probe_2026-05-08.md`
- `docs/reports/goal1548_v1_5_4_optix_collect_k_derived_descriptors_candidate_profile_2026-05-08.jsonl`
- `docs/reports/goal1548_v1_5_4_optix_collect_k_derived_descriptors_control_probe_2026-05-08.json`
- `docs/reports/goal1548_v1_5_4_optix_collect_k_derived_descriptors_control_probe_2026-05-08.md`
- `docs/reports/goal1548_v1_5_4_optix_collect_k_derived_descriptors_control_profile_2026-05-08.jsonl`

## Result

| candidates | control total ms | derived-descriptor total ms | total speedup | control H2D transfers | derived H2D transfers | control merge-launch ms | derived merge-launch ms |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.142971 | 0.129666 | 1.103x | 6 | 3 | 0.062157 | 0.047990 |
| 65537 | 0.428943 | 0.360523 | 1.190x | 156 | 63 | 0.284149 | 0.216721 |
| 131072 | 0.479449 | 0.409456 | 1.171x | 311 | 125 | 0.322240 | 0.252180 |

All candidate cases preserved candidate rows, valid counts, overflow flags, native path, and expected profile topology.

## Implementation Notes

- `RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS` gates the path.
- New derived materialize and compact kernels compute level row pointers from base pointers and segment geometry.
- The runtime still uploads the first-count and second-count arrays for each batched level, so this is reduced descriptor upload, not true zero-copy.
- Merge topology is unchanged: the candidate reduces host-to-device descriptor traffic without adding launches.
- The final two-segment merge remains on the existing parallel compact pair path.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action without the required review and consensus.
