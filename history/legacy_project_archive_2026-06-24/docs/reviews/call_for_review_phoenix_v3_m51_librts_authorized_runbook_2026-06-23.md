# Call For Review: Phoenix V3 M51 LibRTS Authorized-Run Runbook

Date: 2026-06-23

Please critically review whether M51 is a safe, bounded runbook for a future
focused LibRTS stability POD run after M47/M48 review.

Primary runbook:

- `docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`

Required supporting files:

- `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`

Requested verdict labels:

- `accept_m51_runbook_no_run`
- `revise_m51_before_any_execution`
- `reject_m51_accidentally_authorizes_pod`

Review questions:

1. Does M51 require the exact external verdict before any execution?
2. Does it keep dry-run as the required first operation?
3. Does it require separate current and V2.14 roots/Python executables?
4. Does it preserve full copy-back rather than summary-only evidence?
5. Does it define intake stop conditions before speed interpretation?
6. Does it avoid all-app, release, public speedup, V4, embedding, C ABI, and
   true-zero-copy authorization?
7. Does it stay generic runtime-control work rather than LibRTS app tuning?
8. Is the four-question goal-level audit present?

Non-authorization to preserve:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
