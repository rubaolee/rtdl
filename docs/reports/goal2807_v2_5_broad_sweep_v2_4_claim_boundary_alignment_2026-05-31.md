# Goal2807 v2.5 Broad Sweep v2.4 Claim-Boundary Alignment

Date: 2026-05-31

Status: implemented locally.

Verdict: accept-with-boundary.

## Purpose

After Goal2806, a broader pod sweep across 100 v2.4/v2.5-era test modules
found one stale v2.4 assertion:

```text
tests.goal2659_v2_4_benchmark_protocol_integration_test
test_raydb_native_payload_exposes_validated_phase_timing
```

The test still expected the RayDB native payload phase-timing metadata to set
`promoted_performance_path=True`. That conflicts with the later Goal2690
contract-honesty repair and the current v2.5 rule that same-contract timing can
be valid without promoting a public or default performance path.

## Change

The test now asserts:

```python
self.assertFalse(timing["promoted_performance_path"])
self.assertTrue(timing["same_phase_contract_as_basis"])
```

This preserves the important compatibility property: the payload still exposes
validated v2.4 phase timing and still compares the same phase contract as the
basis row. It removes only the obsolete promotion expectation.

## Boundary

This goal does not change runtime behavior. It updates a stale regression test
to match the current v2.5 claim discipline.

It does not authorize:

- v2.5 release;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- Triton preview auto-selection.

## Validation

Local focused validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2659_v2_4_benchmark_protocol_integration_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 13 tests in 0.641s
OK
```

The broader pod sweep should be rerun after this alignment.
