# Goal 1507: Non-Pod OptiX COLLECT_K_BOUNDED Local Readiness

## Verdict

Local non-pod readiness improved. No public performance claim, speedup claim, true zero-copy claim, stable primitive promotion, or release action is authorized.

## What Was Validated Locally

- Windows v1.5.4 evidence/profile guard slice passed after Goal1506 probe hardening.
- Linux host `192.168.1.20` can compile `build/librtdl_optix.so` with `OPTIX_PREFIX=/home/lestat/vendor/optix-dev`.
- Linux host `192.168.1.20` has `NVIDIA GeForce GTX 1070` and can run the Goal1506 profiling hook as a local fallback smoke.
- The local GTX 1070 smoke writes profile JSONL records and preserves parity for `candidate_count=4097`.
- The local GTX 1070 smoke is explicitly classified as `accepted_goal1506_evidence=false` and `local_fallback_smoke_only=true` because it takes `dynamic_row_width_single_thread_fallback`, not the expected tiled path.

## Why This Matters

The next paid pod run should no longer spend time discovering whether the native hook compiles, whether the JSONL path emits records, or whether the Python validator can distinguish accepted tiled-path evidence from old-GPU fallback smoke.

The remaining pod-only question is actual accepted Goal1506 measurement on a GPU that takes the expected `row_width2_bounded_multi_tile_sort_merge` path for `4097`, `65537`, and `131072` candidates.

## Next Pod Command

```bash
OPTIX_PREFIX=/root/vendor/optix-sdk bash scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh
```

If the pod uses a different OptiX SDK location, adjust `OPTIX_PREFIX` only.

## Claim Boundary

This note records local readiness only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, experimental public promotion, release action, or any new GPU performance claim.
