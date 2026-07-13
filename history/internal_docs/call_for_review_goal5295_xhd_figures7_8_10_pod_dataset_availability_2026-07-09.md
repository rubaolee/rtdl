# Call For Review - Goal5295 X-HD Figures 7 / 8 / 10 POD Dataset Availability

Date: 2026-07-09

Please strictly review Goal5295.

## Review Scope

Goal5295 checks whether the current POD can regenerate the missing author-side
numeric matrices for Figures 7, 8, and 10.

This is not a Figure 7/8/10 reproduction claim, not an RTDL route result, and
not a performance ratio.  It determines whether the exact author dataset root
needed by `run_lb.sh`, `run_radius_tuning.sh`, and `run_scalability.sh` exists
on the current POD.

## Files Under Review

```text
history/internal_docs/goal5295_xhd_figures7_8_10_pod_dataset_availability_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json
tests/goal5295_xhd_figures7_8_10_pod_dataset_availability_test.py
```

Supporting evidence:

```text
scripts/current_pod_ssh.py
/tmp/xhd-goal5112/author/expr/common.sh
/tmp/xhd-goal5112/author/expr/run_lb.sh
/tmp/xhd-goal5112/author/expr/run_radius_tuning.sh
/tmp/xhd-goal5112/author/expr/run_scalability.sh
```

## Evidence Summary

POD preflight:

```text
POD_OK
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Author environment:

```text
author repo = /tmp/xhd-goal5112/author
author hd_exec = /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
DATASET_ROOT = /local/storage/shared/HDDatasets
SERIALIZE_ROOT = /local/storage/shared/HDDatasets/ser
```

Current POD dataset status:

```text
/local/storage/shared = missing
/local/storage/shared/HDDatasets = missing
```

Required author-script inputs are missing:

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

Interpretation under review:

```text
The POD itself is usable, but it does not currently have the exact author
HDDatasets root required to regenerate Figures 7/8/10. The partial Dragon/Asian
temporary inputs are insufficient and must not be promoted to paper input
status.
```

## Review Questions

1. Does the evidence correctly show that the POD is reachable and has a usable
   GPU via the project wrapper?
2. Does the evidence correctly show that `/local/storage/shared/HDDatasets` is
   missing on the current POD?
3. Are the required Figure 7 input paths derived correctly from `run_lb.sh`?
4. Are the required Figure 8 input paths derived correctly from
   `run_radius_tuning.sh`?
5. Is the required Figure 10 `all_nodes.wkt` path derived correctly from
   `run_scalability.sh`?
6. Is it correct that the current POD cannot regenerate the exact author Figure
   7/8/10 matrices as-is?
7. Is it correct that the partial `/tmp/xhd_goal5234` Dragon/Asian inputs are
   insufficient for full Figure 7/8/10 regeneration and must not be called paper
   inputs?
8. Does the result avoid claiming Figure 7/8/10 reproduction, exact dataset
   reproduction, author matrix regeneration, RTDL comparison, or performance
   ratio?
9. Is the next-step recommendation correct: mount/recover HDDatasets, define a
   separately named Level-B diagnostic, or pivot?
10. Can Goal5295 be marked externally reviewed and approved, or are amendments
    required?

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

Acceptable verdict examples:

```text
approve_goal5295_pod_dataset_availability__hddatasets_missing_figures7_8_10_regeneration_blocked
revise_goal5295_dataset_path_or_claim_boundary
block_goal5295_due_to_incorrect_pod_or_dataset_evidence
```
