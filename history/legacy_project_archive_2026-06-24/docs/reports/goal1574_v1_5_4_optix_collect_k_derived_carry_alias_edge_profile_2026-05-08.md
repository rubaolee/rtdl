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

- candidates=`3`, path=`row_width2_parallel_bitonic_sort`, total_ms=`0.045216`, sort_sync_ms=`0.004518`, merge_sync_ms=`0.000000`, metadata_ms=`0.013916`, sort_launches=`1`, merge_launches=`0`, carry_copies=`0`
- candidates=`5`, path=`row_width2_parallel_bitonic_sort`, total_ms=`0.044946`, sort_sync_ms=`0.005701`, merge_sync_ms=`0.000000`, metadata_ms=`0.013576`, sort_launches=`1`, merge_launches=`0`, carry_copies=`0`
- candidates=`7`, path=`row_width2_parallel_bitonic_sort`, total_ms=`0.045506`, sort_sync_ms=`0.006041`, merge_sync_ms=`0.000000`, metadata_ms=`0.013436`, sort_launches=`1`, merge_launches=`0`, carry_copies=`0`
- candidates=`32769`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.203125`, sort_sync_ms=`0.030548`, merge_sync_ms=`0.042520`, metadata_ms=`0.008356`, sort_launches=`1`, merge_launches=`19`, carry_copies=`4`
- candidates=`49153`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.212853`, sort_sync_ms=`0.032772`, merge_sync_ms=`0.049443`, metadata_ms=`0.007745`, sort_launches=`1`, merge_launches=`19`, carry_copies=`3`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
