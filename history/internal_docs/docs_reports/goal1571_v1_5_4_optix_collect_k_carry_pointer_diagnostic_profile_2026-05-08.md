# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `9f3ad77c64db192faa34718f8a824f584bdbd359`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `False`
- Local fallback smoke only: `True`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.469720`, sort_sync_ms=`0.036349`, merge_sync_ms=`0.038906`, metadata_ms=`0.008035`, sort_launches=`1`, merge_launches=`23`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.310408`, sort_sync_ms=`0.054734`, merge_sync_ms=`0.119977`, metadata_ms=`0.008105`, sort_launches=`1`, merge_launches=`23`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
