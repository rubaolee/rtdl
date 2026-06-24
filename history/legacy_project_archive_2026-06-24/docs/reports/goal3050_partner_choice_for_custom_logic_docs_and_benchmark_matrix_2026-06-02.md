# Goal3050 Partner Choice For Custom Logic Docs And Benchmark Matrix

Date: 2026-06-02

## Purpose

Users now need a clear answer to a practical v2.x/v2.6 question:

```text
If RTDL primitives are the first choice, but my app still needs custom logic,
should I choose CuPy or Numba?
```

Goal3050 adds learner-facing guidance for that choice and a benchmark-app
matrix that keeps the recommendation evidence-shaped rather than automatic.

## Files Added

| File | Purpose |
| --- | --- |
| `docs/learn/partner_choice_for_custom_logic.md` | Plain-language rule for choosing RTDL primitives, CuPy, Numba, NumPy, or app-owned native extensions. |
| `docs/learn/benchmark_partner_reference_matrix.md` | Benchmark-by-benchmark matrix for the ten promoted research apps. |
| `tests/goal3050_partner_choice_docs_test.py` | Guard test that the learner docs exist, link from the learner door, cover the ten benchmark apps, and preserve claim boundaries. |
| `docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL3050_PARTNER_CHOICE_DOCS_2026-06-02.md` | External review packet for Claude and Gemini consensus. |

## Existing Files Updated

| File | Operation |
| --- | --- |
| `README.md` | Added the partner-choice guide to the current Read Next path without expanding historical clutter. |
| `docs/learn/README.md` | Added the partner-choice guide and benchmark matrix to the learner path. |
| `examples/v2_0/research_benchmarks/README.md` | Added a short pointer from benchmark apps to the partner-choice matrix. |

## Design Boundary

- RTDL primitive-first remains the default when a fused generic primitive
  expresses the work.
- Users choose partners explicitly.
- Benchmark reference implementations may recommend a partner only when
  same-contract evidence supports that recommendation.
- CuPy and Numba continuations are user/app continuation code unless RTDL ships
  and reviews the exact generic continuation contract.
- This goal changes docs and tests only; no native engine code changed.

## Current Recommendation Summary

| Partner path | Recommended use |
| --- | --- |
| RTDL primitive | First choice for fused generic summaries, flags, witnesses, or typed columns. |
| CuPy | CUDA array algebra, RawKernel baselines, existing CUDA-core continuations, and benchmark rows where CuPy remains the measured reference. |
| Numba | v2.6 custom-kernel lane for compact-mask, grouped argmin/argmax, global argmax, and similar generic continuations written in Python syntax. |
| NumPy / CPU reference | Correctness oracle, debugging, small deterministic tests. |
| App-owned C/C++/CUDA extension | Allowed from Python, but outside RTDL partner speedup claims unless separately reviewed. |

## Validation

Local focused validation:

```bash
PYTHONPATH=src:. python -m unittest tests.goal3050_partner_choice_docs_test
```

Result: 3 tests pass.

Local v2.6 partner smoke:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal2990_v2_6_neutral_partner_handoff_test \
  tests.goal2997_numba_compact_mask_prepared_test \
  tests.goal3006_numba_grouped_argmin_argmax_preview_test \
  tests.goal3035_numba_global_argmax_u32_f64_test \
  tests.goal3048_hausdorff_active_frontier_parameter_sweep_test
```

Result: 26 tests pass, 3 skipped.

Pod validation should also include a small selected Numba/CuPy/OptiX evidence
slice while the NVIDIA pod is available, but Goal3050 itself is documentation
and claim-boundary work.

## Release Boundary

This report does not authorize a v2.6 release, package install wording, broad
RT-core speedup wording, broad CuPy/Numba acceleration wording, or any hidden
partner auto-selection. It is a learner-doc cleanup and benchmark-reference
organization step.
