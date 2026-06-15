# Goal4414 3-AI Consensus: V3.0 Midterm Review

Date: 2026-06-15

Status: accepted with boundary. V3.0 may continue to M18 device-side grouped contract work.

Current commit reviewed: `7ab19f4a`

## Consensus State

`v3_0_midterm_accepted_m18_device_side_grouped_contract_allowed`

## Decision

The V3.0 midterm evidence through M17 is accepted as internally consistent and sufficiently bounded to continue implementation.

This consensus authorizes:

- continuing to M18 device-side grouped contract design and implementation;
- preparing no-hidden-copy and same-stream evidence for grouped device-side paths;
- adding tests, reports, runners, and internal evidence artifacts for M18.

This consensus does not authorize:

- public V3 performance claims;
- whole-app benchmark speedup claims;
- author-code parity claims;
- automatic backend or partner selection;
- end-to-end zero-copy claims;
- grouped argmin support for device-column prepared ray batches before M18 evidence exists.

## Reviewed Artifacts

- Midterm packet: `docs/reports/goal4414_v3_0_midterm_review_packet_2026-06-15.md`
- Claude handoff: `docs/handoff/HANDOFF_CLAUDE_GOAL4414_V3_0_MIDTERM_REVIEW_2026-06-15.md`
- Gemini handoff: `docs/handoff/HANDOFF_GEMINI_GOAL4414_V3_0_MIDTERM_REVIEW_2026-06-15.md`
- Claude review: `docs/reviews/goal4414_claude_review_v3_0_midterm_2026-06-15.md`
- Gemini review: `docs/reviews/goal4414_gemini_review_v3_0_midterm_2026-06-15.md`
- M17 report: `docs/reports/goal4413_v3_0_m17_partner_device_ray_prepare_no_hidden_copy_evidence_2026-06-15.md`
- M17 evidence JSON: `docs/reports/goal4413_v3_0_m17_partner_device_ray_prepare_no_hidden_copy_evidence_8192_2026-06-15.json`
- M17 test: `tests/goal4413_v3_0_m17_partner_device_ray_prepare_no_hidden_copy_evidence_test.py`

Additional internal side review:

- Codex sub-agent internal reviewer returned pass/accept-with-boundary with the same M18 recommendation. This is not counted as a Claude/Gemini substitute; it is supporting internal critique only.

## Reviewer Verdicts

| Reviewer | Verdict | Blocking findings | Interpretation |
|---|---|---:|---|
| Codex | `accept-with-boundary` | 0 | Continue to M18; no public claims. |
| Claude | `accept-with-boundary` | 0 | Continue to M18; add Numba/methodology/metadata guardrails. |
| Gemini | `accept-with-boundary` | 0 | Continue to M18; fix no immediate blockers. |

## Shared Findings

The reviewers agree that:

- M1-M17 remains consistent with the Goal4392/4393 app-agnostic V3 boundary.
- M10-M17 measurement windows are honest and explicitly scoped.
- M17 validly closes the M16 ray-id host-bookkeeping debt for the hit-stream-safe device-column prepared ray batch contract.
- The device-column grouped argmin fail-closed behavior is correct, not a blocker.
- M18 device-side grouped contract is the right next target.
- No public performance or end-to-end zero-copy wording is authorized.

## Required M18 Guardrails

M18 must carry these requirements forward:

1. Implement an app-agnostic device-side grouped input contract; no app-specific public Python or native names.
2. Preserve fail-closed behavior for unsupported host-indexed paths.
3. Include CuPy best-partner and Numba reference rows for grouped paths, unless a written Numba omission justification is added before M18 exits.
4. Address the hit-stream Numba gap from M15-M17: either add Numba evidence for the hit-stream row-reduction path or record a written deferral/omission justification.
5. Keep transfer-counter windows explicit and separated for prepare and execution.
6. Add or cite transfer-counter methodology limits in the M18 report or the M12 contract follow-up.
7. Keep `true_zero_copy_ready` and related flags scoped to `measured_window` wording; public-facing prose must prefer "measured-window no-hidden-copy" unless broader evidence exists.
8. Keep final scalar/table materialization outside no-hidden-copy claims unless a future measured window includes it.
9. Keep public speedup, RT-core speedup, author-code parity, and automatic partner/backend selection flags false.

## Residual Risks

| Risk | Consensus handling |
|---|---|
| Micro-evidence has not yet become benchmark-app-scale performance evidence. | Accepted as internal architecture evidence only. |
| M15-M17 hit-stream path is CuPy-only. | Must be addressed or explicitly justified during M18/post-M18. |
| Device-side grouped contract may be substantially harder than hit-stream row reduction. | Accepted as the correct next technical target. |
| Internal JSON has `true_zero_copy_ready=true` for measured windows. | Wording discipline required; no end-to-end public claim. |
| Transfer-counter shim has methodological limits. | Document limits in next evidence packet. |

## External Review Invocations

Claude Code:

```text
npx --yes @anthropic-ai/claude-code -p --permission-mode bypassPermissions --disallowedTools "Edit,Write"
```

Gemini CLI:

```text
gemini -p <prompt> --approval-mode plan --skip-trust --output-format text
```

Both reviewers were instructed not to edit files and not to authorize public claims.

## Final Conclusion

Goal4414 passes 3-AI midterm consensus.

V3.0 may continue to M18 device-side grouped contract work, under the guardrails above. The accepted state is internal engineering progress only; it is not a release, benchmark, or public performance gate.
