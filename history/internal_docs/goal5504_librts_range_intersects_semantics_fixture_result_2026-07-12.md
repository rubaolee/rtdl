# Goal5504: LibRTS Range-Intersects Contract Fixtures

## Status

`implemented__source_driven_semantics_diagnostic__review_pending`

## Purpose

Goal5504 exercises the two contracts discovered in Goal5503 on deterministic
float32 fixtures:

1. the independent CPU inclusive AABB overlap contract; and
2. a source-driven emulation of the author's `RayParams<float,2>::IsHit`
   forward/reverse diagonal shader path.

The fixture runner is app-owned diagnostic code. It does not call the author
binary, does not call RTDL, and does not claim a GPU runtime result.

## Result

The five-case matrix contains four non-discriminating cases and one
float32-boundary discriminator:

| Case | CPU inclusive | GPU RayParams emulation | Meaning |
|---|---:|---:|---|
| interior overlap | true | true | common interior case |
| edge touch | true | true | shared vertical boundary |
| one-ULP gap after box max | false | true | gamma-expanded float32 boundary |
| one-ULP overlap before box max | true | true | one-ULP overlap |
| corner touch | true | true | shared corner / diagonal behavior |

The corrected emulation reproduces the source-level ingredients: float32 arithmetic,
`t0=0`, `t1=nextafterf(1.0, FLT_MAX)`, `tFar` multiplication by
`1 + 2 * FLT_GAMMA(3)`, the query diagonal, and the reverse envelope
diagonal. It also preserves the shader's important `if (!box_hit)` polarity.
On four cases the source-driven behavior agrees with the CPU inclusive
predicate. On the one-ULP gap, the source-driven behavior accepts a query that
the direct CPU inclusive predicate rejects. This is the concrete semantic
distinction carried into Goal5505.

## Interpretation

This result does not explain the two large full-input disagreements. It does
provide a corrected source-level model that can be checked against a real
author/RTDL runtime fixture in Goal5505. Until that check is complete, neither
contract is promoted to a full-input adjudicator.

The correct immediate action is to preserve generic RTDL behavior and carry
the two contracts separately into Goal5505's scalable oracle/decision work.
Do not copy the diagonal-ray behavior into RTDL core merely to make counts
match.

## Claim Boundary

```json
{
  "author_gpu_runtime_executed": false,
  "cpu_oracle_is_author_truth": false,
  "cpu_gpu_equivalence_proven": false,
  "full_input_adjudication": false,
  "rtdl_core_change_authorized": false,
  "author_specific_rtdl_core_behavior_authorized": false,
  "performance_ratio_authorized": false
}
```

Machine-readable evidence:

`Paper-reproduction-apps/librts-paper/results/goal5504_range_intersects_semantics_fixtures.json`
