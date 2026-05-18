# Handoff: Gemini Review For Goal2327 RayJoin Perf Tuning Round 1

Date: 2026-05-18

Please perform an independent read-only review of Goal2327. This is a v2.0
RayJoin benchmark-app performance preparation step, not a release authorization.

## Files To Inspect

- `docs/reports/goal2327_rayjoin_perf_tuning_round1_2026-05-18.md`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `scripts/goal2327_rayjoin_pod_perf_runner.sh`
- `scripts/goal2327_rayjoin_pod_artifact_summary.py`
- `tests/goal2327_rayjoin_prepared_route_contract_test.py`
- `tests/goal2327_rayjoin_perf_tuning_packet_test.py`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does the new prepared OptiX route advance the six requested RayJoin work
   tracks: generic device-resident row stream / continuation, generic
   grouped count/parity reduction, stronger prepared closed-shape membership,
   many-query batching, phase-separated timing, and paper-protocol discipline?
2. Does the change preserve the RTDL rule that native engines remain
   app-agnostic, with RayJoin interpretation staying in Python/app code?
3. Are the claim boundaries still appropriately locked against public
   RayJoin-vs-RTDL speedup claims, broad RT-core claims, true-zero-copy claims,
   and v2.0 release authorization?
4. Is the pod runner safe and useful for a long RTX timing round, including
   visible progress, timeout control, OptiX library precondition, optional
   same-query stream replay, and clear artifact output paths?
5. Are there risks in the route split, PIP/LSI-only support, or overlay
   exclusion that should be documented before the pod run?

## Required Output

Write the review to:

`docs/reviews/goal2328_gemini_review_goal2327_rayjoin_perf_tuning_round1_2026-05-18.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please state explicitly that this is an independent Gemini review, distinct from
Codex. Do not mutate source files other than the requested review document.
