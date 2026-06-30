# Goal4816-B RayJoin v2.14 Capability Map Review

- **Date:** 2026-06-30
- **Reviewer:** Antigravity (AI Coding Assistant)
- **Review Target:** [goal4816_B_rayjoin_v2_14_asset_capability_map_2026-06-30.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4816_B_rayjoin_v2_14_asset_capability_map_2026-06-30.md)
- **Verdict:** `approve_goal4816_B_capability_map_authorize_4816_C`

---

## Verdict Description
The **Goal4816-B** asset and capability mapping is exceptionally thorough, accurate, and honest. It maintains documentation and code integrity by clearly separating the generic primitive structures of RTDL v2.14 from application-specific bundled helpers and Numba partner continuations. The map correctly identifies the key differences between the current native implementation's tie-handling knob and the author-reply determinism contract, and accurately accounts for the missing preprocessed inputs in the current POD workspace. Therefore, the capability map is approved, and **Goal4816-C** is authorized to proceed under the recommended app-only routes.

---

## Findings

### P2 Findings (Minor / Informational)
- **F-01: Minor Export Typo in LSI Primitive Metadata:**
  The asset capability map states that `prepare_segment_pair_intersection_optix` is exported by [__init__.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/__init__.py). However, a codebase audit shows that this primitive is not imported or exported in [__init__.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/__init__.py). Instead, it must be imported directly from its defining module [optix_runtime.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py).
  *Recommendation:* Correct the location notes in a future documentation revision. This is a minor metadata typo that does not impact execution semantics or the validity of the taxonomy.

---

## Answers to the 10 Specific Questions

### 1. Does the map correctly separate `existing_v2_14_primitive`, `bundled_rayjoin_helper`, `numba_partner_continuation`, `paper_app_logic`, `missing_input`, and `unresolved_pip_tie_break_contract`?
Yes. The map defines a clean 8-part taxonomy that covers all of these classifications and applies them systematically to individual code assets and overall Section 5.7 stages.

### 2. Does it correctly classify `prepare_segment_pair_intersection_optix` and `prepare_segment_pair_left_set_optix` as generic/existing prepared LSI primitives while classifying `_run_lsi_rows` as bundled RayJoin helper row reconstruction?
Yes. Both `prepare_segment_pair_intersection_optix` and `prepare_segment_pair_left_set_optix` in [optix_runtime.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py) are classified as `existing_v2_14_primitive`. The helper `_run_lsi_rows` in [rayjoin_overlay.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py) is correctly classified as a `bundled_rayjoin_helper` because it wraps the primitives with RayJoin-specific row reconstruction and intersection coordinate materialization logic.

### 3. Does it correctly classify `prepare_directed_segment_point_location_2d_optix` as an exposed directed point-location primitive with RayJoin policy caveats, while classifying `_PreparedPointLocationRunner` as bundled helper?
Yes. The asset `prepare_directed_segment_point_location_2d_optix` in [optix_runtime.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py) is classified as `existing_v2_14_primitive` with a RayJoin policy caveat since it aliases the RayJoin CDB pipeline and relies on environment-supplied parameters. The context manager `_PreparedPointLocationRunner` is classified as `bundled_rayjoin_helper`.

### 4. Does it correctly avoid claiming the current native `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES` / `nextafterf` behavior as the author's slope-dependent `t_reported` formula?
Yes. The capability map lists the PIP SoS determinism stage under the taxonomy `unresolved_pip_tie_break_contract`. It explicitly notes that the native `allow_equal_ties` implementation relies on `nextafterf(report_t, +inf)` to bypass strict pruning rather than the author-reply slope-dependent perturbation formula.

### 5. Does it correctly state that full 8/8 Section 5.7 remains blocked by missing exact CDB inputs in the current POD state?
Yes. The map states that the current POD check found the historical Goal4380 exact CDB root missing and only contains same-source County x Zipcode data. Thus, full 8/8 Section 5.7 reproduction remains blocked and is classified as `missing_input`.

### 6. Does it correctly preserve historical Goal4380 as 2/8 bounded evidence and avoid treating it as full reproduction?
Yes. The map preserves Goal4380 as 2/8 bounded available-input evidence near the process wall, explicitly warning that it must not be treated as a full reproduction or proof of hot-compute parity.

### 7. Does it correctly state that generic-primitive + Numba full Section 5.7 is not yet proven, while bundled-helper bounded reproduction is feasible?
Yes. The map explains that because the complete overlay path currently relies on bundled helpers for row reconstruction, midpoint projection, and chain assembly, the generic-primitive + Numba route is unproven. It confirms that bounded reproduction using the bundled helpers is feasible (as demonstrated by Goal4380).

### 8. Does the recommended Goal4816-C split into two routes prevent hidden runtime edits and bundled-helper laundering?
Yes. The split forces the separation of the bundled helper route (`bundled_helper_bounded_available_input_reproduction_not_generic`) from the generic primitive attempt (`generic_primitive_numba_attempt`). It requires any missing generic capability to be recorded as a gap rather than patched in the runtime, preventing laundered claims.

### 9. Are any claimed assets misclassified, missing, or overstated?
No. Every asset listed in the inventory corresponds to actual source definitions in the codebase and is accurately classified based on its actual generic reuse potential versus specialized application-bound nature.

### 10. Should Goal4816-C be authorized as an app-only design goal, or must Goal4816-B be amended first?
Goal4816-C is authorized to proceed as an app-only design goal. Goal4816-B has successfully satisfied all mapping goals and requires no amendments.

---

## Authorization Statement
Goal4816-C is **authorized** to proceed as an app-only design goal. Any plan created under Goal4816-C must explicitly separate the two execution routes (`bundled_helper_bounded_available_input_reproduction_not_generic` and `generic_primitive_numba_attempt`) and establish rigorous correctness gates before executing any benchmark runs on the POD.

---

## Non-Authorization Block
This review does **NOT** authorize:
1. Modifying any files under `src/rtdsl/**`, `src/native/**`, or the v2.14 release surface.
2. Running any POD performance or benchmark execution experiments.
3. Adding any new RayJoin-specific RTDL runtime primitives.
4. Presenting bundled-helper output as a generic RTDL language reproduction.
5. Treating scalar LSI/PIP, Numba compact-mask, or side-aware topology preview as a full polygon overlay reproduction.
6. Claiming full 8/8 Section 5.7 reproduction based on the current 2/8 evidence.
