# Goal4849 Audit: Did Prior Goals Already Build The Clean RayJoin RTDL Layering?

Date: 2026-07-01

## User Question

The required architecture is:

1. RTDL core provides generic primitives:
   - segment-pair intersection;
   - directed point-location / PIP;
   - prepared sessions;
   - grouped continuation;
   - Numba/CuPy partner hooks.
2. RayJoin paper reproduction app handles application logic:
   - CDB parsing;
   - author-compatible parameters;
   - output formatting;
   - Section 5.2 / 5.7 workflow.
3. Do not hide RayJoin semantics inside core and then claim the language is generic.

The user asked whether this was already done in prior goals.

## Short Answer

Partly yes, but not fully.

Prior goals **did** build and document many of the generic RTDL primitives and
partner-continuation pieces. They also **did** build a working bundled RayJoin
helper path.

But prior goals **did not finish** the strongest claim:

> A normal user can write the full RayJoin Section 5.7 polygon overlay app from
> public generic RTDL primitives plus explicit Numba continuation, without
> relying on bundled/private RayJoin helpers.

The strongest route remains unfinished because public/generic row-level LSI
coordinate output, full overlay chain assembly, and deterministic PIP/SoS
semantics were not all cleanly exposed and proven as a generic user-level API.

## Evidence Chain

### Goal4380: Bounded RayJoin evidence existed, but it was not full generic language proof

Goal4816-A preserved Goal4380's result:

| Pair | Local Author RT Process | RTDL OptiX Total | LSI Count Match | Complete |
| --- | ---: | ---: | --- | ---: |
| County x Zipcode | 5.521469 | 5.782340 | True | True |
| Block x Water | 27.943863 | 28.649871 | True | True |

Meaning:

- RTDL already had a real bounded RayJoin-compatible path.
- It was 2/8 available input evidence, not full 8/8.
- It was not proof that the full app was written only from clean generic public primitives.

### Goal4816-A: Paper/source contract was extracted correctly

Goal4816-A established that Section 5.7 requires all of:

- LSI;
- vertex PIP / point-location;
- midpoint PIP;
- output-chain assembly;
- author-format output;
- Section 3.2 precision/SoS behavior.

This correctly prevents scalar LSI/PIP counts from being misrepresented as full
polygon overlay reproduction.

### Goal4816-B: The exact taxonomy already existed

Goal4816-B explicitly classified assets into:

- `existing_v2_14_primitive`;
- `bundled_rayjoin_helper`;
- `numba_partner_continuation`;
- `paper_app_logic`;
- `missing_input`;
- `missing_v2_14_capability`;
- `unresolved_pip_tie_break_contract`.

This is almost exactly the architecture the user restated.

#### Generic / reusable assets identified

| Asset | Classification | Status |
| --- | --- | --- |
| `prepare_segment_pair_intersection_optix` | `existing_v2_14_primitive` | Exists; prepared segment-pair intersection over build segments. |
| `prepare_segment_pair_left_set_optix` | `existing_v2_14_primitive` | Exists; prepared left/query segment set. |
| `prepare_directed_segment_point_location_2d_optix` | `existing_v2_14_primitive` with caveat | Exists; directed point-location/PIP-like primitive. |
| `load_cdb`, `chains_to_*` | data helper / primitive support | Exists; useful for CDB-derived columns. |
| `run_numba_compact_mask_i64` | `numba_partner_continuation` | Exists; continuation only, not traversal. |
| `execute_compact_mask_typed_stream_partner_columns` | `numba_partner_continuation` | Exists; typed stream compact-mask path. |
| `filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba` | `numba_partner_continuation` | Exists; topology/owner-face continuation. |

#### Bundled RayJoin helpers identified

| Asset | Classification | Meaning |
| --- | --- | --- |
| `_run_lsi_rows` | `bundled_rayjoin_helper` | Wraps generic segment-pair primitive plus RayJoin row reconstruction/pair dump. |
| `_run_point_location_faces` | `bundled_rayjoin_helper` | Wraps directed point-location into RayJoin face-id arrays. |
| `_PreparedPointLocationRunner` | `bundled_rayjoin_helper` | Prepared helper with RayJoin CDB/query-map/scale policy. |
| `_assemble_output_chains` | `bundled_rayjoin_helper` / `paper_app_logic` | Python RayJoin-like output-chain construction. |
| `run_rayjoin_overlay_rtdl_from_cdb_paths` | `bundled_rayjoin_helper` | High-level shipped helper; not proof of generic user composition. |

Goal4816-B's own conclusion:

> Generic-primitive + Numba full Section 5.7 is not yet proven. Bounded
> reproduction using bundled helpers is feasible.

### Goal4816-C: The correct two-route design was already written

Goal4816-C split the work into:

1. `bundled_helper_bounded_available_input_reproduction_not_generic`
2. `generic_primitive_numba_attempt`

This design explicitly says:

- Route 1 may use `run_rayjoin_overlay_rtdl_from_cdb_paths` and private helpers,
  but must be labeled bundled-helper evidence.
- Route 2 must use released RTDL assets and Numba continuation only.
- Route 2 is blocked unless clean public LSI row/coordinate output exists or is
  accepted.

This means the project already knew the correct distinction. The gap is not
conceptual; it is completion/productization.

### Goal4817-4819: User-mode exact Section 5.7 failed before product fixes

Goal4819 closed the user-mode attempt as:

`blocked_by_released_rtdl_pip_sos_contract_gap`

At that time:

- author public sample byte-equal output failed;
- Numba was only first-class for selected continuations, not full overlay;
- bundled helper evidence could not be laundered into generic RTDL+Numba language evidence.

This was an honest block, but it also showed the public/generic route was not
finished.

### Goal4820: A real core primitive correctness fix was made

Goal4820 repaired a core directed-segment point-location / PIP issue:

- equal-depth SoS tie preference must affect reported OptiX hit distance;
- this is a generic directed point-location contract, not a RayJoin-only kernel;
- public sample byte-equality later passed after the midpoint-face bug was also
  repaired.

This moved the system closer to the clean architecture because it repaired a
core primitive contract instead of adding a hidden RayJoin shortcut.

### Goal4845: A real core LSI candidate-generation defect was fixed

Goal4845 found a County x Zipcode Section 5.2 LSI mismatch:

- AuthorPatch count: `961165`;
- RTDL count before fix: `961164`;
- missing pair caused by a nonzero exact/scaled segment collapsing to one
  `float32` point in the RT candidate stage.

The product repair:

- uses scaled/exact endpoints to decide the author-style edge direction;
- extends collapsed float candidate rays by `nextafterf` when exact geometry is
  nonzero;
- leaves the exact predicate as the final decision.

This is a real core/conservative-candidate-generation repair, not an app output
patch.

### Goal4846 / Goal4848: LSI count correctness is now stronger, but still via RayJoin helper route

Section 5.2 LSI correctness now passes on:

| Pair | AuthorPatch | RTDL | Route |
| --- | ---: | ---: | --- |
| County x Zipcode | 961165 | 961165 | RTDL v2.14 RayJoin LSI / prepared primitive route |
| Block x Water | 649605 | 649605 | RTDL v2.14 RayJoin LSI / prepared primitive route |
| Australia current OSM Lakes/Parks representative | 13622 | 13622 | bundled RayJoin LSI helper, correct direction |

However, Goal4848 also proved a caution:

- the generic RTDL `segment_intersection` kernel produced `103794`, not
  `13622`, on the Australia representative;
- therefore generic segment-intersection rows are not automatically RayJoin
  Section 5.2 LSI semantics.

## What Was Actually Done

### Done

1. Segment-pair OptiX prepared primitives exist.
2. Directed segment point-location/PIP primitive exists.
3. CDB loading and column conversion helpers exist.
4. Numba continuation utilities exist for compact masks/topology/selected
   post-RT continuation.
5. Bundled RayJoin overlay/LSI helper exists.
6. Two important core correctness defects were exposed and repaired:
   - PIP/SoS reported-distance issue;
   - collapsed-float LSI candidate ray issue.
7. Section 5.2 LSI count correctness is now supported on available/representative inputs.

### Not Done / Not Proven

1. A clean public user API for RayJoin-style LSI row + coordinate output is not
   proven as a generic API.
2. Full Section 5.7 overlay chain assembly is still bundled helper / app logic,
   not a clean generic RTDL primitive.
3. Numba partner is available for selected continuation, but no completed
   public RayJoin Section 5.7 generic+Numba app has been proven.
4. Exact 8/8 Section 5.7 paper reproduction remains blocked by missing exact
   Lakes/Parks CDB inputs.
5. Current successful Section 5.2 evidence should not be described as
   "Python+Numba+RTDL replaces author C++/CUDA/OptiX." Numba did not drive the
   Section 5.2 LSI hot path.

## Direct Answer To The User's Question

> "This is what we required. Did previous goals not do it?"

They did **part** of it:

- core RT primitives: yes, many exist;
- Numba/CuPy-style partner continuation: yes, selected pieces exist;
- RayJoin app helper: yes, exists and can match counts in bounded cases;
- strict distinction between generic vs bundled: yes, Goal4816 already wrote it.

They did **not** complete the final clean product claim:

> A user can write full RayJoin Section 5.7 from public generic RTDL primitives
> plus Numba partner, without private/bundled RayJoin helper reliance.

That remains unfinished.

## What The Next Correct Work Should Be

If the goal is to finish the clean architecture rather than merely keep the
bundled helper:

1. Promote or expose a **public RayJoin-style LSI row/coordinate output API**
   if it is genuinely generic enough:
   - not named RayJoin;
   - documented as segment-pair intersection rows with pair ids and coordinates;
   - with correctness tests against AuthorPatch cases.
2. Expose directed point-location/PIP with an explicit deterministic SoS policy
   as a generic primitive contract.
3. Keep output-chain assembly as application code, but provide enough public
   row/face/topology columns for a user app to build it.
4. Rebuild the RayJoin reproduction app using only:
   - public RTDL primitives;
   - public data helpers;
   - explicit Numba continuation for app-owned continuation/output logic.
5. Compare against the bundled helper to ensure the generic route reaches the
   same correctness before claiming it is the clean implementation.

## Goal-Level Decision Audit

1. **Was I being foolish before this audit?**
   Yes, when I implied too loosely that the current successful route might be
   the desired generic RTDL+Numba app route. It is not.

2. **What action made that foolish?**
   I collapsed "RTDL has a bundled RayJoin helper that uses primitives" into
   "RTDL user can write RayJoin from generic primitives." Goal4816 explicitly
   warned against that.

3. **Was there another possibility?**
   Yes. Read the 4816 goal chain first and preserve the route labels:
   bundled-helper evidence vs generic-primitive+Numba attempt.

4. **Can I now follow a better path?**
   Yes. Treat the current RayJoin helper results as valuable bounded evidence,
   while separately finishing or honestly closing the generic public API route.

## Exit Label

`goal4849_audit_complete__prior_goals_built_many_primitives_and_bundled_helper__generic_rtdl_numba_full_rayjoin_not_yet_proven`
