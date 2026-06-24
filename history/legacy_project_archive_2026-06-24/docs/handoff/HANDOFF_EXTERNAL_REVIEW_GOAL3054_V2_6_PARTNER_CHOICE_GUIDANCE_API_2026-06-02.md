# External Review Request: Goal3054 v2.6 Partner Choice Guidance API

Please independently review Goal3054, which turns the v2.6 CuPy-vs-Numba
partner-choice learner guidance into advisory, machine-readable source
metadata.

## Files To Inspect

- `src/rtdsl/v2_6_partner_choice_guidance.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/learn/partner_choice_for_custom_logic.md`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/reports/goal3054_v2_6_machine_readable_partner_choice_guidance_2026-06-02.md`
- `tests/goal3054_v2_6_partner_choice_guidance_test.py`
- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02.md`

## Review Questions

1. Does the helper keep partner choice advisory-only and user-owned, without
   auto-selecting CuPy, Numba, or RTDL primitives?
2. Does it correctly encode the current benchmark recommendations: Numba for
   selected custom continuations, CuPy for rows where CuPy remains the measured
   reference, RTDL primitive-first when fused primitive paths are the right
   answer, and `none` where no custom partner is promoted?
3. Does it cover all ten promoted benchmark apps without making RTDL look like
   a fixed app library?
4. Does it keep release, broad speedup, RT-core, true-zero-copy, and
   app-specific native-engine claims blocked?
5. Are any recommendation rows misleading or unsupported by the current docs
   and Goal3052 pod-refresh artifacts?

## Required Output

Write one review file using one of the allowed verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Claude output path:

```text
docs/reviews/goal3055_claude_review_goal3054_v2_6_partner_choice_guidance_api_2026-06-02.md
```

Gemini output path:

```text
docs/reviews/goal3055_gemini_review_goal3054_v2_6_partner_choice_guidance_api_2026-06-02.md
```

Please state that the review is independent and distinct from Codex authoring.
Do not authorize a v2.6 release, package install wording, broad RT-core speedup
wording, broad CuPy/Numba acceleration wording, true-zero-copy wording, hidden
partner auto-selection, or app-specific native-engine behavior.
