# Handoff: Goal3253 Gemini Review Of Validated Device-Filtered RayJoin PIP Count

Date: 2026-06-03

Please perform a read-only independent review of Goal3253.

## Required Output

Write the review to:

`docs/reviews/goal3253_gemini_review_rayjoin_validated_device_filtered_pip_2026-06-03.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

## Context

Goal3251 added a generic prepared point/closed-shape
`count_device_filtered(...)` path for OptiX. Goal3252 measured that path
directly and showed it matches exact prepared count on the RayJoin PIP
same-slice row while avoiding candidate-row materialization, candidate download,
and host exact refinement.

Goal3253 wires that path into the RayJoin benchmark app and repeated same-slice
runner as an explicit opt-in mode:

```text
count_mode = device_filtered_validated
```

The normal exact `.count(...)` API remains unchanged. In the Goal3253 runner,
each PIP sample first validates exact prepared count and then times the
device-filtered count as the `prepared_query_ms` lane. The exact validation
timing is separately recorded as `validation_exact_query_ms`.

Clean pod evidence on NVIDIA A40, commit
`995394aeb21c0bbbb05b09a44709f4b20608d160`, reported `source_dirty: []`.

Current same-slice results:

- LSI: RayJoin `0.243203 ms`, RTDL `0.513267 ms`, gap `2.11x`,
  visible count matches `269`.
- PIP: RayJoin `0.200462 ms`, RTDL validated device-filtered count
  `0.808567 ms`, gap `4.03x`, RTDL count `1430`, RayJoin PIP count not printed.
- PIP exact-validation lane median: `0.992673 ms`.
- PIP native phase mode: `device_filtered_count`, with candidate write,
  candidate download, and exact refine all zero.

Goal3253 improves the PIP lane from Goal3248's `0.934755 ms` exact-count median
to `0.808567 ms` (`1.16x`), but RayJoin remains much faster.

## Files To Inspect

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `tests/goal2327_rayjoin_prepared_route_contract_test.py`
- `tests/goal3244_rayjoin_same_slice_repeated_count_runner_test.py`
- `tests/goal3253_rayjoin_validated_device_filtered_pip_current_best_test.py`
- `docs/reports/goal3253_rayjoin_validated_device_filtered_pip_current_best_2026-06-03.md`
- `docs/reports/goal3253_rayjoin_current_best_device_filtered_pip_pod_2026-06-03.json`
- `docs/reports/goal3253_rayjoin_current_best_device_filtered_pip_pod_2026-06-03.stdout`

## Questions To Answer

1. Is the fast PIP route explicit, opt-in, and fail-closed against exact
   prepared count?
2. Does it preserve the app-agnostic native-engine boundary?
3. Does the artifact support the stated performance conclusion:
   `1.16x` faster than Goal3248 PIP exact-count lane, but still `4.03x` slower
   than upstream RayJoin PIP on this same-slice comparison?
4. Are the claim boundaries preserved, with no release, broad RT-core speedup,
   true-zero-copy, `RTDL beats RayJoin`, or RayJoin paper-reproduction claim?
5. Is the next engineering diagnosis sound: the remaining PIP gap is now mostly
   generic closed-shape traversal/predicate cost, so further improvement needs a
   stronger generic closed-shape membership/count design rather than more
   host-side runner cleanup?

## Validation To Run If Practical

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3253_rayjoin_validated_device_filtered_pip_current_best_test `
  tests.goal2327_rayjoin_prepared_route_contract_test `
  tests.goal3244_rayjoin_same_slice_repeated_count_runner_test `
  tests.goal3251_closed_shape_device_filtered_count_test `
  tests.goal3252_closed_shape_device_filtered_count_pod_evidence_test
```

This is a review task only. Do not edit source files except for the requested
review file.
