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

- candidates=`7`, path=`row_width2_parallel_bitonic_sort`, total_ms=`0.044675`, sort_sync_ms=`0.006122`, merge_sync_ms=`0.000000`, metadata_ms=`0.013475`, sort_launches=`1`, merge_launches=`0`, carry_copies=`0`
- candidates=`8192`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.107935`, sort_sync_ms=`0.029096`, merge_sync_ms=`0.008867`, metadata_ms=`0.007674`, sort_launches=`1`, merge_launches=`7`, carry_copies=`0`
- candidates=`12289`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.134846`, sort_sync_ms=`0.029375`, merge_sync_ms=`0.014789`, metadata_ms=`0.007645`, sort_launches=`1`, merge_launches=`11`, carry_copies=`1`
- candidates=`16385`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.171535`, sort_sync_ms=`0.029445`, merge_sync_ms=`0.023836`, metadata_ms=`0.007795`, sort_launches=`1`, merge_launches=`15`, carry_copies=`3`
- candidates=`20481`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.166134`, sort_sync_ms=`0.029636`, merge_sync_ms=`0.024615`, metadata_ms=`0.007684`, sort_launches=`1`, merge_launches=`15`, carry_copies=`2`
- candidates=`24577`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.168679`, sort_sync_ms=`0.029807`, merge_sync_ms=`0.025569`, metadata_ms=`0.007785`, sort_launches=`1`, merge_launches=`15`, carry_copies=`2`
- candidates=`32769`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.214637`, sort_sync_ms=`0.030428`, merge_sync_ms=`0.042300`, metadata_ms=`0.007594`, sort_launches=`1`, merge_launches=`19`, carry_copies=`4`
- candidates=`45057`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.207313`, sort_sync_ms=`0.032352`, merge_sync_ms=`0.046387`, metadata_ms=`0.007885`, sort_launches=`1`, merge_launches=`19`, carry_copies=`2`
- candidates=`49153`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.217663`, sort_sync_ms=`0.032772`, merge_sync_ms=`0.049944`, metadata_ms=`0.007675`, sort_launches=`1`, merge_launches=`19`, carry_copies=`3`
- candidates=`65536`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.211020`, sort_sync_ms=`0.036228`, merge_sync_ms=`0.061518`, metadata_ms=`0.007795`, sort_launches=`1`, merge_launches=`19`, carry_copies=`0`
- candidates=`65537`, path=`row_width2_bounded_multi_tile_sort_merge`, total_ms=`0.283337`, sort_sync_ms=`0.036208`, merge_sync_ms=`0.084349`, metadata_ms=`0.008116`, sort_launches=`1`, merge_launches=`23`, carry_copies=`5`

## Claim Boundary

Goal1506 records opt-in host-side stage timing for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
