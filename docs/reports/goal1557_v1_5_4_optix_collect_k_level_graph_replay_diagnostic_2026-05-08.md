# Goal 1557: OptiX COLLECT_K Level Graph Replay Diagnostic

## Verdict

Accepted as a diagnostic engineering result.

The actual four-kernel COLLECT_K_BOUNDED compact-level sequence can be captured and replayed as a CUDA graph on the RTX 4000 Ada pod. In this controlled diagnostic, graph replay was faster than direct launches for all tested pair counts.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `aacde16f08cd64532ccb699fe49c29f2b3152d0c`
- Native evidence: `rtdl_optix_collect_k_level_graph_replay_probe`
- Probe script: `scripts/goal1557_v1_5_4_optix_collect_k_level_graph_probe.py`
- JSON artifact: `docs/reports/goal1557_v1_5_4_optix_collect_k_level_graph_probe_2026-05-08.json`
- Markdown artifact: `docs/reports/goal1557_v1_5_4_optix_collect_k_level_graph_probe_2026-05-08.md`

The probe uses controlled dummy row buffers and the real collect-k compact-level sequence:

1. `collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived`
2. `collect_k_bounded_i64_row_width2_final_mark_counts_level_counts`
3. `collect_k_bounded_i64_row_width2_final_prefix_offsets_level`
4. `collect_k_bounded_i64_row_width2_final_compact_level_derived`

It intentionally does not alter the production `COLLECT_K_BOUNDED` runtime path.

## Result

| pairs | segment capacity | direct ms | graph ms | direct us/replay | graph us/replay | direct/graph | first pair count |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2048 | 54.443597 | 45.854471 | 10.888719 | 9.170894 | 1.187x | 4096 |
| 4 | 2048 | 58.961368 | 50.866699 | 11.792274 | 10.173340 | 1.159x | 4096 |
| 16 | 2048 | 85.732588 | 76.409591 | 17.146518 | 15.281918 | 1.122x | 4096 |

The diagnostic confirms the Goal 1556 target selection: the compact-level merge window is graphable and has a measured launch-submission benefit in isolation.

## Engineering Interpretation

This result narrows the next production experiment. CUDA graph replay should not wrap arbitrary collect-k work and should not target single tiny commands. It should target the existing no-host-sync compact-level block when the current accepted flags already keep the required data dependencies on device.

The remaining production challenge is parameterization. Real collect-k levels change `pair_count`, `blocks_per_pair`, segment/output capacity, input/output bases, and count-buffer pointers. A production candidate must therefore either cache graph executables by fixed topology or update graph node parameters safely before replay.

## Next Work

- Add an opt-in production candidate for one fixed compact-level topology first.
- Keep the current direct-launch path as the default and as the fallback.
- Require same-row parity and same overflow behavior before comparing timing.
- Measure against the accepted Goal 1552 stack on `65537` and `131072` candidates.

## Claim Boundary

This is a diagnostic graphability and replay-overhead result only. It does not publish a user-visible feature, does not change default `COLLECT_K_BOUNDED` behavior, and does not authorize public speedup wording.
