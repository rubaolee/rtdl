# Review Debt: Goal4770 RT-BarnesHut Release Packet Delta

Date: 2026-06-26

Status: **open review debt**

Goal4770 updates the V4 release packet and public docs after Goal4769 corrected
the RT-BarnesHut author phase denominator. It has not yet received the required
external 3-AI completion audit.

## Artifact Under Review

- `future/v4/v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.md`
- `future/v4/evidence/v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.json`
- `future/v4/v4_goal4769_rt_barneshut_author_phase_accounting_2026-06-26.md`

## Key Facts

- Goal4756 matrix is not rewritten.
- Goal4770 is a delta and claim-boundary update.
- Native RT-BarnesHut route is same-input/same-semantics checksum-valid at 10M.
- Checksum relative error: `9.051486889720442e-7`.
- RTDL sort `6.16351s` vs author sort `6.87096s`.
- RTDL internal program with input download `~7.513s` vs author total program
  `10.4391s`.
- RTDL route still downloads input columns for tree build.
- RTDL route uses custom-primitive control geometry, not literal author
  triangle geometry.

## Questions For Reviewer

1. Is it correct not to rewrite the historical Goal4756 matrix and instead add
   Goal4770 as a delta?
2. Is Barnes-Hut's corrected current classification honest?
3. Is the internal-program comparison fair enough for release-packet evidence?
4. What exact additional evidence is required before public RT-BarnesHut paper
   reproduction wording?
5. Are the blocked claims sufficiently explicit?

## Requested Verdict Labels

Use one:

- `accept_goal4770_complete_release_packet_delta`
- `accept_with_required_amendments`
- `reject_requires_rework`
- `blocked_need_more_evidence`

## Non-Authorization

This review debt does not authorize:

- public V4 tag;
- public RT-BarnesHut paper-reproduction wording;
- broad V4 speedup wording;
- V2/V3/V4 public RT-BarnesHut speed table;
- no-copy/device-resident tree-build claims.

