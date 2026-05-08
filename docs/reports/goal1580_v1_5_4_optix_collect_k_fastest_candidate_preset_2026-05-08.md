# Goal 1580: OptiX Collect-K Fastest Candidate Preset

## Verdict

`RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` is now an opt-in candidate preset for the measured positive v1.5.4 `COLLECT_K_BOUNDED` path. It does not change default behavior and does not promote `COLLECT_K_BOUNDED` to stable.

## What Changed

The preset enables the candidate bundle that was used for the positive derived carry alias measurements:

- `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT`
- `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT`
- `RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL`
- `RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE`
- `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT`
- `RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS`
- `RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS`
- `RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS`
- `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC`

The preset does not enable the rejected pointer-carry diagnostics:

- `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC`
- `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC`

## Runner Support

The Goal1579 next-architecture validation runner now accepts `--candidate-preset-smoke`. When present, it writes an extra targeted profile with only `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` enabled, so a pod run can verify the one-flag candidate path without replacing the existing baseline-vs-alias comparison.

## Validation

Local focused tests passed:

- `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_test tests.goal1579_v1_5_4_optix_collect_k_next_arch_runner_test tests.goal1573_v1_5_4_optix_collect_k_derived_carry_alias_diagnostic_test tests.goal1572_v1_5_4_optix_collect_k_carry_pointer_device_counts_diagnostic_test tests.goal1571_v1_5_4_optix_collect_k_carry_pointer_diagnostic_test tests.goal1570_v1_5_4_optix_collect_k_carry_alias_implementation_preflight_test`
- Result: `Ran 26 tests`, `OK`.

NVIDIA pod smoke passed on `NVIDIA RTX 4000 Ada Generation`:

- Static tests: `Ran 9 tests`, `OK`.
- Native build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk` succeeded.
- Runner smoke: `scripts/goal1579_v1_5_4_optix_collect_k_next_arch_validation_runner.py --repeats 1 --skip-targeted --candidate-preset-smoke` completed with `goal1579_next_arch_validation_recorded`.
- Candidate preset JSON: `/tmp/goal1580_candidate_smoke2_candidate_preset.json`.
- Candidate preset outcome: `accepted_goal1506_evidence=True`, `all_parity_passed=True`, `all_profile_topologies_match_expected=True`.

## Claim Boundary

This preset is a validation convenience only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
