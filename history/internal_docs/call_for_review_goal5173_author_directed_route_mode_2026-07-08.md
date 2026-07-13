# Call For Review: Goal5173 Author-Directed Route Mode

Date: 2026-07-08

Please strictly review Goal5173.

## Files Under Review

Result report:

```text
history/internal_docs/goal5173_author_directed_route_mode_result_2026-07-08.md
```

Primary implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
tests/goal5173_author_directed_route_mode_test.py
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/directed2d_asymmetric_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5173_author_directed_inline_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_goal5173_author_directed_exact_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/goal5126_xhd_directed_semantics_discriminating_gate_amendment_2026-07-08.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claim Being Reviewed

Goal5173 adds an explicit route direction policy:

```text
--direction-mode symmetric-diagnostic | directed-a-to-b
```

Allowed claim:

```text
Goal5173 aligns the production RTDL X-HD route with the author HDResult
contract proven by Goal5126. In directed-a-to-b mode, the route runs only the
author-comparison direction, leaves directed_b_to_a null, and still matches
author HDResult and exact directed reference where requested.
```

Forbidden claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
author-performance parity
author-vs-RTDL speedup ratio
claiming symmetric Hausdorff is reproduced by directed-only mode
claiming this changes RTDL core
```

## Critical Context

Goal5126 proved the author `HDResult` contract is directed input1-to-input2,
not symmetric max, using a discriminating fixture:

```text
directed_a_to_b = 0.5
directed_b_to_a = 9.0
symmetric = 9.0
author HDResult = 0.5
```

Therefore the previous production route was doing extra diagnostic work when it
ran `B -> A` while comparing only `A -> B` to author output.

The key review question is whether Goal5173 is legitimate author-contract
alignment, or whether it improperly drops required functionality.

## Evidence Summary

### Local

```text
py -m unittest tests.goal5173_author_directed_route_mode_test \
  tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test

Ran 12 tests OK
```

### POD

```text
python3 -m unittest \
  tests.goal5173_author_directed_route_mode_test \
  tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test

Ran 10 tests OK
```

Full public res4 author-directed inline matrix:

```text
artifact = xhd_seeded_res4full_goal5173_author_directed_inline_matrix_pod.json
matched = true
direction_mode = directed-a-to-b
directed_b_to_a = null
author HDResult = 0.1241602823138237
RTDL directed_a_to_b = 0.12416027787377293
author_abs_diff = 4.440050771492565e-09
route_sec_median = 0.01536349207162857
total_sec_median = 0.0567256361246109
ratio fields = null
```

Sample256 exact-and-author smoke:

```text
artifact = xhd_seeded_sample256_goal5173_author_directed_exact_smoke_pod.json
matched = true
rtdl_matches_exact_reference = true
direction_mode = directed-a-to-b
directed_b_to_a = null
route_sec_median = 0.0032787024974823
```

## Review Questions

1. Does Goal5126's directed-asymmetric evidence justify treating author
   `HDResult` as directed input1-to-input2 for X-HD app route production mode?
2. Is `directed-a-to-b` a legitimate author-contract mode, or does it drop a
   required symmetric Hausdorff computation?
3. Does the implementation preserve the old two-direction diagnostic behavior
   under `symmetric-diagnostic`?
4. Does directed mode correctly compare exact validation to
   `exact["directed_a_to_b"]`, not `exact["hausdorff"]`?
5. Does the matrix handle `directed_b_to_a = null` correctly without hiding or
   fabricating a symmetric result?
6. Do local/POD tests cover both directed-only and symmetric-diagnostic modes?
7. Does the full-res4 POD evidence support the bounded claim that author
   HDResult remains matched while the extra diagnostic direction is skipped?
8. Does the sample256 exact smoke adequately prove exact directed correctness
   for the new mode?
9. Does the report correctly avoid speedup/parity ratio, full paper
   reproduction, exact paper dataset, and RTDL-core-change claims?
10. Should Goal5173 close as
   `completed_author_directed_route_mode__implemented_review_pending`, or are
   amendments required?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
10. ...
```
