# Call For Review: V4.0 Release Candidate Packet

Date: 2026-06-24

## Review Request

Please critically review the V4.0 release-candidate packet. This is a release
readiness review request, not a release authorization.

## Artifacts To Review

- Candidate packet: `future/v4/v4_0_release_candidate_packet_2026-06-24.md`
- V4 front door: `src/rtdsl/v4.py`
- Scope gate: `src/rtdsl/v4_scope.py`
- Scope evidence: `future/v4/evidence/v4_scope_gate_2026-06-24.json`
- Final GPU catalog gate, serious size: `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json`
- Final GPU catalog gate, smoke size: `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_2026-06-24.json`
- Local V4 full test sweep: `future/v4/evidence/v4_local_full_test_sweep_2026-06-24.md`
- Catalog regression script: `scripts/v4_catalog_regression_gate.py`
- Operator planner: `src/rtdsl/v4_operator_catalog.py`
- Tier-3 PTX spike: `future/v4/tier3_numba_ptx_spike.md`
- Tier-3 module-link spike: `future/v4/tier3_optix_module_link_spike.md`

## Questions For Reviewer

1. Is V4.0 correctly scoped to the three measured Torch CUDA Tier-2 surfaces?
2. Does the final GPU catalog gate support the engineering release-candidate status?
3. Are V4.x deferred items fenced clearly enough, especially Tier-3 callbacks and raw OptiX callback APIs?
4. Are user-facing docs/examples coherent and safe for a future release front door?
5. What must change before release authorization can be granted?

## Expected Verdict Labels

- `approve_release_candidate_not_authorized`
- `approve_with_required_amendments`
- `reject_release_candidate_overclaims`
- `reject_release_candidate_insufficient_evidence`

## Non-Authorization

This review request does not authorize V4 release, broad V4 speedup wording,
whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX
callback support, CuPy performance claims, embedding/C-ABI claims, non-Python
host binding claims, or app-specific native engine kernels.
