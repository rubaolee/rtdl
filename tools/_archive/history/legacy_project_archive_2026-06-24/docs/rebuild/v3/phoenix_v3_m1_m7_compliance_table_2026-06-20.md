# Phoenix V3 M1-M7 Compliance Table

Status: active Phoenix compliance table, updated 2026-06-21.

This file applies the formal Goal4392 V3 plan to the current Phoenix rebuild.
It answers:

```text
Which V3 gates are actually complete today, and which are only local prep or
internal evidence?
```

## Short Verdict

Phoenix has a real M1-M7 foundation, but it is not release-grade V3 yet.

Current state:

```text
M1 complete
M2 complete as no-execution skeleton
M3 partial: metadata complete, per-benchmark release evidence incomplete
M4 partial-plus: serious internal grouped-continuation pod evidence exists,
    including RTDBSCAN and RayDB reuse, but it is not M7 release evidence
M5 internal-author-complete: internal topology pod evidence exists for PIP,
    overlay same-contract rows, and RayJoin author-code timing; one bounded
    Spatial topology-stream supplemental row is in the current release surface
M6 row-scoped fused-partner closed: serious Barnes-Hut aggregate-frontier/vector
    rerun passed intake and exactly one fused-partner aggregate-frontier row is
    M7-qualified; prepared OptiX is still not the Barnes-Hut speed path
M7 partial: harness skeleton, serious benchmark artifacts, and a total row
    classification packet exist; twelve base-packet rows plus one bounded
    Spatial supplemental row are in the current surface, but release remains
    blocked
```

The current paired V2.14-vs-V3 result remains a release blocker for broad
timing superiority wording:

```text
Geomean V3 speedup vs V2.14: 1.012x
broad_v3_faster_than_v2_claim_authorized: false
```

## Compliance Table

| Goal4392 gate | Formal exit condition | Current evidence | Phoenix verdict | What must happen next |
| --- | --- | --- | --- | --- |
| M1 execution-graph IR design | Frozen design doc, static tests, no app-specific public API names, no native implementation, external Claude/Gemini review passed. | `goal4393_v3_0_m1_execution_graph_ir_design_2026-06-15.md`; `goal4393_3ai_consensus_v3_0_m1_execution_graph_ir_2026-06-15.md`; M1 tests. | Complete. | Keep M1 as the V3 contract authority. Do not bypass it with route-specific APIs. |
| M2 planner skeleton and validators | Minimum graph validator and plan object without app-specific lowering. | `goal4394_v3_0_m2_execution_graph_skeleton_2026-06-15.md`; `src/rtdsl/v3_0_execution_graph.py`; M2 tests. | Complete as no-execution skeleton. | Use M2 validators to reject route rows that lack named generic capabilities or have app-specific public/native names. |
| M3 residency and phase instrumentation | Timing and movement evidence first-class; CUDA event or Nsight evidence for GPU paths; Embree phase accounting for CPU paths; transfer/build/traversal/continuation phases separated. | `goal4395_v3_0_m3_instrumentation_2026-06-15.md`; `goal4401_v3_0_pod_evidence_probe_2026-06-15.md`; M10-M17 internal evidence. | Partial. Metadata and substrate evidence exist; per-benchmark M3-grade phase packets are not complete across release rows. | Every Phoenix P0 rerun must attach M3-grade phase and movement evidence, not only wall-clock ratios. |
| M4 generic fused continuation pilot | One generic fused continuation path on RTDBSCAN and one non-DBSCAN workload; same primitive reused without DBSCAN-specific names; OptiX, Embree, best partner, and Numba reference policy satisfied; hardware measurements with M3-grade accounting. | `goal4396_v3_0_m4_component_union_pilot_local_prep_2026-06-15.md`; M9/M10/M11/M18/M23/M28 Phoenix pod evidence in `phoenix_v3_m4_grouped_continuation_pod_evidence_2026-06-20.md`; Claude final review in `claude_phoenix_v3_m4_final_evidence_review_2026-06-20.md`; Codex 2-AI closure in `codex_phoenix_v3_m4_grouped_continuation_evidence_2ai_consensus_2026-06-20.md`. | Partial-plus. Serious internal M4 evidence exists at non-toy scale, but M10 is a non-clean pass with accounting warning and the evidence index keeps all public/release flags false. | Classify the M4 rows into the future M7 packet only after M10 warning handling, system-Python packaging repair or waiver, and final row-level release review. |
| M5 RayJoin point-location/topology pilot | PIP and overlay through generic face-id, point-location, compact, and topology streams; author code, RTDL OptiX, and RTDL Embree compared under same contract and separated timing basis. | `goal4397_v3_0_m5_topology_pilot_local_prep_2026-06-15.md`; Phoenix M5 topology pod evidence in `phoenix_v3_m5_topology_pod_evidence_2026-06-20.md`; evidence artifact `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620`; RayJoin author build evidence `docs/rebuild/v3/evidence/rayjoin_author_build_20260620`; author-code-complete 2-AI closure in `codex_phoenix_v3_m5_author_recovery_2ai_consensus_2026-06-20.md`; release-surface breadth gate in `phoenix_v3_release_surface_breadth_gate_2026-06-21.md`. | Internal-author-complete plus one bounded supplemental release-surface row. Internal PIP and overlay same-contract topology evidence exists, and exactly `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7` is now counted as a bounded supplemental row. RayJoin author RT is still faster on PIP, so this is not an `RTDL beats RayJoin` result and not paper reproduction. | Keep M5 public wording row-scoped; do not claim full spatial join, RayJoin paper reproduction, or broad V3-over-V2 speedup. |
| M6 aggregate-tree/frontier pilot | Barnes-Hut-style workloads as generic frontier, node summary, and vector accumulation graphs; traversal and continuation measured separately and together; no native Barnes-Hut force-law engine. | `goal4398_v3_0_m6_frontier_vector_pilot_local_prep_2026-06-15.md`; `goal4402_v3_0_m8_aggregate_frontier_measured_lowering_2026-06-15.md`; `phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md`; artifact `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620`; 2-AI closure in `codex_phoenix_v3_m6_barnes_hut_evidence_2ai_consensus_2026-06-20.md`; final fused-partner M7 candidate and consensus in `docs/reviews/codex_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2ai_consensus_2026-06-21.md`. | Row-scoped fused-partner closed. Serious 32,768 / 65,536 / 131,072-body rerun passed intake with four routes and checksum parity, and exactly `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped` is M7-qualified. Prepared RTDL/OptiX+Numba was slower than fastest fused Numba CUDA, so this is not a Barnes-Hut RT-core speedup result. | Keep Barnes-Hut wording scoped to fused partner weighted-vector aggregation; do not claim full force calculation, prepared OptiX superiority, automatic partner selection, or broad V3-over-V2 speedup. |
| M7 release-grade benchmark harness | Exact datasets, scripts, repeated runs, author-code timing basis, backend/partner disclosure, phase tables, fresh external review. | `goal4399_v3_0_m7_harness_local_prep_2026-06-15.md`; all-app calibrated evidence; same-hardware V2.14-vs-V3 evidence; wording gate; `phoenix_v3_m7_row_classification_packet_2026-06-20.md`; `phoenix_v3_release_surface_breadth_gate_2026-06-21.md`; `phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md`; `phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md`; `phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.md`; `phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md`; `phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.md`; `phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md`; `phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md`. | Partial but broad enough for the current surface: twelve base-packet rows plus one bounded Spatial supplemental row are qualified across 9 / 9 planned capability families. Release authorization remains false, and the thirteen-row installer/reproducibility scope extension is not externally reviewed yet. | Close the thirteen-row installer scope review and then obtain fresh aggregate release-readiness consensus before any release wording. |

## M8-M17 Carry-Forward

M8-M17 are useful for Phoenix, but they are internal architecture evidence:

- M8 proves measured native lowering can be wrapped honestly, but it is
  essentially parity and not a speedup result.
- M9 proves CuPy and Numba grouped-stream partner viability on the pod.
- M10 proves same-stream native-producer to partner-consumer handoff for a
  grouped-union route.
- M11 proves no hidden named-column movement in the measured continuation
  window for that pilot.
- M17 closes the partner-device-ray prepare-time host-bookkeeping debt for the
  hit-stream-safe path.
- Goal4414 3-AI midterm consensus accepts M1-M17 with boundary and authorizes
  continuing internal grouped-contract work, not public claims.
- Phoenix M4 pod evidence now adds M23 DBSCAN and M28 RayDB serious-scale reuse
  evidence, with M10 explicitly marked as a pass with accounting warning.
- RayDB M28 has a separate Claude/Codex 2-AI closure as internal generic
  grouped-reduction evidence only:
  `docs/reviews/codex_phoenix_v3_raydb_m28_grouped_reduction_2ai_consensus_2026-06-20.md`.
- Phoenix M5 pod evidence now adds PIP point-location, RayJoin author
  `query_exec`, and overlay active-count topology rows, with all release/public
  flags false.
- Phoenix M6 pod evidence now adds 32,768 / 65,536 / 131,072-body Barnes-Hut
  route-parity rows for aggregate-frontier/vector accumulation. It confirms
  fused Numba CUDA as the current fastest route on those rerun scales and keeps
  prepared OptiX bounded as device-column evidence, not RT-core speedup.

These artifacts should be cited as evidence for M3/M4 readiness and future P0
row design. They do not replace M7 release-grade benchmark evidence.

The current M7 row classification authority is the base packet plus the
release-surface breadth gate:

```text
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.md
```

The base packet records twelve M7-qualified rows. The release-surface breadth
gate adds one bounded Spatial supplemental row, yielding thirteen current
row-scoped/supplemental release-surface rows. All other route-map rows remain
internal, blocked, or candidate-only.

## Phoenix P0 Gate For Every Row

Every Phoenix row must name one generic capability:

- `aabb_candidate_stream`;
- `collision_flag_stream`;
- `grouped_reduction`;
- `component_union`;
- `compact_positive_stream`;
- `ranked_summary`;
- `threshold_summary`;
- `point_location_topology_stream`;
- `aggregate_frontier`;
- `vector_accumulation`;
- `prepared_graph_chunk`;
- `device_ray_hit_stream`.

Rows without a named generic capability are removed from Phoenix release
evidence.

Every Phoenix P0 row must also record:

- same-contract key;
- OptiX and Embree timing basis when backend comparison is used;
- partner name or `none`;
- Numba reference or written omission justification;
- phase split;
- host/device starting location;
- warmups, repeats, and statistic;
- correctness contract;
- claim flags, all false until M7 closes.

## Quantified Completion Criteria

The word `partial` is not allowed to remain vague. Phoenix must compute
completion against a fixed denominator after the route-to-generic-capability map
is built.

Until that route map exists, M3-M7 completion percentages are not release
numbers. The current conservative count is:

```text
Phoenix M7-qualified release rows: 13
```

That does not mean the existing evidence has no value. It means only the named
grouped-reduction, AABB, component-union, prepared-graph, threshold-summary,
collision-flag-stream, ranked-summary, and aggregate-tree fused partner exact
rows plus the bounded Spatial topology-stream supplemental row have been loaded
into the current release surface; release authorization and the thirteen-row
installer scope extension still need review.

Required completion metrics:

| Gate | Numerator | Denominator | Completion bar |
| --- | --- | --- | --- |
| M3 | P0 rows with phase-complete M3 instrumentation and movement/residency evidence. | All P0 rows in the route-to-generic-capability map. | 100% for release rows; partial rows stay internal. |
| M4 | Component-union or fused-continuation rows with RTDBSCAN plus at least one non-DBSCAN reuse row, best partner plus Numba reference or written omission, same-contract OptiX/Embree evidence, and M3 packets. | Required M4 fused-continuation rows named by the route map. | 100% of required M4 rows. |
| M5 | Topology rows with generic point-location/topology streams, same-contract RTDL OptiX and Embree rows, author-code timing basis when paper-style comparison is claimed, and M3 packets. | Required M5 topology rows named by the route map. | 100% of required M5 rows. |
| M6 | Aggregate-frontier/vector rows with traversal and continuation measured separately and together, same-contract RTDL OptiX and Embree rows, and M3 packets. | Required M6 aggregate-frontier rows named by the route map. | 100% of required M6 rows. |
| M7 | Rows satisfying M3-M6 as applicable plus exact dataset, script, hardware, warmups, repeats, statistic, backend/partner disclosure, correctness contract, and external review. | All rows proposed for Phoenix release evidence. | 100% before release wording. |

## Geomean Denominator Rule

The current broad V3-vs-V2.14 statement is tied to the original 46 comparable
same-metric rows in:

```text
docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md
```

That artifact's 1.012x geomean remains the broad-population figure until a new
full-population paired run supersedes it.

If Phoenix removes or demotes rows that lack a named generic V3 capability, any
new geomean over the remaining rows must be labeled as a subset geomean. It
must not replace the broad 46-row V3-vs-V2.14 result and must not be used for
broad V3 timing superiority wording.

## Next Work Queue

1. Build a machine-readable P0 route-to-generic-capability map.
2. Reject or demote rows that cannot map to a generic V3 capability.
3. Choose the first P0 pod rerun from a capability gap, not from the largest
   historical speedup.
4. Start with one of:
   - RTDBSCAN/grouped continuation for M4;
   - RayJoin topology stream for M5;
   - Barnes-Hut aggregate frontier/vector accumulation for M6.
5. Keep the current all-app evidence as serious candidate evidence, not release
   authorization.

## Goal-Level Decision Audit

Decision: use this M1-M7 table as Phoenix's current gate map.

1. Was I foolish?

   The corrected decision is not foolish. It prevents old local-prep milestones
   from being mistaken for release-grade completion.

2. What actions would make it foolish?

   Treating M4-M7 local prep, M8 parity lowering, or M10-M17 micro-evidence as
   public performance authorization would be foolish.

3. Was there another path?

   Yes. I could have jumped directly into pod tuning from the route matrix.
   That would repeat the route-first mistake.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is capability-first: map P0 rows to generic V3
   capabilities, then rerun only the rows that close a Goal4392 gate.
