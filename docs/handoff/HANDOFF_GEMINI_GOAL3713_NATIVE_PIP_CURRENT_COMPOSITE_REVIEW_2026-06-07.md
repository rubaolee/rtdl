# Handoff: Gemini Review For Goal3713 Native-PIP Current Composite

Please perform a read-only independent review of:

- `docs/reports/goal3713_rayjoin_native_pip_current_composite_2026-06-07.md`
- `docs/reports/goal3713_rayjoin_native_pip_current_composite_a5000/summary.json`
- `tests/goal3713_rayjoin_native_pip_current_composite_test.py`

Context:

- Goal3711 refreshed the RayJoin app-level mixed route with PIP still on CuPy.
- Goal3713 reruns the stronger native-PIP candidate on current `main` at commit `7cf5e2f37e4576a1d3a51d670fcde05cb79d310d`.
- The artifact is from an NVIDIA RTX A5000 pod, public CDB 4096-chain slice, repeat `20`, warmup `5`.
- Goal3713 moves PIP scalar count to the generic RTDL/OptiX native relation-status corrected scalar-count executor while keeping LSI on repaired prepared-left exact count and overlay on RTDL/OptiX active count.

Review questions:

1. Does Goal3713 correctly summarize the artifact numbers: all-CuPy `1.430714336s`, native-PIP mixed `0.005322640s`, `268.798x`, all counts matching?
2. Does it correctly identify the PIP improvement over Goal3711: PIP moves from CuPy parity to RTDL/OptiX native scalar count, with `2.590x` PIP-leg speedup and `1.099x` composite improvement?
3. Does it preserve the app-agnostic boundary: generic closed-shape membership scalar count, not RayJoin-specific native engine logic?
4. Is the claim boundary honest: internal same-contract evidence only, not public speedup, not release, not RTDL-beats-RayJoin, not RayJoin paper reproduction, not broad RT-core speedup, and not true zero-copy?
5. Are there any correctness, metadata, or route-naming issues that should block treating Goal3713 as the current internal recommended RayJoin mixed route pending broader tests?

Expected verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Write your review to:

- `docs/reviews/goal3714_gemini_review_goal3713_native_pip_current_composite_2026-06-07.md`

Do not edit source files other than the requested review file.
