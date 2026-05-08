# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `5111c462f62b7f381c784d58754b09c179983fb2`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`32769`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.200320`, sort_sync_ms=`0.030358`, merge_sync_ms=`0.042480`, metadata_ms=`0.007654`, sort_launches=`1`, merge_launches=`19`, carry_copies=`4`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.265173`, sort_sync_ms=`0.036399`, merge_sync_ms=`0.084020`, metadata_ms=`0.007785`, sort_launches=`1`, merge_launches=`23`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.310318`, sort_sync_ms=`0.054924`, merge_sync_ms=`0.122471`, metadata_ms=`0.007604`, sort_launches=`1`, merge_launches=`23`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
