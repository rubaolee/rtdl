# Goal 1598: Post-Pod Collect-K Consolidation

## Verdict

The threshold-4 OptiX `COLLECT_K_BOUNDED` gated-candidate micro-goal is closed for internal experimental purposes. No additional pod cycling is recommended for this micro-goal unless a new promotion/default-change review explicitly reopens it.

## Current State

- Latest pushed commit during this consolidation: `7ba4a0f3207c7ac8d034e4f1ac5f9bdbd44a617f`
- Feature flag: `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1`
- Gate policy: candidate carry-alias behavior activates only when predicted carry payload-copy reduction is at least `4`.
- Default behavior remains unchanged.
- Public speedup wording, stable primitive promotion, and release action remain unauthorized.

## Evidence Closed

- RTX 4090 threshold-4 validation:
  `docs/reports/goal1596_v1_5_4_optix_collect_k_threshold4_gate_rtx4090_validation_2026-05-09.md`
- RTX 3090 threshold-4 validation:
  `docs/reports/goal1597_v1_5_4_optix_collect_k_threshold4_gate_rtx3090_validation_2026-05-09.md`
- 3-AI consensus:
  `docs/reviews/goal1596_1597_threshold4_collect_k_3ai_consensus_2026-05-09.md`

## Local Validation

Windows focused tests:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal1593_v1_5_4_optix_collect_k_gated_candidate_test `
  tests.goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_test `
  tests.goal1506_v1_5_4_optix_collect_k_stage_profile_plan_test `
  tests.goal1590_v1_5_4_optix_cuda_toolchain_diagnostics_test
```

Result:

- `Ran 26 tests`
- `OK`

Linux local validation host:

- Host: `192.168.1.20`
- Checkout: `/home/lestat/work/rtdl_codex_local_check`
- Commit: `7ba4a0f3207c7ac8d034e4f1ac5f9bdbd44a617f`

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1593_v1_5_4_optix_collect_k_gated_candidate_test \
  tests.goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_test \
  tests.goal1506_v1_5_4_optix_collect_k_stage_profile_plan_test \
  tests.goal1590_v1_5_4_optix_cuda_toolchain_diagnostics_test
```

Result:

- `Ran 26 tests`
- `OK`

## Next Pod Queue

Do not start a pod for more threshold-4 collect-k cycling. The only pod-worthy follow-ups should be batched and started after local preparation:

1. Promotion/default-change review package, if the project explicitly decides to consider changing defaults. This requires a new proposal, explicit criteria, and external review before pod time.
2. A broader OptiX primitive or application-level validation batch that includes multiple pending goals, not only collect-k boundary retesting.
3. Environment-diversity validation only if a new CUDA/driver/toolchain class is being tested and the exact commands are prepared before starting the pod.

## Recommended Next Local Work

- Document the experimental gated-candidate mode in developer-facing collect-k notes without public speedup claims.
- Audit whether `COLLECT_K_BOUNDED` docs clearly distinguish experimental opt-in behavior from stable primitives.
- Prepare a broader v1.5.x closure checklist so future pod time validates multiple items in one run.

## Claim Boundary

This report closes an internal experimental validation slice only. It does not promote `COLLECT_K_BOUNDED`, does not change defaults, does not authorize public speedup wording, and does not publish a release.
