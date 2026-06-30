# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe

## Verdict

`goal1506_optix_collect_k_stage_profile_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `5b05743fbaea51cffa2882bb2a4e54fc870ca0cb`
- Native profile env: `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL`
- Accepted Goal1506 evidence: `True`
- Local fallback smoke only: `False`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, plus opt-in native host-side stage timing emitted by the same native call.

## Cases

- candidates=`7`, path=`row_width2_parallel_bitonic_sort`, total_ms=`0.046718`, sort_sync_ms=`0.006202`, merge_sync_ms=`0.000000`, metadata_ms=`0.013596`, sort_launches=`1`, merge_launches=`0`, carry_copies=`0`
- candidates=`8192`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.106983`, sort_sync_ms=`0.029125`, merge_sync_ms=`0.008507`, metadata_ms=`0.007665`, sort_launches=`1`, merge_launches=`7`, carry_copies=`0`
- candidates=`12289`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.136148`, sort_sync_ms=`0.029336`, merge_sync_ms=`0.014647`, metadata_ms=`0.007815`, sort_launches=`1`, merge_launches=`11`, carry_copies=`1`
- candidates=`16385`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.163610`, sort_sync_ms=`0.029406`, merge_sync_ms=`0.023936`, metadata_ms=`0.007995`, sort_launches=`1`, merge_launches=`15`, carry_copies=`3`
- candidates=`20481`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.165334`, sort_sync_ms=`0.029696`, merge_sync_ms=`0.024906`, metadata_ms=`0.007875`, sort_launches=`1`, merge_launches=`15`, carry_copies=`2`
- candidates=`24577`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.166576`, sort_sync_ms=`0.029896`, merge_sync_ms=`0.025088`, metadata_ms=`0.008176`, sort_launches=`1`, merge_launches=`15`, carry_copies=`2`
- candidates=`32769`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.196943`, sort_sync_ms=`0.030498`, merge_sync_ms=`0.041257`, metadata_ms=`0.007655`, sort_launches=`1`, merge_launches=`19`, carry_copies=`4`
- candidates=`45057`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.203676`, sort_sync_ms=`0.032452`, merge_sync_ms=`0.047049`, metadata_ms=`0.008075`, sort_launches=`1`, merge_launches=`19`, carry_copies=`2`
- candidates=`49153`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.223454`, sort_sync_ms=`0.032973`, merge_sync_ms=`0.046307`, metadata_ms=`0.008667`, sort_launches=`1`, merge_launches=`19`, carry_copies=`3`
- candidates=`65536`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.213454`, sort_sync_ms=`0.036169`, merge_sync_ms=`0.060834`, metadata_ms=`0.008046`, sort_launches=`1`, merge_launches=`19`, carry_copies=`0`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.264321`, sort_sync_ms=`0.036169`, merge_sync_ms=`0.082966`, metadata_ms=`0.007925`, sort_launches=`1`, merge_launches=`23`, carry_copies=`5`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
