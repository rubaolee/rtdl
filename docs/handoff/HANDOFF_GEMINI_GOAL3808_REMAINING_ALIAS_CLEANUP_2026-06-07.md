# Gemini Review Request: Goal3808 Remaining Low-Risk Alias Cleanup

Please perform an independent read-only review of Goal3808 and write your
review to:

`docs/reviews/goal3809_gemini_review_goal3808_remaining_alias_cleanup_2026-06-07.md`

## Scope

Review the current `main` branch after:

- `01e05d81 Goal3808 add remaining current helper aliases`
- `419eeea6 Goal3808 record pod validation`

## Files To Inspect

- `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `docs/reports/goal3808_remaining_low_risk_alias_cleanup_2026-06-07.md`
- `tests/goal3808_remaining_low_risk_alias_cleanup_test.py`
- `docs/research/future_version_to_do_list.md`
- Optional context:
  - `docs/reports/goal3806_active_example_versioned_helper_inventory_2026-06-07.md`
  - `docs/reviews/goal3807_gemini_review_goal3804_3806_typed_alias_inventory_2026-06-07.md`

## Questions

1. Does `describe_bounded_witness_session` preserve the exact generic bounded
   int64 witness-row descriptor from `describe_v2_4_bounded_witness_session`
   while giving users a current app-facing helper name?
2. Does `primitive_first_plan_payload` plus `--mode primitive_first_plan`
   preserve the LibRTS prepared generic AABB index plan from `v2_5_plan_payload`
   while avoiding a stale primary user-facing name?
3. Are the old helper names preserved as compatibility/protocol names rather
   than removed?
4. Does the change avoid native-engine app customization and avoid public
   release, package-install, zero-copy, RT-core speedup, paper reproduction, or
   broad speedup claims?
5. Is it correct to leave the RayJoin `v2_9` topology-reference helper
   intentionally versioned for now because it marks a bounded reference lane,
   not a promoted public route?

## Validation To Reproduce If Useful

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3808_remaining_low_risk_alias_cleanup_test tests.goal3806_active_example_versioned_helper_inventory_test tests.goal2659_v2_4_benchmark_protocol_integration_test tests.goal2736_tier_a_primitive_first_plan_alignment_test
```

Expected local result: 16 tests pass.

The Goal3808 report records A5000 pod validation on clean `origin/main` at
commit `01e05d81`, also with the same 16-test slice passing.

## Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

Please keep the review concise but explicit about any required fixes.
