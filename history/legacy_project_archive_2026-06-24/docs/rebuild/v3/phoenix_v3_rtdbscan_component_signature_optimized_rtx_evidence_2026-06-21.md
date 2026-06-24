# Phoenix V3 RTDBSCAN Component-Signature Optimized RTX Evidence

Status: optimized same-contract RTX evidence, row-scoped M7 approved.

This packet supersedes the earlier RTDBSCAN continuation-bottleneck no-go only
for the specific blocker `rtx_rerun_after_component_signature_optimization_missing`.
It does not authorize release wording by itself.

```text
status: rtdbscan_component_signature_optimized_rtx_evidence_m7_approved_row_scoped
generic_capability: component_union
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: true
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
m7_promotion_authorized: true
```

## Evidence Source

Remote RTX pod:

```text
host: root@213.173.108.14 -p 11592
gpu: NVIDIA RTX 4000 Ada Generation
remote artifact: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_rtdbscan_component_signature_optimized_20260621
```

Copied local artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_component_signature_optimized_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_component_signature_optimized_20260621/summary.md
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_component_signature_optimized_large_repeat5_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_component_signature_optimized_large_repeat5_20260621/summary.md
```

The pod route used the optimized same-contract path:

```text
optix_rt_core_flags_numba_prepared_grid_column_signature_3d
embree_core_flags_numba_prepared_grid_column_signature_3d
```

The optimized OptiX route records:

```text
column_signature_strategy: numba_label_count_and_flag_count_label_columns
column_signature_uses_numba_label_count_and_flag_count: true
column_signature_materializes_point_ids: false
column_signature_materializes_core_flags: false
```

## Result

The first rerun completed all 8 rows without failures:

```text
validation_reference_pass: true
large_signature_pass: true
serious_pair_count: 3
large_pair_count: 1
strongest_serious_optix_speedup_vs_embree: 1.2356860771339773
weakest_serious_optix_speedup_vs_embree: 1.1155694747358242
```

The follow-up repeat=5 rerun for the large rows repaired the external-review
repeat-count blocker:

```text
all_pairs_repeat5_warmup1: true
all_large_signatures_match: true
strongest_optix_speedup_vs_embree: 1.1235504150116034
weakest_optix_speedup_vs_embree: 1.1019949345652873
```

Current candidate pair table:

| Point count | Repeat | Embree sec | OptiX sec | OptiX speedup | RT-threshold speedup | Same signature | Continuation dominates OptiX |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4,096 | 3 | 0.018203578889369965 | 0.01088082417845726 | 1.6729963273748039x | 2.0495545408119726x | true | false |
| 65,536 | 5 | 0.389338705688715 | 0.3150789774954319 | 1.2356860771339773x | 1.2535332852701746x | true | false |
| 262,144 | 5 | 2.698013737797737 | 2.401328593492508 | 1.1235504150116034x | 1.2621183454676224x | true | true |
| 524,288 | 5 | 9.008331146091223 | 8.174566745758057 | 1.1019949345652873x | 1.4801367849201907x | true | true |

## Interpretation

This is a real improvement over the earlier no-go packet:

- the optimized route no longer materializes `point_ids` and `is_core` for the
  compact component signature;
- the serious same-contract rows now show a consistent full-path OptiX advantage
  over Embree on RTX hardware;
- the 4,096-point control passes CPU reference parity;
- the large rows preserve canonical component-size signature equality with
  repeat=5/warmup=1.

But the result remains narrow:

- this is a component-signature route, not full DBSCAN label publication;
- it is not RTDBSCAN paper reproduction;
- it is not a broad V3-over-V2 performance claim;
- it is not a full application benchmark claim;
- the large rows are checked by OptiX/Embree intra-run canonical
  component-signature agreement, not by an independent CPU reference;
- the dataset is a zero-noise four-cluster synthetic `clustered3d` case;
- at 262,144 and 524,288 points the Numba continuation still dominates the
  OptiX threshold phase.

## Candidate Boundary For Review

External review should decide whether this exact row can become an M7-qualified
row-scoped V3 claim:

```text
RTDL V3 includes a generic component-signature continuation route where
prepared OptiX fixed-radius threshold columns feeding the same Numba component
signature are 1.102x to 1.236x faster end-to-end than the same-contract Embree
route on zero-noise four-cluster synthetic clustered3d rows from 65,536 to
524,288 points on an RTX 4000 Ada pod; at 262,144 and 524,288 points, the Numba
continuation still dominates wall time.
```

If accepted, the wording must remain row-scoped. It must not become:

```text
RTDBSCAN is faster.
V3 is faster than V2.
RTDL reproduces the RTDBSCAN paper.
RT cores accelerate full DBSCAN end-to-end.
```

## Current Gate Reading

```text
local_evidence_sufficient_for_external_public_row_review: true
current_packet_external_review_status: claude_approved_after_repeat5_option_b
current_packet_2ai_consensus_status: claude_codex_consensus_complete
m7_promotion_authorized: true
row_scoped_public_speedup_claim_authorized: true
```

External review:

```text
docs/reviews/claude_phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_review_2026-06-21.md
docs/reviews/claude_phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_repeat5_final_review_2026-06-21.md
```

Codex consensus:

```text
docs/reviews/codex_phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2ai_consensus_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: promote exactly one `component_union` row-scoped M7 claim after
Claude approved the repeat=5 repair.

1. Was I foolish?

   No. The previous blocker was explicitly "rerun after optimization missing";
   that blocker is now addressed with RTX artifact evidence and external
   approval.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be converting a modest row-scoped
   speedup into a broad RTDBSCAN, paper, or V3-over-V2 claim.

3. Was there another path?

   Yes. I could keep RTDBSCAN closed as no-go despite the new evidence, or use
   Claude's narrower 65,536-only Option A. The repeat=5 repair supports the
   more useful Option B range.

4. Can I now try a different path that actually solves the problem?

   Yes. Update the generated M7 classification packet and wording gate so this
   row is machine-checked under the approved boundary.
