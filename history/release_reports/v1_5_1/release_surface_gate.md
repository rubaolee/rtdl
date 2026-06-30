# v1.5.1 Release-Surface Gate

The v1.5.1 release-surface candidate docs passed external release-surface gate review and Goal1421 public-doc-link review.

Gate status:

- Candidate docs: publicly discoverable
- Proposed classification: documented experimental public-candidate
- Primitive: `COLLECT_K_BOUNDED`
- Track: Python+RTDL
- Backend scope: Embree and OptiX

This gate does not authorize public docs changes beyond the accepted Goal1421 discoverability link, stable promotion, speedup wording, zero-copy wording, whole-app claims, or release tag action.

Required evidence:

- `docs/reports/three_ai_goal1416_v1_5_1_collect_k_native_parity_consensus_2026-05-06.md`
- `docs/reports/three_ai_goal1417_v1_5_1_collect_k_benchmark_consensus_2026-05-06.md`
- `docs/reports/three_ai_goal1418_v1_5_1_collect_k_readiness_gate_consensus_2026-05-06.md`
- `docs/reports/three_ai_goal1419_v1_5_1_collect_k_release_surface_proposal_consensus_2026-05-06.md`
- `docs/reports/three_ai_goal1420_v1_5_1_collect_k_release_surface_gate_consensus_2026-05-06.md`
- `docs/reports/three_ai_goal1421_v1_5_1_collect_k_public_doc_link_consensus_2026-05-06.md`

Required caution wording:

- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release tag action

Example validation command:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1420_v1_5_1_collect_k_release_surface_gate_test
```
