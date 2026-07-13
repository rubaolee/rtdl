# Call For Review: Goal4971 Exact LSI Device Columns Large Representative Result

Date: 2026-07-04

Please review:

```text
history/internal_docs/goal4971_exact_lsi_device_columns_large_representative_result_2026-07-04.md
```

Artifacts:

```text
history/internal_docs/goal4971_exact_lsi_device_columns_large_representative_artifacts_2026-07-04/
```

## Requested Verdict

One of:

- `approve_goal4971_exact_lsi_large_input_speedup_confirmed_but_root_lsi_gap_remains`
- `approve_with_required_amendments`
- `block_goal4971_due_to_measurement_or_claim_boundary_error`

## Review Questions

1. Did the POD environment repair stay correctly scoped as an environment fix,
   not a product/performance claim?
2. Is the OptiX header change to 7.7 / ABI 84 a valid repair for the POD's
   driver 550.127.05 ABI mismatch?
3. Is the Numba fix (`numba==0.61.2` plus CUDA 12.4 NVVM wheel) correctly
   described as an environment compatibility fix?
4. Do the correctness gates match Goal4970 on the large representative input:
   `lsi_row_count=428322`, both xsect counts `428322`, vertex positives
   `812721/4527305`, and device sort validation true?
5. Is the fresh-route comparison valid:
   `7.851479s` normal fresh vs `5.903873s` exact LSI device columns?
6. Is the LSI-stage comparison valid:
   `4.313502s` normal public rows vs `2.749540s` exact pair-id device columns?
7. Does the report correctly treat prepared replay (`2.636492s`) as diagnostic
   only, not fresh overlay performance?
8. Does the report avoid overclaiming: no public high-performance claim, no text
   byte-equality claim for the binary route, no broad Section 5.7 claim?
9. Is the conclusion right that exact LSI device columns are a useful large-input
   improvement, but do not solve the root LSI compute/traversal bottleneck?
10. Is the proposed next target correct: exact planar-map LSI producer
    computation/predicate/traversal, not another row-residency wrapper?

## Context For Reviewer

Goal4964 previously showed the exact pair-id device-column route was correct but
slower on the public sample:

```text
host exact pair-id rows:       0.893045s
exact pair-id device columns:  0.987424s
```

Goal4970 then established the large top4 County x Zipcode representative input
and the normal fresh binary route.

Goal4971 asks whether the existing exact LSI device-column route becomes useful
at that larger scale. The answer appears to be yes, but only as a bounded
large-input improvement:

```text
normal fresh writer-free binary:       7.851479s
exact LSI device-column fresh binary:  5.903873s
speedup:                               1.33x
```

The remaining LSI production cost is still `2.749540s`, so the root performance
problem remains inside exact planar-map LSI production.
