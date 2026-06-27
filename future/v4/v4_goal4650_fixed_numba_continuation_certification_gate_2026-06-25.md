# V4 Goal4650 Fixed Numba Continuation Certification Gate

Date: 2026-06-25
Status: `goal4650_fixed_numba_continuation_certification_gate_pass_pending_review`

## Purpose

Goal4650 certifies one fixed Numba continuation for the V4 partner-promotion
chain:

- operator: `fixed_radius_graph_component_union_3d`
- API surface: `v4_fixed_radius_graph_component_union_3d_device_arrays`
- partner: `numba`
- target app row: `rt_dbscan`
- source evidence: Goal4635 POD gate

This is not a new broad callback feature. It is a bounded promotion of an
already measured generic continuation into the V4 certification ledger.

## Evidence Source

Primary measured evidence:

- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/README.md`
- `future/v4/reviews/claude_v4_goal4635_component_union_target_protocol_review_2026-06-25.md`

Goal4650 machine evidence:

- `future/v4/evidence/v4_goal4650_fixed_numba_continuation_certification_2026-06-25.json`

Code record:

- `src/rtdsl/v4_numba_fixed_continuation_certification.py`
- exported through `src/rtdsl/v4.py`

Tests:

- `tests/v4_goal4650_fixed_numba_continuation_certification_test.py`

## Certified Scope

The certified scope is fixed and narrow:

| Field | Value |
| --- | --- |
| partner | `numba` |
| contract class | `fixed_continuation_certification` |
| accepted signature | `fixed_radius_graph_component_union_3d(device columns) -> component labels` |
| fixed operator only | `true` |
| arbitrary callback supported | `false` |
| measured partners | `("numba",)` |
| declared unmeasured partners | `("torch", "cupy")` |
| compile/cache timing boundary | compile excluded from hot path but reported as phase telemetry |

## Numeric Gate

The measured Goal4635 gate is reused without reinterpretation.

| Check | Result | Floor |
| --- | ---: | ---: |
| correctness parity | pass | 1.0 |
| canonical component signatures match | pass | required |
| component-signature shortcut blocked | pass | required |
| legacy no-regression | pass | required |
| runner vs Embree hot speedup | 1.393079x | 1.20x |
| runner vs Embree wall speedup | 1.600125x | 1.20x |
| runner vs legacy wall speedup | 1.208004x | 0.98x |
| hot-path host materialization | false | false |

Validated environment from Goal4635:

- GPU: NVIDIA RTX A5000
- driver: 570.195.03
- OptiX ABI: 8.0
- Python: 3.12.3
- Numba: 0.65.1
- dataset: clustered3d, 262144 points

## What This Proves

Goal4650 proves that V4 can expose the existing measured component-union
continuation as a fixed Numba-certified V4 operator surface.

It also preserves the V4 integrity boundary:

- it does not add a DBSCAN-native kernel;
- it does not support arbitrary user Numba callbacks;
- it does not authorize raw OptiX callback support;
- it does not authorize a whole-app RTDBSCAN speedup claim;
- it does not authorize broad V4 speedup wording.

## Verification

Command run:

```text
py -m unittest tests.v4_goal4650_fixed_numba_continuation_certification_test tests.v4_goal4635_component_union_target_test tests.v4_operator_catalog_test tests.v4_goal4648_partner_promotion_contract_test
```

Result:

```text
Ran 30 tests
OK
```

Note: the local Windows Python emitted the known startup warning
`Could not find platform independent libraries <prefix>`, but the tests exited
successfully.

## Goal-Level Decision Audit

Decision:

Certify the existing Goal4635 component-union evidence as the Goal4650 fixed
Numba continuation gate, without running a new POD job.

1. Was I stupid?
   No. The existing Goal4635 POD evidence is exactly the measured source needed
   for this certification; rerunning the POD would be process churn unless the
   evidence is challenged by review.

2. What action would have made the decision stupid?
   Treating this as proof of arbitrary Numba callbacks, broad V4 speedup, or
   whole-app RTDBSCAN acceleration.

3. Was there another path?
   Yes: run another POD job immediately. That would spend resources without
   changing the certification fact unless the reviewers reject the Goal4635
   evidence.

4. Can I now take a better path?
   Yes. Send this bounded certification to review, then use it as an input to
   Goal4651 partner catalog promotion if accepted.

## Non-Authorization

This goal does not authorize release, broad V4 speedup claims, whole-app claims,
all-benchmark claims, arbitrary Numba callback support, raw OptiX callback
support, CuPy performance claims, true-zero-copy claims, C ABI/embedding claims,
non-Python host claims, or app-specific native kernels.
