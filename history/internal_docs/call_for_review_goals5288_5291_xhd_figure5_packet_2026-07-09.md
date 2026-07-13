# Call For Review - Goals5288-5291 X-HD Figure 5 Packet

Date: 2026-07-09

Please strictly review the current X-HD Figure 5 packet. This packet is meant
to decide what the project may honestly claim about Figure 5 at the current
state, and what the next Figure 5 action should be.

## Goals Under Review

```text
Goal5288 - Figure 5 Timing Denominator Audit
Goal5289 - Dragon -> AsianDragon Bounded Same-POD Probe
Goal5290 - Dragon -> AsianDragon Author-Value Precheck
Goal5291 - Dragon -> HappyBuddha Candidate Matrix
```

## Files Under Review

### Goal5288

```text
history/internal_docs/goal5288_xhd_figure5_timing_denominator_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_timing_denominator_audit.py
tests/goal5288_xhd_figure5_timing_denominator_audit_test.py
```

### Goal5289

```text
history/internal_docs/goal5289_xhd_figure5_bounded_same_pod_probe_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5289_figure5_bounded_same_pod_probe_2026-07-09.json
tests/goal5289_xhd_figure5_bounded_same_pod_probe_test.py
```

### Goal5290

```text
history/internal_docs/goal5290_xhd_figure5_graphics_author_value_precheck_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5290_figure5_graphics_author_value_precheck_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5290_author_value_probe_raw_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_graphics_author_value_precheck.py
tests/goal5290_xhd_figure5_graphics_author_value_precheck_test.py
```

### Goal5291

```text
history/internal_docs/goal5291_xhd_figure5_dragon_happy_candidate_matrix_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure5_dragon_happy_candidate_matrix.py
tests/goal5291_xhd_figure5_dragon_happy_candidate_matrix_test.py
```

Supporting artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_phase_matrix_goal5188_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
```

## Current Packet Summary

Goal5288 establishes that Figure 5 author logs have strong coverage:

```text
record_count = 2535
unique_pair_count = 507
complete_author_pair_count = 507
categories = BraTS2020_ValidationData, geo, graphics
author GPU in logs = NVIDIA GeForce RTX 3090
```

But Goal5288 also records that Figure 5 is not reproduced:

```text
brats_full_workload_gate_present = false
geo_full_workload_gate_present = false
figure5_full_matrix_gate_present = false
same_denominator_author_rtdl_performance = false
```

Goal5289 and Goal5290 stop the Dragon -> AsianDragon candidate:

```text
paper-log Dragon -> Asian HDResult = 0.06536811590194702
available unscaled POD author run = 52.4535
available scaled-1e-3 POD author run = 0.0654553
same-POD author X-HD/LB=256 scaled candidate = 0.06545527279376984
same-POD RTDL exact route scaled candidate = 0.06536787240753439
```

Decision:

```text
Dragon -> AsianDragon is not value-matched under available inputs.
Do not run more expensive RTDL timing on this candidate unless exact input
provenance or a value-matched conversion appears.
```

Goal5291 promotes Dragon -> HappyBuddha only as a Level-B value-matched
candidate:

```text
paper-log Dragon -> HappyBuddha HDResult = 0.12572969496250153
author rerun HDResult = 0.12572988867759705
RTDL route HDResult = 0.12572988629271128
tolerance = 1e-6
```

Decision:

```text
Dragon -> HappyBuddha is a value-matched Level-B same-source candidate.
It is not exact paper dataset reproduction.
It is not full Figure 5 reproduction.
No author-vs-RTDL ratio is authorized.
```

## Critical Boundaries To Review

1. **Value match vs exact input identity**
   - Dragon -> HappyBuddha values match within tolerance.
   - Exact paper input bytes / hashes are still unavailable.

2. **One graphics pair vs Figure 5**
   - Dragon -> HappyBuddha is one graphics pair.
   - Figure 5 includes BraTS, geo, and graphics categories.
   - This packet must not be interpreted as Figure 5 full reproduction.

3. **Timing denominators**
   - Paper logs use author internal `Running.AvgTime` / `ReportedTime` on RTX
     3090.
   - Author rerun evidence uses author internal timing and process wall on RTX
     4000 Ada.
   - RTDL evidence uses route/case/load/total timings.
   - A ratio is forbidden unless a separate review accepts a same-denominator
     boundary.

4. **Goal5211/5212 global-bound early-break caveat**
   - The current fast RTDL route preserves the directed-HD / max-nearest value.
   - `per_source_witness_exact=false` and roughly 409k sources early-abort.
   - This packet must not claim exact per-source witness reproduction.

## Review Questions

1. Does Goal5288 correctly characterize Figure 5 author-log coverage as complete
   for 507 author pairs across BraTS, geo, and graphics?
2. Is it correct that Goal5288 forbids a Figure 5 performance ratio under
   current evidence?
3. Do Goal5289 and Goal5290 correctly stop the Dragon -> AsianDragon candidate
   because the available author-side values do not reproduce the paper-log
   value?
4. Does Goal5291 correctly extract the Dragon -> HappyBuddha paper-log value
   and compare it to author rerun and RTDL route values?
5. Is Dragon -> HappyBuddha correctly classified as a Level-B same-source
   value-matched candidate?
6. Is it correct to keep exact paper dataset reproduction, full Figure 5
   reproduction, and full X-HD paper reproduction as false?
7. Are timing denominators separated clearly enough to forbid any
   author-vs-RTDL ratio from this packet?
8. Does the packet carry forward the global-bound early-break witness caveat
   strongly enough?
9. Should the next Figure 5 action be:
   - continue Figure 5 by acquiring / validating BraTS, geo, and exact graphics
     input provenance;
   - narrow to a reviewed graphics-only Level-B question;
   - or stop Figure 5 for now and pivot to Figure 6 phase/counter mapping?
10. Are there any overclaims, missing evidence, stale fields, or hidden
    denominator mismatches in the packet?

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
approve_goals5288_5291_figure5_packet__dragon_happy_level_b_candidate_only
revise_figure5_packet_claim_boundary_or_denominator
block_figure5_packet_due_to_value_or_evidence_error
```
