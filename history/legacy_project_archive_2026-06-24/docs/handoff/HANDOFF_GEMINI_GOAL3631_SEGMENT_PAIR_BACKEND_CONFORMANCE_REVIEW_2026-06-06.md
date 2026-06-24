# Gemini Review Request: Goal3631 Segment-Pair Backend Conformance

Please perform a read-only independent review of Goal3631.

## Files To Read

- `scripts/goal3631_segment_pair_backend_conformance_runner.py`
- `docs/reports/goal3631_segment_pair_backend_conformance_a5000_2026-06-06.md`
- `docs/reports/goal3631_segment_pair_backend_conformance_a5000/summary.json`
- `tests/goal3631_segment_pair_backend_conformance_a5000_test.py`
- Context, if needed:
  - `src/rtdsl/segment_pair_contracts.py`
  - `docs/reports/goal3625_segment_pair_intersection_contract_foundation_2026-06-06.md`
  - `docs/reports/goal3627_segment_pair_typed_output_residency_contract_2026-06-06.md`
  - `docs/reports/goal3629_segment_pair_dense_count_reference_oracle_2026-06-06.md`

## Review Questions

1. Does Goal3631 genuinely prove same-contract count conformance between the Python strict-v0 reference, the CuPy strict-v0 dense baseline, and the RTDL/OptiX prepared dense count route for the tested cases?
2. Does the runner remain app-free and avoid relying on RayJoin-specific loaders or semantics?
3. Does the artifact correctly distinguish device-resident count-column evidence from broader multi-column residency, true-zero-copy, public-speedup, broad RT-core, release, or RayJoin paper-reproduction claims?
4. Are the diagnostics and timings framed as internal conformance evidence rather than public benchmark claims?
5. Are there missing tests, wording issues, or next-step blockers before this segment-pair primitive can be used as a v2.9/v3.0 foundation?

## Expected Output

Write the review to:

`docs/reviews/goal3632_gemini_review_goal3631_segment_pair_backend_conformance_2026-06-06.md`

Use one of these verdict values exactly:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please state clearly that this is an independent Gemini review. Do not edit source files other than the requested review document.
