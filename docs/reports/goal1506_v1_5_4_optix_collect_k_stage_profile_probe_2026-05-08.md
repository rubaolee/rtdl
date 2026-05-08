# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `0274ca32d3dd76d7dfc3f4214375db93b8838908`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`1.526860`, sort_sync_ms=`0.885174`, merge_sync_ms=`0.339783`, metadata_ms=`0.023290`, sort_launches=`2`, merge_launches=`1`, carry_copies=`0`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`79.377400`, sort_sync_ms=`11.748100`, merge_sync_ms=`67.207700`, metadata_ms=`0.067023`, sort_launches=`17`, merge_launches=`16`, carry_copies=`4`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`180.287000`, sort_sync_ms=`23.397100`, merge_sync_ms=`156.370000`, metadata_ms=`0.068723`, sort_launches=`32`, merge_launches=`31`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
