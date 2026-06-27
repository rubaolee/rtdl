# Goal1023 v0.9.6 History Catch-Up

Date: 2026-04-26

Status: accepted history repair.

## Why This Round Exists

Goal1022 detected a narrow but real public-history drift:

- current public docs describe `v0.9.6` as the released boundary;
- `docs/release_reports/v0_9_6/README.md` and
  `docs/release_reports/v0_9_6/audit_report.md` say the release included
  history catch-up through Goal684;
- `history/COMPLETE_HISTORY.md` and `history/revision_dashboard.md` still
  topped out at `v0.9.5-current-main` and did not mention `v0.9.6` or Goal684.

This round appends the missing public-history entry. It does not rewrite older
records.

## Covered Work

| Goal range | Result |
| --- | --- |
| Goal680 | History catch-up and stale history DB repair for Goals658-679. |
| Goal681 | Post-history current-main release gate. |
| Goal682 | `v0.9.6` release-candidate package. |
| Goal683 | Final local candidate gate. |
| Goal684 | Release-level flow audit and public-doc release conversion. |
| Goal1022 | Later audit that detected this public-history drift after additional RTX wording work. |

## Key Evidence Files

- `docs/release_reports/v0_9_6/README.md`
- `docs/release_reports/v0_9_6/audit_report.md`
- `docs/reports/goal680_consensus_2026-04-20.md`
- `docs/reports/goal681_consensus_2026-04-20.md`
- `docs/reports/goal682_consensus_2026-04-21.md`
- `docs/reports/goal683_consensus_2026-04-21.md`
- `docs/reports/goal684_consensus_2026-04-21.md`
- `docs/reports/goal1022_history_release_drift_audit_2026-04-26.md`

## Boundary

- This is a history-index repair, not a new release.
- The current public release remains `v0.9.6`.
- This does not authorize public RTX speedup claims.
- Historical reports are not rewritten; the correction is appended as a new
  structured round.
