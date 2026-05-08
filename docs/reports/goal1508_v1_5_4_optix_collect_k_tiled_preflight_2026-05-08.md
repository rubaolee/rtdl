# Goal 1508: OptiX COLLECT_K_BOUNDED Tiled Preflight

## Verdict

`goal1508_optix_collect_k_tiled_preflight_recorded`

## Scope

- Device: `NVIDIA RTX 2000 Ada Generation`
- Git commit: `0274ca32d3dd76d7dfc3f4214375db93b8838908`
- Max opt-in shared memory per block: `101376` bytes
- Row_width=2 tile shared-memory requirement: `69632` bytes
- All requested counts are Goal1506 profile candidates: `True`

## Cases

- candidates=`4097`, expected_path=`row_width2_bounded_multi_tile_sort_merge`, predicted_profile_native_path=`row_width2_bounded_multi_tile_sort_merge`, shared_memory_sufficient=`True`, accepted_goal1506_profile_candidate=`True`
- candidates=`65537`, expected_path=`row_width2_bounded_multi_tile_sort_merge`, predicted_profile_native_path=`row_width2_bounded_multi_tile_sort_merge`, shared_memory_sufficient=`True`, accepted_goal1506_profile_candidate=`True`
- candidates=`131072`, expected_path=`row_width2_bounded_multi_tile_sort_merge`, predicted_profile_native_path=`row_width2_bounded_multi_tile_sort_merge`, shared_memory_sufficient=`True`, accepted_goal1506_profile_candidate=`True`

## Claim Boundary

Goal1508 is a CUDA shared-memory preflight for the experimental OptiX COLLECT_K_BOUNDED stage-profile path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
