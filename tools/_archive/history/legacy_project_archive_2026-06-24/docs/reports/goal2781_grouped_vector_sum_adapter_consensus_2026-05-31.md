# Goal2781 Consensus - Grouped Vector-Sum Adapter Wiring

Date: 2026-05-31

## Verdict

`accept-with-boundary`

Goal2781 is accepted as a narrow v2.5 adapter-integration step. It wires a
generic grouped 2D vector-sum partner-column adapter through the existing
`grouped_vector_sum_f64x2` continuation contract, proves correctness against the
Torch same-contract path, and records negative Triton performance evidence
honestly.

## Evidence

Codex implementation and validation:

- added `partner_group_vector_sum_2d_by_key`
- added `grouped_vector_sum_2d_partner_columns`
- exported both through the top-level RTDSL facade and the generic reductions
  adapter namespace
- preserved generic names and app-agnostic metadata
- kept the native engine out of the adapter path with
  `native_engine_row_contract="not_called_partner_continuation_only"`
- kept all release, RT-core, public speedup, true-zero-copy, and whole-app
  claim flags blocked

Local Windows validation:

```text
tests.goal2781_grouped_vector_sum_adapter_test
Ran 3 tests in 0.018s
OK (skipped=1)

v2.5 preview slice through Goal2781
Ran 117 tests in 0.083s
OK (skipped=10)
```

Pod validation:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
Driver: 570.211.01

tests.goal2781_grouped_vector_sum_adapter_test
Ran 3 tests in 2.973s
OK

v2.5 preview slice through Goal2781
Ran 117 tests in 2.546s
OK
```

Pod timing artifact:

`docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`

The artifact reports correctness pass at all three scales and shows current
Triton preview performance is slower than Torch scatter-add:

- 8,192 rows / 512 groups: Triton 16.586x slower
- 262,144 rows / 4,096 groups: Triton 6.723x slower
- 1,048,576 rows / 8,192 groups: Triton 4.093x slower

## External Reviews

Gemini:

- `docs/reviews/goal2781_gemini_review_grouped_vector_sum_adapter_2026-05-31.md`
- verdict: `accept-with-boundary`
- confirms generic/app-agnostic adapter wording, `grouped_vector_sum_f64x2`
  routing, blocked claims, and honest negative pod performance evidence
- note: Gemini CLI emitted an invalid-stream warning after writing the completed
  review file; the saved file contains a finished review and explicit verdict

Claude:

- `docs/reviews/goal2781_claude_review_grouped_vector_sum_adapter_2026-05-31.md`
- verdict: `accept-with-boundary`
- confirms the same six review questions and flags only nonblocking coverage
  gaps: empty-input fast paths, CuPy execution, direct helper validation, and
  negative `group_count` validation

## Boundary

This consensus does not authorize:

- public speedup claims
- RT-core speedup claims
- true zero-copy wording
- whole-app speedup claims
- v2.5 release readiness
- promotion of the current Triton grouped-vector-sum kernel as a performance
  path

The adapter surface is useful and correct, but the measured performance says
Torch remains the better selected partner for dense grouped vector sums until a
stronger segmented/block Triton design exists.
