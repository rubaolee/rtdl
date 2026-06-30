# Goal2924 Hausdorff Prepared-Radius Guard And Second-Architecture Smoke

Date: 2026-06-01

Verdict: `accept-with-boundary`.

## Purpose

Goal2924 closes the small-input portability failure found while smoking the v2.5
Hausdorff/X-HD benchmark on the local Linux GTX 1070 host. The failing path was
the exact RTDL/OptiX grouped-reduced Hausdorff implementation after the
Goal2920 `4096` target-points default:

```text
RuntimeError: point_group_nearest_max_distance radius exceeds prepared max_radius
```

The release packet on the RTX A5000 was healthy, but the local second
architecture exposed a rounding-sensitive boundary: the app prepared the
generic point-group nearest-witness scene with `max_radius == upper_bound`, then
queried the native reducer with `radius == upper_bound`. On the GTX 1070 path,
the native side could reject that exact equality after its internal
float/device-parameter representation.

## Change

The prepared-radius guard is intentionally app-level and generic:

- Added `_prepared_radius_guard(radius)`.
- Point-group Hausdorff prepare calls now pass a tiny conservative preparation
  envelope: `radius + max(1e-9, abs(radius) * 1e-6)`.
- Query calls still use the exact original witness/upper-bound radius.
- The native engine ABI, primitive names, and Hausdorff result semantics are
  unchanged.

This keeps the contract easy for users: prepared RTDL scenes may be built with a
slightly wider acceleration bound than the exact query radius, especially when
the query radius is mathematically equal to the preparation limit.

## Evidence

Windows unit validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2924_hausdorff_prepared_radius_guard_test \
  tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test \
  tests.goal2920_rtnn_hausdorff_large_scale_stability_test

Ran 11 tests in 0.006s
OK
```

Windows compile validation:

```text
py -3 -m py_compile \
  examples\v2_0\research_benchmarks\hausdorff_xhd\rtdl_hausdorff_v2_function.py \
  tests\goal2924_hausdorff_prepared_radius_guard_test.py
```

Local Linux clean-clone smoke:

- Host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070, 580.126.09`
- Source commit: `6ad6314192e9db0f659c76acc58a20767a194697`
- Source dirty: `[]`
- OptiX SDK: `/home/lestat/vendor/optix-dev`
- CUDA home: `/usr`
- NVCC: `/usr/bin/nvcc`
- PTX arch: `compute_61`

The clean clone ran:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal2924_hausdorff_prepared_radius_guard_test
make -j2 build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
python3 scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py --points-a 1024 --points-b 1024 --repeat 3 ...
python3 scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py --point-count 4096 --repeat 3 ...
```

Artifact summary:

| Artifact | Status | Key result |
| --- | --- | --- |
| `hausdorff_gtx1070_1024.json` | pass | Exact baseline match, RTDL path reports `uses_rt_cores = true`; `rtdl_over_cupy_grid_elapsed_ratio = 1.503x` on GTX 1070 smoke hardware. |
| `rtnn_gtx1070_4096.json` | pass | All three distributions pass; rows are exact against the CuPy grid contract. |
| `toolchain_gtx1070.json` | recorded | Documents CUDA/OptiX/GPU/toolchain and marks this as second-architecture smoke only. |

## Boundary

This goal is not a release-performance claim. The GTX 1070 has no RT cores and
is not accepted as v2.5 performance evidence. Its value is portability and
toolchain coverage:

- the small Hausdorff input that failed before now passes cleanly,
- the app-level exact-radius contract is less brittle across architectures,
- the core v2.5 claim boundary remains unchanged.

Because Goal2924 changes app code used by the canonical packet, the next packet
must be rerun on the RTX/OptiX pod from a source commit containing this fix
before any current-head packet or release-readiness wording is refreshed. In
short: the next packet must be rerun.
