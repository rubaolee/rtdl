# Goal 1496: COLLECT_K_BOUNDED Device-Pointer Stub Gate Plan

## Verdict

Goal 1496 reserves the proposed `rtdl_optix_collect_k_bounded_i64_device`
native ABI as a fail-closed OptiX symbol.

## Scope

- Native API file: `src/native/optix/rtdl_optix_api.cpp`
- Native prelude file: `src/native/optix/rtdl_optix_prelude.h`
- Symbol: `rtdl_optix_collect_k_bounded_i64_device`

## Intent

The symbol exists so Python+RTDL and future native work have a concrete ABI name
to target. It must not be accepted as device-buffer execution evidence until a
real implementation runs on an OptiX-ready NVIDIA system and passes Goal 1493
intake.

## Claim Boundary

This goal reserves a fail-closed native stub only. It does not implement device
execution, does not run OptiX, does not prove true zero-copy, and does not
authorize public speedup wording, whole-app claims, partner tensor handoff,
stable primitive promotion, or release action.
