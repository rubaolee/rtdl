# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `ef5ce3750ca3329a6022213d0072a533ff95a6f2`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.111742`, sort_sync_ms=`0.028404`, merge_sync_ms=`0.008515`, metadata_ms=`0.007294`, sort_launches=`1`, merge_launches=`7`, carry_copies=`1`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.281974`, sort_sync_ms=`0.036319`, merge_sync_ms=`0.083689`, metadata_ms=`0.007885`, sort_launches=`1`, merge_launches=`23`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.306581`, sort_sync_ms=`0.054624`, merge_sync_ms=`0.120409`, metadata_ms=`0.007585`, sort_launches=`1`, merge_launches=`23`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
