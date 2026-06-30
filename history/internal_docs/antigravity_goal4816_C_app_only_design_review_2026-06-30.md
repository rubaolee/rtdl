# Goal4816-C RayJoin Section 5.7 App-Only Reproduction Design Review

- **Date:** 2026-06-30
- **Reviewer:** Antigravity (AI Coding Assistant)
- **Review Target:** [goal4816_C_rayjoin_app_only_reproduction_design_2026-06-30.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4816_C_rayjoin_app_only_reproduction_design_2026-06-30.md)
- **Verdict:** `approve_goal4816_C_app_only_design_authorize_4816_D`

---

## Verdict Description
The **Goal4816-C** reproduction design is approved. The design correctly and strictly enforces the role constraint of the agent as an RTDL user/application author rather than an RTDL runtime developer. By explicitly splitting the implementation into Route 1 (bundled helper bounded reproduction) and Route 2 (generic primitive + Numba attempt), it prevents the laundering of private helpers as generic capabilities. Furthermore, it accurately identifies key v2.14 limitations (such as the LSI row/coordinate output gap) as capability gaps rather than proposing undocumented runtime modifications. The correctness gates are robust and set appropriate verification boundaries prior to any preflight execution. Thus, **Goal4816-D** is authorized to proceed as a correctness preflight plan.

---

## Findings

### P2 Findings (Minor / Informational)
- **F-01: Portable Path Handling for Windows/Linux Environments:**
  The design document references Unix-style paths such as `/workspace/rayjoin_section57_same_source_cdb` for same-source CDB inputs. Since the local workspace is on a Windows OS (`C:\Users\Lestat\...`), the preflight scripts designed in Goal4816-D must use Python's `pathlib.Path` or environment variables to resolve these paths dynamically across different operating systems.
- **F-02: GPU and OptiX Preflight Dependency Check:**
  Both routes depend on the OptiX backend and custom CUDA/Numba components. Goal4816-D must specify an early validation step in the preflight plan to ensure CUDA, driver libraries, and the OptiX SDK context are properly configured on the execution host before running the smoke tests.

---

## Answers to the 10 Specific Questions

### 1. Does the design correctly enforce the role constraint that the agent is an RTDL user/application author, not an RTDL developer?
Yes. The design document sets forth explicit guidelines in the "Role Constraint: RTDL User, Not RTDL Developer" section. It bans patching, extending, or modifying any RTDL runtime/native code, and forbids treating private underscored helper functions as public user APIs. Gaps must be reported as gaps (`missing_v2_14_capability`, etc.) rather than hidden with runtime edits.

### 2. Does it prohibit modifications to `src/rtdsl/**`, `src/native/**`, and the v2.14 release surface?
Yes. The "Non-Negotiable Rule" section explicitly prohibits modifications to [src/rtdsl/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl), [src/native/](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native), and the v2.14 release surface, as well as the addition of RayJoin-specific primitives.

### 3. Does it correctly split `bundled_helper_bounded_available_input_reproduction_not_generic` from `generic_primitive_numba_attempt`?
Yes. It defines two distinct routes under these exact labels ("Route 1: Bundled Helper Bounded Reproduction" and "Route 2: Generic Primitive + Numba Attempt") and explicitly mandates that they must never be merged in wording or claims.

### 4. Does Route 1 honestly label `rayjoin_overlay` and private helper use as bundled-helper evidence, not generic user-language reproduction?
Yes. Under the Route 1 section, it lists the use of the [rayjoin_overlay.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py) helper paths (such as [_run_lsi_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L794) and [_run_point_location_faces](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L885)) and explicitly bounds the claim: *"This is a bundled helper route. It is not generic RTDL language reproduction."*

### 5. Does Route 2 use released RTDL assets and Numba continuation in a plausible user-mode way without private helper laundering?
Yes. Route 2 lists only public, released assets and Numba continuations, such as [load_cdb](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/datasets.py#L350), [prepare_segment_pair_intersection_optix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py#L3794), [prepare_directed_segment_point_location_2d_optix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py#L4126), [run_numba_compact_mask_i64](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/numba_partner_continuation.py#L1134), [execute_compact_mask_typed_stream_partner_columns](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v2_8_segmented_typed_stream_adapter.py#L1031), and [filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/closed_shape_topology.py#L2648). It explicitly forbids shortcuts like calling the bundled overlay solver or setting internal environment variables.

### 6. Does Route 2 correctly identify the clean generic row/coordinate output problem as a possible `missing_v2_14_capability` rather than patching RTDL?
Yes. The stage plan for Route 2 acknowledges that the generic LSI row/coordinate stage is blocked because v2.14 lacks a clean public API for retrieving intersection pairs and exact coordinates. It labels this as `missing_v2_14_capability` for the generic primitive route instead of suggesting a native or runtime patch to hide the gap.

### 7. Does the design correctly preserve the unresolved author-reply PIP `t_reported` determinism contract?
Yes. The stage plan and correctness gates carry forward the `unresolved_pip_tie_break_contract`. Under Correctness Gate 4, the plan requires documenting whether the pipeline follows the committed author `HEAD` behavior or the perturbed `t_reported` formula from the author-reply determinism contract, and specifically commands checking for repeated-run PIP flips.

### 8. Are the correctness gates sufficient before any POD performance run?
Yes. The design institutes five gates:
1. **Input provenance gate** (specifying source CDB type per pair);
2. **Author baseline gate** (verifying dirty worktree/HEAD state and baseline commands);
3. **Output gate** (verifying full byte-equal or equivalent topology-hash correctness, avoiding scalar-only false passes);
4. **PIP determinism gate** (handling the tie-break and stability contract);
5. **Route-label gate** (maintaining route separation and labels for every result).
These are highly comprehensive and sufficient to govern subsequent correctness runs.

### 9. Does the design avoid treating scalar LSI/PIP counts or Numba compact-mask continuations as full Section 5.7 polygon overlay?
Yes. The design repeatedly states that scalar LSI/PIP counts or intermediate Numba continuations are insufficient for full Section 5.7 overlay correctness. For Route 1, full overlay requires output-chain reconstruction, and Route 2 is identified as blocked from achieving full overlay due to the LSI row/coordinate output capability gap.

### 10. Should Goal4816-D be authorized as a correctness smoke/preflight plan, or must Goal4816-C be amended first?
Goal4816-D is authorized to proceed directly as a correctness preflight plan. The design in Goal4816-C requires no amendments as it is fully aligned with prior extracted contracts and capability maps.

---

## Authorization Statement
Goal4816-D is **authorized** to proceed. Goal4816-D must be designed strictly as a local correctness preflight and smoke validation plan (e.g. running Route 1 on the available County x Zipcode dataset and verifying output topology counts or hashes) and must not plan or execute performance runs or optimizations.

---

## Non-Authorization Block
This review does **NOT** authorize:
1. Modifying any files under `src/rtdsl/**`, `src/native/**`, or the v2.14 release surface.
2. Running any POD performance, scaling, or benchmark timing experiments.
3. Using private underscored helpers as generic user-facing APIs.
4. Claiming full 8/8 Section 5.7 reproduction.
5. Claiming bundled-helper evidence as generic RTDL language evidence.
