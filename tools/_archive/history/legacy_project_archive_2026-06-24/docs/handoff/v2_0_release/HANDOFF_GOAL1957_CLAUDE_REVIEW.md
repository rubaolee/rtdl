# Claude Review Request: Goal1957 Partner Identity-Payload Contract

Please review the Goal1957 contract and implementation as an independent Claude
reviewer distinct from Codex.

Read:

- `docs/reports/goal1957_partner_identity_payload_contract_2026-05-14.md`
- `examples/rtdl_control_apps_cupy_rawkernel.py`
- `tests/goal1957_partner_identity_payload_contract_test.py`
- `docs/reports/goal1956_l4_rawkernel_control_app_optix_v800_pod_2026-05-14.md`

Questions:

1. Does the Goal1957 report correctly identify the cause of the Goal1956 polygon
   slowdown as a poor partner handoff schema rather than an RTDL candidate
   discovery failure?
2. Is `PartnerPairPayloadTable` a reasonable first slice of a general
   identity-preserving partner payload contract, while still bounded to the
   authored axis-aligned polygon control apps?
3. Does the implementation avoid overclaiming true zero-copy, arbitrary polygon
   overlay acceleration, whole-app v2.0 speedup, or release readiness?
4. Are the tests and reports enough for a local checkpoint before pod retesting?

Please write the review to:

`docs/reviews/goal1957_claude_review_partner_identity_payload_contract_2026-05-14.md`

Use one of these verdicts exactly: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

