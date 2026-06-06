# Handoff: Gemini Review For Goal3609/Goal3610 RayJoin Mixed Composite And LSI Mismatch

Please perform a read-only independent review of the new Goal3609/Goal3610 packet on `main`.

## Files To Read

- `docs/reports/goal3609_rayjoin_recommended_mixed_route_composite_2026-06-06.md`
- `docs/reports/goal3609_rayjoin_recommended_mixed_route_composite_a5000/summary.json`
- `scripts/goal3609_rayjoin_recommended_mixed_route_composite.py`
- `tests/goal3609_rayjoin_recommended_mixed_route_composite_test.py`
- `docs/reports/goal3610_rayjoin_lsi_4096_count_mismatch_probe_2026-06-06.md`
- `docs/reports/goal3610_rayjoin_lsi_4096_count_mismatch_probe_a5000/summary.json`
- `scripts/goal3610_rayjoin_lsi_4096_mismatch_probe.py`
- `tests/goal3610_rayjoin_lsi_4096_count_mismatch_probe_test.py`
- Context reports: `docs/reports/goal3608_v2_9_rayjoin_pip_route_decision_after_boundary_signal_2026-06-06.md`, `docs/reports/goal3606_rayjoin_pip_boundary_signal_4096_negative_2026-06-06.md`

## Questions

1. Does Goal3609 honestly support the internal 512-chain mixed-route composite result: PIP CuPy dense, LSI RTDL/OptiX, overlay RTDL/OptiX, with 21.654x versus all-CuPy dense under the stated unweighted hot-median-sum mix?
2. Does Goal3610 correctly block 4096-chain composite claims because LSI same-contract semantics disagree: CuPy `4977` versus RTDL/OptiX `4985`, concentrated in eight +1 left-id deltas?
3. Are the claim boundaries strong enough: no release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, or native default-route authorization?
4. Is the proposed next engineering direction correct: repair or explicitly split the generic segment-pair intersection contract so CuPy and RTDL/OptiX use identical near-degenerate denominator/endpoint/collinearity/tolerance policy before any 4096 composite is published?

## Output

Write the review to:

`docs/reviews/goal3611_gemini_review_goal3609_3610_rayjoin_mixed_composite_lsi_mismatch_2026-06-06.md`

Use one verdict from: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.

Do not edit source files or reports other than writing the requested review.
