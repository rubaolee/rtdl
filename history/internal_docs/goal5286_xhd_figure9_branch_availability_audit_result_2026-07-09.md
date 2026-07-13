# Goal5286 - X-HD Figure 9 Branch Availability Audit

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5285 showed that the pinned author `paper` branch has a Figure-9-like
plotting script but lacks two of the four `run_all/auto_tune` variants expected
by that script. Goal5286 asks whether those missing variants are present on
another pinned author branch.

This goal does not run an RTDL route, does not claim Figure 9 reproduction, and
does not claim a performance ratio.

## Implementation

New app-owned provenance script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_branch_availability_audit.py
```

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json
```

Focused regression:

```text
tests/goal5286_xhd_figure9_branch_availability_audit_test.py
```

No RTDL core or native files were changed.

## Main Evidence

Pinned author branches:

```text
paper  = 8c3846866052e1e8755210021f23fac2cbe8c3d6
main   = 7bf41c8442d059c94f4178355c6d5a10571d9658
hybrid = 4d9046a9e55d87f35daf81dd718444029fab56ce
```

The expected Figure-9 variants remain:

```text
n_points_cell_false_max_hit_false
n_points_cell_true_max_hit_false
n_points_cell_false_max_hit_true
n_points_cell_true_max_hit_true
```

Branch results:

```text
paper:
  run_all/auto_tune records = 1814
  unique pairs = 907
  observed configs:
    n_points_cell_false_max_hit_false = 907
    n_points_cell_true_max_hit_true = 907
  missing:
    n_points_cell_true_max_hit_false
    n_points_cell_false_max_hit_true
  checked-in PDF:
    expr/for_the_paper/auto-tune.pdf

main:
  run_all/auto_tune records = 0
  Figure-9-like script/PDF files = not present

hybrid:
  run_all/auto_tune records = 0
  Figure-9-like script/PDF files = not present
```

## Decision

Goal5286 produces:

```text
status = missing_figure9_variants_not_found_on_pinned_branches__figure9_not_reproduced
any_branch_has_all_expected_figure9_variants = false
figure9_reproduced = false
```

The checked-in `auto-tune.pdf` on the `paper` branch is evidence that the author
saved a rendered artifact.  It is not a reproducible denominator for RTDL/author
comparison unless the data/script mapping behind the plotted quantities is
recovered and externally reviewed.

Allowed summary:

```text
Goal5286 checks all pinned author branches and confirms that the two missing
Figure-9 run_all variants are not present on main or hybrid. The paper branch
contains a checked-in auto-tune.pdf, but that PDF is not promoted to Figure 9
reproduction.
```

Forbidden summaries:

```text
Figure 9 reproduced
missing variants recovered from main or hybrid
checked-in PDF equals reproducible Figure 9
RTDL Figure 9 speedup or parity
```

## Validation

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_figure9_branch_availability_audit.py ^
  --git-dir scratch\xhd_author_goal5285.git ^
  --branches paper main hybrid ^
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json
```

Result:

```text
status = missing_figure9_variants_not_found_on_pinned_branches__figure9_not_reproduced
```

Focused validation to run for closeout:

```text
py -m unittest ^
  tests.goal5286_xhd_figure9_branch_availability_audit_test ^
  tests.goal5285_xhd_figure9_source_script_audit_test ^
  tests.goal5284_xhd_figure9_auto_tune_matrix_test
```

## Claim Boundary

Allowed:

```text
Goal5286 is author-branch availability evidence for Figure 9.
The missing run_all variants are not present on the pinned main or hybrid
branches.
The checked-in PDF exists on paper, but it is not a reproducible RTDL/author
denominator.
```

Not authorized:

```text
Figure 9 reproduced
full adaptive-grid sweep reproduced
paper-selected grid choices recovered
checked-in PDF treated as a reproduced figure
author-vs-RTDL Figure 9 speedup or parity
exact paper dataset reproduction
full X-HD paper reproduction
RTDL route result for Figure 9
```

## Next Recommended Step

Figure 9 now has a clearer blocker:

```text
The missing author-side denominator is not recoverable from the pinned branches
as checked. To continue Figure 9, either regenerate the missing run_all variants
from author scripts and inputs, or establish an externally reviewed mapping from
training sweeps to the plotted PDF quantities.
```

If neither is feasible, close Figure 9 as source-mapped but not reproduced and
move to another full-paper blocker.
