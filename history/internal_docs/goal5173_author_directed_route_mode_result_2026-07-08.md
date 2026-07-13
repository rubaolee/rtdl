# Goal5173 Author-Directed Route Mode Result

Date: 2026-07-08

## Verdict

```text
completed_author_directed_route_mode__implemented_review_pending
```

Goal5173 aligns the X-HD production route with the author `HDResult` contract
proved by Goal5126: author output is directed input1-to-input2, not symmetric
Hausdorff max. The route can now run only the `A -> B` direction when requested,
while preserving the historical two-direction symmetric diagnostic mode.

This is implemented and POD-validated. It is not externally reviewed yet.

## Why This Matters

Before Goal5173, the route compared author `HDResult` to:

```text
directed_a_to_b
```

but still computed both:

```text
directed_a_to_b
directed_b_to_a
```

and reported a symmetric diagnostic:

```text
max(directed_a_to_b, directed_b_to_a)
```

Goal5126 already used a discriminating fixture where:

```text
directed_a_to_b = 0.5
directed_b_to_a = 9.0
symmetric = 9.0
author HDResult = 0.5
```

That proves the author comparison contract is directed input1-to-input2. The
extra `B -> A` direction is useful as a diagnostic, but it is not required for
author-equivalent production functionality.

## What Changed

### Route Gate

File:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
```

New CLI:

```text
--direction-mode symmetric-diagnostic | directed-a-to-b
```

Modes:

```text
symmetric-diagnostic
  Historical compatibility mode.
  Runs A->B and B->A.
  Reports symmetric diagnostic max.
  Exact validation compares against exact["hausdorff"].

directed-a-to-b
  Author-contract mode.
  Runs only A->B.
  Leaves directed_b_to_a = null.
  Leaves symmetric hausdorff diagnostic = null.
  Exact validation compares against exact["directed_a_to_b"].
```

### Performance Matrix

File:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
```

The matrix runner forwards `--direction-mode` and now handles
`directed_b_to_a = null` when the route is in author-directed mode.

## Generic/System Boundary

This is intentionally an app-level route policy, not a new RTDL core primitive.

It does not change:

- generic nearest helpers;
- native cell-MBR collector semantics;
- RTDL core contracts;
- X-HD paper claim boundaries.

It only prevents the X-HD app from paying for a diagnostic direction when the
requested author contract is directed input1-to-input2.

## Validation

### Local Tests

```text
py -m unittest tests.goal5173_author_directed_route_mode_test \
  tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test

Ran 12 tests OK
```

The new tests verify:

- `directed-a-to-b` runs only the author-contract direction;
- `directed_b_to_a` is `null` in directed mode;
- exact validation uses `directed_a_to_b`;
- symmetric diagnostic mode still preserves `B -> A`;
- route and matrix CLIs expose `--direction-mode`.

### POD Tests

```text
python3 -m unittest \
  tests.goal5173_author_directed_route_mode_test \
  tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test

Ran 10 tests OK
```

## POD Evidence

### Full Public Stanford Res4 Author-Directed Matrix

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5173_author_directed_inline_matrix_pod.json
```

Configuration:

```text
case = res4full
point_count_a = 5205
point_count_b = 7108
validation_mode = author-only
frontier_inline_nearest = true
frontier_row_order = native
direction_mode = directed-a-to-b
```

Key fields:

```text
matched = true
author HDResult = 0.1241602823138237
RTDL directed_a_to_b = 0.12416027787377293
author_abs_diff = 4.440050771492565e-09
directed_b_to_a = null
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
route_sec_median = 0.01536349207162857
total_sec_median = 0.0567256361246109
ratio fields = null
```

Compared with Goal5172's same-POD inline-nearest symmetric-diagnostic route:

```text
Goal5172 symmetric-diagnostic inline route median = 0.029158174991607666 s
Goal5173 author-directed inline route median      = 0.01536349207162857 s
```

Interpretation: almost all of the improvement comes from no longer running the
extra diagnostic `B -> A` route in production-style author comparison mode.

### Sample256 Exact-And-Author Smoke

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_goal5173_author_directed_exact_smoke_pod.json
```

Key fields:

```text
matched = true
rtdl_matches_exact_reference = true
direction_mode = directed-a-to-b
directed_b_to_a = null
author_abs_diff = 2.6291111787646315e-09
route_sec_median = 0.0032787024974823
exact_reference_sec_median = 0.10422661155462265
```

This smoke confirms the directed-only route still matches both author HDResult
and exact directed reference on a smaller representative fixture.

## What This Proves

- The app route can now run in author-equivalent directed mode.
- Directed mode avoids extra diagnostic work that the author contract does not
  require.
- Full public Stanford res4 still matches author HDResult in directed mode.
- A smaller exact-and-author smoke verifies exact directed correctness.

## What This Does Not Prove

- It does not prove full X-HD paper reproduction.
- It does not prove exact paper dataset reproduction.
- It does not authorize an author-vs-RTDL speedup or parity ratio.
- It does not align author `Running.AvgTime` with RTDL route time.
- It does not claim the symmetric diagnostic is unnecessary for all future
  analysis; it remains available behind `symmetric-diagnostic`.
- It does not change RTDL core or add an X-HD-specific system primitive.

## Updated Artifacts

Manifest updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

New result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5173_author_directed_inline_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_goal5173_author_directed_exact_smoke_pod.json
```

Review register updated:

```text
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

Status:

```text
Goal5173 implemented; review pending
```
