# Goal2662: v2.5 Partner Continuation Contract 3-AI Consensus

Status: accepted first v2.5 slice.

Date: 2026-05-27

## Reviewed Files

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/__init__.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `docs/reports/goal2662_v2_5_partner_continuation_contract_2026-05-27.md`
- `docs/partner_acceleration_boundaries.md`
- `docs/reports/goal2661_v2_4_completion_3ai_consensus_2026-05-27.md`

## Reviews

- Codex implementation and local validation: accepted.
- Claude review:
  `docs/reports/goal2662_v2_5_partner_continuation_claude_review_2026-05-27.md`
- Gemini review:
  `docs/reports/goal2662_v2_5_partner_continuation_gemini_review_2026-05-27.md`

Claude verdict: accept, no blockers.

Gemini verdict: accept, no blockers.

## Consensus Position

Codex, Claude, and Gemini agree:

```text
Goal2662 is a valid first v2.5 slice.
It defines generic partner-continuation behavior for Triton-first / Numba-
fallback work without authorizing performance claims or replacing RTDL/OptiX
traversal.
```

## Accepted Boundaries

- Triton is the primary v2.5 partner direction.
- Numba is fallback or per-pattern alternative.
- CuPy remains conformance/compatibility, not the long-term ease-of-use center.
- Partners may own preparation, continuation, reduction, compaction, and
  finalization.
- RTDL/OptiX still owns RT-core traversal for RT-core claims.
- No app-specific native vocabulary or app-specific continuation semantics are
  accepted.
- No CuPy RawKernel-style user path is required by the v2.5 contract.
- No public release, public speedup, whole-app speedup, or promoted benchmark
  path is authorized by Goal2662.

## Accepted Operation Set

- `segmented_count_i64`
- `segmented_sum_f64`
- `compact_mask_i64`
- `bounded_collect_finalize_i64`
- `grouped_argmin_f64`

These operations are generic continuation behaviors. They do not encode RayDB,
DBSCAN, Barnes-Hut, graph, contact, collision, robot, RTNN, LibRTS, or
Hausdorff semantics.

## Validation

Focused validation:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2661_v2_4_completion_gate_test \
  tests.goal2658_v2_4_partner_protocol_test
```

Result:

```text
Ran 23 tests
OK
```

Compile and whitespace validation:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/partner_continuation_protocol.py \
  src/rtdsl/__init__.py \
  tests/goal2662_v2_5_partner_continuation_contract_test.py
git diff --check
```

Result: OK.

## Decision

Goal2662 is accepted.

The next v2.5 engineering target is to implement a real Triton continuation
kernel for one generic operation, likely `segmented_sum_f64` or
`compact_mask_i64`, then validate it against the reference semantics before any
benchmark-app pilot or performance comparison.
