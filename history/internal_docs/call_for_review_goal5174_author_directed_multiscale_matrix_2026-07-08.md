# Call For Review: Goal5174 Author-Directed Multiscale Matrix

Date: 2026-07-08

Please strictly review Goal5174.

## Files Under Review

Result report:

```text
history/internal_docs/goal5174_author_directed_multiscale_matrix_result_2026-07-08.md
```

Primary implementation context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
tests/goal5173_author_directed_route_mode_test.py
tests/goal5172_native_inline_nearest_frontier_test.py
tests/goal5155_xhd_production_validation_and_route_profile_test.py
tests/goal5154_xhd_seeded_performance_matrix_test.py
```

Evidence artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_goal5174_author_directed_multiscale_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claim Being Reviewed

Allowed claim:

```text
Goal5174 records a same-POD multiscale Level B profile for the current
author-directed, native inline-nearest RTDL route. Across sample256,
sample1024, sample2048, sample4096, and full public res4, the route matches
author HDResult, leaves directed_b_to_a null by design, and reports route
medians of about 3.07ms, 5.82ms, 6.35ms, 10.63ms, and 14.92ms respectively.
```

Forbidden claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
author-performance parity
author-vs-RTDL speedup ratio
denominator-aligned performance comparison
claiming RTDL implements the author's fused X-HD RT-core algorithm
claiming symmetric Hausdorff is reproduced in directed-a-to-b mode
```

## Critical Context

Goal5126 proved author `HDResult` is directed input1-to-input2. Goal5173 added
the explicit `directed-a-to-b` route mode. Goal5174 uses that mode across the
current representative scale ladder.

The result is intentionally a route profile, not a paper-performance ratio.
Author `Running.AvgTime`, author process wall time, RTDL route time, and RTDL
total time remain distinct phase boundaries.

## Evidence Summary

Artifact:

```text
xhd_seeded_goal5174_author_directed_multiscale_matrix_pod.json
```

All cases:

```text
backend = optix
validation_mode = author-only
frontier_inline_nearest = true
frontier_row_order = native
frontier_nearest_executor = numba_parallel
direction_mode = directed-a-to-b
directed_b_to_a = null
matched = true
ratios_authorized = false
```

Table:

```text
sample256   route 0.003070324659347534s   total 0.0055475011467933655s
sample1024  route 0.005820967257022858s   total 0.019024431705474854s
sample2048  route 0.006353408098220825s   total 0.022940821945667267s
sample4096  route 0.010627664625644684s   total 0.0365026593208313s
res4full    route 0.014921210706233978s   total 0.05398107320070267s
```

Abs diffs against author `HDResult`:

```text
sample256   2.6291111787646315e-09
sample1024  3.7198159136275777e-09
sample2048  5.041705483654901e-09
sample4096  6.270714683620504e-09
res4full    4.440050771492565e-09
```

## Review Questions

1. Does the matrix genuinely run the author-directed `A -> B` route only,
   with `directed_b_to_a = null` in every case?
2. Do all five cases match author `HDResult` within the existing tolerance
   discipline?
3. Are the route and total medians reported from the artifact without false
   precision claims or ratio claims?
4. Does the report maintain the distinction between author `Running.AvgTime`,
   author process wall, RTDL route time, and RTDL total time?
5. Is this correctly framed as Level B same-source representative evidence, not
   exact paper dataset reproduction?
6. Does the result avoid claiming symmetric Hausdorff in directed-only mode?
7. Does the work stay inside generic RTDL route primitives rather than adding
   X-HD-specific core behavior?
8. Does the multiscale profile provide useful current-regression evidence for
   the author-directed route?
9. Are there any hidden app-specific or denominator-mixing claims in the
   manifest/report?
10. Should Goal5174 close as
   `completed_author_directed_multiscale_matrix__implemented_review_pending`,
   or are amendments required?

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
