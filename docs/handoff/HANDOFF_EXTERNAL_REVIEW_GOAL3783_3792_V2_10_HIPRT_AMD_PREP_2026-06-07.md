# External Review Handoff: Goals3783-3792 v2.10 HIPRT/AMD Prep

## Request

Please review the Goal3783-3792 chain and write a formal external review to:

- Claude path, when Claude is available:
  `docs/reviews/goal3793_claude_review_goal3783_3792_v2_10_hiprt_amd_prep_2026-06-07.md`
- Gemini path, if Gemini is used instead or alongside Claude:
  `docs/reviews/goal3793_gemini_review_goal3783_3792_v2_10_hiprt_amd_prep_2026-06-07.md`

Existing Gemini review:
`docs/reviews/goal3793_gemini_review_goal3783_3792_v2_10_hiprt_amd_prep_2026-06-07.md`

Claude should independently verify the source files and artifacts rather than
rubber-stamping the Gemini review.

Allowed verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`,
or `reject`.

## Scope

Review these current reports, artifacts, scripts, and tests:

- `docs/reports/goal3783_v2_10_hiprt_parity_closeout_packet_2026-06-07.md`
- `docs/reports/goal3783_v2_10_hiprt_parity_closeout_a5000.json`
- `docs/reports/goal3784_amd_hiprt_functional_validation_runbook_2026-06-07.md`
- `docs/reports/goal3785_amd_hiprt_functional_pod_runner_2026-06-07.md`
- `docs/reports/goal3785_non_amd_hiprt_functional_runner_control.json`
- `docs/reports/goal3786_current_benchmark_adequacy_after_hiprt_closeout_2026-06-07.md`
- `docs/reports/goal3787_post_hiprt_closeout_regression_packet_2026-06-07.md`
- `docs/reports/goal3787_post_hiprt_closeout_regression_a5000.json`
- `docs/reports/goal3788_hausdorff_generic_alias_and_metadata_audit_2026-06-07.md`
- `docs/reports/goal3790_amd_hiprt_runner_prefix_discovery_2026-06-07.md`
- `docs/reports/goal3792_post_runner_discovery_regression_packet_2026-06-07.md`
- `docs/reports/goal3792_post_runner_discovery_regression_a5000.json`
- `src/rtdsl/v2_10_amd_hiprt_functional_validation.py`
- `scripts/goal3785_amd_hiprt_functional_pod_runner.py`
- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `tests/goal3784_amd_hiprt_functional_validation_runbook_test.py`
- `tests/goal3785_amd_hiprt_functional_pod_runner_test.py`
- `tests/goal3786_current_benchmark_adequacy_after_hiprt_closeout_test.py`
- `tests/goal3787_post_hiprt_closeout_regression_packet_test.py`
- `tests/goal3788_hausdorff_generic_alias_and_metadata_audit_test.py`
- `tests/goal3790_amd_hiprt_runner_prefix_discovery_test.py`
- `tests/goal3792_post_runner_discovery_regression_packet_test.py`

## What To Verify

1. Goal3783 correctly records NVIDIA CUDA/Orochi HIPRT parity closeout evidence
   without presenting it as AMD hardware evidence.
2. Goal3784 defines a fail-closed AMD functional validation gate requiring
   actual AMD hardware, all ten benchmark apps ready/pass, clean source, parity
   acceptance, and all claim flags false.
3. Goal3785's pod runner rejects non-AMD hardware and writes a bounded control
   artifact instead of silently treating NVIDIA HIPRT/Orochi as AMD evidence.
4. Goal3786 correctly refreshes benchmark adequacy: ten ready apps, zero
   Numba-reference gaps, zero AMD performance authorization, and no release
   authorization.
5. Goal3787's combined A5000 regression packet is internally consistent and
   does not overclaim beyond NVIDIA CUDA/Orochi HIPRT control evidence.
6. Goal3788 correctly closes the stale Hausdorff generic-adapter TODO and proves
   the generic alias plus executed-ops metadata are already repaired.
7. Goal3790 makes HIPRT SDK prefix discovery robust enough for future AMD pods:
   explicit overrides still work, version-suffixed SDK directories are
   auto-discovered, archive matches are ignored, the chosen prefix is recorded,
   and the non-AMD control path remains rejected.
8. Goal3792 records the current post-discovery A5000 control regression at
   commit `a7a10228`: 34 modules, 185 tests, scoped source clean, parity and
   adequacy accepted, and all claim-boundary flags false.
9. The chain preserves the app-agnostic engine boundary and avoids automatic
   partner-selection, true-zero-copy, broad RT-core, paper-reproduction, and
   public release claims.

## Known Boundaries

- There is no actual AMD GPU evidence yet.
- The A5000 pod evidence is implementation/control evidence only.
- The next hardware step remains the Goal3785 runner on an AMD pod, producing
  `docs/reports/goal3784_amd_hiprt_functional_pod_validation.json`.
- This handoff does not authorize v2.10 release or public performance wording.

## Suggested Test Command

On Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3784_amd_hiprt_functional_validation_runbook_test `
  tests.goal3785_amd_hiprt_functional_pod_runner_test `
  tests.goal3786_current_benchmark_adequacy_after_hiprt_closeout_test `
  tests.goal3787_post_hiprt_closeout_regression_packet_test `
  tests.goal3788_hausdorff_generic_alias_and_metadata_audit_test `
  tests.goal3790_amd_hiprt_runner_prefix_discovery_test `
  tests.goal3792_post_runner_discovery_regression_packet_test
```

On Linux:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3784_amd_hiprt_functional_validation_runbook_test \
  tests.goal3785_amd_hiprt_functional_pod_runner_test \
  tests.goal3786_current_benchmark_adequacy_after_hiprt_closeout_test \
  tests.goal3787_post_hiprt_closeout_regression_packet_test \
  tests.goal3788_hausdorff_generic_alias_and_metadata_audit_test \
  tests.goal3790_amd_hiprt_runner_prefix_discovery_test \
  tests.goal3792_post_runner_discovery_regression_packet_test
```
