# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `76fe82b35e32b9162d360c880db92b3e2ed7a4e3`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`12289`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.137962`, sort_sync_ms=`0.029336`, merge_sync_ms=`0.014877`, metadata_ms=`0.007765`, sort_launches=`1`, merge_launches=`11`, carry_copies=`1`
- candidates=`20481`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.229374`, sort_sync_ms=`0.029796`, merge_sync_ms=`0.019447`, metadata_ms=`0.010750`, sort_launches=`1`, merge_launches=`15`, carry_copies=`2`
- candidates=`28673`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.164231`, sort_sync_ms=`0.030548`, merge_sync_ms=`0.028262`, metadata_ms=`0.007845`, sort_launches=`1`, merge_launches=`15`, carry_copies=`1`
- candidates=`45057`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.209907`, sort_sync_ms=`0.032641`, merge_sync_ms=`0.047050`, metadata_ms=`0.007704`, sort_launches=`1`, merge_launches=`19`, carry_copies=`2`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
