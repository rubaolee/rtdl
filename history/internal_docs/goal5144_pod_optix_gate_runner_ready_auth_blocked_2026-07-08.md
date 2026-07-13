# Goal5144 - POD OptiX Gate Runner Ready / Auth Blocked (Superseded)

## Superseded Status

This file records the first Goal5144 attempt, which incorrectly classified the
current POD as SSH-auth blocked. The cause was local credential selection: the
default/old key was used instead of the current POD key.

This result is superseded by:

```text
history/internal_docs/goal5144_pod_optix_gate_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5144_pod_optix_gate_result_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/cell_mbr_backend_assisted_optix_gate_summary_pod.json
```

The corrected POD run used:

```text
ssh -i ~/.ssh/id_ed25519_rtdl_codex_current_pod root@213.173.108.24 -p 13502
```

and the OptiX gate passed:

```text
matched = true
broadphase_native_symbol = rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows
```

## Original Useful Artifacts

The reusable runner and CPU summary created during the first attempt remain
valid:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_cell_mbr_backend_assisted_gate.py
Paper-reproduction-apps/x-hd-paper/results/cell_mbr_backend_assisted_cpu_gate_summary.json
```

The original conclusion "OptiX correctness remains pending" is no longer the
current project status.
