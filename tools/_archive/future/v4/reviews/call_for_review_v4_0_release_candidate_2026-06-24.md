# Call For Review: V4.0 Development-State Decision Packet

Date: 2026-06-24

## Review Request

Please critically review the V4.0 development-state decision packet for
`goal4623`. This is a release-readiness decision request, not a release authorization.

## Artifacts To Review

- Decision packet: `future/v4/v4_0_development_state_decision_packet_2026-06-24.md`
- V4 front door: `src/rtdsl/v4.py`
- Scope gate: `src/rtdsl/v4_scope.py`
- Current scope evidence: `future/v4/evidence/v4_goal4623_scope_gate_current_2026-06-24.json`
- Final goal4623 GPU catalog gate:
  `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.json`
- Final goal4623 GPU catalog gate markdown:
  `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.md`
- Local dry-run catalog gate:
  `future/v4/evidence/v4_goal4623_final_catalog_dry_run_include_candidates_2026-06-24.json`
- Catalog regression script: `scripts/v4_catalog_regression_gate.py`
- Operator planner: `src/rtdsl/v4_operator_catalog.py`
- Tier-3 callback protocol:
  `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- Tier-3 PTX spike: `future/v4/tier3_numba_ptx_spike.md`
- Tier-3 module-link spike: `future/v4/tier3_optix_module_link_spike.md`

## Questions For Reviewer

1. Is V4.0 correctly scoped to five measured Torch CUDA Tier-2 surfaces and one
   labeled candidate surface?
2. Does the final GPU catalog gate support development-state documentation
   disclosure, while release authorization remains false?
3. Are V4.x deferred items fenced clearly enough, especially Tier-3 callbacks and raw OptiX callback APIs?
4. Are user-facing docs/examples coherent and safe as a current development
   front door?
5. What must change before release-candidate or release authorization can be
   granted?

## Expected Verdict Labels

- `development_state_documentation_disclosure_not_release`
- `approve_with_required_amendments`
- `reject_goal4623_overclaims_or_insufficient_evidence`

## Non-Authorization

This review request does not authorize V4 release, V4 release-candidate status,
broad V4 speedup wording, whole-application speedup wording, Tier-3 callback/PTX
support claims, raw OptiX callback support, public true-zero-copy wording, CuPy
performance claims, embedding/C-ABI claims, non-Python host binding claims, or
app-specific native engine kernels.
