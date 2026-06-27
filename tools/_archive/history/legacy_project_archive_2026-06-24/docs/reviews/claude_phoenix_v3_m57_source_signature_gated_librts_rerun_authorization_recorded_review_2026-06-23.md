# Claude Review: Phoenix V3 M57 Source-Signature-Gated LibRTS Rerun Authorization

Date: 2026-06-23

Raw reviews:

- initial review:
  `docs/reviews/claude_phoenix_v3_m57_source_signature_gated_librts_rerun_authorization_review_2026-06-23.raw.md`
- initial review stderr:
  `docs/reviews/claude_phoenix_v3_m57_source_signature_gated_librts_rerun_authorization_review_2026-06-23.stderr.txt`
- fail-closed re-review:
  `docs/reviews/claude_phoenix_v3_m57_fail_closed_rereview_2026-06-23.raw.md`
- fail-closed re-review stderr:
  `docs/reviews/claude_phoenix_v3_m57_fail_closed_rereview_2026-06-23.stderr.txt`

Final Claude verdict after fail-closed fix:

```text
authorize_m57_one_source_signature_gated_librts_rerun_after_fail_closed_fix
```

## Review Read

Claude initially authorized one M57 rerun but identified a code-level gap:
`--execute` still ran measured samples after preflight errors. That gap was
fixed before this recorded review was treated as final.

After the fix, Claude confirmed:

- `build_or_run_packet()` now returns `STATUS_FAILED` before
  `execute_schedule()` when `execute_preflight()` returns any errors.
- `test_execute_aborts_before_samples_when_preflight_fails` covers the
  fail-closed behavior.
- The exact authorized token is
  `M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED`.
- The old M54/M55 token remains consumed and is not reused for M57.
- Execution remains limited to one M47 run, unchanged scenarios, exactly 8
  paired samples, real roots, explicit Linux/POD Python paths, target dry-run
  first, and source-signature gate confirmation before execution.

## Residual Risks

- A metadata-fixed rerun may still be performance-red.
- Static source-signature checks do not prove runtime metadata emission.
- No watch-row closure may be claimed from raw output; copied evidence needs a
  later review packet.

## Non-Authorization

Claude did not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure
- no scenario changes
- no sample-count changes
- no second M57 run
