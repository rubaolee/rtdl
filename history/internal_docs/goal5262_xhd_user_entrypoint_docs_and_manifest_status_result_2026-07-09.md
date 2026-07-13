# Goal5262 - X-HD User Entrypoint Docs And Manifest Status Result

Date: 2026-07-09

## Objective

Promote the current X-HD RTDL `hd_exec`-compatible user entrypoint evidence into
the paper app documentation and manifest, without overclaiming full paper
reproduction or performance parity.

This follows Goal5260 and Goal5261:

```text
Goal5260: 400 / 400 public ModelNet40 pair identities matched author rerun HDResult through the hd_exec-compatible batch bridge.
Goal5261: denominator-separated all-400 performance matrix generated for that user entrypoint.
```

## Files Updated

```text
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
tests/goal5110_xhd_paper_app_scaffold_test.py
tests/goal5262_xhd_user_entrypoint_docs_status_test.py
```

## README Changes

The X-HD README now marks the current status as:

```text
xhd_public_modelnet40_all400_hd_exec_entrypoint_complete__full_paper_incomplete
```

It documents the current user-facing RTDL entrypoint:

```text
scripts/run_xhd_rtdl_hd_exec.py
scripts/run_xhd_rtdl_hd_exec_summary_batch.py
```

It records the current all-400 user-entrypoint evidence:

```text
route_label = cell-mbr-exact-witness
dataset_contract = public ModelNet40 pair identities represented in the paper-branch log index
case_count = 400
matched_case_count = 400
failed_case_count = 0
max_author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for all 400 cases
```

It also records the current performance matrix:

```text
RTDL hd_exec route-wall sum = 420.31053318828344 s
RTDL hd_exec batch case-wall sum = 600.8750001639128 s
Author process-wall sum = 255.03741998970509 s
Author internal Running.AvgTime sum = 2794.7910000000006 ms

RTDL route / author process-wall = 1.648034759782505x slower
RTDL route / author internal AvgTime = 150.3906850953375x slower
```

The README explicitly says these ratios must remain denominator-labeled and
that the internal AvgTime ratio is a phase/algorithm gap warning, not a
user-facing process-wall comparison.

## Manifest Changes

The manifest `reproduction_scope.status` now reflects the stronger current
paper-app state:

```text
xhd_public_modelnet40_all400_hd_exec_entrypoint_complete__full_paper_incomplete
```

The manifest evidence list now includes:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
```

The manifest boundaries remain false:

```text
full_paper_reproduction_claimed = false
exact_paper_dataset_reproduction_claimed = false
whole_program_speedup_claimed = false
author_performance_parity_claimed = false
existing_hausdorff_xhd_benchmark_reclassified_as_paper_reproduction = false
```

## Old Statement Corrected

The README previously said exact paper or same-source representative inputs were
not available. That is no longer precise after the Stanford Graphics and
ModelNet40 public-data work. It now distinguishes:

```text
exact paper byte-inputs remain unavailable / unproved
same-source and public representative inputs have separate author-rerun/RTDL gates
representative results do not prove exact paper byte-input identity
```

## Claim Boundary

Allowed:

```text
The RTDL X-HD paper app has a user-facing hd_exec-compatible entrypoint family
with all-400 public ModelNet40 author-rerun coverage through the exact-witness
route.
```

Allowed with denominator label:

```text
RTDL route-wall sum / author process-wall sum = 1.65x slower.
RTDL route-wall sum / author internal Running.AvgTime sum = 150.39x slower.
```

Forbidden:

```text
full X-HD paper reproduction complete
exact paper byte-input identity proved
all X-HD paper datasets reproduced
Figure 5-11 reproduced
author RT-core algorithm equivalence
author performance parity or speedup
RTDL Running.AvgTime comparable to author internal Running.AvgTime without label
```

## Validation

```text
py -m unittest \
  tests.goal5262_xhd_user_entrypoint_docs_status_test \
  tests.goal5110_xhd_paper_app_scaffold_test \
  tests.goal5261_xhd_hd_exec_entrypoint_performance_matrix_test
```

Result:

```text
Ran 8 tests in 0.095s
OK
```

Compile check:

```text
py -m py_compile tests/goal5262_xhd_user_entrypoint_docs_status_test.py
```

Result:

```text
OK
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goals5255-5262 for consolidated strict review.
2. If approved, treat the `hd_exec`-compatible runner and summary bridge as the
   primary X-HD RTDL paper-app user entrypoint.
3. Continue the remaining full-paper blockers separately:
   exact original dataset identity, non-ModelNet40 paper datasets/Figures, and
   author RT-core/internal AvgTime algorithm gap.
