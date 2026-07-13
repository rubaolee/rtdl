# Call For Review - Goal5048 Non-RayJoin Numba PartnerContinuation Genericity

Date: 2026-07-06

Review target:

```text
history/internal_docs/goal5048_non_rayjoin_numba_partner_public_api_genericity_2026-07-06.md
tests/goal5048_non_rayjoin_numba_partner_public_api_genericity_test.py
src/rtdsl/numba_partner_api.py
```

## Requested Verdict Labels

```text
approve_goal5048_non_rayjoin_public_numba_partner_api_genericity_with_pod_smoke_debt
revise_goal5048_before_goal5049
fail_goal5048_genericity_not_proven_or_grouped_reduce_leaked_publicly
```

## Context

Goal5047 introduced the public `NumbaPartnerContinuation` API over
`DeviceColumnBuffer`.  Goal5048 checks that the API is genuinely generic enough
to proceed toward app migration: the proof shape is a ray/triangle hit stream,
not RayJoin overlay.

This goal also records the current export-hygiene boundary around old
grouped/segmented Numba symbols: those lower-level historical exports still
exist, but their operation values are not accepted by the new public
`NumbaPartnerContinuation` contract, and `device_group_by` remains non-public per
Goal5046.

## Review Questions

1. Does the test prove that the public Numba partner API can be planned over a
   non-RayJoin `DeviceColumnBuffer` shape (`ray_ids`, `primitive_ids`)?
2. Does the mocked runner assertion verify real binding behavior through
   `run_numba_partner_continuation(...)` rather than only checking metadata?
3. Does the test avoid RayJoin app structures, output chains, overlay carriers,
   or paper-reproduction formatting?
4. Is the legacy grouped/segmented export situation described correctly: old
   constants/functions may remain exported, but their operation values are not
   part of `NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS` and cannot route
   through the new public API?
5. Does `device_group_by` remain absent from `rt` and `rt.__all__`?
6. Is it correct that the optional live ray/triangle hit-stream CUDA smoke is
   skipped locally and remains POD debt?
7. Does the report avoid performance, true-zero-copy, public group-by, or RT
   traversal replacement claims?
8. Should Goal5049 be authorized next: migrate one RayJoin app path onto the
   public v2.14.4 surfaces without changing the performance headline?

## Non-Authorization

This review must not authorize:

```text
POD_CUDA_runtime_success
public_speedup_claim
true_zero_copy_claim
device_group_by_public_ready
RayJoin_specific_partner_API
replacement_of_RT_traversal
```
