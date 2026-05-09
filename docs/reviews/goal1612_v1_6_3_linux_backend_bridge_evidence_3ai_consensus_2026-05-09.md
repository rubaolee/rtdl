# Goal1612 v1.6.3 Linux Backend Bridge Evidence 3-AI Consensus

Date: 2026-05-09

## Verdict

ACCEPTED as Linux backend bridge evidence for the prepared host-output
measurement path.

This consensus does not authorize performance claims, public speedup wording,
whole-app speedup claims, broad RTX/GPU wording, true zero-copy wording, stable
`COLLECT_K_BOUNDED` promotion, partner tensor handoff claims, package-install
claims, release tags, or release action.

## Reviewed Files

- `docs/reports/goal1612_v1_6_3_linux_backend_bridge_evidence_2026-05-09.md`
- `docs/reports/goal1612_v1_6_3_linux_backend_prepared_host_output_bridge_2026-05-09.json`
- `docs/reports/goal1612_v1_6_3_linux_backend_prepared_host_output_bridge_2026-05-09.md`
- `tests/goal1612_v1_6_3_backend_prepared_host_output_bridge_test.py`

## Evidence

- Linux host: `192.168.1.20` / `lx1`.
- Checkout: `/home/lestat/work/rtdl_codex_local_check`.
- Git commit: `527d38e1a5fb0fb6d63015c0bbabdd7a7b15bf8c`.
- Command required all three backends: `fake_native`, `embree`, and `optix`.
- Artifact status: `accepted_backend_bridge`.
- Backend outcomes: `fake_native=pass`, `embree=pass`, `optix=pass`.
- Required backend skips: none.
- Failures: none.
- Windows-side validation after importing artifacts passed:
  `Ran 36 tests` and `OK`.
- Claude review:
  `docs/reviews/goal1612_v1_6_3_linux_backend_bridge_evidence_claude_review_2026-05-09.md`
  reports `ACCEPTED` with no required fixes.
- Gemini review:
  `docs/reviews/goal1612_v1_6_3_linux_backend_bridge_evidence_gemini_review_2026-05-09.md`
  reports `ACCEPTED` with no required fixes.

## Consensus

All three reviewers agree that the Linux addendum is acceptable as backend
bridge evidence only:

- all required backends passed;
- no skipped required backend was present;
- no failed backend record was present;
- materialization counters match the expected `iterations=5` shape;
- prepared input materialization count is `1`;
- input materialization delta is `4`;
- prepared host-output buffer reuse is recorded as `true`;
- all claim flags remain closed;
- the GTX 1070 host is documented as smoke/behavior evidence only, not RTX
  performance evidence.

## Next Step

Use this Linux evidence as local all-backend bridge coverage. For public
performance or NVIDIA RT-core claims, run a separate measured package on
representative RTX hardware with explicit required backends and fresh external
review.
