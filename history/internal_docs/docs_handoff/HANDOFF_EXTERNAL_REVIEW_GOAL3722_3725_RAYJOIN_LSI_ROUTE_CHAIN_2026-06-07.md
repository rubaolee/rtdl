# External Review Handoff: Goals 3722-3725 RayJoin LSI Route Chain

Date: 2026-06-07

## Reviewer Task

Please perform a read-only external review of the Goal3722-3725 RayJoin LSI route chain on current `main`. This is an important performance/architecture result, so do not rubber-stamp it. Verify the code and artifacts directly.

Write the review to one of these exact paths, depending on reviewer:

- Claude: `docs/reviews/goal3726_claude_review_goal3722_3725_rayjoin_lsi_route_chain_2026-06-07.md`
- Gemini: `docs/reviews/goal3727_gemini_review_goal3722_3725_rayjoin_lsi_route_chain_2026-06-07.md`

Use one of these verdicts only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Context

Recent chain:

- Goal3719 proved Python/ctypes overhead is negligible for the same-source RayJoin LSI count path.
- Goal3723 proved a simple no-any-hit direct-intersection route was slower than the existing RTDL any-hit exact-count route.
- Goal3724 introduced a diagnostic generic grouped/ranged right-primitive exact count route.
- Goal3725 swept and validated the grouped/ranged policy.

Latest pushed commits:

- `aa1f6cfb` - Goal3725 validate RayJoin LSI grouped-range policy.
- `2a9ba4d9` - Goal3725 add default grouped-range validation.

## Files To Inspect

Implementation:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3722_rayjoin_lsi_direct_intersection_route_probe.py`
- `scripts/goal3724_rayjoin_lsi_grouped_range_route_probe.py`

Tests:

- `tests/goal3722_rayjoin_lsi_direct_intersection_route_probe_test.py`
- `tests/goal3723_rayjoin_lsi_direct_intersection_route_probe_test.py`
- `tests/goal3724_rayjoin_lsi_grouped_range_route_probe_test.py`
- `tests/goal3725_rayjoin_lsi_grouped_range_policy_sweep_test.py`

Reports and artifacts:

- `docs/reports/goal3723_rayjoin_lsi_direct_intersection_route_probe_2026-06-07.md`
- `docs/reports/goal3725_rayjoin_lsi_grouped_range_policy_sweep_2026-06-07.md`
- `docs/reports/goal3724_rayjoin_lsi_grouped_range_route_sweep_a5000/summary.json`
- `docs/reports/goal3724_rayjoin_lsi_grouped_range_route_confirm_a5000/summary.json`
- `docs/reports/goal3725_rayjoin_lsi_grouped_range_default_a5000/summary.json`

## Evidence Summary To Verify

Goal3725 default validation at committed `origin/main` (`aa1f6cfb`, artifact copied in `2a9ba4d9`) on NVIDIA RTX A5000 / driver 580.126.09:

- Dataset: RayJoin bundled Brazil county/soil LSI workload.
- Query orientation: soil edges as left/query rays; county edges as right/base segments.
- Correct count: 20,860 intersections.
- RayJoin query: 0.000897725 s.
- RTDL existing any-hit exact count: 0.001428726 s.
- RTDL grouped-range direct exact count with default policy: 0.000272803 s.
- Measured diagnostic ratios: 5.237x vs existing RTDL any-hit route, 3.291x vs RayJoin same-source LSI query contract.
- Default policy: `max_size=1`, `area_enlarge=1.5`.

## Key Questions

1. Is the native implementation app-agnostic, or did RayJoin/LSI/domain logic leak into the engine?
2. Is the "winning" default correctly described as identity-range exact predicate inside the OptiX custom intersection program, not aggressive grouping?
3. Do the artifacts support the stated counts and timing ratios?
4. Is it correct to keep all claim-boundary flags false, despite the strong single-contract timing?
5. Are there any correctness risks from evaluating the exact predicate inside the intersection program?
6. Does this close the earlier Goal3723 conclusion ("no-any-hit alone was not enough") in a coherent way, or are the conclusions contradictory?
7. What should be the next engineering target: make this route non-diagnostic for count/parity contracts, extend it to grouped count/Boolean outputs, or test additional RayJoin contracts/datasets first?

## Validation Command

Please run at least:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3722_rayjoin_lsi_direct_intersection_route_probe_test tests.goal3723_rayjoin_lsi_direct_intersection_route_probe_test tests.goal3724_rayjoin_lsi_grouped_range_route_probe_test tests.goal3725_rayjoin_lsi_grouped_range_policy_sweep_test
```

## Boundaries

This review must not authorize:

- Public "RTDL beats RayJoin" claims.
- RayJoin paper reproduction claims.
- Broad RT-core speedup claims.
- Release claims.
- True zero-copy claims.
- Whole-app RayJoin acceleration claims.

The narrow question is whether the Goal3722-3725 chain is a technically sound, app-agnostic, claim-bounded performance result for one same-source RayJoin LSI count contract.
