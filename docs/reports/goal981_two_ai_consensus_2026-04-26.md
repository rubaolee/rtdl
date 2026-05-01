# Goal981 Two-AI Consensus

Status: `ACCEPT`

Goal981 is closed for the local Embree graph correctness repair.

## Codex Verdict

Accept. The native repair widens only BVH candidate bounds for graph edge-point and 2D triangle user geometry while leaving exact graph and visibility callbacks unchanged. This is conservative: traversal may deliver extra candidates, but accepted rows still come from the exact predicates.

The focused verification passed:

```text
RTDL_FORCE_EMBREE_REBUILD=1 PYTHONPATH=src:. python3 -m unittest \
  tests.goal903_embree_graph_ray_traversal_test \
  tests.goal980_graph_baseline_correctness_audit_test \
  tests.goal978_rtx_speedup_claim_candidate_audit_test \
  tests.goal979_deferred_cpu_timing_repair_test \
  tests.goal977_optix_only_artifact_intake_test \
  tests.goal971_post_goal969_baseline_speedup_review_package_test \
  tests.goal846_active_rtx_claim_gate_test \
  tests.goal836_rtx_baseline_readiness_gate_test
```

Result:

```text
Ran 28 tests in 9.021s
OK
```

## Claude Verdict

Claude returned `ACCEPT` in `/Users/rl2025/rtdl_python_only/docs/reports/goal981_claude_review_2026-04-26.md`.

Claude verified:

- the fix is correct and conservative because exact callbacks are unchanged
- Goal903 and Goal980 support moving graph correctness from blocked to repaired
- Goal978 correctly moves `graph_analytics` to `needs_timing_baseline_repair`
- public RTX speedup claims remain unauthorized

Claude noted one non-blocking residual risk: candidate padding can increase false-candidate callback delivery at high graph densities. After same-scale probing, the pad was raised to `2.5e-1f` to cover larger coordinate ranges; this remains a conservative correctness fix because exact callbacks are unchanged, but it should be watched during future graph-density performance tests.

## Final State

- Embree graph correctness audit: `ok`
- Goal980 mismatch count: `0`
- Goal978 graph recommendation after Goal981: `needs_timing_baseline_repair`
- Goal978 graph recommendation after Goal982: `reject_current_public_speedup_claim`
- public RTX speedup claims authorized: `0`

Goal982 completed the next graph timing-baseline repair and showed that the current OptiX graph phase is slower than the same-scale Embree baseline. Public speedup claims remain unauthorized.
