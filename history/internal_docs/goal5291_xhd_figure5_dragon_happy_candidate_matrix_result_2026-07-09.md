# Goal5291 - X-HD Figure 5 Dragon -> HappyBuddha Candidate Matrix

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5288 established the Figure 5 author-log timing denominator. Goal5289 and
Goal5290 stopped the Dragon -> AsianDragon candidate because the currently
available POD input variants do not reproduce the paper-branch author-log value
even on the author side.

Goal5291 consolidates the strongest currently available Figure 5 graphics
candidate: Dragon -> HappyBuddha. This goal does not run new code. It builds a
matrix from existing author-log, author rerun, and RTDL route artifacts so that
review can decide whether this is a valid value-matched Level-B candidate.

## Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_dragon_happy_candidate_matrix.py
```

Focused regression:

```text
tests/goal5291_xhd_figure5_dragon_happy_candidate_matrix_test.py
```

## Inputs

Goal5291 reads:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_phase_matrix_goal5188_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
```

Candidate:

```text
pair = dragon.ply -> happy_buddha.ply
category = graphics
level = level_b_same_source_candidate_only
point counts = 437645, 543652
exact paper dataset identity proven = false
```

## Value Evidence

The value matrix is:

```text
paper-branch log HDResult      = 0.12572969496250153
author rerun HDResult          = 0.12572988867759705
RTDL fresh route HDResult      = 0.12572988629271128
RTDL explicit-warm HDResult    = 0.12572988629271128

author rerun vs paper log abs diff   = 1.9371509552001953e-07
RTDL fresh vs author rerun abs diff  = 2.3848857610975216e-09
RTDL warm vs author rerun abs diff   = 2.3848857610975216e-09
tolerance                            = 1e-6
```

Result:

```text
status = figure5_graphics_dragon_happy_value_matched_candidate_ready__ratio_not_authorized
value_matched_candidate = true
matched = true
```

This is a value-matched candidate. It is not proof of byte-identical paper input
files.

## Separated Denominators

The matrix keeps the timing denominators separate:

```text
paper log:
  GPU = NVIDIA GeForce RTX 3090
  records = 5
  fields = Running.AvgTime and ReportedTime median
  rt_gpu Running.AvgTime = 8.2398 ms
  eb_gpu Running.AvgTime = 4.4662 ms
  hybrid_gpu Running.AvgTime = 4.6754 ms
  auto_tune records = 5.7734 ms and 4.6558 ms

author rerun:
  GPU = NVIDIA RTX 4000 Ada Generation
  Goal5186 Running.AvgTime = 7.823 ms
  Goal5188 Running.AvgTime = 7.603 ms
  Goal5188 process wall = 1.973201423883438 s

RTDL Goal5188 baseline:
  route wall = 7.303133897483349 s
  case total = 7.490384787321091 s
  load full inputs = 2.5199945867061615 s
  total = 10.011082544922829 s

RTDL Goal5212 fresh:
  route wall = 0.8517371863126755 s
  case total = 0.851749412715435 s
  load full inputs = 0.6782490611076355 s
  artifact total = 1.5306707620620728 s

RTDL Goal5212 explicit warm:
  warmup = 0.8415441885590553 s
  measured route wall = 0.2880803421139717 s
  measured case total = 0.2880931422114372 s
  artifact total = 1.8082116544246674 s
```

No ratio is reported or authorized.

## Important Caveat

The Goal5211/Goal5212 route uses global-bound early break:

```text
global_bound_early_break = true
per_source_witness_exact = false
early-break count = 409376 fresh / 409627 explicit-warm
```

Therefore this matrix supports exact directed-HD / max-nearest value evidence,
not exact per-source nearest-witness reproduction for every source point.

## Claim Boundary

Allowed:

```text
Dragon -> HappyBuddha is the strongest current Figure 5 graphics Level-B
value-matched candidate. Author rerun and RTDL route values both match the
paper-branch log value within 1e-6.
```

Not authorized:

```text
Figure 5 reproduced
Figure 5 full matrix reproduced
author-vs-RTDL performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
exact per-source witness reproduction under early break
```

## Validation

Command:

```text
py -m unittest tests.goal5291_xhd_figure5_dragon_happy_candidate_matrix_test
```

Expected:

```text
Ran 4 tests OK
```

## Next Recommended Step

Send Goals5288-5291 as the current Figure 5 packet:

```text
Goal5288: author timing denominator audit
Goal5289: Dragon -> Asian same-POD probe no-go
Goal5290: Dragon -> Asian author-only value precheck no-go
Goal5291: Dragon -> HappyBuddha value-matched candidate matrix
```

After review, decide whether to continue Figure 5 by pursuing BraTS/geo inputs
and exact graphics provenance, or pivot to Figure 6 phase/counter mapping.
