# Goal3896 RayJoin Hot-Path Accounting

## Purpose

Goal3896 fixes a reader-facing measurement problem in the RayJoin benchmark
packet. The ten-app scale runner reports the `spatial_rayjoin` row as a single
wrapper elapsed time, but the actual RayJoin evidence is a mixed set of four
contract-level hot paths:

- one-shot PIP scalar count;
- repeated PIP requests over a prepared point/closed-shape executor;
- LSI scalar count;
- overlay active count.

The wrapper elapsed time includes orchestration, data loading, Numba JIT, and
sub-probe setup. It is useful for pod budgeting, but it is not the hot-path
metric for the RayJoin contracts.

## What Changed

`scripts/goal3866_rayjoin_representative_scale_profile.py` now emits:

- `wrapper_elapsed_sec`;
- `representative_hot_path_summary.metric_scope =
  per_contract_hot_medians_not_wrapper_wall_time`;
- explicit recommended routes for the four contracts;
- false claim flags inside the hot-path summary.

This is accounting hardening, not a new native primitive and not automatic
dispatch. It is not automatic dispatch.

## A5000 Evidence

Pod:

`ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex`

Fresh pod clone:

`/root/rtdl_goal3896_rayjoin_hotpath_clean_1780900348`

Source commit:

`23723c6e`

GPU:

`NVIDIA RTX A5000, 580.126.09`

Artifact:

`docs/reports/goal3896_rayjoin_hot_path_accounting_a5000/summary.json`

The script wrote stdout/stderr to `/tmp` first and copied the completed files
into the artifact directory only after execution, so the payload records an
empty `git_status_short`.

## Result

- `exit_code`: `0`
- `all_counts_match`: `true`
- `git_status_short`: empty string
- `wrapper_elapsed_sec`: `9.270`

| Contract | Recommended route | Partner median sec | RTDL/OptiX median sec | Ratio |
| --- | --- | ---: | ---: | ---: |
| PIP one-shot scalar count | Numba CUDA JIT scalar count | `0.000525` | `0.002171` | `0.242x` RTDL/OptiX vs Numba |
| PIP repeated requests | RTDL/OptiX prepared batch executor | `0.204769` ms single request | `0.024048` ms/request batched | `8.515x` per-request batching speedup |
| LSI scalar count | RTDL/OptiX prepared segment-pair count | `0.020657` | `0.000090` | `230.624x` RTDL/OptiX vs Numba |
| Overlay active count | RTDL/OptiX prepared shape-pair active count | `0.048688` | `0.000197` | `247.692x` RTDL/OptiX vs Numba |

## Interpretation

RayJoin should be described as a mixed-route benchmark, not a single 10-second
row:

It is not a single 10-second row.

- one-shot bounded public-CDB PIP remains a Numba-reference route;
- repeated PIP requests are RTDL/OptiX-favorable once the prepared executor is
  reused;
- LSI and overlay active count are strongly RTDL/OptiX-favorable through fused
  generic scalar-count primitives;
- route choice remains explicit and user-controlled.

This makes the performance story sharper without changing the app-agnostic
engine boundary.

## Boundary

Goal3896 does not authorize release action, public speedup wording, whole-app
RayJoin acceleration wording, broad RT-core wording, RayJoin paper-reproduction
wording, true-zero-copy wording, AMD performance wording, automatic
partner/backend selection, or app-specific native-engine logic.

The scale-runner elapsed is not the hot-path metric; it remains pod-budget and
orchestration evidence only.

## Validation

Added `tests/goal3896_rayjoin_hot_path_accounting_test.py`.

Added `tests/goal3896_rayjoin_hot_path_accounting_a5000_test.py`.

Local validation:

`py -3 -m unittest tests.goal3896_rayjoin_hot_path_accounting_test tests.goal3866_rayjoin_representative_scale_profile_test tests.goal3828_current_benchmark_scale_profile_registry_test`

Result:

`10 tests OK`
