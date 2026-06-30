# External Review Handoff: Goal4182 Current 10-App Scale Packet

Please perform an independent read-only review of Goal4182.

## Files To Read

- `docs/reports/goal4182_current_benchmark_scale_profile_refresh_rtx4000ada_2026-06-09.md`
- `docs/reports/goal4182_current_benchmark_scale_profile_refresh_rtx4000ada/current_scale_profile_packet.json`
- `tests/goal4182_current_benchmark_scale_profile_refresh_test.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `src/rtdsl/current_benchmark_route_decisions.py`

## Context

Goal4182 refreshes the current 10 promoted benchmark app scale-profile packet on
an RTX 4000 Ada pod after the Goal4176-4181 RT-DBSCAN declared all-items
direct-status work.

The packet result is `all_pass: true`, `json_pass_count: 10`, and
`runtime_environment.working_tree_clean: true` at source commit
`79afb95a65bfb7a359efb56210294c89ec210060`.

RayJoin initially failed only because the public-CDB slice files were missing on
the pod. The final clean packet used RayJoin public raw text samples converted
outside the repository worktree through the existing
`scripts/goal2159_rayjoin_public_cdb_runner.py` materialization path.

## Questions To Answer

1. Does the Goal4182 report accurately describe the packet and its boundaries?
2. Does the artifact support only internal scale-profile/route-health evidence,
   not release or public performance claims?
3. Are all 10 benchmark app rows present, JSON-parseable, and claim-boundary
   clean?
4. Is the RayJoin contract split described honestly: Numba for bounded PIP
   one-shot, RTDL/OptiX for LSI scalar count, overlay active count, and repeated
   PIP batch?
5. Are there any missing tests, misleading wording, or next-step blockers before
   this packet can be used as internal v2.10 direction evidence?

## Required Output

Write a review file:

- Claude: `docs/reviews/goal4183_claude_review_goal4182_current_scale_packet_2026-06-09.md`
- Gemini: `docs/reviews/goal4184_gemini_review_goal4182_current_scale_packet_2026-06-09.md`

Use one of these verdicts exactly: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Do not edit source code or artifacts. This is a read-only review.
