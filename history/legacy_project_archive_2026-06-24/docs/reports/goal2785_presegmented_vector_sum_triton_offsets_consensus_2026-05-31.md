# Goal2785 Consensus - Presegmented Vector-Sum Triton Offsets

Date: 2026-05-31

## Scope

Goal2785 adds a generic prepared-row vector-sum path for Triton:

- caller supplies rows already grouped by key;
- caller supplies `row_offsets`;
- Triton reduces one group per program;
- the offset path avoids global atomic adds;
- the primitive remains generic and does not embed Barnes-Hut or other
  application force-law logic.

This is a bounded v2.5 preview contract, not a release gate and not a public
performance claim.

## Evidence

Implementation and tests:

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `tests/goal2785_presegmented_vector_sum_triton_offsets_test.py`

Report and pod artifact:

- `docs/reports/goal2785_presegmented_vector_sum_triton_offsets_2026-05-31.md`
- `docs/reports/goal2785_pod_artifacts/goal2785_presegmented_vector_sum_offsets_pod_69_30_85_171_2026-05-31.json`

Independent review:

- `docs/reviews/goal2785_gemini_review_presegmented_vector_sum_offsets_2026-05-31.md`

## Review Result

Gemini reviewed the implementation, adapter path, test, report, pod artifact,
and future-debt note. Its verdict was `accept-with-boundary`.

The accepted boundary is:

- the row-offset path is generic and app-agnostic;
- the offset kernel avoids global atomic adds when `row_offsets` are used;
- correctness matches the Torch branch on CUDA validation;
- performance is honestly bounded: the offsets path is only a small improvement
  over the old Triton atomic preview and remains slower than Torch on measured
  dense shapes;
- RT-core, true-zero-copy, whole-app, public speedup, and release claims remain
  blocked.

## Validation

Local Windows validation:

```text
Ran 7 tests in 0.030s
OK (skipped=2)

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2785_consensus2
OK
```

Pod validation:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
Driver: 570.211.01

Ran 7 tests in 2.270s
OK
```

Pod timing summary:

| Rows | Groups | Rows/group | Offsets / Torch | Offsets / Atomic |
| ---: | ---: | ---: | ---: | ---: |
| 8,192 | 512 | 16 | 14.627x | 0.907x |
| 262,144 | 4,096 | 64 | 6.498x | 0.917x |
| 1,048,576 | 8,192 | 128 | 4.268x | 0.993x |

## Consensus Verdict

`accept-with-boundary`

Goal2785 is accepted as a generic atomics-free row-offset preview and as a useful
prepared-row contract for v2.5 design exploration. It is not promoted as the
selected vector-sum performance path because Torch remains faster on the
measured shapes, and it does not authorize any public release or speedup claim.
