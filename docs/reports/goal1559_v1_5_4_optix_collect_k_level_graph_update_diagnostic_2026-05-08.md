# Goal 1559: OptiX COLLECT_K Level Graph Update Diagnostic

## Verdict

Accepted as a diagnostic engineering result.

CUDA graph executable kernel-node parameter update works for the real four-kernel COLLECT_K_BOUNDED compact-level sequence on the RTX 4000 Ada pod. The diagnostic captured the sequence with `initial_pair_count=1`, updated the graph executable to target `pair_count=4` and `pair_count=16`, and replayed the updated graph successfully.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `5a6fa1be68a531ced64cd4dd76a43b59fa414c8d`
- Native evidence: `rtdl_optix_collect_k_level_graph_update_probe`
- Probe script: `scripts/goal1559_v1_5_4_optix_collect_k_level_graph_update_probe.py`
- JSON artifact: `docs/reports/goal1559_v1_5_4_optix_collect_k_level_graph_update_probe_2026-05-08.json`
- Markdown artifact: `docs/reports/goal1559_v1_5_4_optix_collect_k_level_graph_update_probe_2026-05-08.md`

The probe uses `cuGraphGetNodes`, filters four `CU_GRAPH_NODE_TYPE_KERNEL` nodes, and applies `cuGraphExecKernelNodeSetParams` with rebuilt `CUDA_KERNEL_NODE_PARAMS` for each target topology.

## Result

| initial pairs | target pairs | segment capacity | direct ms | graph-update ms | direct us/replay | graph-update us/replay | direct/graph-update | nodes | first pair count |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 2048 | 58.728800 | 50.801607 | 11.745760 | 10.160321 | 1.156x | 4 | 4096 |
| 1 | 16 | 2048 | 86.580558 | 76.446273 | 17.316112 | 15.289255 | 1.133x | 4 | 4096 |

Both updated graph cases found exactly four kernel nodes and produced the expected first-pair count of `4096`.

## Engineering Interpretation

This result removes the largest uncertainty from Goal 1558. The next production candidate can cache a graph executable for the compact-level sequence and update kernel-node parameters per merge level, instead of capturing a fresh graph for every level.

This still does not prove a production collect-k speedup. The diagnostic uses controlled buffers and one compact-level sequence. Production integration must preserve row parity, emitted count, overflow behavior, fallback behavior, and same-contract timing against the accepted current stack.

## Next Work

- Implement opt-in `RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1`.
- Scope the first production candidate to the device-count/device-prefix/derived-descriptor compact-level path.
- Use `cuGraphExecKernelNodeSetParams` before replaying each eligible non-final compact level.
- Fall back to the current direct-launch path if graph capture, node discovery, parameter update, or topology validation fails.
- Measure `65537` and `131072` candidates against the accepted Goal 1552 stack before accepting or rejecting the production path.

## Claim Boundary

This is a diagnostic graph executable update result only. It does not publish a user-visible feature, does not change default `COLLECT_K_BOUNDED` behavior, and does not authorize public speedup wording.
