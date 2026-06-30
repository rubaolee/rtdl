# Goal1220 External Review Request

Please review Goal1220 as an external AI reviewer for RTDL.

## Scope

Goal1220 is the final authorization record for the v0.9.8 bounded RTX app
evidence and public-claim cleanup release.

It must not itself tag, push, publish, upload packages, or bump `VERSION`.
Instead, it should authorize a separate release-action step only after Goal1220
has external review and saved two-AI consensus.

## Files To Review

- `docs/reports/goal1220_v0_9_8_final_authorization_2026-05-01.md`
- `tests/goal1220_v0_9_8_final_authorization_test.py`
- `docs/release_reports/v0_9_8/tag_preparation.md`
- supporting evidence:
  - `docs/reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.md`
  - `docs/reports/goal1219_two_ai_consensus_2026-05-01.md`
  - `docs/release_reports/v0_9_8/README.md`
  - `docs/release_reports/v0_9_8/release_statement.md`
  - `docs/release_reports/v0_9_8/support_matrix.md`
  - `docs/release_reports/v0_9_8/audit_report.md`

## Validation Already Run

Run or verify:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1220_v0_9_8_final_authorization_test -v
```

Expected result: 3 tests OK.

## Requested Verdict

Please answer with `ACCEPT` or `BLOCK`.

Focus on:

1. Whether Goal1220 correctly authorizes a future release-action step only after
   Goal1220 itself has 2-AI consensus.
2. Whether it avoids performing or prematurely claiming tag/push/publish/version
   bump.
3. Whether it preserves the v0.9.8 public RTX claim boundaries.
4. Whether no additional pod is required before release action for the bounded
   claims.

If accepted, write or return a concise review suitable for saving as:

`docs/reports/goal1220_gemini_v0_9_8_final_authorization_review_2026-05-01.md`
