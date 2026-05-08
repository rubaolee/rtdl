# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `3600b67343a93c08bda474c7d05e5115c6c9a77a`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.518460`, sort_sync_ms=`0.028851`, merge_sync_ms=`0.007471`, metadata_ms=`0.013791`, sort_launches=`1`, merge_launches=`6`, carry_copies=`1`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.918335`, sort_sync_ms=`0.053322`, merge_sync_ms=`0.044934`, metadata_ms=`0.013880`, sort_launches=`1`, merge_launches=`18`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.922655`, sort_sync_ms=`0.088593`, merge_sync_ms=`0.071061`, metadata_ms=`0.013821`, sort_launches=`1`, merge_launches=`18`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
