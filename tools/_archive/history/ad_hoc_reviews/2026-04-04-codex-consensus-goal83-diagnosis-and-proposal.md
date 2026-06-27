# Codex Consensus: Goal 83 Diagnosis and Proposal

Package under review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_diagnosis_and_proposal_2026-04-04.md`

Review outcomes:

- Codex: `APPROVE`
- Gemini 2.5 Pro: `APPROVE`
- Claude: attempted twice, no usable saved verdict returned

## Consensus

2-AI consensus is reached on the diagnosis/proposal package.

Accepted points:

1. The first long exact-source Embree result is a real correctness failure, not
   just a performance loss.
2. The native Embree positive-hit path is structurally flawed because it mixes
   traversal with final truth inside the callback path.
3. The correct first repair is:
   - candidate generation in Embree
   - host exact finalize after candidate collection
   - GEOS-backed finalize when available
4. Goal 83 should not be published as a performance result until exact-source
   Linux parity is restored and then remeasured.
