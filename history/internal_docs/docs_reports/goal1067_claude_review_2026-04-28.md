# Goal1067 Scale-Contract Repair Audit — Claude Review

Date: 2026-04-28  
Reviewer: Claude (claude-sonnet-4-6)  
Verdict: **PASS** with minor test-coverage gaps noted

---

## Criteria Assessment

### 1. Correctly blocks Hausdorff due to analytic tiled oracle

**PASS.**

The Hausdorff dry-run (`copies: 20000`, `point_count_a/b: 80000`) records a
`cpu_reference_total_sec` of ~0.000105 s — sub-millisecond, essentially free.
The audit correctly diagnoses this as an analytic tiled oracle artefact: the
fixture inflates logical point count without creating a real CPU benchmark, so
no same-semantics comparison against an RTX run is possible.

Decision and pod policy are correct:
- `decision: blocked_scale_contract_not_repaired`
- `pod_policy: no_pod_until_benchmark_contract_changes`
- `next_local_action` explicitly forbids submitting this as a public speedup
  candidate and prescribes either reclassifying it as a parity path or
  redesigning with a non-analytic contract.

The Hausdorff source dry-run itself (`cloud_claim_contract.activation_status:
deferred_until_real_rtx_phase_run_and_review`) is consistent with the block.

### 2. Barnes-Hut 1M treated as future pod candidate after review only

**PASS.**

The 200 k dry-run `cpu_reference_total_sec` is 0.035 s (below the 100 ms
scale target). The 1M dry-run raises this to 0.171 s, crossing the threshold
while preserving full node-coverage semantics (`covered_body_count: 1000000`).

The audit correctly upgrades recommendation to 1M bodies and sets:
- `decision: pod_candidate_after_review`
- `pod_policy: eligible_for_next_pod_after_review`
- `next_local_action` explicitly keeps public wording blocked until real RTX
  timing, baseline comparison, and 2-AI review exist.

The `recommended_cloud_scale.skip_validation: true` flag is acceptable here:
the `validation_reference` field mandates one smaller validated RTX pass before
large timing repeats, and the `pod_candidate_after_review` gate requires review
before the recommendation is acted on. No validation bypass is being exercised
locally.

### 3. No-cloud / no-public-speedup boundaries preserved

**PASS.**

The audit JSON `boundary` field reads verbatim:
> "Goal1067 is a local scale-contract audit. It does not run OptiX, does not
> run cloud, does not change public wording, and does not authorize public RTX
> speedup claims."

Both input dry-run files carry `activation_status:
deferred_until_real_rtx_phase_run_and_review`. The script writes no OptiX
calls, issues no cloud jobs, and modifies no public documentation. The
`recommended_cloud_scale` block is a forward recommendation only, guarded by
the `pod_candidate_after_review` gate.

### 4. Test adequacy

**ADEQUATE with minor gaps.**

The two tests collectively cover:

| Check | Covered |
| --- | --- |
| `payload["valid"]` is True | ✓ |
| Row counts (2 total, 1 blocked, 1 pod-after-review) | ✓ |
| Hausdorff decision and pod_policy exact strings | ✓ |
| `"analytic tiled oracle"` in Hausdorff reason | ✓ |
| Hausdorff cpu_reference < 0.01 s | ✓ |
| Barnes decision exact string | ✓ |
| Barnes recommended body_count == 1 000 000 | ✓ |
| Barnes tested_scales[-1] cpu_reference >= 0.1 s | ✓ |
| Boundary contains `"does not run cloud"` | ✓ |
| CLI writes valid JSON and markdown end-to-end | ✓ |

**Gaps (non-blocking):**

1. Boundary string is only partially asserted (`"does not run cloud"`); the
   clauses `"does not run OptiX"` and `"does not authorize public RTX speedup
   claims"` are not independently checked.
2. No assertion that `recommended_cloud_scale.validation_reference` is present
   when `skip_validation` is True — a future schema change could silently drop
   the mitigation text.
3. No assertion that `next_local_action` for Barnes explicitly mentions the
   2-AI review requirement (the policy intent is load-bearing but untested).

None of these gaps affects the correctness of the audit logic or the validity
flag; they represent boundary conditions worth tightening before the pod
submission workflow is automated.

---

## Overall Assessment

The audit is logically sound, internally consistent, and correctly applies the
scale-contract criteria. Hausdorff is blocked for the right reason (analytic
oracle, not a scale failure). Barnes-Hut 1M is the sole repaired candidate and
is correctly gated behind review. The no-cloud/no-public-speedup boundary is
explicitly encoded in the output and honoured by the script. The test suite
covers the critical decision paths; the three noted gaps are improvements, not
defects.

**Verdict: PASS. Goal1067 artifacts are fit to merge as-is. The three test
gaps should be addressed before any downstream automation uses the audit output
to trigger pod submissions.**
