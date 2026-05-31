# Goal2872 Triton Tie-Break Conformance Smoke

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Goal2868 review feedback correctly noted that v2.5 determinism policy was
contract-level: it declared tie-break and tolerance behavior, but did not prove
that preview kernels obey those contracts. Goal2872 adds a first CUDA-gated
Triton conformance smoke for the highest-risk continuation behaviors.

This is not the complete per-partner conformance matrix. It is the first
hardware-executable guard for the tie-break and ordered-fixture cases most
likely to drift.

## Coverage

The test compares Triton preview outputs to
`execute_v2_5_partner_continuation_reference(...)` for:

- `grouped_argmin_f64`: lowest score, then lowest item id;
- `grouped_argmax_f64`: highest score, then lowest item id;
- `grouped_topk_f64`: lowest score, item-id tie-break, duplicate item policy,
  rank order, row offsets, and missing groups;
- `segmented_sum_f64` and `grouped_vector_sum_f64x2`: exact ordered-fixture
  float sums.

The test is skipped when Triton CUDA is not available and is intended to run on
the NVIDIA pod.

## Implementation

Updated:

- `src/rtdsl/v2_5_internal_readiness.py`

Added:

- `tests/goal2872_triton_tie_break_conformance_smoke_test.py`

The readiness packet now requires this report so the conformance-smoke result is
not a loose artifact.

## Boundary

This is a conformance smoke, not a v2.5 release authorization, not a public speedup claim,
not a broad RT-core claim, not a whole-app speedup claim, not a
true-zero-copy claim, and not package-install wording.

Before release review, this should grow into the broader partner x operation x
hardware conformance matrix requested by the external reviews.

## Validation

Local validation should skip CUDA-gated methods without a CUDA Triton runtime:

```text
py -3 -m unittest tests.goal2872_triton_tie_break_conformance_smoke_test

Ran 6 tests in 0.047s
OK (skipped=4)
```

Pod validation should run the CUDA methods on NVIDIA hardware.

## Codex Verdict

`accept-with-boundary`
