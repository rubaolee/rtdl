# Handoff: Gemini Review Goal3349-3351 Owner-Face Priority Chain

Please perform an independent read-only review of the current v2.8 owner-face priority chain and write the review to:

- `docs/reviews/goal3352_gemini_review_owner_face_priority_contract_and_rank_signals_2026-06-04.md`

## Scope

Review the changes through commit `14282ada`:

- Goal3349: formal explicit-priority owner-face pipeline contract.
- Goal3350: primitive catalog wiring to the formal contract.
- Goal3351: deterministic priority-row derivation from caller-supplied rank signals.

Read at minimum:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/primitive_hierarchy.py`
- `docs/rtdl_primitive_catalog.md`
- `tests/goal3349_owner_face_priority_pipeline_contract_test.py`
- `tests/goal3350_owner_face_priority_contract_catalog_wiring_test.py`
- `tests/goal3351_owner_face_priority_rank_signal_derivation_test.py`
- `docs/reports/goal3349_owner_face_priority_pipeline_contract_2026-06-04.md`
- `docs/reports/goal3350_owner_face_priority_contract_catalog_wiring_2026-06-04.md`
- `docs/reports/goal3351_owner_face_priority_rank_signal_derivation_2026-06-04.md`

## Verification Already Run

- Goal3349 focused chain: `Ran 19 tests in 0.026s OK`
- Goal3350 catalog/discovery set: `Ran 30 tests in 0.093s OK`
- Broader owner-face chain after Goal3350: `Ran 53 tests in 0.026s OK`
- Goal3351 focused set: `Ran 18 tests in 0.021s OK`
- Broader owner-face chain after Goal3351: `Ran 59 tests in 0.027s OK`
- Final Goal3351 focused rerun: `Ran 6 tests in 0.003s OK`

## Review Questions

1. Does the chain remain app-agnostic?
2. Does Goal3351 correctly derive priorities only from caller-supplied generic rank signals, without engine-inferred ownership?
3. Are missing, duplicate, and tied-rank fail-closed behaviors sufficient before native/device lowering?
4. Does the catalog wiring avoid primitive promotion while improving discovery?
5. What, if anything, should be fixed before the next v2.8 engineering step?

## Required Boundaries

- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
- Do not authorize release, public speedup, broad RT-core speedup, true zero-copy, RTDL-beats-RayJoin, or RayJoin paper reproduction claims.
- The native engine must not infer CDB/RayJoin ownership semantics.
- If accepting, state exactly what remains blocked before promotion from Python reference contract to device/native implementation.
