# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `d876074f0681125fbb1631bb080ac2cc838a391a`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.497069`, sort_sync_ms=`0.028881`, merge_sync_ms=`0.007400`, metadata_ms=`0.013290`, sort_launches=`1`, merge_launches=`6`, carry_copies=`1`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`1.350490`, sort_sync_ms=`0.053423`, merge_sync_ms=`0.031241`, metadata_ms=`0.014180`, sort_launches=`1`, merge_launches=`96`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`1.854850`, sort_sync_ms=`0.089113`, merge_sync_ms=`0.036822`, metadata_ms=`0.013690`, sort_launches=`1`, merge_launches=`189`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
