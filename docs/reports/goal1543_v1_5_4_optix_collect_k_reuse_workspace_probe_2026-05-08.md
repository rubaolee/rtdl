# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `ddf7d20e737799e6eab527d61afc412ce5fbab1f`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.138536`, sort_sync_ms=`0.028901`, merge_sync_ms=`0.007300`, metadata_ms=`0.012520`, sort_launches=`1`, merge_launches=`6`, carry_copies=`1`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.447407`, sort_sync_ms=`0.053512`, merge_sync_ms=`0.045182`, metadata_ms=`0.013610`, sort_launches=`1`, merge_launches=`18`, carry_copies=`5`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.545801`, sort_sync_ms=`0.089183`, merge_sync_ms=`0.071134`, metadata_ms=`0.012171`, sort_launches=`1`, merge_launches=`18`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
