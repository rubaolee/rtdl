# Goal3909 RayJoin LSI/Overlay Subprobe Phase Timing

Date: 2026-06-08

## Purpose

Goal3908 showed that the RayJoin representative wrapper spends most of its wall time inside the combined LSI/overlay subprobe, even though the RTDL/OptiX hot scalar-count routes themselves are already fast. Goal3909 adds per-case timing fields inside that subprobe so the next pod run can tell whether the remaining wall cost comes from dataset loading, Numba preparation, RTDL/OptiX preparation, hot repeats, or plain wrapper orchestration.

## Change

The script `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py` now records:

- `numba_load_case_sec`
- `numba_prepare_sec`
- `numba_hot_total_sec`
- `cupy_prepare_sec` and `cupy_hot_total_sec` when CuPy is enabled
- `rtdl_optix_prepare_total_sec`
- `rtdl_optix_hot_total_sec`
- `case_total_sec`

The top-level summary also reports `wrapper_phase_timing_available: true`.

## Boundary

This is instrumentation only. It does not change native RTDL, OptiX kernels, partner kernels, RayJoin semantics, dispatch policy, or public speedup claims. It prepares the next optimization decision by making the LSI/overlay wrapper cost measurable.

## Local Validation

The new unit test uses mocked backend calls to validate the JSON timing contract without requiring CUDA or OptiX locally:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3909_rayjoin_lsi_overlay_subprobe_phase_timing_test tests.goal3907_rayjoin_wrapper_phase_timing_test tests.goal3908_rayjoin_wrapper_phase_timing_a5000_test
```

Expected result: all tests pass.

## Next Pod Step

Run `scripts/goal3866_rayjoin_representative_scale_profile.py` again on the A5000 pod at a clean commit. The resulting payload should now include both the wrapper-level phase timing from Goal3907 and the nested per-case LSI/overlay timing from Goal3909. The next optimization should target whichever nested phase dominates.
