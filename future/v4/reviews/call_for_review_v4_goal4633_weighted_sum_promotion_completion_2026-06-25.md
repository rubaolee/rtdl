# Call For Review: V4 Goal4633 Weighted-Sum Promotion Completion

Date: 2026-06-25

Requested verdict labels:

- `approve_goal4633_promote_measured_after_catalog_update`
- `approve_goal4633_threshold_pass_but_keep_candidate`
- `reject_goal4633_evidence_or_boundary`
- `reject_goal4633_requires_rerun`

Primary files:

- `future/v4/v4_goal4633_weighted_sum_promotion_decision_2026-06-25.md`
- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json`
- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md`
- `src/rtdsl/v4_weighted_sum_promotion_decision.py`
- `tests/v4_goal4633_weighted_sum_promotion_decision_test.py`

Context:

- Claude reviewed the Goal4633 protocol and returned
  `approve_with_required_amendments`.
- The required amendment was applied: the comparison is now called
  same-operator comparable-route, with explicit wording that it measures host
  materialization path versus device-resident output path, not pure kernel
  speedup.
- The POD gate ran on RTX A5000 with Torch CUDA.

Gate results:

| Rays | Parity | Ratio |
|---:|---|---:|
| 32768 | true | 2.1459x |
| 131072 | true | 1.6329x |
| 262144 | true | 1.3564x |
| 524288 | true | 1.2011x |

Thresholds:

- per-shape floor: `>=1.20x`
- geomean floor: `>=1.50x`
- observed min: `1.2011325646448796`
- observed geomean: `1.5457333064727565`

Questions:

1. Is the evidence sufficient to promote weighted-sum to a measured Torch CUDA
   V4 Tier-2 surface after catalog/docs/tests are updated?
2. Does the largest row barely clearing the threshold require keeping it
   candidate despite threshold pass?
3. Is the comparison boundary honest and sufficient?
4. Are any reruns required before promotion?
5. If approved, what exact catalog/coverage wording is authorized?

Do not authorize:

- V4 release;
- whole-application speedup wording;
- broad V4 speedup wording;
- CuPy performance claims;
- Tier-3 support;
- public true-zero-copy wording;
- C ABI / embedding / non-Python-host scope.
