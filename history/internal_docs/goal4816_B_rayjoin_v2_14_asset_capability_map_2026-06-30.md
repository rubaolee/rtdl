# Goal4816-B RayJoin v2.14 Asset And Capability Map

Date: 2026-06-30

Status: `goal4816_B_capability_map_complete_pending_review`

Authorized by:

- `history/internal_docs/antigravity_goal4816_A_contract_extraction_review_2026-06-30.md`
- Verdict: `approve_goal4816_A_contract_extraction_authorize_4816_B`

This is a read-only inventory/classification step. It does not start
implementation, does not authorize POD performance runs, and does not authorize
changes to `src/rtdsl/**`, `src/native/**`, or the v2.14 release surface.

## Purpose

Goal4816-B answers one question:

> For RayJoin Section 5.7 Polygon Overlay, which stages can be built from
> existing RTDL v2.14 generic primitives plus explicit Numba continuation, which
> stages require bundled RayJoin helper code, and which stages are blocked by
> missing inputs or unresolved semantics?

This prevents three old failure modes:

1. treating bundled `rayjoin_overlay` code as generic RTDL language capability;
2. treating scalar LSI/PIP or candidate continuations as full overlay;
3. patching runtime/native code instead of recording a product/capability gap.

## Evidence Read For This Map

Repository files:

- `src/rtdsl/__init__.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/rayjoin_overlay.py`
- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/numba_partner_continuation.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

Historical evidence:

- `history/internal_docs/docs_reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.md`
- `history/release_reports/v2_14_internal_closeout_2026-06-30/rayjoin_author_vs_rtdl_caveat.md`
- `history/release_reports/v2_14_internal_closeout_2026-06-30/public_rt_vs_embree_comparison.md`

POD read-only input availability check:

- `/workspace/rayjoin_section57_data/cdb_topology/...`: current POD check found
  the old Goal4380 exact CDB root missing;
- `/workspace/rayjoin_section57_same_source_cdb/...`: current POD check found
  `dtl_cnty` and `USAZIPCodeArea` present;
- therefore current POD state is not identical to old Goal4380's 2/8 exact-ready
  artifact state.

No benchmark/performance command was run for this goal.

## Taxonomy

Every Section 5.7 stage is classified as one or more of:

- `existing_v2_14_primitive`
- `bundled_rayjoin_helper`
- `numba_partner_continuation`
- `paper_app_logic`
- `author_baseline_only`
- `missing_input`
- `missing_v2_14_capability`
- `unresolved_pip_tie_break_contract`

## Asset Inventory

### Public / Generic Prepared Primitives

| Asset | Location | Classification | Notes |
| --- | --- | --- | --- |
| `prepare_segment_pair_intersection_optix` | `src/rtdsl/optix_runtime.py`; direct import from `rtdsl.optix_runtime` | `existing_v2_14_primitive` | Prepared segment-pair intersection over right/build segments. Can count and, through supporting paths, produce pair rows. It is not currently a top-level `rtdsl.__init__` export. |
| `prepare_segment_pair_left_set_optix` | `src/rtdsl/optix_runtime.py`; used by examples/helper | `existing_v2_14_primitive` | Prepared left/query segment set for replay against prepared right/build segments. |
| `prepare_directed_segment_point_location_2d_optix` | `src/rtdsl/optix_runtime.py`; exported by `src/rtdsl/__init__.py` | `existing_v2_14_primitive` with RayJoin policy caveat | Public app-agnostic name for directed segment point-location. The implementation aliases the RayJoin CDB point-location pipeline and depends on env-supplied query-map/scale/tie policy. |
| `prepare_rayjoin_cdb_point_location_2d_optix` | `src/rtdsl/optix_runtime.py`; exported by `src/rtdsl/__init__.py` | `existing_v2_14_primitive` / RayJoin-CDB-specific primitive | It is exposed, but its name and record format are RayJoin CDB specific; do not call it proof of a general polygon overlay language. |
| `load_cdb`, `chains_to_*` helpers | `src/rtdsl/datasets.py`; exported by `src/rtdsl/__init__.py` | `existing_v2_14_primitive` / data helper | Useful for loading and deriving columns from CDB-like files; not the paper's ArcGIS-to-CDB preprocessing pipeline by itself. |

### Bundled RayJoin Helpers

| Asset | Location | Classification | Notes |
| --- | --- | --- | --- |
| `_run_lsi_rows` | `src/rtdsl/rayjoin_overlay.py` | `bundled_rayjoin_helper` | Wraps generic segment-pair primitive plus RayJoin overlay row reconstruction/pair dump behavior. |
| `_run_point_location_faces` | `src/rtdsl/rayjoin_overlay.py` | `bundled_rayjoin_helper` | Wraps directed point-location into RayJoin face-id arrays. |
| `_PreparedPointLocationRunner` | `src/rtdsl/rayjoin_overlay.py` | `bundled_rayjoin_helper` | Prepared helper used by overlay route; sets query-map/scale env and converts rows to face arrays. |
| `_assemble_output_chains` | `src/rtdsl/rayjoin_overlay.py` | `bundled_rayjoin_helper` / `paper_app_logic` | Implements RayJoin-like output-chain construction in Python. It is application logic, not a generic primitive. |
| `run_rayjoin_overlay_rtdl_from_cdb_paths` | `src/rtdsl/rayjoin_overlay.py` | `bundled_rayjoin_helper` | High-level bundled helper for RTDL's RayJoin overlay route. Calling it proves a shipped helper path, not generic user composition. |
| `rtdl_rayjoin_v2_spatial_join_app.py` front door | `examples/current/research_benchmarks/spatial_rayjoin/` | `bundled_rayjoin_helper` / benchmark app | Public research benchmark app surface; includes scalar/count, overlay-seed, and preview continuation paths with guarded claims. |

### Numba / Partner Continuation Assets

| Asset | Location | Classification | Notes |
| --- | --- | --- | --- |
| `execute_compact_mask_typed_stream_partner_columns` | `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`; exported | `numba_partner_continuation` when `partner="numba"` | Generic compact-mask typed-stream adapter. It is post-RT continuation only, not LSI/PIP traversal or overlay. |
| `run_numba_compact_mask_i64` | `src/rtdsl/numba_partner_continuation.py`; exported | `numba_partner_continuation` | Generic compact-mask CUDA path used by the typed-stream adapter. |
| `filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba` | `src/rtdsl/closed_shape_topology.py`; exported | `numba_partner_continuation` | Generic owner-face/side filtering over topology columns. Useful for app-owned continuation, not a full overlay solver. |
| `run_rayjoin_v2_6_numba_compact_mask_preview` | `examples/current/research_benchmarks/spatial_rayjoin/...` | `numba_partner_continuation` / preview | Explicitly marked preview, post-RT continuation, no paper reproduction or public speedup authorization. |
| `run_rayjoin_v2_9_numba_side_aware_topology_reference` | same example file | `numba_partner_continuation` / `paper_app_logic` | App-owned Numba reference over generic topology columns; not the promoted RTDL/OptiX overlay route. |

## Section 5.7 Stage Capability Map

| Stage | Required Section 5.7 behavior | Best existing v2.14 asset | Classification | Current status |
| --- | --- | --- | --- | --- |
| Paper CDB inputs | Exact preprocessed CDB pairs for all 8 Section 5.7 rows | Historical Goal4380 exact-ready artifacts for 2/8; current POD same-source has County x Zipcode only | `missing_input` for full 8/8 | Current POD does not have the old 2/8 exact root; it has same-source County x Zipcode. Full 8/8 is blocked by missing exact inputs. |
| CDB/topology loading | Read chain/face topology, points, segments, face ids | `load_cdb`, `load_cdb_overlay_packed_inputs` | `existing_v2_14_primitive` plus `bundled_rayjoin_helper` | Data loading exists. Exact paper preprocessing from raw ArcGIS/OSM to CDB is not solved by this alone. |
| LSI traversal | Query map segments as rays over `[0,1]`, exact segment intersection after RT candidate generation | `prepare_segment_pair_intersection_optix`, `prepare_segment_pair_left_set_optix` | `existing_v2_14_primitive` | Generic primitive exists for segment-pair intersection. Full overlay row reconstruction uses bundled helper `_run_lsi_rows`. |
| LSI row reconstruction | Materialize/derive pair rows and intersection coordinates for overlay | `_run_lsi_rows`, `_rows_from_segment_pair_ids` | `bundled_rayjoin_helper` / `paper_app_logic` | Exists as bundled helper. Not proof that generic users get full RayJoin overlay by primitive call alone. |
| Vertex PIP / point-location | Vertical ray point-location with face-id result for each vertex in both maps | `prepare_directed_segment_point_location_2d_optix`; `_PreparedPointLocationRunner` | primitive plus `bundled_rayjoin_helper` | Prepared primitive exists, helper produces face arrays. Exact author-clarified equal-height determinism is still a separate contract. |
| PIP SoS determinism | Author-reply `t_reported` perturbation for equal-height tie candidates | Current native has `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES` / `nextafterf(report_t,+inf)`, not the slope-dependent formula | `unresolved_pip_tie_break_contract` | Do not claim exact clarified author behavior until verified. Current code has a tie-related knob, but it is not the documented author-reply formula. |
| Midpoint projection | Sort intersections per edge, project midpoints between adjacent intersections | `_run_rayjoin_overlay_packed` internal logic | `bundled_rayjoin_helper` / `paper_app_logic` | Exists inside helper. No standalone generic public primitive identified for exact Section 5.7 midpoint projection. |
| Midpoint PIP | Locate midpoint pieces in opposite map | `_PreparedPointLocationRunner` reused inside helper | `bundled_rayjoin_helper` | Exists as part of bundled overlay route; exact deterministic PIP caveat carries forward. |
| Output-chain assembly | Split chains at intersections, flush output chains, assign face ids, write author format | `_assemble_output_chains`, `write_output_chains` | `bundled_rayjoin_helper` / `paper_app_logic` | Exists as Python helper. It is not a generic RTDL primitive and historically dominated large full-output paths. |
| Numba app continuation | User/application continuation over candidate columns or topology columns | compact-mask and owner-face/side Numba helpers | `numba_partner_continuation` | Useful for app-owned continuation stages. It does not replace LSI/PIP traversal or output-chain construction. |
| Author baseline | Original RayJoin C++/CUDA/OptiX source/binary | `/workspace/RayJoin_fresh` commit `02bf622...` | `author_baseline_only` | Source available; working tree dirty, so use `git show HEAD:<file>` for semantics. |

## Explicit Answers Required By Goal4816-B

### Is full 8/8 Section 5.7 blocked by missing inputs?

Yes. Historical Goal4380 had 2/8 exact-ready evidence, but the current POD check
did not find the old exact CDB root. The currently observed same-source root has
County x Zipcode only. Full 8/8 exact paper reproduction is blocked by missing
exact CDB inputs unless the exact CDBs are restored/acquired.

### Is author source/build access blocked?

No for source semantics. The source is available at `/workspace/RayJoin_fresh`,
commit `02bf6220d6d20b04af77ee20364eced75cc029c9`. The working tree is dirty, so
source semantics must be read through `git show HEAD:<file>`. This goal did not
test build/performance execution.

### Is generic-primitive + Numba full Section 5.7 currently proven feasible?

No. v2.14 has meaningful generic primitives and Numba continuations, but the
current complete overlay path relies on bundled RayJoin helper/application code
for row reconstruction, midpoint logic, and output-chain assembly. A future app
could attempt to reimplement those stages in user Python/Numba without runtime
edits, but that is not yet proven.

### Is bundled-helper bounded reproduction feasible?

Yes, as a bounded path. Goal4380 already showed 2/8 available-input overlay
evidence near local author process wall under its selected protocol. That path
must be labeled `bundled_rayjoin_helper` or benchmark-app helper evidence, not
generic language reproduction.

### Is PIP exact deterministic reproduction fully closed?

No. The author-reply summary requires slope-dependent `t_reported` perturbation.
Current RTDL native code has an `allow_equal_ties`/`nextafterf` tie knob, but
this is not the same formula and the bundled helper does not establish exact
author-clarified behavior. Treat this as `unresolved_pip_tie_break_contract`
until tested or otherwise proven.

## Recommended Next Step

Proceed to Goal4816-C only if reviewers accept this map. Goal4816-C should
design an app-only reproduction path with two explicitly separated routes:

1. `bundled_helper_bounded_available_input_reproduction_not_generic`: uses the
   existing RayJoin helper path and preserves the bounded claim.
2. `generic_primitive_numba_attempt`: uses generic prepared primitives plus
   user/application Python+Numba for continuation/output stages; any missing
   generic capability must be recorded rather than patched.

No POD performance run should start before Goal4816-C defines which route is
being tested.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   Not in this step. The map makes the uncomfortable distinction explicit:
   v2.14 has useful primitives, but full Section 5.7 currently flows through
   bundled RayJoin helper/application code.

2. **What would make this foolish?**
   It would be foolish to call `_run_lsi_rows` or `_assemble_output_chains`
   generic language capability, to claim Numba compact-mask preview as full
   overlay, or to hide the unresolved PIP tie-break contract.

3. **Is there another path that avoids being trapped in one bad idea?**
   Yes. Keep two routes separate: bounded bundled-helper reproduction versus
   generic-primitive + Numba attempt.

4. **Can I try a better path now?**
   Yes. Goal4816-C can now design those routes without touching runtime/native
   code, and can define correctness gates before any POD performance work.

## Exit Label

`goal4816_B_capability_map_complete_pending_review`
