# Goal 1573: OptiX COLLECT_K_BOUNDED Derived Carry Alias Diagnostic

## Verdict

`RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1` is a positive diagnostic result.

It preserves accepted parity and keeps the derived descriptor fast path while reducing odd-carry row-copy cost. Unlike the pointer-descriptor diagnostics from Goal1571 and Goal1572, it does not add per-level pointer descriptor uploads.

This is not yet a public speedup claim or release action. It is a measured internal candidate for production promotion after review and broader validation.

## Scope

- Repository commit measured on pod: `b0932bfcd5066c7725a4290dce9f89f3bb5b440f`.
- Pod: `root@157.157.221.29 -p 22942`, NVIDIA RTX 4000 Ada Generation, driver `550.127.05`.
- CUDA/OptiX: CUDA `12.8`, OptiX SDK at `/root/vendor/optix-sdk`.
- Library: `/root/rtdl_goal1545_pod/build/librtdl_optix.so`.
- Baseline env: `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1`, `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`, `RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1`, `RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1`, `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`, `RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1`, `RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1`, `RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1`.
- Diagnostic env: baseline env plus `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1`.

## Results

| Case | Path | Accepted | Parity | Stage total ms | Merge launch ms | Merge sync ms | Carry copy ms | H2D fields | D2H fields |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 65537 | Baseline derived descriptors | Yes | Yes | 0.283868 | 0.084640 | 0.082657 | 0.036309 | 1 | 34 |
| 65537 | Derived carry alias diagnostic | Yes | Yes | 0.269772 | 0.081665 | 0.083326 | 0.018225 | 1 | 34 |
| 98305 | Baseline derived descriptors | Yes | Yes | 0.311099 | 0.086795 | 0.102333 | 0.028826 | 1 | 50 |
| 98305 | Derived carry alias diagnostic | Yes | Yes | 0.303535 | 0.088007 | 0.102073 | 0.018175 | 1 | 50 |
| 131072 | Baseline derived descriptors | Yes | Yes | 0.311220 | 0.091204 | 0.120417 | 0.000000 | 1 | 65 |
| 131072 | Derived carry alias diagnostic | Yes | Yes | 0.310168 | 0.090081 | 0.121850 | 0.000000 | 1 | 65 |

For `65537`, stage total improves by about `0.014096 ms`, and carry-copy time improves by about `0.018084 ms`.

For `98305`, stage total improves by about `0.007564 ms`, and carry-copy time improves by about `0.010651 ms`. This case exercises the topology guard where a carry alias must eventually be copied back before it would become a derived-paired segment.

For `131072`, there is no odd carry level, so the diagnostic is effectively neutral.

## Design

The derived descriptor path assumes paired segments are contiguous under `current_base + segment_index * segment_capacity * 2`. Prior pointer diagnostics avoided copying the odd carry by switching the whole level to pointer descriptors, but that lost the fastest path and added descriptor upload overhead.

Goal1573 keeps the derived descriptor path for all paired segments. For an odd carry segment, the code aliases `current_rows.back()` only when the next topology is safe:

- the next segment count is odd, so the aliased carry remains unpaired in the following derived merge level, or
- the next segment count is `2`, so the final merge uses explicit row pointers rather than derived offsets.

If the next topology would pair the carried segment under derived descriptors, the code falls back to the normal device-to-device row copy and restores the derived layout.

## Claim Boundary

This diagnostic does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.

The result does support one internal engineering conclusion: carry-copy elimination can help only when it preserves the derived descriptor fast path and avoids pointer descriptor uploads.

## Artifacts

- `docs/reports/goal1573_v1_5_4_optix_collect_k_derived_carry_alias_baseline_profile_2026-05-08.json`
- `docs/reports/goal1573_v1_5_4_optix_collect_k_derived_carry_alias_baseline_profile_2026-05-08.md`
- `docs/reports/goal1573_v1_5_4_optix_collect_k_derived_carry_alias_diagnostic_profile_2026-05-08.json`
- `docs/reports/goal1573_v1_5_4_optix_collect_k_derived_carry_alias_diagnostic_profile_2026-05-08.md`
