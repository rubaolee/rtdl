I have all files needed. Here is the verdict.

---

**Verdict**: acceptable

**Findings**: No blocking issues. Three minor observations for the record:

1. **C++/Python prediction parity confirmed.** `collect_k_predicted_carry_payload_copies` in `rtdl_optix_api.cpp:640–668` is structurally identical to `_predicted_carry_payload_copies` in the probe script: same segment-halving loop, same `derived_carry_alias_safe_next` condition (`next == 2 || next % 2 != 0`), same copy-increment logic. The gate expression `baseline_copies >= candidate_copies + min_payload_copy_reduction` at C++:688 matches the Python at probe:100 exactly.

2. **`use_gated_candidate_mode` activates the CUB-tile-sort bundle for all multi-tile counts when the env is set, even when the per-count carry-alias gate does not fire.** This is visible in both the C++ (`use_gated_or_candidate_bundle = use_gated_candidate_mode || use_candidate_bundle_for_case` at line 937–938) and the probe's `expected_topology`. It means setting `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1` changes tile behavior globally while restricting carry-alias to gated counts only. The documentation in the report describes this correctly ("the opt-in flag still enables the optimized baseline bundle… but the candidate carry-alias behavior is restricted"). No correctness risk, but reviewers should be aware the env is not a zero-effect switch for non-gated counts.

3. **65536 RTX 3090 row shows -0.002928ms / 3/5 despite gate-off.** The gate is correctly off (0→0 copies), so this delta is bundle-overhead noise, not carry-alias gain. The report labels it correctly as "gate-off, noise-scale." No issue, but it confirms the flag is not a no-op even for counts that don't pass the threshold.

Gate boundary arithmetic verified independently: 65537 → baseline=5, candidate=0, reduction=5≥4 (activates); 69632 → baseline=4, candidate=0, reduction=4≥4 (activates); 69633 → baseline=4, candidate=1, reduction=3<4 (does not activate); 49153 → reduction=2<4 (does not activate). All consistent with evidence tables and test assertions.

Test `goal1593` checks C++ source strings directly (`assertIn("min_payload_copy_reduction = 4", source)`, etc.) and cross-validates probe topology predictions for all boundary counts. All 26 tests reported OK on both GPUs.

**Recommendation**: Stop GPU pod cycling for this micro-goal. Two architectures (Ada Lovelace / RTX 4090, Ampere / RTX 3090) agree on gate-on and gate-off behavior across the same six counts. The threshold-4 policy is internally self-consistent and the evidence does not require further per-count or per-GPU iteration. Any next step (default-on consideration, promotion discussion) should move to external review and broader design criteria, not more pod work.

**Claim Boundary**: Clear and enforced at three layers. `claim_flags` in the probe script explicitly sets all six authorization flags to `False`; `validate_probe` raises on any deviation; both validation reports state the boundary explicitly. The no-promotion / no-public-speedup / no-default-change scope is unambiguous and machine-checked.
