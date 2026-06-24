# Goal1625 v1.6.5 OptiX Collect-K Threshold-4 A4500 Probe 3-AI Consensus

Date: 2026-05-09

## Verdict

ACCEPTED as internal same-host RTX A4500 OptiX collect-k threshold-4
diagnostic evidence only.

This consensus does not authorize public speedup wording, true zero-copy
wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording,
whole-app speedup claims, release tags, or release action.

## Review Inputs

- Codex implementation and validation:
  - `scripts/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe.py`
  - `docs/reports/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_2026-05-09.json`
  - `docs/reports/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_2026-05-09.md`
  - `tests/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_test.py`
- Claude review:
  - `docs/reviews/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_claude_review_2026-05-09.md`
- Gemini review:
  - `docs/reviews/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe_gemini_review_2026-05-09.md`

## Consensus Findings

Codex, Claude, and Gemini agree that the Goal1625 evidence supports the narrow
internal interpretation:

- The run was on `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Parity passed for all measured rows.
- Copy-reduction regions were consistently favorable:
  - `65537`: payload copies `5 -> 0`, median delta `-0.023551 ms`, faster `5/5`.
  - `65538`: payload copies `5 -> 0`, median delta `-0.022162 ms`, faster `4/5`.
  - `65552`: payload copies `5 -> 0`, median delta `-0.022011 ms`, faster `4/5`.
  - `69632`: payload copies `4 -> 0`, median delta `-0.017811 ms`, faster `5/5`.
- No-copy-reduction controls remain non-claim-worthy:
  - `65536`: payload copies `0 -> 0`, median delta positive, faster `1/5`.
  - `69633`: payload copies `4 -> 4`, median delta near zero and treated as noise-scale.

## Claim Boundary

All reviewers agree that Goal1625 is internal diagnostic evidence only. It does
not authorize:

- public speedup wording
- true zero-copy wording
- stable `COLLECT_K_BOUNDED` promotion
- broad RTX/GPU wording
- whole-app speedup claims
- release tags
- release action

Future public performance wording or default behavior changes require a
separate proposal, measured exact-scope evidence, and fresh external review.
