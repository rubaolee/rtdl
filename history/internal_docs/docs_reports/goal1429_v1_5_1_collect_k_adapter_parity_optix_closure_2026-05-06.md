# Goal 1429 v1.5.1 COLLECT_K_BOUNDED Adapter Parity OptiX Closure

## Verdict

Post-adapter polygon-pair parity is now accepted for both Embree and OptiX.

This closes the adapter-parity blocker recorded in Goal 1428. It does not claim
built generic i64 symbol validation, stable primitive promotion, speedup,
zero-copy, whole-app behavior, broad workload coverage, or release action.

## Pod Evidence

Pod:

- SSH: `root@69.30.85.196 -p 22030 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_pod_69_30_85_196`
- GPU: NVIDIA RTX A5000
- Driver: 580.126.09
- CUDA toolkit used by build: CUDA 13.0, `nvcc` V13.0.88
- OptiX headers: `/root/vendor/optix-dev/include/optix.h`
- Git HEAD: `da7664f88c54aefdbe4d6f6069f26e5c4eb2e8da`

Build artifact:

- `docs/reports/goal1429_v1_5_1_collect_k_build_optix_2026-05-06.txt`
- Built library on pod: `/workspace/rtdl/build/librtdl_optix.so`

Environment artifact:

- `docs/reports/goal1429_v1_5_1_collect_k_pod_env_2026-05-06.json`

Required OptiX parity artifact:

- `docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.md`
- Result: accepted
- OptiX: pass=4, fail=0, skipped=0
- Required backend skips: none

## Prior Evidence

Goal 1428 already recorded:

- Windows optional parity accepted with Embree pass=4, fail=0, skipped=0
- Linux required-Embree parity accepted with Embree pass=4, fail=0, skipped=0
- Linux required-OptiX was not accepted only because `librtdl_optix` was missing

The new RTX A5000 pod required-OptiX run supersedes the Goal 1428 OptiX-pending
state.

## Still Pending

- Validate `rtdl_embree_collect_k_bounded_i64` and
  `rtdl_optix_collect_k_bounded_i64` in built libraries.
- Add Embree/OptiX generic ABI parity tests against the built generic i64
  symbols.
- Rerun stable-promotion review only after built generic symbol validation and
  generic ABI parity tests pass.
