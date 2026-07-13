# Call For Review - Goals5268-5271 X-HD Figure 6 Packet

Date: 2026-07-09

Please strictly review the current X-HD Figure 6 packet. This packet decides
whether the current Dragon -> AsianDragon evidence can support Figure 6
reproduction, or only a separately named Level-B pruning diagnostic.

## Goals Under Review

```text
Goal5268 - Figure 6 Pruning Phase/Counter Mapping
Goal5269 - Figure 6 LB=256 Correctness Probe
Goal5270 - Figure 6 Exact-Input Availability / Diagnostic Decision
Goal5271 - Level-B Pruning Diagnostic
```

## Files Under Review

### Goal5268

```text
history/internal_docs/goal5268_xhd_figure6_pruning_phase_counter_mapping_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5268_figure6_pruning_phase_counter_mapping_2026-07-09.json
tests/goal5268_xhd_figure6_pruning_mapping_test.py
```

### Goal5269

```text
history/internal_docs/goal5269_xhd_figure6_lb256_correctness_probe_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5269_figure6_lb256_correctness_probe_2026-07-09.json
tests/goal5269_xhd_figure6_lb256_correctness_probe_test.py
```

### Goal5270

```text
history/internal_docs/goal5270_xhd_figure6_exact_input_availability_decision_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5270_figure6_exact_input_availability_decision_2026-07-09.json
tests/goal5270_xhd_figure6_exact_input_decision_test.py
```

### Goal5271

```text
history/internal_docs/goal5271_xhd_level_b_pruning_diagnostic_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5271_level_b_pruning_diagnostic_2026-07-09.json
tests/goal5271_xhd_level_b_pruning_diagnostic_test.py
```

## Packet Summary

Goal5268 maps the author Figure-6-style script and profiling fields:

```text
author script = /tmp/xhd-goal5112/author/expr/run_rt_comparison.sh
flags = --eb, --prune, --lb, --profiling
profiling fields = Hits, ComparedPoints, RTTime, CUDATime, OffloadingSize
variants = noopt, eb, eb_prune, xhd_lb256
```

On the current Level-B public/same-source Dragon -> AsianDragon scaled
candidate, the first three variants are correctness-clean:

```text
noopt:
  HDResult = 0.06536787003278732
  AvgTime = 6976.301 ms
  Hits = 128,532,825
  ComparedPoints = 176,279,179,922

eb:
  HDResult = 0.06536787003278732
  AvgTime = 1841.428 ms
  Hits = 15,269,735
  ComparedPoints = 21,009,262,745

eb_prune:
  HDResult = 0.06536787003278732
  AvgTime = 146.486 ms
  Hits = 15,163,664
  ComparedPoints = 586,805,995
```

But the author Figure 6 XHD setting on the current candidate is not
correctness-clean:

```text
xhd_lb256:
  eb = true
  prune = true
  lb = 256
  HDResult = 0.06545527279376984
  reference = 0.06536787003278732
  check=true aborts with wrong Hausdorff distance
```

Goal5269 shows the threshold split:

```text
lb=0      correct
lb=32..1152 wrong same HDResult = 0.06545527279376984
lb=1280+  correct
lb=2048   check=true passes
```

But `lb=2048` is not the author Figure 6 setting and is not authorized as a
Figure 6 substitute.

Goal5270 records the exact-input blocker:

```text
/local/storage/shared/HDDatasets missing
/local/storage/shared/HDDatasets/graphics/dragon.ply missing
/local/storage/shared/HDDatasets/graphics/asian_dragon.ply missing
```

Therefore:

```text
Figure 6 reproduced = false
exact input blocker = true
Level-B pruning diagnostic allowed = true
lb=2048 substitute authorized as Figure 6 = false
```

Goal5271 builds the separately named Level-B diagnostic:

```text
EB time speedup vs NoOpt = 3.7885x
EB+Prune time speedup vs EB = 12.5707x
EB+Prune time speedup vs NoOpt = 47.6244x
EB ComparedPoints reduction vs NoOpt = 8.3905x
EB+Prune ComparedPoints reduction vs EB = 35.8027x
EB+Prune ComparedPoints reduction vs NoOpt = 300.4045x
```

These are candidate-level author profiling effects, not RTDL speedups and not
paper Figure 6 values.

## Critical Boundaries To Review

1. **Figure 6 script setting**
   - Author Figure 6 XHD setting is `eb=true, prune=true, lb=256`.
   - Current Level-B candidate fails correctness at `lb=256`.
   - Passing at `lb=2048` cannot be silently substituted.

2. **Exact input provenance**
   - Exact `/local/storage/shared/HDDatasets` graphics files are absent.
   - Current files are public/same-source Level-B candidates.
   - Matching point counts or close MBRs does not prove exact paper input
     identity.

3. **Diagnostic vs reproduction**
   - Goal5271 is useful pruning diagnostic evidence.
   - Goal5271 is not Figure 6 reproduction.
   - Its speedup/reduction factors are author candidate profiling effects, not
     author-vs-RTDL performance claims.

4. **RTDL scope**
   - Goals5268-5271 are primarily author-side/source/provenance diagnostics.
   - They do not prove RTDL implements Figure 6's full author XHD path.
   - They do not authorize full paper reproduction claims.

## Review Questions

1. Does Goal5268 correctly identify the author flags, script, and profiling
   fields needed for Figure 6-style evidence?
2. Are the noopt / eb / eb_prune profile counters and derived reductions
   correctly extracted?
3. Is it correct that the current Level-B candidate cannot reproduce Figure 6
   because `lb=256` is not correctness-clean?
4. Is it correct to forbid using `lb=2048` as a Figure 6 substitute even though
   it passes `check=true` on the candidate?
5. Does Goal5270 adequately prove that exact Figure 6 input paths are absent on
   the current POD?
6. Is Goal5271 correctly named and bounded as a Level-B pruning diagnostic, not
   Figure 6 reproduction?
7. Does the packet avoid author-vs-RTDL performance ratio, author RT-core
   equivalence, exact input identity, and full paper reproduction claims?
8. Should the next action be:
   - stop Figure 6 until exact inputs are available;
   - continue only a named Level-B diagnostic line;
   - or pivot to another full-paper blocker?
9. Are there any stale values, missing artifacts, or hidden overclaims?

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
  Q9: ...
recommended_next_action:
```

Possible verdict labels:

```text
approve_goals5268_5271_figure6_packet__level_b_diagnostic_only
revise_figure6_packet_claim_boundary_or_lb_substitute
block_figure6_packet_due_to_incorrect_counter_or_input_evidence
```
