# Goal 1551: OptiX COLLECT_K_BOUNDED Cumulative Status

## Verdict

Current clean `main` at `1d11185542f93712029368ee477d09e22e579ae9` preserves parity and materially improves the accepted Goal 1545 OptiX `COLLECT_K_BOUNDED` row-width-2 path.

The cumulative improvement comes from three accepted opt-in layers after Goal 1545:

- Goal 1548: derived level descriptors, removing row-pointer descriptor uploads in batched compact levels.
- Goal 1549: device-level counts, keeping batched-level counts on GPU until the final two-segment merge.
- Goal 1550: skipped tile emitted-count download when device-level counts are active.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Current clean commit: `1d11185542f93712029368ee477d09e22e579ae9`
- Repeats: `31`

## Artifacts

- `docs/reports/goal1551_v1_5_4_optix_collect_k_cumulative_current_probe_2026-05-08.json`
- `docs/reports/goal1551_v1_5_4_optix_collect_k_cumulative_current_probe_2026-05-08.md`
- `docs/reports/goal1551_v1_5_4_optix_collect_k_cumulative_current_profile_2026-05-08.jsonl`
- Baseline: `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_candidate_probe_2026-05-08.json`

## Result

| candidates | Goal 1545 total ms | current total ms | cumulative speedup | current merge-launch ms | current H2D transfers | current D2H transfers | current metadata fields |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.157087 | 0.118765 | 1.323x | 0.033373 | 1 | 6 | 6 |
| 65537 | 0.429634 | 0.283587 | 1.515x | 0.078520 | 1 | 36 | 36 |
| 131072 | 0.480390 | 0.312012 | 1.540x | 0.088458 | 1 | 67 | 67 |

All current cases preserved candidate rows, valid counts, overflow flags, native path, and expected profile topology.

## Current Bottleneck

At `131072`, the current median total is `0.312012 ms`. The remaining high-order bottleneck is the multi-kernel merge pipeline itself, not Python bulk copying:

- sort sync: `0.055085 ms`
- merge launch/orchestration: `0.088458 ms`
- merge sync: `0.052531 ms`
- tile metadata download: `0.007615 ms`

Further major gains likely require reducing or replaying the kernel launch sequence, for example with CUDA graph-style execution or a deeper fused deterministic compact design. More host metadata cleanup is now lower leverage.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action without the required review and consensus.
