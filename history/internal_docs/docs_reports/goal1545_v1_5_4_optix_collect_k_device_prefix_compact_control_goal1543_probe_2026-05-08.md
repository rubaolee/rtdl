# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `2a2000c30875b9221f607eda280f6c47bae9987c`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.153340`, sort_sync_ms=`0.028384`, merge_sync_ms=`0.007756`, metadata_ms=`0.013686`, sort_launches=`1`, merge_launches=`6`, carry_copies=`1`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.448761`, sort_sync_ms=`0.036118`, merge_sync_ms=`0.035779`, metadata_ms=`0.014087`, sort_launches=`1`, merge_launches=`18`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.491491`, sort_sync_ms=`0.054653`, merge_sync_ms=`0.050094`, metadata_ms=`0.014187`, sort_launches=`1`, merge_launches=`18`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
