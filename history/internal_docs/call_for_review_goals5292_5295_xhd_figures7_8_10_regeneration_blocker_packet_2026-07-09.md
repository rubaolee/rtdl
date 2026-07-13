# Call For Review - Goals5292-5295 X-HD Figures 7 / 8 / 10 Regeneration Blocker Packet

Date: 2026-07-09

Please strictly review the current X-HD Figures 7 / 8 / 10 regeneration blocker
packet.

This packet extends the Goals5292-5294 source/log audit with Goal5295's live POD
dataset availability check.  It asks whether the project has correctly
classified Figures 7, 8, and 10 as blocked on missing author-side numeric
matrices and missing current-POD exact datasets, rather than blocked on RTDL
route work.

## Goals Under Review

```text
Goal5292 - Figure 7 Load-Balance / Heavy-Cell Offload Source-Log Audit
Goal5293 - Figure 8 Radius-Strategy Source-Log Audit
Goal5294 - Figure 10 Scalability / Overlap Source-Log Audit
Goal5295 - Figures 7/8/10 POD Dataset Availability Decision
```

## Files Under Review

```text
history/internal_docs/goal5292_xhd_figure7_load_balance_audit_result_2026-07-09.md
history/internal_docs/goal5293_xhd_figure8_radius_strategy_audit_result_2026-07-09.md
history/internal_docs/goal5294_xhd_figure10_scalability_overlap_audit_result_2026-07-09.md
history/internal_docs/goal5295_xhd_figures7_8_10_pod_dataset_availability_result_2026-07-09.md

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5292_figure7_load_balance_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json

tests/goal5292_xhd_figure7_load_balance_audit_test.py
tests/goal5293_xhd_figure8_radius_strategy_audit_test.py
tests/goal5294_xhd_figure10_scalability_overlap_audit_test.py
tests/goal5295_xhd_figures7_8_10_pod_dataset_availability_test.py
```

Supporting source:

```text
.codex_tmp/xhd_author_repo/expr/run_lb.sh
.codex_tmp/xhd_author_repo/expr/draw_lb.py
.codex_tmp/xhd_author_repo/expr/run_radius_tuning.sh
.codex_tmp/xhd_author_repo/expr/draw_tune_radius.py
.codex_tmp/xhd_author_repo/expr/run_scalability.sh
.codex_tmp/xhd_author_repo/expr/draw_scalability.py
/tmp/xhd-goal5112/author/expr/common.sh
```

## Evidence Summary

### Author source/log state

Goal5292:

```text
Figure 7 source scripts exist:
  run_lb.sh
  draw_lb.py
Required matrix:
  logs/lb_comparison lb=0/lb=256
Checked-in matrix:
  total_json_count = 0
run_all:
  LB=256 profiling-style records exist
  LB=0 counterpart absent
figure7_reproduced = false
```

Goal5293:

```text
Figure 8 source scripts exist:
  run_radius_tuning.sh
  draw_tune_radius.py
Required matrix:
  logs/tune_radius add/double/adaptive over geo + graphics
Checked-in matrix:
  total_json_count = 0
run_all:
  no Figure 8 radius-strategy records
figure8_reproduced = false
```

Goal5294:

```text
Figure 10 source scripts exist:
  run_scalability.sh
  draw_scalability.py
Required matrix:
  logs/scalability size + translate/overlap sweeps
Checked-in matrix:
  total_json_count = 0
run_all:
  4535 workload-family records
  no scale/overlap subset labels or diagnostics
figure10_reproduced = false
```

### Current POD regeneration state

Goal5295:

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

Partial temporary inputs exist only for Dragon / Asian:

```text
/tmp/xhd_goal5234/data/dragon.ply = present
/tmp/xhd_goal5234/data/asian_dragon.ply = present
/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply = present
/tmp/xhd_goal5234/data/thai_statuette.ply = missing
/tmp/xhd_goal5234/data/happy_buddha.ply = missing
```

## Packet Interpretation

The current evidence supports this interpretation:

```text
Figures 7/8/10 are not reproduced.
The author scripts exist, but their numeric matrices are not checked in.
The current POD is usable, but it does not have the exact author HDDatasets root
needed to regenerate those matrices.
RTDL comparison work should not begin for Figures 7/8/10 until an author-side
numeric denominator exists.
```

## Shared Claim Boundary

Allowed:

```text
Figures 7/8/10 source/log audits are implemented.
Current POD dataset availability has been checked through the wrapper.
Current POD is usable but missing /local/storage/shared/HDDatasets.
Figures 7/8/10 exact author matrix regeneration is blocked on the current POD.
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
   and must not be promoted to paper inputs?
8. Does the packet avoid Figure reproduction, exact dataset, performance ratio,
   and RTDL parity overclaims?
9. Is the recommended next action correct: mount/recover HDDatasets, define
   separately named Level-B diagnostics, or pivot to another blocker?
10. Can Goals5292-5295 be marked externally reviewed and approved, or are
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
  Q10: ...
recommended_next_action:
```

Possible verdict labels:

```text
approve_goals5292_5295_figures7_8_10_regeneration_blocker_packet
revise_figures7_8_10_regeneration_packet_claim_boundary_or_dataset_paths
block_figures7_8_10_regeneration_packet_due_to_incorrect_author_or_pod_evidence
```
