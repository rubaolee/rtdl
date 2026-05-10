# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX A4500`
- Git commit: `ad57f8193c5452ff0036a4c853860ea656d44a3d`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`262144`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.680568`, sort_sync_ms=`0.105803`, merge_sync_ms=`0.322667`, metadata_ms=`0.011250`, sort_launches=`1`, merge_launches=`27`, carry_copies=`0`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
