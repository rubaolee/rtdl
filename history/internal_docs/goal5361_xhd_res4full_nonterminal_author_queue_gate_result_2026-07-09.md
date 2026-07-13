# Goal5361 - X-HD Res4Full Nonterminal Author Queue Gate

## Status

```text
implemented_review_pending
```

Exit label:

```text
res4full_nonterminal_queue_trace_matches__explicit_tune_radius_still_unmapped
```

## Purpose

Goal5360 proved that the `hd_exec`-compatible RTDL wrapper can expose an
author-like radius queue trace for the bounded terminal fixture. Goal5361 tests
the next harder case: a nonterminal author trace where `NumOutputPoints > 0`,
the generic `radius_growth_step` helper updates the radius, and a second
iteration converges.

The test case is the available res4full Stanford Dragon -> HappyBuddha author
POD run:

```text
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
```

## Key Implementation Changes

### 1. Generic partial frontier-nearest support

`src/rtdsl/partner_continuations.py` now adds an explicit default-off option:

```text
nearest_witness_from_cell_mbr_frontier_numpy_columns(..., allow_missing=False)
```

Default behavior remains fail-closed. With `allow_missing=True`, the helper
returns partial nearest columns plus metadata:

```text
missing_query_count
coverage_complete
allow_missing
```

This lets route orchestration preserve already computed frontier-nearest rows
and then use the existing generic pairwise fallback only for missing queries.
This is app-neutral and does not add X-HD semantics to RTDL core.

### 2. Route orchestration now uses partial + fallback correctly

`run_xhd_cell_mbr_frontier_route_gate.py` now calls the helper with
`allow_missing=True` and then invokes the existing
`_fill_missing_nearest_with_pairwise_fallback`.

This fixes a real coverage edge case exposed by the res4full author radius:
two source rows were not covered by frontier rows at the first radius. The
previous app-side coarse catch would have discarded partial frontier work and
fallen back to an expensive all-source pairwise path; that was not accepted.

### 3. Author-like CMax2 state model

The author `CMax2` field is not simply "max nearest distance over every active
source". Source inspection shows it is a global `cmax2_` state initialized from
the HD lower bound and updated only by confirmed / non-miss computation paths.

The app-owned queue simulator and cell-MBR queue route now use:

```text
author_like_global_cmax2_state_confirmed_points_only
```

For the res4full author trace this matches the nonterminal first iteration
where `CMax2 ~= Radius^2`, then the terminal second iteration where `CMax2`
becomes the final HDResult squared.

### 4. Wrapper trace metadata

`run_xhd_rtdl_hd_exec.py` now includes:

```text
RTDL.radius_trace_metadata.uses_radius_growth_step
```

This is evidence metadata only. It does not enable explicit author
`-tune_radius`.

## Evidence Artifact

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5361_res4full_nonterminal_author_queue_gate.py
```

Wrapper output:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5361_res4full_nonterminal_author_queue_wrapper_output.json
```

Summary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5361_res4full_nonterminal_author_queue_gate.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5361.res4full_nonterminal_author_queue_gate.v1
```

Status:

```text
res4full_nonterminal_author_like_queue_trace_matches
```

## Result

Author HDResult:

```text
0.1241602823138237
```

RTDL wrapper HDResult:

```text
0.12416027787377293
```

Absolute difference:

```text
4.440050771492565e-09
```

Required preprocessing:

```text
translate_each_input_to_min_bound
```

This is not optional for this case. The author JSON input MBR starts at zero,
and the local PLY files match that MBR only after per-input translation to the
minimum bound.

Author rows versus RTDL wrapper rows:

```text
Iteration 1:
  Radius          author=0.1218298003077507  rtdl=0.1218298003077507
  NumInputPoints  author=5205                rtdl=5205
  NumOutputPoints author=4                   rtdl=4
  CMax2           author=0.014842499978840351
                  rtdl=0.014842500243026413

Iteration 2:
  Radius          author=0.15791678428649902 rtdl=0.15791678945732696
  NumInputPoints  author=4                   rtdl=4
  NumOutputPoints author=0                   rtdl=0
  CMax2           author=0.015415775589644909
                  rtdl=0.015415774601692507
```

All row fields match within tolerance `1e-6`, and integer queue fields match
exactly.

The route metadata reports:

```text
uses_radius_growth_step = true
author_tune_radius_supported = false
has_nonterminal_iteration = true
```

## What This Proves

Goal5361 proves that the RTDL `hd_exec`-compatible wrapper can run an
app-owned, author-like radius queue diagnostic route on a nonterminal
same-source input and match the author JSON trace fields:

```text
Iteration / Radius / NumInputPoints / NumOutputPoints / CMax2 / HDResult
```

It also proves that the generic `allow_missing=True` frontier-nearest path can
be used safely by route orchestration while the public default remains
fail-closed.

## What This Does Not Prove

Goal5361 does not claim:

```text
author RT-core algorithm equivalence
explicit author -tune_radius support
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
exact paper dataset reproduction
```

The route is still labeled:

```text
cell-mbr-author-queue-diagnostic
```

Explicit author `-tune_radius` remains unmapped and must still fail closed.

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5361_res4full_nonterminal_author_queue_gate.py

py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5361_res4full_nonterminal_author_queue_gate.json

py -m unittest tests.goal5361_res4full_nonterminal_author_queue_gate_test tests.goal5360_hd_exec_author_queue_wrapper_gate_test tests.goal5359_cell_mbr_author_like_queue_route_test tests.goal5358_author_like_radius_queue_reference_test tests.goal5149_cell_mbr_frontier_nearest_continuation_test
```

Observed test result:

```text
Ran 15 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

Recommended next goal:

```text
decide_whether_explicit_author_tune_radius_can_be_supported_under_a_bounded_internal_route_label
```

That decision must remain narrow:

1. It may use the now-matching terminal and nonterminal queue evidence.
2. It must not claim author RT-core parity or Figure 8 reproduction.
3. It should keep explicit author options fail-closed unless the option surface
   is mapped with evidence and review.
