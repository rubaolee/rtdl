# Handoff: Gemini Review For Goal3660 RayJoin PIP Batch Executor Throughput

Date: 2026-06-06

Please perform an independent read-only review of Goal3660 and write the review to:

`docs/reviews/goal3661_gemini_review_goal3660_rayjoin_pip_batch_executor_throughput_2026-06-06.md`

## Files To Inspect

- `docs/reports/goal3660_rayjoin_pip_batch_executor_throughput_2026-06-06.md`
- `docs/reports/goal3660_rayjoin_pip_batch_executor_throughput_a5000/summary.json`
- `docs/reports/goal3657_v2_9_rayjoin_lsi_10s_integration_2026-06-06.md`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `tests/goal3660_rayjoin_pip_batch_executor_throughput_test.py`
- `tests/goal3657_v2_9_rayjoin_lsi_10s_integration_test.py`
- `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py`

## Questions To Answer

1. Does the implementation stay generic and app-agnostic: prepared point-probe columns, prepared closed-shape scene, reusable count executor, and stream policy, with no RayJoin/CDB native-engine logic?
2. Does the new runner path correctly mark the timing contract as `batched_repeated_request_throughput_not_one_shot_latency` and avoid confusing it with one-shot latency?
3. Does the clean A5000 artifact support the bounded finding: clean commit `def665eb`, `source_dirty: []`, exact count `1417`, batch size `100`, `auto` stream policy, RTDL `0.034225ms/request`, RTDL total `1027.254ms` for `30000` measured requests, RayJoin query timing `0.192133ms`, and ratio `0.178x`?
4. Does the report honestly preserve the Goal3658 one-shot/sequential reading: RTDL one-shot/sequential PIP improved but still trails RayJoin, while Goal3660 is only a batched repeated-request throughput win?
5. Are all claim boundaries intact: no release authorization, no public speedup wording, no broad RT-core claim, no whole-app RayJoin claim, no RayJoin paper-reproduction claim, no RTDL-beats-RayJoin one-shot claim, no true-zero-copy claim, and no app-specific native-engine logic?

## Required Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Expected boundary if accepted: Goal3660 is a valid internal v2.9 batched-throughput performance improvement, not release/public-speedup/paper-reproduction/one-shot-RayJoin-beating authorization.

## Validation Already Run By Main AI

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3660_rayjoin_pip_batch_executor_throughput_test tests.goal3657_v2_9_rayjoin_lsi_10s_integration_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
py -3 -m py_compile scripts\goal3244_rayjoin_same_slice_repeated_count_runner.py examples\v2_0\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py
```

Result: 33 tests OK; py_compile OK.
