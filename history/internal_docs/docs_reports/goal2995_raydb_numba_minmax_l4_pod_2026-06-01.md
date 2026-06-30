# Goal2995: RayDB-Style Numba Segmented Min/Max L4 Pod Evidence

Date: 2026-06-01

Status: passed on NVIDIA L4 pod.

## What This Proves

Goal2995 extends the v2.6 user-selected Numba lane from Goal2994's
`count`/`sum`/`avg_as_sum_count` RayDB-style demonstrator to the full scalar
aggregate set used by the app:

- `count` -> `segmented_count_i64`
- `sum` -> `segmented_sum_f64`
- `min` -> `segmented_min_f64`
- `max` -> `segmented_max_f64`
- `avg_as_sum_count` -> `segmented_sum_f64` plus `segmented_count_i64`

The new min/max operations are generic grouped reductions over
`group_ids:int64` and `values:float64`. They are not RayDB-specific native
engine logic.

## Pod Environment

- SSH endpoint supplied by the user: `root@157.157.221.29 -p 29842`
- Key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA L4`
- Driver: `565.57.01`
- Source commit: `b41369e4b4becb3534e729658db41642c643abe2`
- Isolated Numba CUDA module:
  `/root/rtdl_goal2991_v26_pod/.pydeps_v26_numba_cuda/numba_cuda/numba/cuda/__init__.py`
- Numba version: `0.65.1`
- NumPy version: `2.1.2`
- Required environment:
  `NUMBA_CUDA_USE_NVIDIA_BINDING=1`
  `NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=1`

## Run

Runner:

`scripts/goal2995_raydb_numba_minmax_pod_runner.py`

Parameters:

- rows: `1,000,000`
- groups: `4,096`
- block size: `256`

Artifact:

`docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.json`

## Results

All five modes matched the CPU NumPy reference:

| Mode | Operations | CPU Match | Max Abs Error |
| --- | --- | --- | ---: |
| `count` | `segmented_count_i64` | true | `0.0` |
| `sum` | `segmented_sum_f64` | true | `9.094947017729282e-13` |
| `min` | `segmented_min_f64` | true | `0.0` |
| `max` | `segmented_max_f64` | true | `0.0` |
| `avg_as_sum_count` | `segmented_sum_f64`, `segmented_count_i64` | true | `6.821210263296962e-13` |

Every mode reports:

- neutral handoff status: `accept`
- continuation path: `v2_6_numba_neutral_front_door`
- `uses_legacy_torch_carrier`: false
- `uses_torch_conversion`: false
- `promoted_performance_path`: false

## Boundary

This is runtime conformance evidence for the v2.6 user-selected Numba lane and
for one benchmark-app demonstrator. It does not authorize:

- v2.6 release
- public speedup claims
- whole-app speedup claims
- broad RT-core speedup claims
- true zero-copy claims
- Numba speedup claims
- RayDB paper reproduction claims
- automatic partner selection claims

The one caveat from execution is that the wrapper command's final JSON summary
here-doc had a quoting typo after the runner had already written a passing
artifact. The artifact was copied back and validated locally; the pod runner
payload itself records `status: pass`.
