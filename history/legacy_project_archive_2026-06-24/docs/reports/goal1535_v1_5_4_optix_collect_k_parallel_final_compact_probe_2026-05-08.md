# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `78d22ac360df0f14e97f2f06c62a2cd5e86db10f`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`4097`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`1.388150`, sort_sync_ms=`0.884514`, merge_sync_ms=`0.003740`, metadata_ms=`0.015231`, sort_launches=`2`, merge_launches=`3`, carry_copies=`0`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`30.245900`, sort_sync_ms=`13.573100`, merge_sync_ms=`15.934500`, metadata_ms=`0.065040`, sort_launches=`17`, merge_launches=`7`, carry_copies=`4`
- candidates=`131072`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`42.281200`, sort_sync_ms=`23.399000`, merge_sync_ms=`18.225900`, metadata_ms=`0.063463`, sort_launches=`32`, merge_launches=`7`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
