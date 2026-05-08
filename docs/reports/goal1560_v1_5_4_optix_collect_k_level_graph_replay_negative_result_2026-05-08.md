# Goal 1560: OptiX COLLECT_K Level Graph Replay Negative Result

## Verdict

Rejected as a production implementation path.

The opt-in candidate `RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1` preserved parity, but it regressed both long target cases. The runtime candidate was reverted and the env flag was not kept.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `31a0415dbb954fbf2d3e1655a844cfed0b7d8da1`
- Evidence type: uncommitted working-tree production candidate copied to the pod for measurement only
- Control JSON: `docs/reports/goal1560_v1_5_4_optix_collect_k_level_graph_replay_control_2026-05-08.json`
- Candidate JSON: `docs/reports/goal1560_v1_5_4_optix_collect_k_level_graph_replay_candidate_2026-05-08.json`
- Claude read-only review: `docs/reports/goal1560_claude_graph_replay_readonly_review_2026-05-08.md`

Both runs used the accepted current stack:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1 RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1 RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1`

The rejected candidate additionally used:

`RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1`

## Result

| candidates | level graph replay | total ms | merge launch ms | merge sync ms | merge launches | metadata fields | parity |
|---:|:---:|---:|---:|---:|---:|---:|:---:|
| 4097 | off | 0.179259 | 0.051848 | 0.008676 | 7 | 4 | accepted |
| 4097 | on | 0.150685 | 0.071315 | 0.004387 | 7 | 4 | accepted |
| 65537 | off | 0.285391 | 0.085694 | 0.082879 | 23 | 34 | accepted |
| 65537 | on | 0.328192 | 0.198987 | 0.008337 | 23 | 34 | accepted |
| 131072 | off | 0.308394 | 0.092326 | 0.119396 | 23 | 65 | accepted |
| 131072 | on | 0.345594 | 0.234765 | 0.009358 | 23 | 65 | accepted |

The candidate improved only the smallest target. It regressed `65537` from `0.285391 ms` to `0.328192 ms` and `131072` from `0.308394 ms` to `0.345594 ms`.

Claude independently reviewed the transient candidate before the final rejection and recommended parity-first, timing-second acceptance. The measured package satisfied parity but failed the long-case timing requirement.

## Interpretation

Goal 1559 showed that graph executable parameter update is useful when the updated graph is replayed many times. The production candidate updates graph kernel nodes once per merge level inside a single collect-k call. That update/capture/synchronization cost is not amortized enough, and it is larger than the launch-submission savings for the long cases.

The next graph direction should not be per-call, per-level graph-update replay. If graph work continues, it should investigate persistent topology caches across repeated calls or a fused native kernel path that removes launches without per-level graph update overhead.

## Claim Boundary

This is a negative engineering result only. It does not change the accepted current collect-k path, does not publish a user-visible feature, and does not authorize public speedup wording.
