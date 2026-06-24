# Handoff: Goal1846 External Review Of Goal1845 Witness Contract

Please perform a read-only independent review of Goal1845.

Files to read:

- `docs/reports/goal1845_optix_partner_witness_output_contract_2026-05-13.md`
- `tests/goal1845_optix_partner_witness_output_contract_test.py`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`

Write your review to:

- `docs/reviews/goal1846_claude_review_goal1845_witness_contract_2026-05-13.md`

Review questions:

1. Is the new witness output contract the right next step after the boolean
   `any_hit_flags` output, rather than trying to reconstruct identity in an
   app-level adapter?
2. Does the implementation preserve the correct boundary: one first-hit witness
   per ray, not the full multi-hit segment/polygon row collector?
3. Are the Python validators strict enough for same-device contiguous `uint32`
   output columns?
4. Are the public claim boundaries correct, especially no v2.0 release, no broad
   RT-core speedup, and no full app-level `segment_polygon_anyhit_rows` claim?
5. What should the next engineering goal be: pod-validate this first-hit witness
   contract, or design the bounded all-witness output contract first?

Use only these verdict values:

- `accept`
- `accept-with-boundary`
- `reject`
- `needs-more-evidence`

Do not edit source files or reports under review except for writing the review
file.
