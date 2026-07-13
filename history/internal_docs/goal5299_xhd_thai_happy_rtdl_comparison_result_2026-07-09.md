# Goal5299 - X-HD ThaiStatuette -> HappyBuddha RTDL Level-B Comparison

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5299 takes one Goal5298 value-matched author graphics case and runs RTDL on
the same current POD inputs.

Selected case:

```text
ThaiStatuette scaled 1e-3 -> HappyBuddha
```

Reason:

```text
Goal5298 showed this case matches the paper-branch author-log HDResult on the
current POD author rerun. It also exercises one of the newly uploaded files.
```

## Inputs

```text
input1 = /tmp/xhd_goal5298/data/thai_statuette_scaled_1e-3.ply
input2 = /tmp/xhd_goal5298/data/happy_buddha.ply
n_dims = 3
input_type = ply
preprocessing = translate_each_input_to_min_bound
```

Point counts:

```text
input1 = 4,999,996
input2 =   543,652
```

This remains a Level-B same-source public Stanford candidate, not exact paper
dataset reproduction.

## Artifacts

Matrix:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_level_b_rtdl_comparison_matrix_2026-07-09.json
```

RTDL route artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_exact_witness_process_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_fast_scalar_process_pod.json
```

Author source:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/thai_happy_scaled_author.json
```

## Result

Author rerun from Goal5298:

```text
HDResult              = 0.21912431716918945
paper-log HDResult    = 0.21912434697151184
paper-log abs diff    = 2.9802322387695312e-08
author Running.AvgTime = 26.57 ms
author process wall    = 2.3395375460386276 s
```

RTDL routes:

```text
route                  HDResult              abs diff vs author   route wall   total sec   process wall   witness exact
cell-mbr-exact-witness 0.2191243235042005    6.335e-9            5.0015s     5.9969s     6.9526s       true
cell-mbr-fast-scalar   0.2191243235042005    6.335e-9            1.0029s     2.0014s     2.9271s       false
```

Both RTDL routes match the author rerun and paper-log HDResult within `1e-6`.

## Important Caveat

The two RTDL routes prove different things:

```text
cell-mbr-exact-witness:
  scalar HDResult matches;
  per_source_witness_exact = true.

cell-mbr-fast-scalar:
  scalar HDResult matches;
  per_source_witness_exact = false;
  global_bound_early_break = true;
  global_bound_early_break_count = 4,982,182.
```

Therefore the fast route is valid as an exact scalar directed-HD route under
the Goal5211-style max-nearest contract, but it must not be described as exact
per-source witness reproduction.

## Performance Boundary

No author-vs-RTDL ratio is authorized here.

Reason:

```text
author Running.AvgTime, author process wall, RTDL route wall, RTDL total, and
RTDL process wall are different denominators.
```

The numbers are reported side by side only.

## Claim Boundary

Allowed:

```text
Level-B same-source ThaiStatuette-scaled -> HappyBuddha RTDL scalar-value
comparison against the current POD author rerun and paper-branch author log.
```

Not authorized:

```text
exact paper dataset reproduction
Figure 5 reproduction
Figure 7/8/10 reproduction
full X-HD paper reproduction
author RT-core algorithm equivalence
author-vs-RTDL performance ratio
fast-scalar per-source exact witness claim
```

## Validation

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_level_b_rtdl_comparison_matrix_2026-07-09.json
py -m unittest tests.goal5299_xhd_thai_happy_rtdl_comparison_test
```
