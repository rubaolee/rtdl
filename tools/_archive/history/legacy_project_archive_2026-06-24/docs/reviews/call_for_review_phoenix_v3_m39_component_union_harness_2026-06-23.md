# Call For Review: Phoenix V3 M39 Component-Union Harness

Date: 2026-06-23

Status: `request_m39_component_union_harness_review_no_pod_run`

Review these files:

- `scripts/v3_phoenix_component_union_m38_pod_ab.py`
- `tests/v3_phoenix_m39_component_union_harness_test.py`
- `docs/reports/phoenix_v3_m39_component_union_harness_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m38_component_union_focused_pod_protocol_2ai_consensus_2026-06-23.md`

Question: does M39 satisfy the M38 harness gate strongly enough to allow the
single focused component-union POD run already conditionally authorized by the
M38 consensus?

Use exactly one verdict:

- `accept_m39_authorize_one_focused_component_union_pod`
- `accept_m39_harness_only_require_revision_before_pod`
- `revise_m39_harness`
- `reject_m39_harness`

Specific checks:

1. Does the harness preserve the M38 component-label contract?
2. Does it block component-signature-only substitution?
3. Are the Embree, legacy OptiX, and productized runner variants same-contract
   enough for a focused A/B?
4. Does the productized route actually use
   `run_radius_graph_component_union_3d_prepared_session`?
5. Are heartbeat and hard-cap enforcement sufficient for paid POD use?
6. Does the known `radius=3.0` density risk need a protocol revision before
   POD, or is fail-closed hard-cap evidence acceptable?
7. Are any non-authorization boundaries weakened?

Non-authorization: do not authorize V3 release, all-app POD, public speedup
wording, broad V3-over-V2 wording, true-zero-copy wording, automatic partner
selection, V4 work, C ABI work, or embedding work.

## Goal-Level Decision Audit

Decision: request external review before using the M39 harness on paid POD.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   It would be foolish to treat a passing dry-run as enough evidence for paid
   measurement without external scrutiny.

3. Was there another path?

   Yes. Spend the focused POD immediately. That would weaken the review
   discipline that Phoenix V3 now depends on.

4. Can I now try a different path that actually solves the problem?

   Yes. Ask for a verdict on harness readiness, then run exactly one focused
   POD only if the verdict accepts it.
