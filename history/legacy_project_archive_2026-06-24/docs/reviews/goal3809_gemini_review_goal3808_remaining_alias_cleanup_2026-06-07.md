# Independent Gemini Review for Goal3808 Remaining Low-Risk Alias Cleanup

**Reviewer:** Gemini CLI
**Date:** 2026-06-07

## Scope Reviewed

Commits:
- `01e05d81 Goal3808 add remaining current helper aliases`
- `419eeea6 Goal3808 record pod validation`

## Files Inspected

- `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `docs/reports/goal3808_remaining_low_risk_alias_cleanup_2026-06-07.md`
- `tests/goal3808_remaining_low_risk_alias_cleanup_test.py`
- `docs/research/future_version_to_do_list.md`
- `docs/reports/goal3806_active_example_versioned_helper_inventory_2026-06-07.md` (Optional Context)
- `docs/reviews/goal3807_gemini_review_goal3804_3806_typed_alias_inventory_2026-06-07.md` (Optional Context)

## Questions and Answers

### 1. Does `describe_bounded_witness_session` preserve the exact generic bounded int64 witness-row descriptor from `describe_v2_4_bounded_witness_session` while giving users a current app-facing helper name?

**Answer:** Yes. The `describe_bounded_witness_session` function in `rtdl_contact_manifold_benchmark_app.py` directly calls `describe_v2_4_bounded_witness_session` and explicitly adds metadata `"current_helper": "describe_bounded_witness_session"` and `"legacy_helper_alias": "describe_v2_4_bounded_witness_session"`. The `test_contact_current_descriptor_alias_preserves_generic_protocol` in `tests/goal3808_remaining_low_risk_alias_cleanup_test.py` verifies that core descriptor properties like `primitive`, `native_symbols`, and `row_schema` remain identical. It also confirms that no contact/collision-specific vocabulary is introduced, ensuring the preservation of the exact generic bounded int64 witness-row descriptor.

### 2. Does `primitive_first_plan_payload` plus `--mode primitive_first_plan` preserve the LibRTS prepared generic AABB index plan from `v2_5_plan_payload` while avoiding a stale primary user-facing name?

**Answer:** Yes. The `primitive_first_plan_payload` function in `rtdl_librts_spatial_index_benchmark_app.py` calls `v2_5_plan_payload` and adds alias metadata (`"mode": "primitive_first_plan"`, `"current_helper": "primitive_first_plan_payload"`, `"legacy_helper_alias": "v2_5_plan_payload"`). The `main` function correctly processes the `--mode primitive_first_plan` CLI argument. The tests `test_librts_current_plan_alias_preserves_primitive_first_contract` and `test_librts_cli_current_plan_mode_is_available` in `tests/goal3808_remaining_low_risk_alias_cleanup_test.py` confirm that the content of `v2_5_primitive_first_plan`, including `selected_path` and `selected_primitives`, is fully preserved.

### 3. Are the old helper names preserved as compatibility/protocol names rather than removed?

**Answer:** Yes. Both `describe_v2_4_bounded_witness_session` (in `rtdl_contact_manifold_benchmark_app.py`) and `v2_5_plan_payload` (in `rtdl_librts_spatial_index_benchmark_app.py`) remain defined and are utilized by their new alias functions. The `docs/reports/goal3808_remaining_low_risk_alias_cleanup_2026-06-07.md` report explicitly states under "Boundary": "No old compatibility helper was removed." This is further verified by the `test_report_and_todo_record_scope` in `tests/goal3808_remaining_low_risk_alias_cleanup_test.py`, which checks for this statement in the report.

### 4. Does the change avoid native-engine app customization and avoid public release, package-install, zero-copy, RT-core speedup, paper reproduction, or broad speedup claims?

**Answer:** Yes. The `docs/reports/goal3808_remaining_low_risk_alias_cleanup_2026-06-07.md` report's "Boundary" section explicitly states: "No native engine code changed." and "No paper reproduction, release, package-install, true-zero-copy, public speedup, broad RT-core speedup, or app-specific native-engine claim is authorized." The related tests in `tests/goal3808_remaining_low_risk_alias_cleanup_test.py` confirm that the `claim_boundary` dictionaries in the respective payloads correctly reflect these restrictions by setting flags for public speedup, zero-copy, and Triton speedup claims to `False`.

### 5. Is it correct to leave the RayJoin `v2_9` topology-reference helper intentionally versioned for now because it marks a bounded reference lane, not a promoted public route?

**Answer:** Yes. The `docs/reports/goal3808_remaining_low_risk_alias_cleanup_2026-06-07.md` report explicitly states: "The RayJoin `run_rayjoin_v2_9_numba_side_aware_topology_reference` helper is not migrated in this goal. That name still marks a bounded topology-reference lane rather than a promoted public route." This position is reinforced in `docs/research/future_version_to_do_list.md`: "The RayJoin topology-reference helper remains intentionally versioned because it marks a bounded future/reference lane, not a promoted public route."

## Validation

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3808_remaining_low_risk_alias_cleanup_test tests.goal3806_active_example_versioned_helper_inventory_test tests.goal2659_v2_4_benchmark_protocol_integration_test tests.goal2736_tier_a_primitive_first_plan_alignment_test
```

Expected local result: 16 tests pass.

**Actual local result:** Due to limitations in the available toolset, I was unable to execute the validation commands or perform a `git show` to inspect the commits directly. The answers above are derived solely from reading the provided file contents and internal reports.

## Verdict

`accept`