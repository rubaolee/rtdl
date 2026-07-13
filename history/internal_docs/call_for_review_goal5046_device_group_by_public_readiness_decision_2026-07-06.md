# Call For Review - Goal5046 device_group_by Public-Readiness Decision

Date: 2026-07-06

Please review:

```text
history/internal_docs/goal5046_device_group_by_public_readiness_decision_2026-07-06.md
```

Code/test changes:

```text
tests/goal5046_device_group_by_public_readiness_decision_test.py
```

Requested verdict labels:

```text
approve_goal5046_keep_device_group_by_internal_until_device_resident_reduce
revise_goal5046_public_readiness_evidence
fail_goal5046_hidden_public_group_by_or_host_copy_overclaim
```

## Context

Goal5045 publicized `device_order_by`.  Goal5046 asks whether `device_group_by` should also become public in v2.14.4.

The proposed conclusion is:

```text
completed_internal_only_device_group_by_until_device_resident_reduce
```

## Review Questions

1. Is it correct that `device_group_by` must remain non-public in v2.14.4?
2. Does `columnar_partner.py` still document host `row_values` blockers for grouped count/sum native execution?
3. Do existing Numba segmented/grouped assets exist, but fall short of a complete public `device_group_by` contract?
4. Is it correct to treat Numba grouped assets as internal/partner continuation capabilities rather than a public grouped-reduce primitive?
5. Does the guard test correctly verify that `rt.device_group_by` is absent and absent from `rt.__all__`?
6. Does `device_order_by` correctly keep `device_group_by_public_claim_authorized=False`?
7. Does the report avoid implying that public grouped reduce is impossible, while requiring a future POD/device-residency proof before promotion?
8. Should Goal5046 close with:

```text
completed_internal_only_device_group_by_until_device_resident_reduce
```

## Non-Authorization Boundary

Approval of Goal5046 does not authorize:

- public `device_group_by`;
- public grouped-reduce speedup claims;
- true-zero-copy claims;
- hidden host `row_values` staging under a device-resident label;
- RayJoin carrier/output-chain semantics as core grouped reduce.
