# Goal 1545: OptiX COLLECT_K_BOUNDED Device Prefix Compact Intake

## Verdict

Accepted as a small opt-in experimental improvement for long OptiX `COLLECT_K_BOUNDED` row-width-2 candidate lists.

The candidate path moves batched compact level block-offset prefixing from host code to a small device kernel, preserving deterministic sorted-unique output while removing the host block-count prefix loop and offset upload from those levels.

The path remains opt-in behind:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`

The clean pod evidence at commit `2a2000c30875b9221f607eda280f6c47bae9987c` preserved parity and improved the long-count target cases versus a fresh Goal 1543 control on the same pod. The smallest target case, `4097`, is recorded as slightly slower and is not claimed as improved.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility libraries: `cuda-compat-12-8=570.211.01-0ubuntu1`, with `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8`
- Runner command: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64 PYTHONPATH=src:. python3 scripts/goal1545_v1_5_4_optix_collect_k_device_prefix_pod_runner.py --library build/librtdl_optix.so --counts 4097 65537 131072 --repeats 11 ...`

The compatibility library path was required because CUDA 12.8 NVRTC generated PTX that the base 550.127.05 user-mode driver rejected with `the provided PTX was compiled with an unsupported toolchain`.

## Artifacts

- `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_control_goal1543_probe_2026-05-08.json`
- `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_control_goal1543_probe_2026-05-08.md`
- `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_control_goal1543_profile_2026-05-08.jsonl`
- `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_candidate_probe_2026-05-08.json`
- `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_candidate_probe_2026-05-08.md`
- `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_candidate_profile_2026-05-08.jsonl`
- `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_confirm_summary_2026-05-08.json`
- `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_confirm_summary_2026-05-08.md`

## Result

Compared with the fresh Goal 1543 control on the same pod:

| candidates | control total ms | device-prefix total ms | total speedup | control merge launches | device-prefix merge launches | control merge-launch ms | device-prefix merge-launch ms |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.153340 | 0.157087 | 0.976x | 6 | 7 | 0.070914 | 0.064322 |
| 65537 | 0.448761 | 0.429634 | 1.045x | 18 | 23 | 0.305510 | 0.284809 |
| 131072 | 0.491491 | 0.480390 | 1.023x | 18 | 23 | 0.333593 | 0.322764 |

The candidate adds one small prefix kernel per batched compact level, increasing merge launches. It still improves the long-count totals because it removes host-side block-count prefixing and offset upload from those levels. The win is modest and should be described as a long-count internal experimental improvement only.

## Implementation Notes

- `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT` enables the path explicitly.
- The new kernel `collect_k_bounded_i64_row_width2_final_prefix_offsets_level` computes per-block offsets and per-pair emitted counts on device for each batched compact level.
- The compact kernel remains deterministic because it still uses stable per-block offsets, not unordered atomics.
- The final two-segment merge remains on the existing parallel compact path.
- Default behavior remains unchanged unless the explicit env flag is set.

## Current Bottleneck

At `131072`, the device-prefix candidate measured:

- total: `0.480390 ms`
- sort sync: `0.088813 ms`
- merge sync: `0.051678 ms`
- merge launch overhead: `0.322764 ms`
- allocation: `0.000200 ms`

The remaining bottleneck is still host launch/orchestration overhead. The device-prefix path reduces CPU/GPU metadata work but adds kernel launches, so future improvements likely need CUDA graph replay, a prepared execution model, or a deeper fused deterministic compact algorithm.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action without the required review and consensus.
