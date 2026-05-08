# Goal 1555: OptiX CUDA Graph Replay Feasibility

## Verdict

Accepted as a feasibility finding, not as a collect-k optimization.

CUDA graph replay is not useful for a single tiny CUDA driver command in this probe, but it becomes promising once replay captures a small batch of commands. This supports investigating graph replay for the current COLLECT_K_BOUNDED merge sequence, where the long cases still spend time across many small launches.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `9d75c642f7c5ea86b364fc20d4ea614e1eaf155d`
- Native evidence: `rtdl_optix_cuda_graph_replay_probe`
- Probe script: `scripts/goal1555_v1_5_4_optix_cuda_graph_replay_probe.py`
- JSON artifact: `docs/reports/goal1555_v1_5_4_optix_cuda_graph_replay_probe_2026-05-08.json`
- Markdown artifact: `docs/reports/goal1555_v1_5_4_optix_cuda_graph_replay_probe_2026-05-08.md`

The probe compares direct repeated CUDA driver memsets against replaying a captured CUDA graph containing the same number of memsets. It intentionally does not run COLLECT_K_BOUNDED.

## Result

| commands per replay | direct ms | graph ms | direct us/replay | graph us/replay | direct/graph |
|---:|---:|---:|---:|---:|---:|
| 1 | 33.549103 | 41.812512 | 1.677455 | 2.090626 | 0.802x |
| 4 | 136.524054 | 126.256458 | 6.826203 | 6.312823 | 1.081x |
| 8 | 269.166945 | 241.430325 | 13.458347 | 12.071516 | 1.115x |
| 16 | 538.777420 | 467.484224 | 26.938871 | 23.374211 | 1.153x |

The single-command case is negative. The batched cases are positive, with the best measured direct-over-graph ratio at `1.153x` for `16` commands per replay.

## Engineering Interpretation

The useful signal is not "CUDA graphs are always faster." They are not. The useful signal is narrower: graph replay can amortize launch-submission overhead when one replay represents a batch of small commands.

That matches the remaining collect-k performance direction from Goal 1553. The current long-case bottleneck is no longer just metadata transfer; it is the multi-kernel merge sequence. A future collect-k graph path should therefore target a replayable fixed-topology chunk of that sequence, not a one-kernel or one-command replay.

## Next Work

- Prototype graph replay around a fixed collect-k merge chunk only after identifying which launches can be captured without host-visible data dependencies.
- Keep the path opt-in until parity and same-contract timing are measured against the accepted Goal 1552 stack.
- Do not use this probe to claim public collect-k speedup.

## Claim Boundary

This is a launch-mechanics feasibility result only. It does not change RTDL semantics, does not publish a new user-visible feature, does not measure COLLECT_K_BOUNDED, and does not authorize public speedup wording.
