# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `f4e13c59502546b4fe968fba9a69371755539194`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`32769`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.216400`, sort_sync_ms=`0.030327`, merge_sync_ms=`0.042670`, metadata_ms=`0.008406`, sort_launches=`1`, merge_launches=`19`, carry_copies=`4`
- candidates=`49153`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.219806`, sort_sync_ms=`0.033123`, merge_sync_ms=`0.051458`, metadata_ms=`0.007885`, sort_launches=`1`, merge_launches=`19`, carry_copies=`3`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
