# V4 Goal4648: Partner Promotion Contract With Numeric Bars

Date: 2026-06-25
Status: candidate completion record, pending external completion review
Previous goal:
`future/v4/reviews/goal4647_completion_consensus_and_review_debt_2026-06-25.md`
Code:
`src/rtdsl/v4_partner_promotion_contract.py`
Front-door export:
`src/rtdsl/v4.py`
Machine-readable evidence:
`future/v4/evidence/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.json`

## Purpose

Goal4648 freezes the pre-run contract for promoting CuPy and fixed Numba
partner surfaces into V4. It does not certify those partners. It defines what
Goal4649 and Goal4650 must prove before any support or performance wording can
change.

The key rule from Claude AM1 remains binding:

```text
Partner migration is not a V4 speed win.
```

## Code-Level Contract

Goal4648 adds a code-visible contract module:

```text
src/rtdsl/v4_partner_promotion_contract.py
```

The unified V4 front door now exports:

- `v4_partner_promotion_contracts()`
- `v4_partner_promotion_contract(partner, fixed=False)`
- `v4_partner_promotion_candidate_allowed(candidate_id, partner=...)`
- `V4_GOAL4648_PARTNER_PROMOTION_CONTRACT_STATUS`

Unsupported promotion requests fail closed. For example, `torch` has no
Goal4648 promotion contract because it is already the main measured V4 partner,
and `numba` must be requested with `fixed=True` because arbitrary callbacks are
not supported.

## Frozen Numeric Bars

These bars are frozen before Goal4649/4650 runs:

| Gate | Required value |
|---|---:|
| Correctness parity | `1.0` / `100%` |
| Representative speedup floor | `>= 1.20x` unless a stricter row-specific floor is frozen before measurement |
| Partner parity floor | `>= 0.98x` |
| Host materialization in hot path | `false` for certified surfaces |

Rows that only prove partner migration or partner parity cannot contribute to
`formal_high_performance_v4_supported`.

Both boundaries are code-visible:

- `partner_migration_counts_as_v4_speed_win = false`
- `partner_parity_counts_as_v4_speed_win = false`

## CuPy Contract

Contract class:
`device_array_frontdoor_certification`

Goal4649 candidate IDs:

- `cupy_grouped_reduction_device_columns_262144`
- `cupy_grouped_reduction_device_columns_524288`
- `cupy_segment_polygon_hitcount_prepared_scaling`
- `cupy_hausdorff_witness_continuation`

Accepted dtypes:

- `float32`
- `float64`
- `int32`
- `int64`
- `uint64`
- `bool`

Layout and ownership:

- contiguous 1D or column-major CuPy device columns;
- caller-owned CuPy CUDA device arrays on the same device as the V4 session;
- outputs are V4-allocated or caller-provided CuPy device outputs;
- no Python rows or host materialization in the hot path.

Required telemetry:

- correctness parity;
- representative speedup;
- partner parity;
- host materialization in hot path;
- denominator;
- scale;
- stream mode;
- output ownership.

Claim boundary:

CuPy performance claims remain blocked until Goal4649 reruns and certifies exact
V4 surfaces under this contract.

## Fixed Numba Contract

Contract class:
`fixed_continuation_certification`

Goal4650 candidate ID:

- `numba_component_union_current_v4_surface`

Accepted signature:

```text
fixed_radius_graph_component_union_3d(device columns) -> component labels
```

Boundaries:

- fixed operators only;
- no arbitrary user callback support;
- no raw OptiX callback support;
- compile/cache timing excluded from hot path but reported as phase telemetry.

Required telemetry:

- correctness parity;
- representative speedup;
- partner parity;
- host materialization in hot path;
- compile time seconds;
- cache hit;
- denominator;
- scale.

## Fail-Closed Planner/Catalog Behavior

The existing V4 planner remains fail-closed for unmeasured partners. The new
Goal4648 tests assert that:

- CuPy requests still return `tier2_declared_unmeasured_partner` until Goal4649;
- no CuPy API surface is exposed before certification;
- arbitrary Numba callbacks are not supported;
- unsupported promotion contracts raise `ValueError`;
- candidate allowlisting fails closed for unsupported partners such as `torch`
  or unknown partner names;
- Barnes-Hut and Tier-3 PTX spike rows are not promotion candidates.

## Tests

Command:

```text
py -m unittest tests.v4_goal4648_partner_promotion_contract_test tests.v4_operator_catalog_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_frontdoor_test
```

Result:

```text
Ran 31 tests in 1.290s
OK
```

The local Python launcher printed a `<prefix>` environment warning, but the
unittest command exited successfully.

## Non-Authorization

Goal4648 does not authorize:

- public V4 release/tag wording;
- broad V4 speedup claims;
- whole-app or all-benchmark V4 speedup claims;
- CuPy performance claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- POD benchmark spending;
- partner migration or partner parity as V4 speed evidence.

## Goal-Level Decision Audit

1. Did I make a foolish decision?

No. The goal stayed on the revised chain: freeze contracts and bars before any
partner certification run.

2. If yes, what actions made it foolish?

Not applicable. The risky action would have been to run CuPy first and invent
bars afterward; this goal prevents that.

3. Was there another possibility that avoided being trapped in one idea?

Yes. The contract could have been documentation-only. Instead, it is also a
code-visible table with regression tests, so later goals cannot rely on memory
or scattered prose.

4. Can I start a different path that actually solves the problem?

Yes. Goal4649 can now select exact CuPy surfaces and run against the frozen
contract. Goal4650 can confirm the fixed Numba continuation boundary without
expanding into arbitrary callbacks.

## Exit Status

Goal4648 has enough local evidence for completion review:

- contract module implemented;
- V4 front-door exports added;
- numeric bars frozen;
- fail-closed behavior covered by tests;
- no claim expansion authorized.

External completion review is still required, or recorded review debt if a
reviewer is unavailable under the user's rule.
