# Gemini Review for Goal2793: Partner Role Reconciliation (2026-05-31)

## Goal
Review Goal2793, which reconciles v2.5 partner-role wording after the Goal2773 Claude review: Numba is the generic fallback partner, while CuPy is conformance/interoperability and may be explicitly app-chosen for DBSCAN component work.

## Files Inspected
- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2793_v2_5_partner_role_reconciliation_test.py`
- `tests/goal2696_v2_5_partner_support_matrix_test.py`
- `docs/reports/goal2793_v2_5_partner_role_reconciliation_2026-05-31.md`

## Questions and Answers

### 1. Does the protocol/support matrix clearly keep Triton primary, Numba fallback, and CuPy conformance/interoperability?
**Answer:** Yes, the protocol (`src/rtdsl/partner_continuation_protocol.py`) and support matrix (`src/rtdsl/v2_5_partner_support_matrix.py`) clearly define these roles.
- `V2_5_PRIMARY_PARTNER = "triton"`
- `V2_5_FALLBACK_PARTNER = "numba"`
- `V2_5_CONFORMANCE_PARTNER = "cupy_conformance"`
The `_select_partner_for_operation` function in `partner_continuation_protocol.py` confirms this hierarchy, and the `v2_5_partner_support_matrix` explicitly states `partner_choice_policy: "explicit_per_boundary_app_choice"` and `no_partner_forced: True`, while explicitly noting that CuPy remains an "app-chosen conformance/interoperability partner" for operations where it doesn't have a specific preview.

### 2. Does the RT-DBSCAN migration row now frame CuPy as an explicit app-chosen phase rather than the generic v2.5 fallback partner?
**Answer:** Yes, the `rt_dbscan` entry in `V2_5_TRITON_BENCHMARK_APP_PLANS` within `src/rtdsl/v2_5_triton_app_migration.py` explicitly frames CuPy as an app-chosen phase.
- `current_hot_path_partner: "app_chosen_cupy_component_phase_with_numba_as_generic_fallback_partner"`
- `v2_5_status: "app_chosen_cupy_phase_allowed_generic_fallback_partner_remains_numba"`
- `first_port_action`: "Wire generic Triton compaction and bounded finalize previews where they fit; keep any CuPy component/union-find phase as an explicit app-chosen phase, not as the v2.5 generic fallback partner."
- `notes`: "...The declared v2.5 fallback partner is Numba; CuPy remains conformance/interoperability or an explicit app-chosen phase."
This clearly indicates CuPy is for explicit app-chosen component work, with Numba retaining the generic fallback role.

### 3. Does the change preserve partner choice without forcing Triton or removing CuPy?
**Answer:** Yes, the changes preserve partner choice.
- `src/rtdsl/v2_5_partner_support_matrix.py` explicitly sets `no_partner_forced: True` and `partner_choice_policy: "explicit_per_boundary_app_choice"`.
- `src/rtdsl/partner_continuation_protocol.py`'s `_select_partner_for_operation` function provides a selection mechanism rather than a forced choice.
- The documentation and status for CuPy consistently describe it as an "app-chosen conformance/interoperability partner" rather than being removed or forced. Triton is primary, but not exclusively forced, with Numba as a fallback and CuPy for specific conformance/app-chosen tasks.

### 4. Are speedup, release, and traversal-replacement claims still blocked?
**Answer:** Yes, speedup, release, and traversal-replacement claims are still explicitly blocked.
- `src/rtdsl/partner_continuation_protocol.py` sets:
    - `V2_5_PERFORMANCE_PATH_AUTHORIZED = False`
    - `V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED = False`
    - `V2_5_PREVIEW_RELEASE_TAG_AUTHORIZED = False`
    - `V2_5_PREVIEW_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED = False`
    - `V2_5_RAWKERNEL_REQUIRED_ALLOWED = False`
- `src/rtdsl/v2_5_partner_support_matrix.py` in `V2_5_PARTNER_SUPPORT_CLAIM_BOUNDARY` and `V25PartnerSupportCell` post-init validation explicitly forbids these claims.
- `src/rtdsl/v2_5_triton_app_migration.py` also explicitly sets `public_speedup_claim_authorized: False` in `v2_5_tiered_benchmark_manifest()` and `v2_5_triton_benchmark_app_migration_plan()`.

## Verdict
accept
