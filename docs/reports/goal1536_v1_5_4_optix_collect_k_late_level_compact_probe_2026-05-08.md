# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `58e82b3dfaf0b5ac59d8397eb1b0d771eabf3c2e`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`1.645010`, sort_sync_ms=`0.884886`, merge_sync_ms=`0.268451`, metadata_ms=`0.024951`, sort_launches=`2`, merge_launches=`1`, carry_copies=`0`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`24.060700`, sort_sync_ms=`13.562300`, merge_sync_ms=`9.792510`, metadata_ms=`0.044751`, sort_launches=`17`, merge_launches=`9`, carry_copies=`4`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`32.583600`, sort_sync_ms=`23.395900`, merge_sync_ms=`8.518870`, metadata_ms=`0.044382`, sort_launches=`32`, merge_launches=`12`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
