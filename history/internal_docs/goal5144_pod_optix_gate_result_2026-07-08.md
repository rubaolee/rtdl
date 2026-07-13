# Goal5144 - POD OptiX Gate Result

## Verdict

`pod_optix_gate_matched__backend_assisted_frontdoor_verified`

## Correction To Earlier Attempt

The earlier Goal5144 status classified the current POD endpoint as SSH-auth
blocked. That was a local credential-selection error, not a POD outage. The
current POD key was:

```text
id_ed25519_rtdl_codex_current_pod
```

Using that key, the POD was reachable:

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

The earlier auth-blocked file is preserved as historical evidence but is
superseded by this verified result.

## What Was Run

The minimal workspace was synced to:

```text
/tmp/rtdl_goal5144
```

The current OptiX backend library was built from the synced source:

```text
cd /tmp/rtdl_goal5144
make build-optix
```

Result:

```text
exit_code_0
library = /tmp/rtdl_goal5144/build/librtdl_optix.so
OPTIX_PREFIX = /root/vendor/optix-dev
```

CPU sanity gate:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_cell_mbr_backend_assisted_gate.py \
  --backend cpu \
  --summary Paper-reproduction-apps/x-hd-paper/results/cell_mbr_backend_assisted_cpu_gate_summary_pod.json
```

OptiX gate:

```text
RTDL_OPTIX_LIB=/tmp/rtdl_goal5144/build/librtdl_optix.so \
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_cell_mbr_backend_assisted_gate.py \
  --backend optix \
  --summary Paper-reproduction-apps/x-hd-paper/results/cell_mbr_backend_assisted_optix_gate_summary_pod.json
```

## Result

```text
matched = true
backend = optix
row_count = 6
broadphase_row_count = 6
exact_candidate_row_count = 6
broadphase_native_symbol = rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows
native_abi_contract = generic_cell_mbr_nearest_frontier_native_abi_v1
assisted_contract = generic_cell_mbr_nearest_frontier_aabb_membership_2d
```

Summary files:

```text
Paper-reproduction-apps/x-hd-paper/results/cell_mbr_backend_assisted_cpu_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/cell_mbr_backend_assisted_optix_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5144_pod_optix_gate_result_2026-07-08.json
```

## Interpretation

Goal5144 verifies that the Goal5142 backend-assisted 2-D cell-MBR front door can
run on a CUDA/OptiX POD through the generic AABB membership native backend and
produce the same Goal5140 frontier row table as the reference route.

This is still not a completed native Goal5140 backend. The route uses:

```text
generic expanded-AABB membership backend
-> exact point-to-cell-MBR distance filter
-> nearest-state frontier classification
-> Goal5140 ABI-shaped row table
```

The verified native symbol is the generic AABB broadphase:

```text
rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows
```

It is not an X-HD-specific primitive and it is not the full X-HD algorithm.

## Claim Boundary

Allowed:

- POD OptiX correctness gate passed for the bounded Goal5142 synthetic fixture.
- The backend-assisted front door can use the generic OptiX AABB membership
  broadphase and match the reference row table.
- The previous SSH-auth-blocked status is superseded by this authenticated POD
  run.

Not allowed:

- Native Goal5140 backend exists.
- X-HD paper performance improved.
- Full X-HD paper reproduction.
- Exact paper dataset reproduction.
- Author algorithm parity.
