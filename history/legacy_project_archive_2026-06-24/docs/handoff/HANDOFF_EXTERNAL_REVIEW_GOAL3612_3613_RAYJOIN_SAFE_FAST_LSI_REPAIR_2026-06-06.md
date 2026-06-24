# Handoff: External Review For Goal3612/Goal3613 RayJoin Safe/Fast LSI Repair

Please perform a read-only independent review of the Goal3612/Goal3613 RayJoin evidence on `main`.

## Files To Read

- `docs/reports/goal3612_rayjoin_safe_mixed_route_composite_2026-06-06.md`
- `docs/reports/goal3612_rayjoin_safe_mixed_route_composite_a5000/summary.json`
- `scripts/goal3612_rayjoin_safe_mixed_route_composite.py`
- `tests/goal3612_rayjoin_safe_mixed_route_composite_test.py`
- `docs/reports/goal3613_lsi_left_id_dense_count_exact_predicate_2026-06-06.md`
- `docs/reports/goal3613_lsi_left_id_dense_count_exact_predicate_a5000/mismatch_after_patch.json`
- `docs/reports/goal3613_lsi_left_id_dense_count_exact_predicate_a5000/fast_mixed_after_patch.json`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `tests/goal3613_lsi_left_id_dense_count_exact_predicate_test.py`
- `tests/goal3613_lsi_left_id_dense_count_exact_predicate_artifact_test.py`
- Context: `docs/reports/goal3610_rayjoin_lsi_4096_count_mismatch_probe_2026-06-06.md`, `docs/reviews/goal3611_gemini_review_goal3609_3610_rayjoin_mixed_composite_lsi_mismatch_2026-06-06.md`

## Questions

1. Does Goal3612 honestly repair the 4096 mixed-route composite by using exact prepared RTDL/OptiX LSI count, with all counts matching and a reported `193.939x` safe mixed speedup versus all-CuPy dense?
2. Does Goal3613 correctly tighten the specialized left-id dense count pipeline from conservative candidate counting to strict segment predicate counting without introducing RayJoin/CDB app-specific engine logic?
3. Does the Goal3613 evidence support that the repaired dense count route now matches CuPy exactly at 4096 (`4977` vs `4977`, `diff_count=0`) and yields a valid mixed composite of `188.997x`, with LSI route speedup over `2000x`?
4. Are the boundaries clear enough: internal evidence only, no release/public speedup/RayJoin-paper reproduction/RTDL-beats-RayJoin/broad RT-core/true-zero-copy/default-route authorization?
5. What risks remain before any public RayJoin claim or release packet? Pay special attention to float strict predicate versus host double exact refinement, dataset diversity, and whether the primitive contract needs a documented tolerance policy.

## Output

For Gemini, write:

`docs/reviews/goal3614_gemini_review_goal3612_3613_rayjoin_safe_fast_lsi_repair_2026-06-06.md`

For Claude, write:

`docs/reviews/goal3615_claude_review_goal3612_3613_rayjoin_safe_fast_lsi_repair_2026-06-06.md`

Use one verdict from: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.

Do not edit source files or reports other than writing the requested review file.
