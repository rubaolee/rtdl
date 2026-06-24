# Handoff: Gemini Review For Goal3711 RayJoin App-Level Rebaseline

Please perform a read-only independent review of:

- `docs/reports/goal3711_rayjoin_app_level_rebaseline_after_segment_pair_exact_count_2026-06-07.md`
- `docs/reports/goal3711_rayjoin_app_level_rebaseline_a5000/summary.json`
- `tests/goal3711_rayjoin_app_level_rebaseline_after_segment_pair_exact_count_test.py`

Context:

- Goal3709 set the next direction: RayJoin app-level rebaseline plus generic dense-boundary scalar-count work.
- Goal3711 uses the current `scripts/goal3612_rayjoin_safe_mixed_route_composite.py` runner at commit `4129ca8f912c3ad197c3c70a27c8bea0b4327456`.
- The artifact is from an NVIDIA RTX A5000 pod, 4096-chain public CDB slice, repeat `20`, warmup `5`.

Review questions:

1. Does Goal3711 correctly summarize the artifact numbers: all-CuPy `1.430871006s`, recommended mixed `0.005847813s`, `244.685x`, all counts matching?
2. Does it correctly describe the three subcontracts: PIP still CuPy parity, LSI repaired RTDL/OptiX prepared-left exact count, and overlay RTDL/OptiX active count?
3. Is the claim boundary honest: same-contract all-CuPy comparison only, not RayJoin paper reproduction, not RTDL-beats-RayJoin, not public speedup, not broad RT-core speedup, not true zero-copy, and not release authorization?
4. Does the report clearly identify the next work: original-RayJoin same-dataset comparison, dense-boundary exact scalar count, seconds-scale expansion, and weak-row visibility?
5. Are there any correctness or metadata issues in the artifact/test that would make this unsuitable as internal performance evidence?

Expected verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Write your review to:

- `docs/reviews/goal3712_gemini_review_goal3711_rayjoin_app_level_rebaseline_2026-06-07.md`

Do not edit source files other than the requested review file.
