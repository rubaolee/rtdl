# External Review: LibRTS Goals5519-5525 Final Closeout

Date: 2026-07-13

## Overall Verdict

```text
approve
```

Blocking findings: none.

Required amendments: none.

## Per-Goal Verdicts

```text
Goal5519: approve
Goal5520: approve
Goal5521: approve
Goal5522: approve
Goal5523: approve
Goal5524: approve
Goal5525: approve
```

## Verified Findings

### Goal5519 is a generic semantic correction

The operation-scoped packed-AABB validity rule is a genuine geometric contract,
not author fitting. The synthetic discriminating probe establishes:

```text
point_contains  = 1
range_contains  = 1
range_intersects = 0
```

A packed zero-width box can still contain a point or box on its inclusive
boundary even though it is invalid for the strict segment-based
`range_intersects` contract. Goal5519 therefore correctly narrows Goal5508's
blanket strict-validity guard to `range_intersects`. The implementation and
tests remain app-neutral and introduce no LibRTS or paper identity into RTDL
core.

### Exact contains matrices are complete at count scope

- `point_contains`: 14/14 exact same-input count matches.
- `range_contains`: 14/14 exact same-input count matches.
- Distinct query members, per-member SHA-256 identity, and coverage accounting
  prevent answer replay or accidental double counting.

Count equality remains separate from pointwise relation equality. The separate
representative PIP gate records 71,626 canonical relation rows equal; that
relation result is not transferred to the count-only archive matrices.

### Range-intersects closes with an honest ledger

The authoritative state is:

```text
14 exact count matches
2 pinned-author CUDA capacity failures
26 not checkpointed
```

No complete matrix is claimed. Goal5524 correctly applies the project stop-loss
rules: additional matrix enumeration is frozen because it would produce no new
generic capability and answer no unresolved semantic question.

### System and app ownership remain separated

RTDL gained reusable, app-neutral AABB column, prepared-query, mutable-index,
sparse-refit, rollback/fail-closed, operation-scoped validity, and batch-reuse
capabilities. WKT/archive ingestion, caches, author wrappers, comparators, and
paper matrix selection remain app-owned.

### Verification and cleanup are sufficient

- 176 LibRTS-focused local tests passed.
- The focused final subset passed.
- POD transient data was removed while preserving the official archive,
  author executable, and corrected RTDL OptiX build.
- Local Python cache directories were removed after validation.

## Claim Boundary

The review approves only:

```text
LibRTS scoped correctness and system extraction complete
```

It does not approve full-paper reproduction, Figure 6 reproduction,
performance parity, author algorithm equivalence, complete range-intersects
coverage, pointwise equality for count-only cases, zero-copy, or Embree support.

## Non-Blocking Notes

1. Goal5519 demonstrates why discriminating semantic probes are required when
   a generic correction changes multiple predicates. Goal5508's broad rule was
   reasonable evidence at the time but incomplete across operations.
2. The pre-existing native identifier `author_block_merge64` should be included
   in a future native naming/export audit. It is unrelated to Goals5519-5525
   and does not block this closeout.
3. The external reviewer directly inspected the seven gate JSON artifacts,
   closeout packet, and Goal5519 native code. The reviewer did not rerun the
   176/24-test suites because of sandbox instability; the recorded successful
   test evidence remains part of the approved packet.

## Final Disposition

Goals5519-5525 are externally reviewed and approved. The LibRTS workstream is
closed at scoped correctness and system extraction. Reopening requires a new
semantic discrepancy, a denominator-aligned paper figure explicitly approved
as new scope, or a reusable generic capability with a non-LibRTS consumer.
