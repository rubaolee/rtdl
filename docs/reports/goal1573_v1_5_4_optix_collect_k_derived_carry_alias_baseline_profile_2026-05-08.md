# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `b0932bfcd5066c7725a4290dce9f89f3bb5b440f`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.283868`, sort_sync_ms=`0.036398`, merge_sync_ms=`0.082657`, metadata_ms=`0.007855`, sort_launches=`1`, merge_launches=`23`, carry_copies=`5`
- candidates=`98305`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.311099`, sort_sync_ms=`0.049364`, merge_sync_ms=`0.102333`, metadata_ms=`0.007955`, sort_launches=`1`, merge_launches=`23`, carry_copies=`4`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.311220`, sort_sync_ms=`0.054814`, merge_sync_ms=`0.120417`, metadata_ms=`0.007754`, sort_launches=`1`, merge_launches=`23`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
