# Goal 1553: OptiX COLLECT_K_BOUNDED Cumulative Status After Device Final Counts

## Verdict

Current clean `main` at `ef5ce3750ca3329a6022213d0072a533ff95a6f2` preserves parity and improves the accepted Goal 1545 OptiX `COLLECT_K_BOUNDED` row-width-2 path.

This refresh supersedes the Goal 1551 cumulative status by including Goal 1552 device final counts.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Current clean commit: `ef5ce3750ca3329a6022213d0072a533ff95a6f2`
- Repeats: `31`

## Artifacts

- `docs/reports/goal1553_v1_5_4_optix_collect_k_cumulative_current_probe_2026-05-08.json`
- `docs/reports/goal1553_v1_5_4_optix_collect_k_cumulative_current_probe_2026-05-08.md`
- `docs/reports/goal1553_v1_5_4_optix_collect_k_cumulative_current_profile_2026-05-08.jsonl`
- Baseline: `docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_candidate_probe_2026-05-08.json`

## Result

| candidates | Goal 1545 total ms | current total ms | cumulative speedup | current sort sync ms | current merge-launch ms | current merge-sync ms | current D2H transfers | current metadata fields |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.157087 | 0.111742 | 1.406x | 0.028404 | 0.034025 | 0.008515 | 4 | 4 |
| 65537 | 0.429634 | 0.281974 | 1.524x | 0.036319 | 0.081495 | 0.083689 | 34 | 34 |
| 131072 | 0.480390 | 0.306581 | 1.567x | 0.054624 | 0.089912 | 0.120409 | 65 | 65 |

All current cases preserved candidate rows, valid counts, overflow flags, native path, and expected profile topology.

## Current Bottleneck

At `131072`, the current median total is `0.306581 ms`. Host metadata transfer is now small: only one host-to-device transfer and `65` device-to-host metadata fields remain in the measured accounting.

The remaining high-order bottleneck is the merge pipeline itself. In this run, merge sync measured larger than in Goal 1551, while the total still improved. Treat the per-stage split as a guide rather than a standalone claim; the safe conclusion is that further major gains likely require reducing, fusing, or replaying the multi-kernel merge sequence.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action without the required review and consensus.
