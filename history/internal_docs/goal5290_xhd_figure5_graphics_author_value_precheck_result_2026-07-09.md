# Goal5290 - X-HD Figure 5 Graphics Author-Value Precheck

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5289 showed that the current Dragon -> AsianDragon scaled-1e-3 bounded
same-POD probe is not value-matched between author X-HD/LB=256 and the RTDL
exact route. Goal5290 performs the cheaper author-only precheck that should
precede any future Figure 5 timing attempt: compare available POD author input
variants to the paper-branch Figure 5 graphics log value before running RTDL.

This is a candidate-screening goal, not a performance goal.

## Inputs

Paper-log target:

```text
pair = dragon.ply -> asian_dragon.ply
category = graphics
paper log HDResult = 0.06536811590194702
paper log records = 5
paths = /local/storage/shared/HDDatasets/graphics/dragon.ply
        /local/storage/shared/HDDatasets/graphics/asian_dragon.ply
point counts = 437645, 3609600
```

Available POD files checked:

```text
/tmp/xhd_goal5234/data/dragon.ply
/tmp/xhd_goal5234/data/asian_dragon.ply
/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
```

POD author-only raw probe:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5290_author_value_probe_raw_pod_2026-07-09.json
```

## Result

Goal5290 artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5290_figure5_graphics_author_value_precheck_2026-07-09.json
```

Candidate values:

```text
unscaled AsianDragon:
  author stdout HDResult = 52.4535
  abs diff vs paper log = 52.38813188409805
  matches_paper_log_value = false

scaled-1e-3 AsianDragon:
  author stdout HDResult = 0.0654553
  abs diff vs paper log = 8.718409805297256e-05
  matches_paper_log_value = false
```

Decision:

```text
status = figure5_graphics_author_value_precheck_ready__no_available_candidate_matches_paper_log
continue_to_rtdl_timing = false
matching_candidate_labels = []
```

## Interpretation

Neither currently available POD input variant reproduces the paper-branch
Dragon -> AsianDragon Figure 5 graphics author-log HDResult under author
X-HD/LB=256. Therefore this candidate should not proceed to RTDL timing or
author-vs-RTDL ratio work.

This strengthens the Goal5289 no-go: the problem is already visible on the
author-only side, before RTDL enters the picture.

## Claim Boundary

Allowed:

```text
Goal5290 proves that the currently available POD Dragon -> AsianDragon variants
do not reproduce the paper-log author HDResult, so this Figure 5 candidate
should be stopped before expensive RTDL timing.
```

Not authorized:

```text
Figure 5 reproduced
RTDL/author Figure 5 speedup
RTDL timing result
same-denominator performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Validation

Focused regression:

```text
tests/goal5290_xhd_figure5_graphics_author_value_precheck_test.py
```

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_figure5_graphics_author_value_precheck.py ^
  --log-index Paper-reproduction-apps\x-hd-paper\results\xhd_paper_branch_log_index_goal5176_2026-07-08.json ^
  --raw-pod-author-probe Paper-reproduction-apps\x-hd-paper\results\xhd_goal5290_author_value_probe_raw_pod_2026-07-09.json ^
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5290_figure5_graphics_author_value_precheck_2026-07-09.json
```

Expected builder status:

```text
matched = true
status = figure5_graphics_author_value_precheck_ready__no_available_candidate_matches_paper_log
```

## Next Recommended Step

Do not run RTDL timing on this candidate again.

Next choices:

```text
1. Recover the exact author graphics input files or conversion provenance.
2. Search for another Figure 5 pair with available value-matched inputs.
3. Move to another paper blocker: Figure 6 phase/counter mapping, Figure 7/8/10
   author-log semantics, or exact input provenance.
```
