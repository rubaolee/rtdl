# Goal3912 RayJoin Representative Subprobe Timing Propagation

Date: 2026-06-08

## Purpose

Goal3909 added nested phase timings to the RayJoin LSI/overlay subprobe, and Goal3910 added shared loaded-case reuse inside that subprobe. The representative RayJoin profile, however, summarizes subprobe rows through `_case_summary(...)`. Goal3912 ensures the top-level representative payload carries the nested timing and loaded-case route metadata upward, so the next pod artifact can diagnose wrapper time from one file.

## Change

`scripts/goal3866_rayjoin_representative_scale_profile.py` now preserves these fields in each representative case summary when present:

- `rtdl_optix_execution_route`
- `loaded_case_reuse_enabled`
- `subprobe_wrapper_phase_timing_sec`

Old rows without nested timing remain valid and unchanged.

## Boundary

This is artifact propagation only. It does not change RayJoin semantics, native RTDL, partner code, dispatch policy, or claim authorization.

## Local Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3912_rayjoin_representative_subprobe_timing_propagation_test tests.goal3907_rayjoin_wrapper_phase_timing_test tests.goal3896_rayjoin_hot_path_accounting_test
```

Expected result: all tests pass.
