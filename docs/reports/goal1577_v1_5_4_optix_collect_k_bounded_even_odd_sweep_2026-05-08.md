# Goal 1577: OptiX COLLECT_K_BOUNDED Bounded Even/Odd Sweep

## Verdict

`RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1` passed a bounded even/odd sweep on the RTX 4000 Ada pod.

The sweep strengthens the promotion case: parity remained accepted across bitonic, no-carry, blocked-carry, mixed blocked/safe carry, and safe-carry merge topologies. Most carry cases improved; no-carry cases were neutral within small timing noise. A targeted repeat-9 rerun resolved the initially suspicious cases as non-regressing.

This still does not authorize public speedup wording or release action.

## Scope

- Repository commit measured on pod: `5b05743fbaea51cffa2882bb2a4e54fc870ca0cb`.
- Pod: `root@157.157.221.29 -p 22942`, NVIDIA RTX 4000 Ada Generation, driver `550.127.05`.
- CUDA/OptiX: CUDA `12.8`, OptiX SDK at `/root/vendor/optix-sdk`.
- Baseline env: Goal1506 OptiX collect-k flags without derived carry alias.
- Alias env: baseline env plus `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1`.

## Sweep Results

| Case | Tile Count | Baseline ms | Alias ms | Delta ms | Baseline payload copies | Alias payload copies | Parity |
|---:|---:|---:|---:|---:|---:|---:|---|
| 7 | 0 | 0.044675 | 0.046718 | 0.002043 | 0 | 0 | Pass |
| 8192 | 0 | 0.107935 | 0.106983 | -0.000952 | 0 | 0 | Pass |
| 12289 | 7 | 0.134846 | 0.136148 | 0.001302 | 1 | 1 | Pass |
| 16385 | 9 | 0.171535 | 0.163610 | -0.007925 | 3 | 0 | Pass |
| 20481 | 11 | 0.166134 | 0.165334 | -0.000800 | 2 | 1 | Pass |
| 24577 | 13 | 0.168679 | 0.166576 | -0.002103 | 2 | 1 | Pass |
| 32769 | 17 | 0.214637 | 0.196943 | -0.017694 | 4 | 0 | Pass |
| 45057 | 23 | 0.207313 | 0.203676 | -0.003637 | 2 | 1 | Pass |
| 49153 | 25 | 0.217663 | 0.223454 | 0.005791 | 3 | 1 | Pass |
| 65536 | 32 | 0.211020 | 0.213454 | 0.002434 | 0 | 0 | Pass |
| 65537 | 33 | 0.283337 | 0.264321 | -0.019016 | 5 | 0 | Pass |

All sweep cases produced accepted Goal1506-style evidence with profile topology matching expected.

## Targeted Rerun

The first sweep showed small positive deltas for `49153` and `65536`, so these were rerun with `9` repeats together with `65537`.

| Case | Baseline ms | Alias ms | Delta ms | Baseline payload copies | Alias payload copies |
|---:|---:|---:|---:|---:|---:|
| 49153 | 0.218344 | 0.211631 | -0.006713 | 3 | 1 |
| 65536 | 0.212703 | 0.211039 | -0.001664 | 0 | 0 |
| 65537 | 0.287245 | 0.277356 | -0.009889 | 5 | 0 |

The targeted rerun remained accepted and parity-clean, and all three cases were non-regressing.

## Interpretation

The diagnostic is now supported by:

- positive long carry cases,
- blocked-alias topology validation,
- topology/payload-copy accounting,
- a bounded even/odd sweep,
- one external Claude review.

The evidence supports keeping the derived carry alias as the strongest current candidate for production promotion, but the remaining promotion blocker is still hardware diversity: the current evidence is from one RTX 4000 Ada pod.

## Next Gate

Before making the alias default, run the same focused suite on at least one additional NVIDIA architecture if a pod becomes available. If that passes, the next step can be a small production-promotion patch that removes the diagnostic gate or folds it into the default fastest OptiX collect-k preset.

No public speedup claim, stable primitive promotion, or release action is authorized by this report.

## Artifacts

- `docs/reports/goal1577_v1_5_4_optix_collect_k_bounded_even_odd_sweep_baseline_profile_2026-05-08.json`
- `docs/reports/goal1577_v1_5_4_optix_collect_k_bounded_even_odd_sweep_baseline_profile_2026-05-08.md`
- `docs/reports/goal1577_v1_5_4_optix_collect_k_bounded_even_odd_sweep_alias_profile_2026-05-08.json`
- `docs/reports/goal1577_v1_5_4_optix_collect_k_bounded_even_odd_sweep_alias_profile_2026-05-08.md`
- `docs/reports/goal1577_v1_5_4_optix_collect_k_targeted_rerun_baseline_profile_2026-05-08.json`
- `docs/reports/goal1577_v1_5_4_optix_collect_k_targeted_rerun_alias_profile_2026-05-08.json`
