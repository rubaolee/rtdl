# Call For Review: V4 Goal4649 CuPy Front-Door Certification Gate

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4649_complete`
- `accept_with_minor_edits`
- `reject_goal4649_incomplete`
- `blocked_missing_context`

## Context

Goal4649 certifies the first CuPy V4 partner front-door surface under the
Goal4648 numeric contract. It is intentionally narrow: two CuPy
`grouped_vector_sum_f64x2` grouped-reduction targets passed on the POD. This is
not blanket CuPy support, not all-app performance, not RT-core Tier-2 CuPy, and
not public speedup wording.

## Files To Review

- Goal4649 report:
  `future/v4/v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md`
- Target code:
  `src/rtdsl/v4_cupy_certification.py`
- Gate script:
  `scripts/v4_goal4649_cupy_grouped_reduction_certification_gate.py`
- POD live evidence:
  `future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json`
- POD live markdown:
  `future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.md`
- Tests:
  `tests/v4_goal4649_cupy_certification_gate_test.py`
  `tests/v4_goal4649_cupy_certification_pod_evidence_test.py`
- Previous goal completion:
  `future/v4/reviews/goal4648_completion_consensus_2026-06-25.md`

## Local Verification

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
CuPy: 14.1.1
```

## Questions

1. Is Goal4649 complete enough to start Goal4650?
2. Do the two passed rows legitimately certify a narrow CuPy
   `grouped_vector_sum_f64x2` partner front-door surface?
3. Is it correct that Hausdorff/hitcount CuPy remain mapping debt, not support?
4. Is the denominator honest enough for a certification floor check after the
   correction from group formula to full Python row loop?
5. Are the evidence fields sufficient: correctness, scale, denominator,
   environment, hot host-materialization flag, claim boundaries?
6. Does this preserve AM1: partner migration/parity cannot become V4 speed
   evidence?
7. Should any public catalog/docs be updated now, or should promotion wait for
   Goal4651 catalog gate?

## Non-Authorization

This review must not authorize:

- public V4 release/tag wording;
- broad V4 speedup language;
- app-level V4-vs-V2.14/V3 claims;
- blanket CuPy support;
- CuPy RT-core Tier-2 claims;
- Hausdorff CuPy claims;
- hitcount CuPy claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- true-zero-copy claims;
- treating partner migration or partner parity as V4 speed evidence.
