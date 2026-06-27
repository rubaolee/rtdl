# Goal 1562: OptiX COLLECT_K Parallel Compact Threshold Negative Result

## Verdict

Do not tune `RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY` upward as a shortcut for launch reduction.

The default threshold package at `4096` remains valid. Raising the threshold to `8192` failed the probe warmup parity check, so the matrix stopped before timing could be accepted.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Commit: `d323550a09b26a5e518f73e0b413af5210842ddf`
- Threshold control artifact: `docs/reports/goal1562_v1_5_4_optix_collect_k_threshold_4096_control_2026-05-08.json`
- Threshold failure transcript: `docs/reports/goal1562_v1_5_4_optix_collect_k_threshold_matrix_failure_2026-05-08.txt`

The attempted matrix used the accepted current stack and varied only:

`RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY`

## Result

| threshold | result |
|---:|---|
| 4096 | profile recorded |
| 8192 | failed warmup parity before timing |

The exact blocker for `8192` was:

`RuntimeError: warmup collect-k parity failed before timing`

No timing claim is valid for thresholds above `4096` from this run.

## Interpretation

The threshold knob changes which merge levels use the four-kernel parallel compact path versus the older single-kernel merge path. That is not a safe pure performance knob under the current device-count/device-prefix stack. At `8192`, the probe failed before measurement because output parity was not preserved.

This reinforces the Goal 1561 direction: launch reduction should not be pursued by simply forcing more levels onto the older merge path. The next implementation direction should be a deliberately tested fusion candidate or a separate repeated-call topology-cache diagnostic.

## Claim Boundary

This is a negative engineering result only. It does not change runtime behavior, does not publish a user-visible feature, and does not authorize public speedup wording.
