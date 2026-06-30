# Handoff - Gemini Review for Goal3036/3037 Numba Argmax Composition

Date: 2026-06-02

Please independently review the Goal3036/Goal3037 chain on current `main`.

## Context

RTDL v2.6 is developing first-class, user-selectable partner support while
keeping the native engine app-agnostic. The current chain is about a generic
device-resident continuation path:

1. Goal3033/3034: OptiX writes prepared point-group nearest-witness rows into
   caller-owned CuPy device columns.
2. Goal3035: Numba consumes generic `item_ids:uint32` and `scores:float64`
   columns and computes global argmax.
3. Goal3036: hardened Goal3035 by replacing fragile global CUDA atomics with
   `multi_stage_block_reduce_no_global_atomics`.
4. Goal3037: clean RTX A4000 pod proof that the OptiX device-column producer
   composes with the Numba global-argmax consumer through neutral handoff.

## Files to Inspect

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/reports/goal3036_numba_global_argmax_block_reduce_hardening_2026-06-02.md`
- `docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.md`
- `docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.json`
- `tests/goal3035_numba_global_argmax_u32_f64_test.py`
- `tests/goal3036_numba_global_argmax_block_reduce_hardening_test.py`
- `tests/goal3037_point_group_nearest_numba_argmax_a4000_pod_test.py`

## Evidence Already Collected

The latest pushed commit is:

`c56c8909bf471e55f135f4396050052711c055bf`

On pod `root@157.157.221.29 -p 19771`:

- GPU: NVIDIA RTX A4000, driver 580.159.03
- CUDA: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`
- Numba dependency boundary:
  - `numba==0.61.2`
  - `numpy==2.2.6`
  - `cupy-cuda12x==14.1.1`
  - `cuda-python>=12,<13`
  - `NUMBA_CUDA_USE_NVIDIA_BINDING=1`
  - minor-version compatibility disabled

The focused clean-source pod slice passed:

```text
Ran 13 tests in 1.054s

OK
```

Goal3037 artifact records:

- `source_commit=5aebe6e5a80aa8b6783e98bf66a84ec8a58cd468`
- `source_dirty=[]`
- `query_count=4096`
- `search_count=6144`
- `group_count=49`
- device columns match raw row-view oracle exactly
- Numba argmax matches the raw row-view oracle exactly

The latest `main` commit `c56c8909...` only adds the Goal3037 report, artifact,
test, and roadmap/future-list indexing on top of that clean-source pod evidence.

## Review Questions

Please answer these directly:

1. Does Goal3036 correctly replace fragile global atomic argmax logic with a
   generic block-reduction implementation while preserving the contract
   `highest_score_then_lowest_item_id_then_lowest_row_index`?
2. Does Goal3037 honestly prove a clean generic composition path from OptiX
   device columns to Numba global argmax, without host row materialization on
   the new path?
3. Are all claim boundaries preserved?
   - no v2.6 release authorization
   - no public speedup authorization
   - no broad RT-core speedup authorization
   - no true-zero-copy authorization
   - no automatic partner selection
   - no app-specific native-engine behavior
4. Is the dependency finding correct and useful for future pod setup, especially
   the `cuda-python>=12,<13` and `NUMBA_CUDA_USE_NVIDIA_BINDING=1` requirement?
5. What should be the next v2.6 step: benchmark-app wiring for this composition,
   same-contract performance comparison against the current CuPy grouped-grid
   reference, or a larger generic active-set/candidate-frontier primitive?

## Required Output

Write the review to:

`docs/reviews/goal3038_gemini_review_goal3036_3037_numba_argmax_composition_2026-06-02.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Please keep the review independent and explicitly state that it is a
Gemini review distinct from Codex authoring.
