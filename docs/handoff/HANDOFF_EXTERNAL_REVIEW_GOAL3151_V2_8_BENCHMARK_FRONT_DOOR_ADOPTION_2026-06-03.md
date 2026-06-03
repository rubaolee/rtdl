# External Review Handoff: Goal3151 v2.8 Benchmark Front-Door Adoption

Please perform an independent read-only review of Goal3151.

## Scope

Review the Goal3151 benchmark-app front-door adoption audit and the implementation changes that route safe benchmark continuations through the generic v2.8 typed-stream partner front door.

Primary files:

- `docs/reports/goal3151_v2_8_benchmark_front_door_adoption_audit_2026-06-03.md`
- `tests/goal3151_v2_8_benchmark_front_door_adoption_audit_test.py`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `tests/goal2999_triangle_counting_numba_compact_mask_wiring_test.py`
- `tests/goal3002_rayjoin_numba_compact_mask_wiring_test.py`

## Questions To Answer

1. Does the report classify all ten promoted v2.8 benchmark apps honestly, without hiding remaining runtime gaps?
2. Are `spatial_rayjoin` and `triangle_counting` the only safe migrations in this goal, and do their legacy helper names remain usable?
3. Do the migrated helpers route through `build_segmented_typed_stream_adapter` plus `execute_segmented_typed_stream_partner_continuation` rather than calling `rt.run_numba_compact_mask_i64(...)` directly from app code?
4. Is the new optional `block_size` front-door parameter generic and limited to preserving the existing compact-mask tuning knob?
5. Do all claim boundaries remain blocked: no release, public speedup, RT-core speedup, true-zero-copy, paper reproduction, hidden dispatch, or app-specific engine-logic authorization?
6. Are there any app-specific terms or policies leaking into the native/runtime front-door layer rather than staying in app wrappers and docs?

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test tests.goal2999_triangle_counting_numba_compact_mask_wiring_test tests.goal3002_rayjoin_numba_compact_mask_wiring_test tests.goal3147_compact_mask_front_door_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
```

If reviewing on Linux:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test tests.goal2999_triangle_counting_numba_compact_mask_wiring_test tests.goal3002_rayjoin_numba_compact_mask_wiring_test tests.goal3147_compact_mask_front_door_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
```

## Expected Output

Write the review to one of these paths, depending on reviewer:

- Claude: `docs/reviews/goal3152_claude_review_goal3151_v2_8_benchmark_front_door_adoption_2026-06-03.md`
- Gemini: `docs/reviews/goal3152_gemini_review_goal3151_v2_8_benchmark_front_door_adoption_2026-06-03.md`

Use one of the standard verdict values: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This handoff does not request release approval. It is only a review of the Goal3151 internal adoption audit.

