# V4 Goal4758 Local Completion Audit

Status: `local_v4_0_completion_audit_passed_external_release_review_open`

This audit checks the active V4.0 objective requirement by requirement. It is
not a public-tag authorization; it exists so the final external reviewer does
not have to infer completion from scattered files.

## Audited Requirements

| Requirement | Status | Evidence |
| --- | --- | --- |
| V4.0 is a V2/V3 superset for promoted benchmark routes | Proved | `src/rtdsl/v4_app_compatibility.py`, `tests/v4_goal4751_app_compatibility_catalog_test.py`, `future/v4/evidence/v4_goal4751_app_compatibility_catalog_2026-06-26.json` |
| Complete same-semantics NVIDIA RT-core V2.14/V3.0.2/V4.0 benchmark matrix | Proved | `future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/`, `future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json`, `future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md` |
| First-class explicit CuPy partner support | Proved, bounded | `src/rtdsl/v4_cupy_certification.py`, `tests/v4_goal4649_cupy_certification_gate_test.py`, `future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json`, `future/v4/tier2_operator_catalog.md` |
| First-class explicit Numba partner support | Proved, bounded | `src/rtdsl/v4_numba_fixed_continuation_certification.py`, `src/rtdsl/v4_custom_predicate_early_exit.py`, `tests/v4_goal4650_fixed_numba_continuation_certification_test.py`, `tests/v4_goal4716_custom_predicate_early_exit_productization_test.py`, `future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.json` |
| Clean current docs/examples | Proved | `README.md`, `docs/current_v4_status.md`, `docs/app_level_benchmark_summary.md`, `docs/learn/performance_wording.md`, `future/v4/README.md`, `examples/README.md`, `tutorials/current/README.md` |
| Current-tree V4.0 Python wheel builds after final packet/audit changes | Proved | `dist/goal4758_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`, `future/v4/evidence/v4_goal4758_package_wheel_build_2026-06-26.log` |
| Current-tree V4.0 wheel installs with dependencies and exposes V4 front door | Proved | `future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/summary.json`, `future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/wheel_install_with_deps.log`, `future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/import_claim_boundary_after_install.log` |
| Final review evidence manifest records artifact hashes | Proved | `future/v4/evidence/v4_goal4759_final_review_evidence_manifest_2026-06-26.json`, `future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md` |
| Final release review evidence prepared | Proved, external review open | `future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md`, `future/v4/reviews/call_for_review_v4_goal4757_final_v4_0_release_after_goal4756_2026-06-26.md`, `future/v4/reviews/v4_goal4757_final_release_external_review_debt_2026-06-26.md` |

## Machine Gate

- `src/rtdsl/v4_goal4758_local_completion_audit.py`
- `tests/v4_goal4758_local_completion_audit_test.py`

The gate validates:

- measured partner set is exactly `cupy`, `numba`, `rtdl_native`, `torch`;
- certified partner set includes both `cupy` and `numba`;
- all ten app compatibility rows are ready and no app requires repair;
- the complete matrix has `10` apps and `30` version rows;
- material candidates are exactly `triangle_counting` and `barnes_hut`;
- hot-path regression set is empty;
- public tag and broad speedup claims are still unauthorized;
- public docs contain the current boundary language and no stale Barnes-Hut or
  Spatial overclaim wording.
- current-tree wheel exists with sha256
  `4f349985e0daa8e16cbbfe90cab8663c8517815b1f22c8d6be67901a7da2eed5`.
- installed-wheel front-door smoke returns status `ok`, `10` matrix apps,
  `30` matrix rows, and measured partners `cupy`, `numba`, `rtdl_native`,
  `torch`.
- final review manifest indexes `20` artifacts with file sizes and sha256
  hashes.

## Latest Local Verification

Focused objective gate:

```text
Ran 29 tests in 3.965s
OK
```

Full V4 gate:

```text
Ran 601 tests in 79.220s
OK
```

Full log:
`future/v4/evidence/v4_goal4759_full_v4_unittest_discover_with_review_manifest_2026-06-26.log`

## Limitations

- Broad CuPy performance wording is not authorized. CuPy support is explicit
  and bounded to measured/certified surfaces.
- Arbitrary Numba ray-action callbacks are not V4.0 support. They remain
  V4.1/Tier-3 work.
- The app matrix does not authorize broad all-benchmark speedup wording.
- Public V4.0 tagging still requires the external release verdicts requested in
  the Goal4757 review packet.

## Non-Authorization

This audit says local development, testing, docs, and review evidence are ready
for external release review. It does not close the external review debt and does
not authorize a public V4.0 tag.
