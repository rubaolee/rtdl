# Goal3812 Current Benchmark Docs And Adequacy Aliases

Date: 2026-06-07

## Purpose

The active learner and benchmark front-door docs still described the current
surface as v2.8 even though the benchmark adequacy source of truth had advanced
to the v2.10 post-HIPRT-closeout position in Goal3786. Goal3812 refreshes that
reader-facing surface and adds current, non-versioned benchmark adequacy helper
aliases.

## Changes

| Area | Operation |
| --- | --- |
| `src/rtdsl/v2_9_benchmark_adequacy.py` | Added `current_benchmark_adequacy_rows`, `current_benchmark_adequacy`, `summarize_current_benchmark_adequacy`, and `validate_current_benchmark_adequacy` as current aliases over the v2.10 adequacy source. |
| `src/rtdsl/__init__.py` | Exported the current benchmark adequacy helpers and version/status constants. |
| `README.md` | Updated the current source-tree surface from v2.8 to v2.10 and linked Goal3786 as the current adequacy/AMD-HIPRT readiness position while preserving the historical Goal3518 link. |
| `docs/README.md` | Updated the learner-door status and directory map to v2.10 and split historical v2.8 matrix from current v2.10 adequacy. |
| `docs/tutorials/README.md` | Updated tutorial framing to v2.10 and removed stale "v2.8 App Building" display text. |
| `docs/learn/partner_choice_for_custom_logic.md` | Updated status to v2.10, pointed programmatic guidance at `current_benchmark_adequacy`, and aligned Numba/CuPy lessons with current adequacy evidence. |
| `docs/learn/benchmark_partner_reference_matrix.md` | Updated status to v2.10, replaced old `v2_8_benchmark_matrix` guidance with current adequacy helpers, and corrected rows where Numba coverage had advanced. |
| `docs/learn/primitive_discovery_workflow.md` and `docs/learn/prepared_execution_pattern.md` | Updated current status/examples from v2.8 to v2.10. |
| `examples/v2_0/research_benchmarks/README.md` | Updated benchmark front-door framing to v2.10 and clarified current CuPy/Numba roles. |

## Boundary

- This is a learner-doc and metadata alias refresh, not a release gate.
- Historical `v2_8_*` and `v2_9_*` helpers remain available.
- Historical Goal3518 links remain because they point to historical evidence.
- No native engine code changed.
- No public speedup, whole-app speedup, broad RT-core speedup, package-install,
  true-zero-copy, paper-reproduction, AMD performance, automatic partner
  selection, or release claim is authorized.

## Validation

Focused local validation should cover:

```text
tests.goal3812_current_benchmark_docs_and_adequacy_aliases_test
tests.goal3519_v2_8_learner_docs_cleanup_test
tests.goal3050_partner_choice_docs_test
tests.goal3786_current_benchmark_adequacy_after_hiprt_closeout_test
```
