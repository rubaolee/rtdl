# Handoff: Gemini Review For Goal3975/3976 Helper Reproducibility Chain

Date: 2026-06-08

Please perform an independent read-only review of the Goal3975/3976 current
scale-profile pod setup chain.

## Commits

- `078cc92f` Goal3975 add current scale partner pod setup helper
- `4e7b6dab` Goal3976 validate fresh helper current scale run

## Files To Inspect

- `scripts/goal3975_current_scale_partner_pod_setup.sh`
- `docs/reports/goal3975_current_scale_partner_pod_setup_helper_2026-06-08.md`
- `tests/goal3975_current_scale_partner_pod_setup_helper_test.py`
- `docs/reports/goal3976_fresh_helper_current_scale_validation_2026-06-08.md`
- `docs/reports/goal3976_fresh_helper_current_scale_validation_2026-06-08/summary.json`
- `docs/reports/goal3976_fresh_helper_current_scale_validation_2026-06-08/helper.stdout.log`
- `docs/reports/goal3976_fresh_helper_current_scale_validation_2026-06-08/build_optix.stdout.log`
- `docs/reports/goal3976_fresh_helper_current_scale_validation_2026-06-08/run.stdout.log`
- `docs/reports/goal3976_fresh_helper_current_scale_validation_2026-06-08/outputs/`
- `tests/goal3976_fresh_helper_current_scale_validation_test.py`
- context: `docs/reviews/goal3973_gemini_review_goal3971_current_head_scale_profile_2026-06-08.md`

## Questions To Answer

1. Does Goal3975 correctly codify the driver-550 partner setup lesson from
   Goal3971/3974, including the CUDA 12.4 compiler-package pin for Numba and
   separate RTDL OptiX CUDA prefix?
2. Does Goal3976 provide valid fresh-checkout evidence that the helper can
   reproduce the current ten-app scale-profile packet on the RTX 4000 Ada pod?
3. Are the Goal3975/3976 tests sufficient to guard the helper, artifact, source
   commit, clean checkout, partner smoke, and claim-boundary discipline?
4. Does the chain avoid overclaiming release, public speedup, whole-app
   acceleration, broad RT-core acceleration, true zero-copy, AMD performance,
   package-install readiness, paper reproduction, automatic partner/backend
   selection, or app-specific native-engine logic?
5. What, if anything, is still required before this setup can be treated as a
   reusable pod runbook for future current-scale packets?

## Required Output

Use the verdict vocabulary `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Write the review to:

`docs/reviews/goal3977_gemini_review_goal3975_3976_helper_repro_chain_2026-06-08.md`

Please keep this read-only except for writing the requested review file.
