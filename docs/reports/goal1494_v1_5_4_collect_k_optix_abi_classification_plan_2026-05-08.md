# Goal 1494: COLLECT_K_BOUNDED OptiX ABI Classification Plan

## Verdict

Goal 1494 classifies the current `rtdl_optix_collect_k_bounded_i64` ABI before
any future pod run tries to treat it as device-buffer evidence.

## Scope

- Native API file: `src/native/optix/rtdl_optix_api.cpp`
- Native prelude file: `src/native/optix/rtdl_optix_prelude.h`
- Symbol: `rtdl_optix_collect_k_bounded_i64`

## Expected Finding

The current symbol is expected to remain a host-pointer native-library boundary:
it receives `const int64_t* candidate_rows`, writes `int64_t* rows_out`, and
performs host-side vector sort/deduplication.

That is useful for parity and API continuity, but it is not sufficient for Goal
1493 device-buffer execution evidence.

## Required Next Step

Add or identify a separate device-buffer ABI shape whose candidate input and
bounded output buffers are explicit CUDA device pointers, and whose execution
result includes transfer accounting.

## Claim Boundary

This goal classifies ABI shape only. It does not run OptiX, does not prove true
zero-copy, and does not authorize public speedup wording, whole-app claims,
partner tensor handoff, stable primitive promotion, or release action.
