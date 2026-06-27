# Phoenix V3 Hausdorff Threshold Runner POD A/B

Status: `hausdorff_threshold_runner_m5_collected_not_release`

This focused packet is not release authorization and not an all-app rerun.

## Configuration

- Points per side: `1048576`
- Threshold: `0.4`
- Repeat/warmup: `5` / `1`

## Checks

- Failed checks: `['runner_regressed_vs_legacy_phase_total', 'runner_regressed_vs_legacy_wrapper_wall']`
- Runner vs legacy phase-total speedup: `0.9754875667505253`
- Runner vs legacy wrapper-wall speedup: `0.9776448018048591`
- Runner vs Embree phase-total speedup: `1.2113392724078669`

## Non-Authorization

Release, public speedup wording, broad V3-over-V2 wording, all-app rerun, whole-Hausdorff claims, true zero-copy claims, and V4 external-buffer claims remain false.
