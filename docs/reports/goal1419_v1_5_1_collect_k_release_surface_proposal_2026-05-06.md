# Goal 1419 v1.5.1 COLLECT_K_BOUNDED Release-Surface Proposal

## Verdict

Propose `COLLECT_K_BOUNDED` for a v1.5.1 documented experimental public-candidate surface after external release-surface review.

This proposal is not public docs authorization, not stable primitive promotion, not speedup wording, not zero-copy wording, not release-tag action, and not a whole-app claim.

## Proposed Surface

- Primitive: `COLLECT_K_BOUNDED`
- Track: `python_rtdl`
- Proposed classification: `documented_experimental_public_candidate`
- Proposed scope: bounded candidate-id row collection over Embree and OptiX for the measured Python+RTDL package
- Required review: `3-AI release-surface review`
- Required reviewers: Codex, Claude, Gemini

## Evidence Basis

- Readiness consensus: `docs/reports/three_ai_goal1418_v1_5_1_collect_k_readiness_gate_consensus_2026-05-06.md`
- Parity consensus: `docs/reports/three_ai_goal1416_v1_5_1_collect_k_native_parity_consensus_2026-05-06.md`
- Benchmark consensus: `docs/reports/three_ai_goal1417_v1_5_1_collect_k_benchmark_consensus_2026-05-06.md`

## Not Proposed

- Stable primitive promotion
- Whole-app speedup wording
- Public speedup wording
- Zero-copy wording
- Release tag action
- New backend expansion

## Allowed Next Actions

- Request external release-surface review.
- Draft user docs only after release-surface review accepts.
- Keep v1.5 public docs unchanged until authorization.

## Validation

```cmd
set PYTHONPATH=src;.
py -3 -m unittest tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test tests.goal1417_v1_5_1_collect_k_benchmark_test tests.goal1416_v1_5_1_collect_k_native_parity_test
```
