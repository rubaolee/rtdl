# Goal4649 Completion Consensus

Date: 2026-06-25
Goal:
`future/v4/v4_goals_4647_4658_revised_partner_promotion_and_app_gate_2026-06-25.md#goal4649---cupy-front-door-certification-gate`

## Verdict

```text
goal4649_complete__goal4650_may_start
```

Goal4649 is complete as a narrow CuPy partner front-door certification gate for
`grouped_vector_sum_f64x2`. It does not authorize blanket CuPy support, public
performance wording, or catalog promotion before Goal4651.

## Completion Evidence

- Report:
  `future/v4/v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md`
- Target code:
  `src/rtdsl/v4_cupy_certification.py`
- Gate script:
  `scripts/v4_goal4649_cupy_grouped_reduction_certification_gate.py`
- POD evidence:
  `future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json`
- POD markdown:
  `future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.md`
- Tests:
  `tests/v4_goal4649_cupy_certification_gate_test.py`
  `tests/v4_goal4649_cupy_certification_pod_evidence_test.py`
- Call for review:
  `future/v4/reviews/call_for_review_v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md`

## Local And POD Verification

Local:

```text
py -m unittest tests.v4_goal4649_cupy_certification_gate_test tests.v4_goal4649_cupy_certification_pod_evidence_test tests.v4_goal4648_partner_promotion_contract_test
Ran 13 tests in 1.256s
OK

GOAL4649_POD_JSON_OK
```

POD:

```text
root@194.68.245.170 -p 22089
GPU: NVIDIA RTX A5000
driver: 570.195.03
Python: 3.12.3
CuPy: 14.1.1
```

Final live summary:

```text
status: goal4649_cupy_gate_passed_pending_review
ready_target_count: 2
live_rows_passed: 2
live_rows_failed: 0
all_correctness_parity: true
all_no_hot_host_materialization: true
min_representative_speedup: 1716.8217704918034
cupy_performance_claim_authorized: false
```

## Review Seats

| Seat | Result | Notes |
|---|---|---|
| Claude | `accept_goal4649_complete` | Accepted narrow CuPy grouped-vector-sum certification; said catalog/docs wait for Goal4651. |
| Antigravity | `accept_goal4649_complete` | Accepted evidence and non-authorization boundaries. |
| Carver subagent | `accept_goal4649_complete` | Accepted completion and independently ran/read 13-test verification. |

## Scope Certified

Certified by this goal:

```text
CuPy grouped_vector_sum_f64x2 partner front-door gate at:
- 262144 rows / 1024 groups
- 524288 rows / 2048 groups
```

Not certified by this goal:

- blanket CuPy support;
- Hausdorff CuPy;
- hitcount CuPy;
- CuPy RT-core Tier-2 claim;
- whole-app or all-benchmark speedup;
- public V4 performance wording;
- true zero-copy.

## Denominator Correction

An earlier live run used a misleading group-level synthetic denominator. That
run is not used for completion. The final evidence uses a full Python row loop
over every input row and records it as `cpu_row_loop_seconds`.

This denominator is accepted only as a certification floor check against the
pre-frozen `>=1.20x` gate. It is not public speedup wording.

## Non-Authorization Preserved

Goal4649 does not authorize:

- public V4 release/tag wording;
- broad V4 speedup claims;
- whole-app / all-benchmark V4 speedup claims;
- blanket CuPy support;
- CuPy RT-core Tier-2 claims;
- Hausdorff CuPy claims;
- hitcount CuPy claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- true-zero-copy claims;
- partner migration or partner parity as V4 speed evidence.

## Goal-Level Decision Audit

1. Did I make a foolish decision?

Yes, briefly: the first POD live denominator was too weak because it looped over
groups rather than every row.

2. If yes, what actions made it foolish?

I used a convenient synthetic formula and could have let it pass because the
test was otherwise green. That would have produced an audit problem.

3. Was there another possibility that avoided being trapped in one idea?

Yes. Replace it with a full Python row-loop denominator and rerun the POD gate.
That is what was done.

4. Can I start a different path that actually solves the problem?

Yes. Start Goal4650: fixed Numba continuation certification, while keeping
arbitrary callbacks blocked.

## Next Authorized Work

Goal4650 may start:

```text
Fixed Numba Continuation Certification Gate
```

Goal4651 must handle any public catalog promotion. Goal4649 itself does not
change public measured catalog/docs.
