# Handoff: Gemini Review For Goal3658 RayJoin PIP Tuned Device Predicate

Date: 2026-06-06

Please perform an independent read-only review of Goal3658 and write the review to:

`docs/reviews/goal3659_gemini_review_goal3658_rayjoin_pip_tuned_device_predicate_2026-06-06.md`

## Files To Inspect

- `docs/reports/goal3658_rayjoin_pip_tuned_device_predicate_2026-06-06.md`
- `docs/reports/goal3658_rayjoin_pip_tuned_device_predicate_a5000/summary.json`
- `docs/reports/goal3657_v2_9_rayjoin_lsi_10s_integration_2026-06-06.md`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `tests/goal3658_rayjoin_pip_tuned_device_predicate_test.py`
- `tests/goal3657_v2_9_rayjoin_lsi_10s_integration_test.py`
- `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py`

## Questions To Answer

1. Does the new `RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS` specialization remain generic and app-agnostic, with no RayJoin/CDB logic in the native OptiX implementation?
2. Does the runner correctly scope and record `--rtdl-pip-device-predicate-eps`, and does the measured route remain fail-closed by validating each sample against the exact prepared count?
3. Does the clean A5000 artifact support the stated bounded finding: exact count `1417`, clean commit `9c85c2a0`, empty dirty list, `0.283574ms` RTDL tuned median over `30000` internal repeats, faster than prior project-owned CuPy dense baseline `0.437917ms`, but still slower than RayJoin `query_exec` `0.191354ms`?
4. Are the claim boundaries intact: no release authorization, no public speedup wording, no broad RT-core claim, no whole-app RayJoin claim, no paper reproduction claim, no RTDL-beats-RayJoin claim, no true zero-copy claim, and no app-specific native-engine logic?
5. Are the Goal3657 integration text and tests updated honestly, so the current PIP position says RTDL/OptiX now beats the prior CuPy scalar-count row for this bounded public-CDB slice while still trailing RayJoin?

## Required Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Expected boundary if accepted: Goal3658 is a valid internal v2.9 performance improvement and positioning update, not release/public-speedup/paper-reproduction authorization.

## Validation Already Run By Main AI

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3658_rayjoin_pip_tuned_device_predicate_test tests.goal3657_v2_9_rayjoin_lsi_10s_integration_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test tests.goal3598_v2_9_rayjoin_performance_first_addendum_test
py -3 -m py_compile scripts\goal3244_rayjoin_same_slice_repeated_count_runner.py
```

Result: 33 tests OK; py_compile OK.
