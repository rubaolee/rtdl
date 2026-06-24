# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `41ae7926f69fdf4bb9c2aa140fa2a583d2d666fc`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.130758`, sort_sync_ms=`0.028464`, merge_sync_ms=`0.008246`, metadata_ms=`0.013976`, sort_launches=`1`, merge_launches=`7`, carry_copies=`1`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.358179`, sort_sync_ms=`0.036298`, merge_sync_ms=`0.037652`, metadata_ms=`0.014277`, sort_launches=`1`, merge_launches=`23`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.406921`, sort_sync_ms=`0.054743`, merge_sync_ms=`0.051607`, metadata_ms=`0.014087`, sort_launches=`1`, merge_launches=`23`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
