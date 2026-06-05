# External Review Handoff: Goal3427/Goal3428 Prepared Refiner and Chunk Guard

Please perform an independent read-only review of the latest `main` branch after Goal3428.

## Scope

Review the Goal3427 reusable prepared CuPy closed-shape refiner and the Goal3428 ordinal chunk-guard follow-up.

Primary files:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/goal3427_prepared_cupy_refiner_timing_probe.py`
- `tests/goal3424_closed_shape_instance_identity_refinement_test.py`
- `tests/goal3427_prepared_cupy_refiner_timing_test.py`
- `docs/reports/goal3427_prepared_cupy_refiner_timing_2026-06-04.md`
- `docs/reports/goal3427_prepared_cupy_refiner_timing_probe_2026-06-04.json`
- `docs/reports/goal3428_closed_shape_ordinal_chunk_guard_2026-06-05.md`
- Prior reviews: `docs/reviews/goal3425_claude_review_goal3424_instance_identity_refinement_2026-06-04.md` and `docs/reviews/goal3426_gemini_review_goal3424_instance_identity_refinement_2026-06-04.md`

## Questions To Answer

1. Does Goal3427 remain app-agnostic? In particular, does the prepared refiner cache generic point/shape lookup arrays and consume generic ordinal-bearing candidate columns, without moving RayJoin/CDB policy into the native engine?
2. Does the prepared refiner preserve correctness and fail closed when ordinal columns are missing, length-mismatched, or out of range?
3. Is the Goal3427 pod timing artifact coherent? Key expected values are: host exact median `0.084061s`, candidate stream median `0.018988s`, one-shot CuPy refine median `0.091222s`, prepared CuPy refine median `0.001425s`, candidate+prepared total median `0.020430s`, prepared total vs host median ratio `0.243033`, all counts matching host.
4. Does Goal3428 fully close Claude Goal3425 Finding 1 by setting `lp.point_index_offset = static_cast<uint32_t>(point_offset)` inside the closed-shape candidate-column chunk loop?
5. Does Goal3428 add meaningful regression coverage for the duplicate-public-ID ordinal path?
6. Are all public/release/performance/zero-copy/native-default-route claims still blocked?

## Required Output Paths

Claude:

- `docs/reviews/goal3429_claude_review_goal3427_3428_prepared_refiner_and_chunk_guard_2026-06-05.md`

Gemini:

- `docs/reviews/goal3430_gemini_review_goal3427_3428_prepared_refiner_and_chunk_guard_2026-06-05.md`

Use one of the normal verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not edit source code. If you find a bug, record it as a finding with file/line evidence and required before next-step guidance.
