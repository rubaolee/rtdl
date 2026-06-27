# Phoenix V3 Aggregate Release-Readiness Review — 13-Row / 9-Capability Surface

Date: 2026-06-22

```text
Reviewer: Claude
Verdict: `release_ready`
Scope: Phoenix V3 aggregate 13-row / 9-capability release-readiness packet.
```

---

## Summary

The 13-row / 9-capability Phoenix V3 surface is coherent, all technical
sub-reviews have been accepted, the installer scope has been reviewed and
closed, and no P0 or P1 blockers remain. Release is authorized for the exact
`source_tree_pod_gated_thirteen_row` scope defined below.

---

## Required Question Answers

### 1. Does the 13-row / 9-capability surface remove the old surface-width and missing-Spatial blocker?

Yes. The release-surface breadth gate records:

```text
m7_capability_family_count: 9
minimum_m7_capability_families_for_major_release: 9
missing_m7_capability_families: []
total_m7_row_count: 13
```

The new supplemental row
`point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`
was reviewed by Claude (`accept-with-amendments`) and Codex 2-AI consensus,
closing the `point_location_topology_stream` family gap. The surface integrity
manifest verifies all 13 rows have existing evidence, review, and consensus
paths, with all unsupported-claim flags blocked.

### 2. Does the reviewed `source_tree_pod_gated_thirteen_row` installer scope close the scoped installer/reproducibility blocker?

Yes. The install-reproducibility gate records:

```text
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row
source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true
aggregate_13_row_installer_scope_review_required: false
staged_gpu_pod_gate_available: true
```

The scope extension was reviewed by Claude (`accept-with-amendments-not-release`)
and Codex 2-AI consensus. The install-reproducibility blocker is closed for the
`source_tree_pod_gated_thirteen_row` scope. The installer requires the explicit
`--accept-experimental-pod-gate` flag, correctly preventing accidental
general-release invocation.

### 3. Remaining P0/P1 blockers?

None found.

**P0 scan:**
- Incorrect unsupported claims in current docs: **none** (wording gate passes,
  0 violations, all required claim strings present).
- Missing required capability families: **none** (9/9 covered).
- Broken or unreviewed installer: **installer reviewed and accepted**.
- Fabricated evidence: **all 13 integrity paths verified to exist**.

**P1 scan:**
- Scope ambiguity: **all release scope boundaries explicit and documented**.
- Hardware portability overclaim: **single-RTX hardware waiver reviewed**;
  `multi_gpu_performance_portability_claim_authorized: false`.
- Public speedup overclaim: **blocked**;
  `public_speedup_claim_authorized: false`.
- Broad V3-over-V2 speedup overclaim: **blocked**;
  `broad_v3_faster_than_v2_claim_authorized: false`.
- V4 / C ABI / embedding in V3 surface: **excluded**;
  `v4_cabi_embedding_out_of_v3_public_surface: true`.
- Package-install wording: **blocked**;
  `package_install_claim_authorized: false`.
- Doc alignment: **short user path restored**, wording gate scans current docs.

**Process note:** The two remaining gate blocking reasons
(`release_authorization_false`, `updated_thirteen_row_release_readiness_consensus_required`)
are satisfied by this verdict. There are no remaining substantive technical
blockers.

### 4. Required fixes before release

None. All previous P0 and P1 issues from prior reviews have been addressed:
- The missing Spatial topology-stream family is closed by the reviewed
  supplemental row.
- The installer scope mismatch (12-row → 13-row) has been reviewed and closed.
- The Hausdorff P0 repair was accepted.
- The secondary platform blocker is closed by a reviewed hardware-scope waiver.

### 5. Exact release authorization

**Authorized:**

Phoenix V3 may be released under the following exact conditions:

- **Scope**: `source_tree_pod_gated_thirteen_row`
- **Hardware**: Single NVIDIA RTX 4000 Ada SFF, driver 550.127.05, GPU pod
  environment
- **Installer**: `scripts/v3_install_gpu_pod_env.sh --accept-experimental-pod-gate`
- **Surface**: Exactly these 13 row IDs:
  ```text
  grouped_reduction_sum_scalar_broadcast_repeat100_262144
  grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups
  grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups
  aabb_candidate_stream_all_count_only_float32_32768
  aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50
  aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50
  rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02
  component_union_clustered3d_65536_524288_repeat5_row_scoped
  prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
  hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped
  collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped
  aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped
  point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7
  ```
- **Capability families**: 9 generic capability families as documented in the
  surface breadth gate (aabb_candidate_stream, aggregate_frontier,
  collision_flag_stream, component_union, grouped_reduction,
  point_location_topology_stream, prepared_graph_chunk, ranked_summary,
  threshold_summary)
- **Wording**: Must pass the current wording gate with 0 violations

### 6. Non-authorized claim boundaries

The following remain explicitly **forbidden** after this release authorization:

| Claim category | Status |
| --- | --- |
| Package-install wording (`pip install`, PyPI, conda) | **Forbidden** — `general_release_installer_ready: false` |
| Broad V3-over-V2 speedup ("V3 is faster than V2") | **Forbidden** — paired geomean 1.012x; `broad_v3_faster_than_v2_claim_authorized: false` |
| Public Spatial speedup claim | **Forbidden** — Spatial row is bounded supplemental only |
| RTDL-beats-RayJoin claim | **Forbidden** — not supported by current evidence |
| True zero-copy product claim | **Forbidden** — internal accounting, not product wording |
| C ABI / embedding claim | **Forbidden** — out of V3 public surface |
| Multi-GPU / hardware portability claim | **Forbidden** — `secondary_multi_gpu_portability_false: true` |
| Whole-app RayDB / RTDBSCAN / RTNN / Triangle / Spatial claims | **Forbidden** — row-scoped only |
| App-specific native engine claims | **Forbidden** — rows are generic capability rows |
| V4 in V3 surface | **Forbidden** — quarantined under history |
| Count-only rows as throughput claims | **Forbidden** — `aabb_count_only` is count path, not intersection throughput |

---

## Findings by Severity

### No P0 findings

No P0 issues found. All critical claim boundaries are enforced by machine gates,
not only prose discipline.

### No P1 findings

No P1 issues found. The following items were checked and are satisfactory:

1. **Spatial row scope**: The `point_location_topology_stream` supplemental row
   uses a guarded squared-boundary prefilter path. The review correctly keeps
   this from becoming a general Spatial speedup claim. The naming convention
   (`guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`)
   encodes the exact scope.

2. **1.012x paired geomean**: The same-RT-hardware paired report is honest about
   the raw timing geomean. The claim boundaries correctly prevent this from
   being presented as a speedup story. The V3 value proposition is cleaner
   API surface and route health, not raw timing dominance.

3. **Single-hardware scope**: The RTX 4000 Ada pod restriction is clearly
   documented, the waiver is reviewed, and portability claims are blocked.
   This is not a defect in the evidence — it is an honest statement of scope.

4. **Installer gate flag**: The `--accept-experimental-pod-gate` flag requirement
   is appropriate for the current scope. It prevents misuse as a general
   package installer.

5. **Barnes-Hut future work**: The `barnes_hut_vector_accumulation_frontier_shape`
   future work item is correctly recorded as future research, not an active
   promotable queue item.

### Observations (no severity — informational)

- The full V3 rebuild matrix (103 modules / 503 tests OK) provides strong local
  health evidence. It is not release authorization by itself, but it supports
  confidence in the current surface.
- The objective conformance gate satisfying all 5 required capability objectives
  (RayDB grouped-reduction, RTDBSCAN component-union, Spatial topology-stream,
  Triangle prepared-graph, RTNN ranked-summary) verifies the original design
  intent is met.
- The wording gate at `final_public_surface_claim_boundary_gate` level with 0
  violations means the current docs are safe to expose at release time.

---

## Goal-Level Decision Audit

1. **Was I foolish?** No. I read the actual gate JSON files rather than
   accepting the stale memory note or the gate's self-reported blocked status
   at face value. I verified that the only remaining gate blockers are the
   circular `release_authorization_false` and the process requirement
   `updated_thirteen_row_release_readiness_consensus_required`, neither of which
   reflects a substantive technical defect.

2. **What actions would have been foolish?**
   - Issuing `approve_blocked_not_release` out of caution without naming a
     specific remaining substantive blocker would have been process theater.
   - Issuing `release_ready` without reading the gate files would have been
     irresponsible.
   - Accepting the `codex_fallback_consensus` verdict as sufficient rather than
     providing a genuine independent review would have violated the intake guard
     intent.

3. **Was there another path?** Yes — I could have deferred with
   `approve_blocked_not_release` and asked for further documentation. That would
   only be correct if I had identified a specific substantive defect. I found
   none.

4. **Can I try a different path now?** The correct path was taken. The 13-row
   surface is coherent, the claim boundaries are enforced, and the scoped
   release is responsible. `release_ready` is the accurate verdict.
