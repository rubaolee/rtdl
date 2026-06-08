# Handoff: Claude Review Goal3872-3874 Prepared-Session Chain

You are a fresh Claude reviewer. Please perform a read-only review of the
Goal3872-Goal3874 prepared-session amortization/residency chain in the RTDL
workspace.

## Context

The user wants RTDL to keep improving benchmark-app performance while remaining
an app-agnostic language/runtime. Recent work found that several current
scene-heavy benchmark rows are dominated by cold preparation rather than hot
query execution, then added an explicit prepared-session residency contract and
current profile registry.

## Files To Inspect

- `scripts/goal3872_prepared_session_amortization_probe.py`
- `docs/reports/goal3872_prepared_session_amortization_2026-06-08.md`
- `docs/reports/goal3872_prepared_session_amortization_a5000/summary.json`
- `src/rtdsl/prepared_session_residency.py`
- `docs/reports/goal3873_prepared_session_residency_contract_2026-06-08.md`
- `tests/goal3873_prepared_session_residency_contract_test.py`
- `src/rtdsl/current_prepared_session_residency_profiles.py`
- `docs/reports/goal3874_current_prepared_session_residency_profiles_2026-06-08.md`
- `tests/goal3874_current_prepared_session_residency_profiles_test.py`
- `src/rtdsl/__init__.py`
- `docs/research/future_version_to_do_list.md`

## Validation To Run

If available in your environment, run:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal3874_current_prepared_session_residency_profiles_test tests.goal3873_prepared_session_residency_contract_test tests.goal3872_prepared_session_amortization_test tests.goal3828_current_benchmark_scale_profile_registry_test
```

## Review Questions

1. Does Goal3872 honestly show cold prepare vs hot query dominance without
   converting that into public speedup, release, or true-zero-copy claims?
2. Does `prepared_session_residency.py` stay app-agnostic and reject
   app-shaped primitive names while exposing useful explicit cache-key,
   lifetime, invalidation, and timing contracts?
3. Does `current_prepared_session_residency_profiles.py` correctly connect the
   Goal3872 rows to Goal3873 contract metadata without pretending the profiles
   are an implemented hidden cache or a release packet?
4. Are the false claim-boundary flags comprehensive and machine-checkable?
5. What work remains before this could become user-facing runtime ergonomics
   rather than internal metadata/profile evidence?

## Required Output

Write your review to:

`docs/reviews/goal3875_claude_review_goal3872_3874_prepared_session_chain_2026-06-08.md`

Use a verdict of one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please lead with findings, include file-level evidence, and explicitly state
that this review does not authorize release action, public speedup wording,
broad RT-core wording, true-zero-copy wording, automatic partner/backend
selection, or app-specific native-engine logic.
