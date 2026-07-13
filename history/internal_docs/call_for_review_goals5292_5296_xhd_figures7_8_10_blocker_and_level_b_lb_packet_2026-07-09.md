# Call For Review - Goals5292-5296 X-HD Figures 7 / 8 / 10 Blocker And Level-B LB Packet

Date: 2026-07-09

Please strictly review the current X-HD Figures 7 / 8 / 10 blocker packet plus
the first separately named Level-B load-balance diagnostic.

This packet has two purposes:

```text
1. Verify that Figures 7, 8, and 10 remain not reproduced because the author
   numeric matrices and exact current-POD HDDatasets are missing.
2. Verify that Goal5296 is correctly scoped as a temporary-input author-only
   Level-B load-balance diagnostic, not Figure 7 reproduction and not RTDL
   comparison.
```

## Goals Under Review

```text
Goal5292 - Figure 7 Load-Balance / Heavy-Cell Offload Source-Log Audit
Goal5293 - Figure 8 Radius-Strategy Source-Log Audit
Goal5294 - Figure 10 Scalability / Overlap Source-Log Audit
Goal5295 - Figures 7/8/10 POD Dataset Availability Decision
Goal5296 - Level-B Dragon -> AsianDragon Author LB Diagnostic
```

## Files Under Review

```text
history/internal_docs/goal5292_xhd_figure7_load_balance_audit_result_2026-07-09.md
history/internal_docs/goal5293_xhd_figure8_radius_strategy_audit_result_2026-07-09.md
history/internal_docs/goal5294_xhd_figure10_scalability_overlap_audit_result_2026-07-09.md
history/internal_docs/goal5295_xhd_figures7_8_10_pod_dataset_availability_result_2026-07-09.md
history/internal_docs/goal5296_xhd_level_b_dragon_asian_lb_diagnostic_result_2026-07-09.md

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5292_figure7_load_balance_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json

tests/goal5292_xhd_figure7_load_balance_audit_test.py
tests/goal5293_xhd_figure8_radius_strategy_audit_test.py
tests/goal5294_xhd_figure10_scalability_overlap_audit_test.py
tests/goal5295_xhd_figures7_8_10_pod_dataset_availability_test.py
tests/goal5296_xhd_level_b_lb_diagnostic_test.py
```

Supporting source / remote state:

```text
.codex_tmp/xhd_author_repo/expr/run_lb.sh
.codex_tmp/xhd_author_repo/expr/draw_lb.py
.codex_tmp/xhd_author_repo/expr/run_radius_tuning.sh
.codex_tmp/xhd_author_repo/expr/draw_tune_radius.py
.codex_tmp/xhd_author_repo/expr/run_scalability.sh
.codex_tmp/xhd_author_repo/expr/draw_scalability.py
/tmp/xhd-goal5112/author/expr/common.sh
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

## Evidence Summary

### Goal5292 - Figure 7 author matrix missing

```text
Author source:
  expr/run_lb.sh exists
  expr/draw_lb.py exists

Expected author matrix:
  logs/lb_comparison with lb=0/lb=256 records

Checked-in matrix:
  total_json_count = 0

run_all state:
  LB=256 profiling-style records exist
  LB=0 counterpart absent

figure7_reproduced = false
```

### Goal5293 - Figure 8 author matrix missing

```text
Author source:
  expr/run_radius_tuning.sh exists
  expr/draw_tune_radius.py exists

Expected author matrix:
  logs/tune_radius add/double/adaptive over geo + graphics

Checked-in matrix:
  total_json_count = 0

run_all state:
  no Figure 8 radius-strategy records

figure8_reproduced = false
```

### Goal5294 - Figure 10 author matrix missing

```text
Author source:
  expr/run_scalability.sh exists
  expr/draw_scalability.py exists

Expected author matrix:
  logs/scalability size and translate/overlap sweeps

Checked-in matrix:
  total_json_count = 0

run_all state:
  4535 workload-family records
  no Figure 10 scale/overlap subset labels or diagnostics

figure10_reproduced = false
```

### Goal5295 - current POD cannot regenerate exact matrices

```text
POD wrapper preflight = POD_OK
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
author build exists = true
/local/storage/shared = missing
/local/storage/shared/HDDatasets = missing
```

Required author inputs are missing:

```text
Figure 7 graphics:
  dragon.ply, asian_dragon.ply, thai_statuette.ply, happy_buddha.ply

Figure 8 geo:
  dtl_cnty.wkt, uszipcode.wkt, USADetailedWaterBodies.wkt,
  USACensusBlockGroupBoundaries.wkt, lakes.bz2.wkt, parks.bz2.wkt

Figure 8 graphics:
  dragon.ply, asian_dragon.ply, thai_statuette.ply, happy_buddha.ply

Figure 10:
  geo/all_nodes.wkt
```

Partial temporary inputs:

```text
/tmp/xhd_goal5234/data/dragon.ply = present
/tmp/xhd_goal5234/data/asian_dragon.ply = present
/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply = present
/tmp/xhd_goal5234/data/thai_statuette.ply = missing
/tmp/xhd_goal5234/data/happy_buddha.ply = missing
```

### Goal5296 - temporary-input Level-B author LB diagnostic

Goal5296 uses only the partial temporary Dragon -> AsianDragon input:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
```

Author `hd_exec` results:

```text
lb=0:
  HDResult = 52.453487396240234
  Running.AvgTime = 107.254 ms
  process wall = 16.25388788431883 s
  LargeCells = 0
  WL Heavy Peak = 0
  Iteration 3 ComparedPoints = 7,969,408,615
  Iteration 3 RTTime = 96.854 ms
  Iteration 3 CUDATime = 0.054 ms

lb=256:
  HDResult = 52.453487396240234
  Running.AvgTime = 131.841 ms
  process wall = 17.09253077954054 s
  LargeCells = 5060
  WL Heavy Peak = 217,071,920
  Iteration 3 ComparedPoints = 1,242,037,623
  Iteration 3 RTTime = 45.519 ms
  Iteration 3 CUDATime = 75.923 ms
  Iteration 3 OffloadingSize = 27,133,990
```

Interpretation:

```text
The two author runs return equal HDResult. On this temporary input, lb=256
reduces iteration-3 compared points and RTTime but adds heavy offload work and
is slower by author Running.AvgTime and process wall. This is useful diagnostic
evidence for author load-balance behavior, but it is not Figure 7 reproduction
and not RTDL comparison.
```

## Packet Interpretation

The current evidence supports this combined interpretation:

```text
Figures 7/8/10 are not reproduced.
The author scripts exist, but their numeric matrices are not checked in.
The current POD is usable, but it lacks the exact author HDDatasets root needed
to regenerate those matrices.
The partial Dragon/Asian temporary inputs can support separately named Level-B
diagnostics only.
Goal5296 is one such author-only Level-B diagnostic. It must not be promoted to
Figure 7 reproduction.
```

## Shared Claim Boundary

Allowed:

```text
Figures 7/8/10 source/log audits are implemented.
Current POD dataset availability has been checked through the wrapper.
Current POD is usable but missing /local/storage/shared/HDDatasets.
Figures 7/8/10 exact author matrix regeneration is blocked on the current POD.
Goal5296 provides author-only temporary-input LB behavior for Dragon->Asian.
```

Not authorized:

```text
Figure 7 reproduced
Figure 8 reproduced
Figure 10 reproduced
author matrices regenerated
exact paper dataset reproduction
RTDL/author parity or performance ratio for Figures 7/8/10
partial /tmp inputs promoted to paper inputs
Goal5296 treated as Figure 7 reproduction
load-balance speedup claim for RTDL
POD called broken
```

## Review Questions

1. Are Goals5292-5294 correct that the author scripts exist but the checked-in
   numeric matrices for Figures 7/8/10 are missing?
2. Is Goal5294 correct that paper-branch `run_all` workload-family records are
   not a substitute for Figure 10 scale/overlap labels and diagnostics?
3. Is Goal5295 correct that the current POD is usable through the wrapper?
4. Is Goal5295 correct that `/local/storage/shared/HDDatasets` is missing on the
   current POD?
5. Are the required input paths for Figures 7/8/10 derived correctly from the
   author scripts?
6. Is it correct that the current POD cannot regenerate exact author matrices
   for Figures 7/8/10 as-is?
7. Is it correct that the partial Dragon/Asian temporary inputs are insufficient
   for exact Figure 7/8/10 regeneration and must not be promoted to paper
   inputs?
8. Is Goal5296 correctly framed as a separately named Level-B author-only
   diagnostic rather than Figure 7 reproduction?
9. Does Goal5296 correctly report that `lb=0` and `lb=256` return the same
   HDResult on the temporary Dragon->Asian input?
10. Does Goal5296 correctly avoid claiming a load-balance speedup, given that
    `lb=256` is slower by author `Running.AvgTime` and process wall on this
    diagnostic input?
11. Does the packet avoid Figure reproduction, exact dataset, performance
    ratio, and RTDL parity overclaims?
12. Is the recommended next action correct: mount/recover HDDatasets, define
    separately named Level-B diagnostics, or pivot to another blocker?
13. Can Goals5292-5296 be marked externally reviewed and approved, or are
    amendments required?

## Expected Answer Shape

Please answer with:

```text
verdict_label: ...
blocking_findings:
required_amendments:
non_blocking_notes:
answers:
  Q1: ...
  Q2: ...
  ...
  Q13: ...
recommended_next_action:
```

Possible verdict labels:

```text
approve_goals5292_5296_figures7_8_10_blocker_and_level_b_lb_packet
revise_goals5292_5296_claim_boundary_or_dataset_lb_evidence
block_goals5292_5296_due_to_incorrect_author_or_pod_evidence
```
