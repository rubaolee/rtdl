# Goal 1572: OptiX COLLECT_K_BOUNDED Carry Pointer Device-Counts Diagnostic

## Verdict

Do not promote `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC` to the production OptiX `COLLECT_K_BOUNDED` path.

The diagnostic preserves parity and is accepted measured Goal1506-style evidence, but it is slower than the same-session derived-descriptor baseline for the odd long case. It reduces carry-copy time, but the pointer descriptor traffic increases merge launch time enough to make total time worse.

## Scope

- Repository commit measured on pod: `128ec41e328ff9c9a18f890a7dd14602b9d5eec4` plus the uncommitted Goal1572 diagnostic patch.
- Pod: `root@157.157.221.29 -p 22942`, NVIDIA RTX 4000 Ada Generation, driver `550.127.05`.
- CUDA/OptiX: CUDA `12.8`, OptiX SDK at `/root/vendor/optix-sdk`.
- Library: `/root/rtdl_goal1545_pod/build/librtdl_optix.so`.
- Baseline env: `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1`, `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`, `RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1`, `RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1`, `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`, `RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1`, `RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1`, `RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1`.
- Diagnostic env: the baseline env plus `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC=1`.

## Results

| Case | Path | Accepted | Parity | Stage total ms | Merge launch ms | Merge sync ms | Carry copy ms | H2D fields | D2H fields |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 65537 | Baseline derived descriptors | Yes | Yes | 0.284950 | 0.081785 | 0.083701 | 0.037389 | 1 | 34 |
| 65537 | Device-count carry pointer diagnostic | Yes | Yes | 0.336458 | 0.148261 | 0.081975 | 0.018446 | 94 | 34 |
| 131072 | Baseline derived descriptors | Yes | Yes | 0.307693 | 0.089981 | 0.121340 | 0.000000 | 1 | 65 |
| 131072 | Device-count carry pointer diagnostic | Yes | Yes | 0.308364 | 0.090702 | 0.120547 | 0.000000 | 1 | 65 |

For `65537`, the diagnostic reduces carry-copy time by about `0.018943 ms`, but increases merge-launch time by about `0.066476 ms`. Net stage total worsens by about `0.051508 ms`.

For `131072`, there is no odd carry level, so the diagnostic is effectively neutral.

## Interpretation

The Goal1571 host-count pointer diagnostic was too expensive because it downloaded counts and uploaded pointer/count descriptors. Goal1572 removed the host count round trip by reading device level counts directly, and that did help the carry-copy substage. However, the odd carry level still leaves the fastest derived-descriptor layout and uploads three pointer descriptor arrays for each affected merge level.

This means the current long-case bottleneck is not simply the device-to-device carry row copy. The winning direction must avoid both:

- copying the odd carry row payload, and
- switching the merge level from derived descriptors to uploaded pointer descriptors.

## Next Direction

The next promising route is a derived-layout carry alias design that preserves the derived descriptor fast path while allowing the odd carry row to be referenced without a payload copy. The design must solve the layout invariant directly instead of escaping to pointer descriptors.

The current diagnostic should remain available only as an internal measurement flag. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, or release action.

## Artifacts

- `docs/reports/goal1572_v1_5_4_optix_collect_k_carry_pointer_device_counts_diagnostic_profile_2026-05-08.json`
- `docs/reports/goal1572_v1_5_4_optix_collect_k_carry_pointer_device_counts_diagnostic_profile_2026-05-08.md`
- `docs/reports/goal1572_v1_5_4_optix_collect_k_baseline_same_session_profile_2026-05-08.json`
- `docs/reports/goal1572_v1_5_4_optix_collect_k_baseline_same_session_profile_2026-05-08.md`
