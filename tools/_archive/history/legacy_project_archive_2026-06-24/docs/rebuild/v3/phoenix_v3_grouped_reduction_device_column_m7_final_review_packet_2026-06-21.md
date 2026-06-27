# Phoenix V3 Grouped-Reduction Device-Column M7 Final Review Packet

Packet path: `docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md`

Status: grouped_reduction_device_column_scoped_row_evidence_not_release.

```text
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: true
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
m7_promotion_authorized: true
Phoenix scoped row-evidence rows from this packet: 2
```

## Candidate Rows

| Candidate row id | Rows | Groups | Logical rays | Host-packed OptiX/device-column OptiX cold+loop | Embree/device-column OptiX cold+loop | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups | 262,144 | 1,024 | 38,043,648 | 3.599x | 100.019x | m7_row_evidence_scoped_not_release_after_claude_codex_consensus |
| grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups | 524,288 | 2,048 | 76,087,296 | 73.586x | 174.645x | m7_row_evidence_scoped_not_release_after_claude_codex_consensus |

These rows are exact `cupy_device_columns` prepared grouped_sum candidates. They
do not replace the existing host-packed/scalar-broadcast M7 row.

## Phase Attribution

The cold-prepare win includes workload-build/input-path collapse, ray-batch
preparation, native prepare, and other measured cold setup. It must not be
described as only ray-batch preparation.

| Candidate row id | Host/device workload build | Host/device ray-batch prepare | Note |
| --- | ---: | ---: | --- |
| grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups | 32.466x | 5.538x | At 262,144 rows both workload_build_sec and prepared_ray_batch_sec improve materially. |
| grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups | 1362.274x | 8.243x | At 524,288 rows the largest cold-prepare win is mostly workload_build_sec collapsing from host-packed ray materialization to deferred device columns. |

## Source Provenance

The raw POD evidence JSONs do not have a git HEAD:

```text
fatal: not a git repository (or any of the parent directories): .git
```

Source traceability is therefore:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/source_manifest.sha256
```

Manifest entries:

```text
c1cc6ce99096d1d12968d44a890518b8dc8a8cb212b7bf31cf578c9a0b221e20  VERSION
218d58519fd0e13ba0dad4049d3e06f11f863e03772f157e2ebfac88e93fa93c  src/rtdsl/optix_runtime.py
df703fa260488258ee4db68ab1fcf795ae6edf2ed50f5c89f0b18a7071f18c80  examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
3eed5a1bf688a2cc7da6c66cbe4ce23ea3884949275a44fc5e3a8942993f36c7  scripts/v3_0_m28_raydb_prepared_grouped_refresh.py
```

Manifest scope note:

```text
The remote pod directory was not a git checkout. The source manifest hashes the runtime, benchmark app, VERSION, and measured M28 benchmark entry point, but not the local orchestration wrappers. Claude accepted this as a traceability gap rather than an integrity failure for this run; future reruns should expand the manifest scope.
```

## Public Wording

Current wording status:

```text
claude_external_approve_with_required_fixes_p1_applied_2026-06-22
claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22
```

Approved wording:

```text
For a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada Generation pod, 262,144 rows / 1,024 groups, 38,043,648 logical rays, warmup=3 and actual repeat=100, RTDL's OptiX route prepared the ray batch from cupy_device_columns with host_packed_ray_count=0. Compared with the host-packed OptiX route, cold prepare plus the measured repeat100 loop was 3.599x faster. Embree remains the host-packed route while the OptiX candidate uses cupy_device_columns; under that same grouped_sum contract, the OptiX device-column route was 100.019x faster than Embree for cold prepare plus repeat100 loop. That Embree/device-column ratio is same-contract context, not a pure backend-only ratio. This is a row-scoped prepared grouped_reduction result, not a whole-app, whole-database, true_zero_copy_authorized, or broad V3-over-V2 speedup claim.

For a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada Generation pod, 524,288 rows / 2,048 groups, 76,087,296 logical rays, warmup=3 and actual repeat=100, RTDL's OptiX route prepared the ray batch from cupy_device_columns with host_packed_ray_count=0. Compared with the host-packed OptiX route, cold prepare plus the measured repeat100 loop was 73.586x faster. Embree remains the host-packed route while the OptiX candidate uses cupy_device_columns; under that same grouped_sum contract, the OptiX device-column route was 174.645x faster than Embree for cold prepare plus repeat100 loop. That Embree/device-column ratio is same-contract context, not a pure backend-only ratio. This is a row-scoped prepared grouped_reduction result, not a whole-app, whole-database, true_zero_copy_authorized, or broad V3-over-V2 speedup claim.
```

## P1 Review Fixes

- approved public wording states that Embree remains host-packed while the OptiX candidate uses cupy_device_columns
- approved public wording frames Embree/device-column ratios as same-contract context, not pure backend-only ratios
- 218.248x appears only as a labeled cold-prepare phase ratio near workload-build/input-path-collapse attribution, not as a headline/public row claim
- real Claude external review supersedes the earlier Codex-subagent-only procedural gap
- source manifest scope explicitly records that orchestration wrappers are not hashed and that the manifested M28 script is the measured benchmark entry point

## Promotion Conditions

- `external_public_row_review_closed_by_claude_external_review`
- `2_ai_consensus_closed_by_claude_codex`
- `prior_subagent_only_gap_superseded_by_real_claude_review`
- `p1_wording_fix_embree_context_applied`
- `p1_wording_fix_218x_not_headline_applied`
- `p1_source_manifest_orchestration_scope_acknowledged`
- `source_manifest_traceability_recorded`
- `missing_git_head_acknowledged`
- `exact_device_column_row_identities_recorded`
- `phase_attribution_not_only_ray_batch_preparation`
- `whole_app_and_broad_v3_over_v2_claims_remain_false`

## Remaining Boundaries

- release_authorized remains false
- public_speedup_claim_authorized remains false for broad/global V3 claims
- whole_app_speedup_claim_authorized remains false
- broad_v3_faster_than_v2_claim_authorized remains false
- true_zero_copy_authorized remains false
- the existing host-packed/scalar-broadcast row is retained and not silently replaced

## Forbidden Public Wording

- Do not claim: V3 is 218x faster
- Do not claim: RTDL is 218x faster end to end
- Do not claim: RayDB is universally accelerated
- Do not claim: true zero-copy is proven
- Do not claim: all grouped_reduction rows are public claims
- Do not claim: the old grouped_reduction M7 row has been replaced
- Do not claim: the Embree/device-column ratios are pure backend-only ratios

## Review Targets

External review target:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md
```

External AI blocked note:

```text
docs/reviews/external_ai_blocked_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
```

Codex consensus target:

```text
docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_claude_supersession_consensus_2026-06-22.md
```

Prior substitute review, kept as historical but superseded:

```text
docs/reviews/codex_subagent_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2ai_consensus_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: promote both exact cupy_device_columns grouped_sum rows as supplemental row-scoped M7 evidence after real Claude external review, P1 fixes, and Codex supersession consensus

1. Was I foolish?
   No for this corrected decision. It replaces the old Codex-subagent-only procedural gap with a real Claude external review, applies the required P1 fixes, and still keeps V3 release, true_zero_copy_authorized, whole-app, and broad V3-over-V2 claims false.
2. If yes, what actions made the decision foolish?
   It would be foolish to headline the 218.248x cold-prepare phase ratio, call the Embree/device-column comparison pure backend-only, or imply that two grouped_sum rows finish the V3 release.
3. Was there another path that would have avoided getting stuck on that idea?
   Keep the rows pending because the old packet used a Codex subagent. That would be procedurally safer than pretending subagent review was enough, but now the real Claude review lets us close the gap directly.
4. Can I now try a different path that actually solves the problem?
   Record Claude's superseding external review, keep the old subagent route as historical, promote only the exact rows, update global M7 classification, and continue the generic-engine queue.
