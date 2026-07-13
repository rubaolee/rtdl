# Goal4836 — Examples-Internal Regression Harness Cleanup

Date: 2026-06-30

## Purpose

Goal4836 removes stale regression-harness references to the old public path `examples/internal` after the v2.14 public surface cleanup moved internal/demo/history material under `history/examples_internal`.

This is not a RayJoin algorithm change and not a public documentation change. It is regression-gate hygiene needed before broader v2.14 checks can be interpreted.

## Scope

Allowed:

- Update tests and maintainer scripts that still imported `examples.internal`.
- Add package markers so archived internal examples can be imported from `history.examples_internal`.
- Keep public `examples/` clean: no `examples/internal` resurrection.

Not allowed:

- Do not change RayJoin semantics.
- Do not change `src/rtdsl/**` or `src/native/**` for this goal.
- Do not make Embree evidence part of the current RayJoin line.
- Do not move archived/internal examples back into the user-facing surface.

## Files Updated

- `history/__init__.py`
- `history/examples_internal/__init__.py`
- `examples/current/apps/analytics/rtdl_database_analytics_app.py`
- `examples/current/partners/rtdl_control_apps_cupy_rawkernel.py`
- `scripts/goal1155_db_compact_summary_precloud_audit.py`
- `scripts/goal2617_current_surface_audit.py`
- `scripts/goal409_generate_file_audit_ledger.py`
- `scripts/rtdl_sorting_demo.py`
- `tests/baseline_integration_test.py`
- `tests/goal209_nearest_neighbor_scaling_note_test.py`
- `tests/goal2102_examples_directory_organization_audit_test.py`
- `tests/goal2103_root_scripts_tests_organization_audit_test.py`
- `tests/goal3058_v2_6_release_candidate_doc_total_audit_test.py`
- `tests/goal3066_v2_6_release_action_test.py`
- `tests/goal4274_current_doc_recheck_test.py`
- `tests/goal686_app_catalog_cleanup_test.py`
- `tests/rtdl_sorting_test.py`
- `tests/rtdsl_language_test.py`
- `tests/rtdsl_ray_query_test.py`
- `history/examples_internal/internal/rtdl_goal165_optix_animation_variants.py`
- `history/examples_internal/legacy_or_backend_proofs/rtdl_apple_rt_demo_app.py`

## Verification

### Stale Path Scan

Command:

```powershell
rg -n "from examples\.internal|import examples\.internal|examples/internal" tests src scripts examples docs README.md history/examples_internal -g "*.py" -g "*.md"
```

Result:

- No matches.

### Targeted Migration Tests

Command:

```powershell
py -3 -m unittest tests.goal2102_examples_directory_organization_audit_test tests.goal209_nearest_neighbor_scaling_note_test tests.rtdsl_language_test tests.rtdsl_ray_query_test tests.rtdl_sorting_test
```

Result:

- `Ran 27 tests in 41.329s`
- `OK (skipped=5)`

Notes:

- The skipped tests are environment/backend availability skips.
- Windows Embree link probes still emit `__floattidf` linker failures before skip/skip-equivalent handling. This is a separate Windows Embree toolchain debt, not a stale `examples.internal` failure.

### RayJoin Focused Gate

Command:

```powershell
py -3 -m unittest tests.goal4834_rayjoin_sos_synthetic_contract_test tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4374_rayjoin_exact_paper_suite_test
```

Result:

- `Ran 38 tests in 3.179s`
- `OK`

## What This Proves

- The current public-surface cleanup did not leave Python tests depending on a deleted `examples/internal` package.
- Maintainer-only archived examples remain reachable through the explicitly internal `history.examples_internal` package.
- The RayJoin correctness line remains green after the harness cleanup.

## What This Does Not Prove

- It does not prove the full v2.14 regression matrix is green.
- It does not resolve Windows Embree linker/toolchain failures.
- It does not prove full RayJoin Section 5.7 reproduction.
- It does not authorize any performance claim.

## Open Follow-Up

The v2.14-wide regression gate remains open because the previous full matrix failed on:

1. stale `examples.internal` imports, now addressed here;
2. Windows Embree linker failures, still outside the current no-Embree RayJoin scope.

The next product-scoped RayJoin step should run Linux/OptiX-focused confirmation on the POD, then continue with the unresolved County x Zipcode / chain-level mismatch work.

## Goal-Level Decision Audit

1. **Was I being foolish?**
   Partly yes, before this cleanup: treating full-matrix failure as one undifferentiated blocker would have been foolish.

2. **What action would have made the decision foolish?**
   Re-exposing `examples/internal` to satisfy old tests, or using Windows Embree failures as a reason to stop the no-Embree OptiX RayJoin line.

3. **Was there another path?**
   Yes: move test imports to the archived internal package and keep the public example surface clean.

4. **Can I now try a better path that solves the real problem?**
   Yes: this cleanup isolates one harness debt, so the next work can focus on Linux/OptiX RayJoin correctness and exact reproduction evidence rather than path churn.

## Exit Label

`completed_examples_internal_path_cleanup__rayjoin_focused_gate_still_green__full_matrix_still_has_non_rayjoin_embree_debt`
