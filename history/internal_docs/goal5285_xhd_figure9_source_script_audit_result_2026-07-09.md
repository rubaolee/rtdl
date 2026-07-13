# Goal5285 - X-HD Figure 9 Source / Script Audit

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5285 follows Goal5284's conclusion that the author paper-branch
`run_all/auto_tune` logs are useful but do not reproduce Figure 9.  Goal5285
audits the pinned author source/scripts directly to answer a narrower question:

```text
Is there enough source/script provenance to promote the existing auto-tune logs
or training sweeps into a Figure 9 reproduction?
```

This goal does not run an RTDL route, does not claim Figure 9 reproduction, and
does not claim any RTDL/author performance ratio.

## Implementation

New app-owned provenance script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_source_audit.py
```

Input author repo:

```text
repository = https://github.com/pwrliang/X-HD.git
rev = paper
head = 8c3846866052e1e8755210021f23fac2cbe8c3d6
audit_method = git object access; no checkout required
```

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5285_figure9_source_script_audit_2026-07-09.json
```

Focused regression:

```text
tests/goal5285_xhd_figure9_source_script_audit_test.py
```

No RTDL core or native files were changed.

## Main Evidence

The author source contains a Figure-9-like plotting script:

```text
path = expr/for_the_paper/effective_autoune.py
active tail calls draw_mri_modelnet()
saves auto-tune.pdf
loads logs/run_all/auto_tune
```

The active plotting function expects four variants:

```text
n_points_cell_false_max_hit_false
n_points_cell_true_max_hit_false
n_points_cell_false_max_hit_true
n_points_cell_true_max_hit_true
```

The current paper-branch `run_all/auto_tune` logs contain only two observed
config labels:

```text
n_points_cell_false_max_hit_false = 907
n_points_cell_true_max_hit_true = 907
record_count = 1814
unique_pair_count = 907
complete_two_config_pair_count = 907
```

The two variants missing from current `run_all/auto_tune` logs are:

```text
n_points_cell_true_max_hit_false
n_points_cell_false_max_hit_true
```

The checked runner script also explains the two-config shape:

```text
path = expr/for_the_paper/effective_autotune.sh
enabled = run_modelnet
disabled/commented = run_mri, run_geo, run_graphics
literal run_hd pairs detected = false/false and true/true
```

The source also contains training sweeps:

```text
path = expr/for_the_paper/gen_train.sh
script_n_points_cell_list = [1, 4, 8, ..., 80]
script_max_hit_list = [1, 16, 32, 64, 128, 256, 512]
logs/train n_points_cell values = 1..30
```

But these are not the same denominator as the Figure-9-like plotting script:

```text
gen_train.sh / logs/train = training/tuning sweeps
effective_autoune.py = reads logs/run_all/auto_tune for the figure
```

Therefore training sweeps must not be promoted to Figure 9 reproduction without
an externally reviewed mapping from the training logs to the plotted figure.

## Decision

Goal5285 produces:

```text
status = figure9_plot_script_expects_missing_run_all_variants__figure9_not_reproduced
figure9_reproduced = false
```

Allowed summary:

```text
Goal5285 maps the author paper-branch Figure-9-like plotting script and shows
that the current run_all auto_tune logs lack two of the four variants expected
by that script. Training sweeps exist, but they are a separate source and are
not promoted to Figure 9 reproduction.
```

Forbidden summaries:

```text
Figure 9 reproduced
all auto-tune variants recovered
training sweep equals Figure 9
RTDL Figure 9 speedup or parity
```

## Validation

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_figure9_source_audit.py ^
  --git-dir scratch\xhd_author_goal5285.git ^
  --rev paper ^
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5285_figure9_source_script_audit_2026-07-09.json
```

Result:

```text
status = figure9_plot_script_expects_missing_run_all_variants__figure9_not_reproduced
```

Focused validation to run for closeout:

```text
py -m unittest ^
  tests.goal5285_xhd_figure9_source_script_audit_test ^
  tests.goal5284_xhd_figure9_auto_tune_matrix_test
```

## Claim Boundary

Allowed:

```text
Goal5285 is source/script provenance evidence for Figure 9.
The author source contains a Figure-9-like auto-tune plotting script.
The checked current run_all auto_tune logs do not provide all four variants that
the plotting script expects.
```

Not authorized:

```text
Figure 9 reproduced
full adaptive-grid sweep reproduced
paper-selected grid choices recovered
training sweeps treated as Figure 9 output
author-vs-RTDL Figure 9 speedup or parity
exact paper dataset reproduction
full X-HD paper reproduction
RTDL route result for Figure 9
```

## Next Recommended Step

If Figure 9 remains the target:

```text
Recover or reconstruct the missing author-side denominator first:
  either locate/generate the two missing run_all variants expected by
  effective_autoune.py,
  or produce an externally reviewed script/data mapping from training sweeps to
  the plotted Figure 9 quantities.
```

Until that author-side denominator is complete, do not implement more RTDL route
work for Figure 9 and do not publish a Figure 9 performance comparison.
