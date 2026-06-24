# Claude External Review: Goal3054 v2.6 Partner Choice Guidance API

Date: 2026-06-02
Reviewer: Claude (Sonnet 4.6), acting as an independent external reviewer
Verdict: **accept**

This review is independent and distinct from Codex authoring. It does not
authorize a v2.6 release, package-install wording, broad RT-core speedup
wording, broad CuPy/Numba acceleration wording, true-zero-copy wording, hidden
partner auto-selection, or app-specific native-engine behavior.

---

## Files Inspected

- `src/rtdsl/v2_6_partner_choice_guidance.py`
- `src/rtdsl/__init__.py` (imports and `__all__` section)
- `src/rtdsl/v2_6_roadmap.py`
- `docs/learn/partner_choice_for_custom_logic.md`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/reports/goal3054_v2_6_machine_readable_partner_choice_guidance_2026-06-02.md`
- `tests/goal3054_v2_6_partner_choice_guidance_test.py`
- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02.md`

---

## Review Question 1: Advisory-only and user-owned

The helper is structurally enforced as advisory-only through multiple
independent mechanisms.

The `V26PartnerChoiceGuidanceRow` dataclass (line 47) sets
`automatic_partner_selection_allowed: bool = False` as a default and its
`__post_init__` (lines 76-86) raises `ValueError` if any blocked boolean
field — including `automatic_partner_selection_allowed` — is True. It is
impossible to construct a row that authorizes auto-selection.

The top-level `v2_6_partner_choice_guidance()` dict also sets
`automatic_partner_selection_allowed: False` and
`partner_choice_rule: "users_choose_supported_partners_explicitly"`.

Both `plan_v2_6_partner_choice` and `explain_v2_6_partner_choice` return
`auto_select_partner_allowed: False`. The explain helper further sets
`user_choice_remains_authority: True` and only annotates whether the
user-preferred partner matches the recommendation — it does not redirect
or override the user choice.

`V2_6_PARTNER_CHOICE_GUIDANCE_STATUS = "internal_guidance_not_release_authorization"`
is explicit.

**Finding: passes cleanly.**

---

## Review Question 2: Correct encoding of benchmark recommendations

Ten rows were reviewed individually against the Goal3052 pod-refresh report
and the benchmark partner reference matrix.

**Numba-recommended rows (recommended_reference_path):**
- `spatial_rayjoin` / `row_stream_compact_mask` → `numba`; evidence artifact
  `rayjoin_numba_compact_mask_1m.json` exists on disk.
- `raydb_style` / `unfused_grouped_minmax_count_sum_avg` → `numba`; evidence
  artifact `raydb_numba_minmax_1m.json` exists on disk.
- `triangle_counting` / `candidate_row_compact_mask` → `numba`; evidence
  artifact `triangle_numba_compact_mask_1m.json` exists on disk.

All three Numba rows name the correct Goal3052 evidence and point to JSON
artifacts that were confirmed present under
`docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/`. Each row's
`numba_role` field accurately describes the scope (compact-mask,
grouped-scalar continuation) rather than claiming general Numba superiority.

**RTDL-primitive-recommended rows (recommended_reference_path):**
- `hausdorff_xhd` / `active_frontier_exact_distance` → `rtdl_primitive`;
  evidence artifact `hausdorff_active_frontier_small_refresh.json` exists.
  The `numba_role` field correctly keeps Numba as "contract evidence for score
  rows and global argmax; not the current default," consistent with Goal3018
  and Goal3046/3048 findings that CuPy grouped-grid beats Numba for dense 2D
  Hausdorff and the active-frontier RTDL/OptiX path is the current winner.
- `rtnn` / `ranked_summary_quality_probe` → `rtdl_primitive`; no promoted
  Numba path yet, which is consistent with the roadmap.

**CuPy-measured-reference rows (measured_reference_path):**
- `rt_dbscan` / `component_labeling` → `cupy`; CuPy as the current measured
  component-continuation reference is accurate per benchmark history.
- `barnes_hut` / `force_vector_continuation` → `cupy`; CuPy as the active
  force-vector reference is accurate; Numba not promoted.

**No-promoted-partner rows (no_promoted_partner):**
- `robot_collision`, `contact_manifold`, `librts_spatial_index` → `none`.
  Each row's `numba_role` says "future candidate, not promoted." This is
  appropriate; none of these apps have measured Numba-specific evidence.

The consistency check between the recommendation rows and the learner docs
(`docs/learn/benchmark_partner_reference_matrix.md`) is exact. The matrix
table rows match the guidance rows one-for-one.

**Finding: passes cleanly.**

---

## Review Question 3: All ten apps covered without fixing RTDL as an app library

`V2_6_PROMOTED_BENCHMARK_APPS` has exactly ten entries and the ten
`V2_6_PARTNER_CHOICE_ROWS` cover exactly those ten apps, one row each. The
`validate_v2_6_partner_choice_guidance` function confirms this with
`app_count == len({row["benchmark_app"] for row in rows})`.

The `primitive_first_rule` field is generic:
`"use_fused_generic_rtdl_primitive_when_it_exactly_expresses_the_answer"`.
The `partner_choice_rule` is `"users_choose_supported_partners_explicitly"`.
The `benchmark_role` field is
`"reference_or_recommended_implementations_require_same_contract_evidence"`.

None of these field values name app-specific logic in the native engine. App
names appear only in advisory metadata rows, not as engine dispatch keys.
The native engine itself is unchanged.

**Finding: passes cleanly.**

---

## Review Question 4: Blocked claims

Every `V26PartnerChoiceGuidanceRow` instance carries seven blocked-claim
boolean fields, all defaulting to `False`:

- `automatic_partner_selection_allowed`
- `public_speedup_claim_authorized`
- `rt_core_speedup_claim_authorized`
- `broad_partner_speedup_claim_authorized`
- `true_zero_copy_claim_authorized`
- `release_authorized`
- `app_specific_native_engine_logic_authorized`

The `__post_init__` validates that every field in this set is False, so the
row is rejected at construction time if any is True. The same seven fields
appear at the top-level guidance dict and are also False there. The
`validate_v2_6_partner_choice_guidance` function (lines 374-396) repeats
these checks at both the per-row and aggregate levels.

`V2_6_PARTNER_CHOICE_CLAIM_BOUNDARY` (lines 38-44) explicitly names each
blocked category as text visible to callers.

The `__init__.py` imports the four public functions but they do not appear in
`__all__`, keeping them out of the promoted public API surface.

**Finding: passes cleanly.**

---

## Review Question 5: No misleading or unsupported rows

Cross-checking each row against the Goal3052 pod-refresh artifacts and the
benchmark matrix reveals no misleading recommendations.

The three Numba-promoted rows all have 1M-row L4/A4000 conformance JSON
artifacts from Goal3052. The hausdorff row correctly withholds Numba
promotion: Goal3052 shows CuPy grouped-grid as the current CUDA-core
reference and the active-frontier RTDL path as the current winner; Numba is
contract evidence, not the current performance recommendation.

The CuPy-measured rows (rt_dbscan, barnes_hut) have no false claims: both
say "not promoted yet" for Numba, matching the absence of Numba evidence in
those apps. The primitive-first RTDL rows (hausdorff_xhd, rtnn) are backed
by OptiX and prepared-summary evidence respectively.

The no-partner rows (robot_collision, contact_manifold, librts_spatial_index)
use `no_promoted_partner` status and state "future candidate, not promoted"
for Numba — accurate given the absence of same-contract Numba evidence for
those apps.

The `evidence_goal` and `evidence_artifact` fields in each row are populated
and point to real report files or example READMEs. No row invents a partner
recommendation without a named evidence source.

**Finding: no misleading rows found.**

---

## Test Alignment

The test file `tests/goal3054_v2_6_partner_choice_guidance_test.py` has five
test methods that collectively verify:

1. Full-guidance validation passes with `app_count=10`, `row_count=10`, and
   all blocked-claim fields False.
2. The three Numba rows each carry the correct 1M-row JSON artifact path.
3. Hausdorff, rt_dbscan, barnes_hut, and rtnn have the correct non-Numba
   recommendations.
4. No-partner and unknown-app rows fail closed (`none`, `no_measured_guidance`).
5. The explain helper respects user choice without auto-selecting; the four
   public functions are `hasattr` accessible but absent from `rt.__all__`.

All five test methods are consistent with the reviewed source. The `__all__`
grep confirmed the four new functions (`v2_6_partner_choice_guidance`,
`plan_v2_6_partner_choice`, `explain_v2_6_partner_choice`,
`validate_v2_6_partner_choice_guidance`) are imported but not listed in
`__all__`, satisfying the `assertNotIn` assertions.

The roadmap validator (`validate_v2_6_roadmap`) also indexes Goal3054 and
checks that the guidance report file exists and that `not_auto_select` and
`not_release_not_speedup` appear in the `partner_choice_guidance_status`
field. Both conditions are met.

---

## Summary

Goal3054 correctly turns the v2.6 CuPy-vs-Numba partner-choice learner
guidance into advisory, machine-readable source metadata. The implementation
is honest about what is measured, keeps all blocked claims structurally
enforced at construction time, covers all ten promoted apps without
over-promising, and leaves the native engine unchanged and app-agnostic.

**Verdict: accept**
