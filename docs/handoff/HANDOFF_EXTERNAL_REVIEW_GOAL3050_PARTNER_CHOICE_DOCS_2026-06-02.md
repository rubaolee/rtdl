# External Review Request: Goal3050 Partner Choice Docs

Please independently review Goal3050, which adds current v2.x/v2.6 learner
guidance for choosing a custom continuation partner after RTDL primitives.

## Files To Inspect

- `docs/learn/partner_choice_for_custom_logic.md`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/reports/goal3050_partner_choice_for_custom_logic_docs_and_benchmark_matrix_2026-06-02.md`
- `docs/learn/README.md`
- `README.md`
- `examples/v2_0/research_benchmarks/README.md`
- `tests/goal3050_partner_choice_docs_test.py`

## Review Questions

1. Does the guide clearly answer when a user should choose CuPy vs Numba for
   custom logic, while keeping RTDL primitive-first as the default?
2. Does the benchmark matrix cover the promoted benchmark apps without
   overclaiming performance?
3. Does the wording preserve the rule that users choose partners explicitly and
   that RTDL does not accelerate arbitrary CuPy/Numba programs?
4. Are the v2.6 Numba statements honest: first-class for selected generic
   continuation contracts, but not automatically faster than CuPy?
5. Are any benchmark rows misleading, missing, or inconsistent with current
   evidence?

## Required Output

Write one review file using one of the allowed verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Claude output path:

```text
docs/reviews/goal3051_claude_review_goal3050_partner_choice_docs_2026-06-02.md
```

Gemini output path:

```text
docs/reviews/goal3051_gemini_review_goal3050_partner_choice_docs_2026-06-02.md
```

Please state that the review is independent and distinct from Codex authoring.
Do not authorize a v2.6 release, package install wording, broad RT-core speedup
wording, broad CuPy/Numba acceleration wording, or hidden partner auto-selection.
