# Goal2786 Consensus - Batched Vector-Sum Offsets Tuning

Date: 2026-05-31

## Scope

Goal2786 tested a generic Triton row-offset vector-sum tuning candidate:

- presegmented rows are described by `row_offsets`;
- the kernel can reduce several groups per Triton program through
  `groups_per_program`;
- no global atomic adds are used in the offset path;
- the continuation remains a generic grouped vector-sum contract and does not
  embed Barnes-Hut, N-body, or force-law application logic.

The goal also refreshes v2.5 partner-selection and app-migration guidance so
dense grouped vector sums remain blocked from automatic Triton selection.

## Evidence

Implementation and tests:

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2786_batched_vector_sum_offsets_tuning_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`

Report and pod artifact:

- `docs/reports/goal2786_batched_vector_sum_offsets_tuning_2026-05-31.md`
- `docs/reports/goal2786_pod_artifacts/goal2786_batched_vector_sum_offsets_pod_69_30_85_171_2026-05-31.json`

Independent review:

- `docs/reviews/goal2786_gemini_review_batched_vector_sum_offsets_tuning_2026-05-31.md`

## Review Result

Gemini reviewed the implementation, tests, report, pod artifact, guidance
refreshes, and future-work note. Its verdict was `accept-with-boundary`.

The accepted boundary is:

- the primitive remains generic and app-agnostic;
- the batched offset kernel is atomics-free and correctness-tested against the
  Torch same-contract branch;
- pod timing is interpreted honestly: `groups_per_program=1` remained best, all
  batched values were slower, and Torch remained faster than every Triton offset
  variant;
- Triton auto-selection remains blocked for dense grouped vector sums;
- public speedup, RT-core speedup, true-zero-copy, whole-app, and v2.5 release
  claims remain blocked.

## Validation

Local Windows guidance-inclusive gate:

```text
Ran 22 tests in 0.046s
OK (skipped=4)

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2786_final2
OK
```

Pod guidance-inclusive gate:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000

Ran 22 tests in 2.508s
OK
```

Pod timing summary:

| Rows | Groups | Best offset groups/program | Best / Torch | Best / Atomic |
| ---: | ---: | ---: | ---: | ---: |
| 8,192 | 512 | 1 | 16.852x | 0.978x |
| 262,144 | 4,096 | 1 | 5.694x | 0.945x |
| 1,048,576 | 8,192 | 1 | 3.756x | 0.929x |

## Consensus Verdict

`accept-with-boundary`

Goal2786 is accepted as a measured generic tuning attempt and a negative design
result. The batched row-offset candidate is not promoted, the default remains
the single-group offset path, and dense grouped vector sums remain blocked from
automatic Triton selection until a stronger same-contract implementation wins
timing.
