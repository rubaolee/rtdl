# Phoenix V3 Hausdorff Threshold-Summary Repeat=5 RTX Evidence

Status: repeat=5 same-contract RTX evidence, row-scoped M7 approved.

This packet supersedes the old Hausdorff threshold-summary boundary only for
the blockers `repeat1_no_multi_run_variance_evidence` and
`no_current_rtx_pod_rerun`. It does not authorize M7, release, whole-app, or
paper-reproduction wording by itself.

```text
status: hausdorff_threshold_summary_repeat5_rtx_evidence_m7_approved_row_scoped
generic_capability: threshold_summary
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: true
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
full_hausdorff_witness_claim_authorized: false
m7_promotion_authorized: true
```

## Evidence Source

Remote RTX pod:

```text
host: root@213.173.108.14 -p 11592
gpu: NVIDIA RTX 4000 Ada Generation
remote artifact: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_hausdorff_threshold_summary_repeat5_20260621
```

Copied local artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_repeat5_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_repeat5_20260621/summary.md
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_large_stability_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_large_stability_20260621/summary.md
```

The rerun used the same prepared fixed-radius threshold-decision contract for
both backends:

```text
--optix-summary-mode directed_threshold_prepared
--hausdorff-threshold 0.4
--repeat 5
--warmup 1
```

The OptiX rows additionally required:

```text
--require-rt-core
```

Oracle definition:

```text
The oracle is expected_tiled_hausdorff(copies=N): the app computes the exact
Hausdorff summary on the four-point authored base fixture using brute force,
then scales deterministic row-count metadata by N because the benchmark input
is a tiled repetition of that fixture. The threshold-summary route checks both
directed fixed-radius decisions against oracle_within_threshold =
oracle["hausdorff_distance"] <= threshold.
```

Prepared-mode timing definition:

```text
directed_threshold_prepared uses prepared fixed-radius threshold traversal for
the hot query phase. The reported phase-total metric still includes input
construction, scene preparation, the sum of directed query medians, Python
postprocess, and validation. Scene preparation is not excluded from the
phase-total claim.
```

## Result

All pairs completed successfully:

```text
all_pairs_match_oracle: true
all_pairs_same_decision: true
all_pairs_repeat_warmup: true
strongest_query_optix_speedup_vs_embree: 1.8914684826636867
weakest_query_optix_speedup_vs_embree: 1.6854780771390951
strongest_phase_total_optix_speedup_vs_embree: 1.2643173197147244
weakest_phase_total_optix_speedup_vs_embree: 0.5832587404633324
```

| Copies | Points in A | Points in B | Repeat | Embree query sec | OptiX query sec | Query OptiX/Embree | Embree phase total sec | OptiX phase total sec | Phase-total OptiX/Embree | Wrapper OptiX/Embree | Oracle |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 16,384 | 65,536 | 65,536 | 5 | 0.495685674 | 0.262063935 | 1.891468x | 1.032692268 | 1.770556010 | 0.583259x | 1.146542x | true |
| 65,536 | 262,144 | 262,144 | 5 | 2.130100906 | 1.163202390 | 1.831238x | 4.395329364 | 4.418867908 | 0.994673x | 1.377555x | true |
| 262,144 | 1,048,576 | 1,048,576 | 5 | 10.239592515 | 6.075185820 | 1.685478x | 19.904695973 | 15.743433759 | 1.264317x | 1.588497x | true |

## P0 Stability Repair

Claude's first review required stability data before any authorization flag
could be flipped. I reran the largest candidate as five independent paired
process samples on the same RTX 4000 Ada pod. Each sample still used
repeat=5/warmup=1 internally.

Artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_large_stability_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_large_stability_20260621/summary.md
```

Stability summary:

```text
all_pairs_match_oracle: true
all_pairs_same_decision: true
all_phase_total_pairs_above_1x: true
weakest_phase_total_optix_speedup_vs_embree: 1.2243669013234328
phase_total_ratio_mean: 1.240042444838897
phase_total_ratio_stddev: 0.01179874030631055
query_ratio_mean: 1.6386841066991966
query_ratio_stddev: 0.020920743964462737
wrapper_ratio_mean: 1.5558395967131606
wrapper_ratio_stddev: 0.015463555481955769
```

| Sample | Query OptiX/Embree | Phase-total OptiX/Embree | Wrapper OptiX/Embree | Oracle |
| ---: | ---: | ---: | ---: | --- |
| 1 | 1.632712x | 1.224367x | 1.548646x | true |
| 2 | 1.675899x | 1.254087x | 1.583280x | true |
| 3 | 1.626931x | 1.243634x | 1.547965x | true |
| 4 | 1.629953x | 1.246100x | 1.552223x | true |
| 5 | 1.627925x | 1.232025x | 1.547083x | true |

## Interpretation

This is useful V3 evidence for a reusable threshold-summary route:

- OptiX is consistently faster than Embree for the measured query phase.
- The exact threshold decision matches the oracle for all tested rows.
- The run uses repeat=5/warmup=1 on the current RTX pod instead of the earlier
  repeat=1 artifact.
- The largest row is faster in query, phase total, and wrapper time.

But the evidence remains mixed:

- the 65,536-points-per-side row is slower in phase total because OptiX scene
  preparation dominates;
- the 262,144-points-per-side row is phase-total parity, not a clear phase-total
  win;
- only the 1,048,576-points-per-side row is a clear phase-total win;
- this is threshold-decision evidence, not full exact Hausdorff distance or
  witness materialization.
- all evidence is from one RTX 4000 Ada pod;
- the claim is only for threshold 0.4;
- the claim is only for the prepared threshold-summary contract, whose
  phase-total metric still includes scene preparation.

## Candidate Boundary For Review

External review should decide whether this exact large row can become a
row-scoped M7 V3 claim:

```text
RTDL V3 includes a generic Hausdorff threshold-summary route where, at
1,048,576 points per side and threshold 0.4 on a single RTX 4000 Ada pod,
prepared OptiX fixed-radius threshold decisions beat the same-contract Embree
route across five independent paired process samples: query speedup mean
1.639x, phase-total speedup mean 1.240x (phase-total includes scene
preparation), weakest phase-total speedup 1.224x, with repeat=5/warmup=1
inside each sample. Smaller rows in the same rerun are query wins but not
phase-total wins.
```

If accepted, the wording must remain row-scoped. It must not become:

```text
RTDL computes full Hausdorff faster.
Hausdorff V3 is faster end to end.
X-HD is reproduced.
V3 is faster than V2.
OptiX is faster for all Hausdorff scales.
OptiX is faster for all threshold values.
OptiX is faster for all RTX GPUs.
```

## Current Gate Reading

```text
local_evidence_sufficient_for_external_public_row_review: true
current_packet_external_review_status: claude_approved_after_p0_repair_and_scene_prepare_wording
current_packet_2ai_consensus_status: claude_codex_consensus_complete
m7_promotion_authorized: true
row_scoped_public_speedup_claim_authorized: true
```

External review:

```text
docs/reviews/claude_phoenix_v3_hausdorff_threshold_summary_repeat5_m7_review_2026-06-21.md
docs/reviews/claude_phoenix_v3_hausdorff_threshold_summary_p0_repair_final_review_2026-06-21.md
```

Codex consensus:

```text
docs/reviews/codex_phoenix_v3_hausdorff_threshold_summary_p0_repair_2ai_consensus_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: send only the large threshold-summary row for external row-scoped M7
review, while keeping smaller rows blocked.

1. Was I foolish?

   No. The evidence repairs the old repeat and RTX blockers, but the mixed
   phase-total rows make all-scale promotion unsafe.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be promoting all Hausdorff
   threshold-summary rows from query speedup alone.

3. Was there another path?

   Yes. I could keep the entire Hausdorff capability blocked without review.
   That would be safer but would waste the large-row phase-total evidence now
   available.

4. Can I now try a different path that actually solves the problem?

   Yes. The correct path is external review of exactly the large row, followed
   by either row-scoped classification or an explicit no-go boundary.
