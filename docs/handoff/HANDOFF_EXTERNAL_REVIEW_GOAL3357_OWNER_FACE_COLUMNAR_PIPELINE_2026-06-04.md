# Handoff: External Review Goal3349-3356 Owner-Face Columnar Pipeline

Please perform an independent review of the v2.8 owner-face priority and columnar pipeline chain through commit `9f810c9f`.

Expected review output:

- Claude: `docs/reviews/goal3357_claude_review_owner_face_columnar_pipeline_2026-06-04.md`
- Gemini: `docs/reviews/goal3357_gemini_review_owner_face_columnar_pipeline_2026-06-04.md`

If only one external AI is available, write the corresponding review file. Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Important Note

A previous Gemini Flash run for Goal3349-3351 produced only a pending template review, so that stub was removed and must not be counted as review evidence.

## Scope

Read at minimum:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/primitive_hierarchy.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal3349_owner_face_priority_pipeline_contract_2026-06-04.md`
- `docs/reports/goal3350_owner_face_priority_contract_catalog_wiring_2026-06-04.md`
- `docs/reports/goal3351_owner_face_priority_rank_signal_derivation_2026-06-04.md`
- `docs/reports/goal3353_owner_face_priority_columnar_derivation_2026-06-04.md`
- `docs/reports/goal3354_owner_face_columnar_selection_front_door_2026-06-04.md`
- `docs/reports/goal3355_owner_face_columnar_filter_front_door_2026-06-04.md`
- `docs/reports/goal3356_v2_8_owner_face_columnar_pipeline_status_2026-06-04.md`
- `tests/goal3349_owner_face_priority_pipeline_contract_test.py`
- `tests/goal3350_owner_face_priority_contract_catalog_wiring_test.py`
- `tests/goal3351_owner_face_priority_rank_signal_derivation_test.py`
- `tests/goal3353_owner_face_priority_columnar_derivation_test.py`
- `tests/goal3354_owner_face_columnar_selection_front_door_test.py`
- `tests/goal3355_owner_face_columnar_filter_front_door_test.py`
- `tests/goal3356_v2_8_owner_face_columnar_pipeline_status_test.py`

## What Changed

- Goal3349 formalized `OWNER_FACE_PRIORITY_PIPELINE_CONTRACT`.
- Goal3350 wired primitive discovery/catalog to the formal contract while keeping the node `candidate_behavior`.
- Goal3351 added row priority derivation from caller-supplied rank signals.
- Goal3353 added columnar priority derivation.
- Goal3354 added columnar owner-face selection.
- Goal3355 added columnar owner-face membership filtering.
- Goal3356 summarized the complete row/column reference pipeline and review state.

## Validation Already Run

- Goal3349 focused chain: `Ran 19 tests in 0.026s OK`
- Goal3350 catalog/discovery set: `Ran 30 tests in 0.093s OK`
- Broader owner-face chain after Goal3350: `Ran 53 tests in 0.026s OK`
- Goal3351 focused set: `Ran 18 tests in 0.021s OK`
- Broader owner-face chain after Goal3351: `Ran 59 tests in 0.027s OK`
- Goal3353 focused set: `Ran 15 tests in 0.018s OK`
- Broader owner-face chain after Goal3353: `Ran 64 tests in 0.028s OK`
- Goal3354 focused set: `Ran 20 tests in 0.020s OK`
- Broader owner-face chain after Goal3354: `Ran 69 tests in 0.031s OK`
- Goal3355 focused set: `Ran 26 tests in 0.024s OK`
- Broader owner-face chain after Goal3355: `Ran 75 tests in 0.031s OK`
- Goal3356 status stack: `Ran 28 tests in 0.023s OK`

## Review Questions

1. Does the chain stay app-agnostic, with CDB/RayJoin semantics outside the native engine?
2. Are rank-signal priority derivation, columnar selection, and columnar filtering correctly framed as Python reference contracts rather than native/device implementations?
3. Are the fail-closed conditions adequate before any device/native lowering?
4. Does the primitive catalog avoid premature promotion while improving discovery?
5. What should be fixed before the next v2.8 engineering step?

## Required Boundaries

- No release authorization.
- No public speedup claim.
- No RayJoin paper reproduction claim.
- No RTDL-beats-RayJoin claim.
- No broad RT-core speedup claim.
- No true zero-copy claim.
- Native engine must not infer ownership policy.
- If accepting, state exactly what remains blocked before promotion from Python reference contract to device/native implementation.
