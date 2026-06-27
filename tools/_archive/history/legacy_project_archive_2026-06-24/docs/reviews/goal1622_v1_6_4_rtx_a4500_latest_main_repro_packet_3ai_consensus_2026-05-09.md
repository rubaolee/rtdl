# Goal1622 v1.6.4 RTX A4500 Latest-Main Repro Packet 3-AI Consensus

Date: 2026-05-09

## Verdict

ACCEPTED as latest-main reproducibility evidence for the v1.6.4
`COLLECT_K_BOUNDED` required-backend packet.

This consensus does not authorize public speedup wording, true zero-copy
wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, release
tags, or release action.

## Review Inputs

- Codex implementation and validation:
  - `docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09_report.md`
  - `docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09.json`
  - `docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09.md`
  - `tests/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_test.py`
- Claude review:
  - `docs/reviews/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_claude_review_2026-05-09.md`
- Gemini review:
  - `docs/reviews/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_gemini_review_2026-05-09.md`

## Consensus Findings

Codex, Claude, and Gemini agree that the package demonstrates successful
latest-main replay of the required-backend packet on the RTX A4500 pod at
commit `6fde3868de2525414d9902afcbc9d24b64831113`.

The accepted evidence is limited to packet reproducibility:

- Packet status: `accepted_packet_execution`
- Packet accepted: `true`
- Required backends: `fake_native`, `embree`, `optix`
- Failed subpackages: none
- Goal1614 bounds stress subpackage: accepted
- Goal1615 reduced-copy/materialization-count benchmark subpackage: accepted

## Claim Boundary

All reviewers agree this consensus is not a stable-promotion consensus. The
following remain unauthorized:

- public speedup wording
- true zero-copy wording
- whole-app speedup claims
- broad RTX/GPU wording
- stable `COLLECT_K_BOUNDED` promotion
- release tags
- release action

Stable promotion still requires a separate stable-promotion decision package
and explicit 3-AI consensus for that decision.
