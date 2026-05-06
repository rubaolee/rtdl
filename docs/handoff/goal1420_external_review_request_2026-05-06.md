# Goal1420 External Review Request: v1.5.1 COLLECT_K_BOUNDED Release-Surface Gate

Please review the Goal1420 v1.5.1 `COLLECT_K_BOUNDED` release-surface gate and candidate docs in this repository.

## Files To Inspect

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `src/rtdsl/__init__.py`
- `tests/goal1420_v1_5_1_collect_k_release_surface_gate_test.py`
- `docs/release_reports/v1_5_1/README.md`
- `docs/release_reports/v1_5_1/collect_k_bounded.md`
- `docs/release_reports/v1_5_1/release_surface_gate.md`
- `docs/reports/goal1420_v1_5_1_collect_k_release_surface_gate_2026-05-06.md`
- `docs/reports/three_ai_goal1419_v1_5_1_collect_k_release_surface_proposal_consensus_2026-05-06.md`

## Review Questions

1. Are the candidate docs suitable for a v1.5.1 `COLLECT_K_BOUNDED` documented experimental public-candidate surface?
2. Does the gate correctly require caution wording and reject forbidden overclaims?
3. Does it correctly avoid authorizing public docs changes by this gate, stable promotion, speedup wording, zero-copy wording, whole-app claims, and release-tag action?
4. Are the allowed next actions appropriately limited?
5. Are there blockers before treating this as the release-surface gate package for a later public-doc link patch or explicit release decision?

## Required Output

Write a concise Markdown review with sections:

- Verdict
- Accepted Evidence
- Blockers
- Notes

Use `ACCEPT` only if the gate and candidate docs are suitable for the measured v1.5.1 release-surface scope. Use `BLOCK` if any issue invalidates the gate. Do not authorize public promotion, speedup wording, zero-copy wording, or release action.
