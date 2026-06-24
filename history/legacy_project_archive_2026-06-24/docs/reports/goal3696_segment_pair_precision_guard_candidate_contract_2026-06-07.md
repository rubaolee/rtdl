# Goal3696 Segment-Pair Precision-Guard Candidate Contract

Date: 2026-06-07

## Purpose

Goal3693 localized the same-source RayJoin LSI mismatch to one endpoint-near segment pair. Exact arithmetic includes the pair, but simulated float32 candidate arithmetic rounds the parametric `t` value below zero and can drop the candidate before exact refinement sees it.

Goal3696 turns that lesson into an app-agnostic executable contract:

```text
robust segment-pair candidate emission must not under-emit exact or ambiguous near-boundary pairs merely because a low-precision traversal predicate rounded a parameter outside [0, 1].
```

## Implementation

Updated module:

- `src/rtdsl/segment_pair_contracts.py`

New generic contract helpers:

- `SEGMENT_PAIR_PRECISION_GUARD_VERSION`
- `SEGMENT_PAIR_FLOAT32_PARAM_GUARD_EPSILON`
- `SegmentPairCandidateEmissionDecision`
- `segment_pair_intersection_float32_candidate_v0(...)`
- `segment_pair_precision_guard_candidate_v0(...)`
- `segment_pair_precision_guard_cases()`
- `validate_segment_pair_precision_guard_cases(...)`

New test:

- `tests/goal3696_segment_pair_precision_guard_contract_test.py`

The contract is metadata/reference logic only. It does not change native runtime behavior yet.

## Fixture

The first precision-guard fixture is a generic endpoint-near segment pair:

```text
left:  (-53.129979511, -28.763491093) -> (-53.123623658, -28.755028817)
right: (-53.130100000, -28.756700000) -> (-53.128600000, -28.840900000)
```

The exact predicate reports:

```text
hit = true
t   ~= 0.00007568719169345676
u   ~= 0.08064670444292429
```

The simulated float32 candidate predicate reports:

```text
hit = false
t   ~= -0.00018010620260611176
u   ~= 0.08066143840551376
```

So the precision-guard candidate decision is:

```text
emit_candidate = true
refine_required = true
reason = exact_hit_low_precision_miss_requires_refine
```

## Design Boundary

This is still generic RTDL language/runtime design. It does not add:

- RayJoin-specific native logic,
- CDB-specific geometry rules,
- app-shaped ABI names,
- public release evidence,
- public speedup wording,
- RayJoin paper reproduction claims.

The contract tells the next native implementation what must be true. It does not claim the OptiX runtime has already been repaired.

## Next Native Work

The next implementation should choose one generic strategy:

1. native ambiguous candidate emission near parametric endpoints, then exact host/partner refine,
2. native high-precision or scaled segment-pair candidate predicate,
3. typed status columns that mark `refine_required` / `endpoint_near` / `precision_guarded` rows.

Any implementation must rerun the same-source LSI pair-set probe and require:

- RayJoin pair count `20860`,
- RTDL normalized pair count `20860`,
- missing count `0`,
- extra count `0`,
- no RayJoin/CDB vocabulary in native ABI.

## Boundary

This report does not authorize release, route promotion, public speedup claims, RTDL-beats-RayJoin claims, RayJoin paper reproduction claims, broad RT-core claims, or zero-copy claims.

