# Claude Task: Review v1.6.11 Release-Candidate Evidence Packet

Please perform a read-only independent Claude review of the Goal1729 v1.6.11 release-candidate evidence packet after it is written.

## Context

The current evidence chain includes:

- Goal1714: RTX 4000 Ada pod build and source/runtime smoke validation after source recovery.
- Goal1716: all 16 active current-version Goal1659 pod rows completed after GEOS link and graph binding fixes.
- Goal1718: raw Goal1660 cross-version attempt showed current 28/28 rows ran but tagged v1.0 rejected many original `--backend` command shapes.
- Goal1720: v1.0 OptiX adapter recovered 12 more v1.0 OptiX artifacts, yielding 16 real comparable v1.0/current artifact pairs.
- Goal1722: manifest corrected to 16 real comparable rows, 20 blocked/excluded/current-only rows.
- Goal1723: comparable artifact consolidation.
- Goal1726: companion evidence resolves the three Goal1723 timing-artifact boundaries.
- Goal1727/Goal1728: Claude/Gemini independent reviews accepted Goal1726.

## Review Goals

After Codex writes `docs/reports/goal1729_v1_6_11_release_candidate_evidence_packet_2026-05-12.md` and its test:

1. Confirm the packet accurately summarizes the evidence chain above.
2. Confirm it does not authorize release tagging, publication, or public speedup wording.
3. Confirm it distinguishes current-version row execution from v1.0/current comparable artifact evidence.
4. Confirm it treats unsupported v1.0 Embree rows as unsupported/current-only, not failed/slower/faster baselines.
5. Confirm it states that final release action still requires explicit user decision and final release consensus.

## Output

Write your review to:

`docs/reviews/goal1730_claude_review_goal1729_v1_6_11_release_candidate_packet_2026-05-12.md`

Use verdicts from `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`. State explicitly that this is an independent Claude review distinct from Codex and Gemini.
