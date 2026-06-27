# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `fe92cebe3c3da35692e079b4bb76a3a008a96c71`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`1.314240`, sort_sync_ms=`0.074492`, merge_sync_ms=`0.657455`, metadata_ms=`0.038582`, sort_launches=`3`, merge_launches=`2`, carry_copies=`1`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`12.166200`, sort_sync_ms=`0.906544`, merge_sync_ms=`10.493700`, metadata_ms=`0.057433`, sort_launches=`33`, merge_launches=`10`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`13.028600`, sort_sync_ms=`1.788600`, merge_sync_ms=`10.497500`, metadata_ms=`0.055032`, sort_launches=`64`, merge_launches=`13`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
