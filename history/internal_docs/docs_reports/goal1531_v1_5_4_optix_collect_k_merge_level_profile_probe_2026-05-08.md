# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `fc24b7646d7526346b878b0394f3dd0802221d43`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`1.482120`, sort_sync_ms=`0.885395`, merge_sync_ms=`0.268480`, metadata_ms=`0.023441`, sort_launches=`2`, merge_launches=`1`, carry_copies=`0`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`34.268000`, sort_sync_ms=`13.571700`, merge_sync_ms=`20.176700`, metadata_ms=`0.066172`, sort_launches=`17`, merge_launches=`5`, carry_copies=`4`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`52.840800`, sort_sync_ms=`23.399000`, merge_sync_ms=`28.930200`, metadata_ms=`0.068783`, sort_launches=`32`, merge_launches=`5`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
