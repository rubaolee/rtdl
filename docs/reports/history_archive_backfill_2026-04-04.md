# History Archive Backfill

Date: 2026-04-04

## Problem

The structured history system had drifted out of sync with the published
project state.

Recent completed goals were present in:

- `docs/`
- `docs/reports/`
- `history/ad_hoc_reviews/`

but many of them had never been registered into:

- `history/history.db`
- `history/revisions/<round-slug>/`

As a result, the generated dashboards:

- `history/revision_dashboard.md`
- `history/revision_dashboard.html`

stopped reflecting the real accepted project history after the earlier rounds.

## Repair Performed

Backfilled structured archive rounds for the later completed goals that had
been published but not registered:

- Goal 40
- Goal 41
- Goal 43
- Goal 44
- Goal 47
- Goal 50
- Goal 51
- Goal 52
- Goal 53
- Goal 54
- Goal 55
- Goal 56
- Goal 57
- Goal 59
- Goal 60
- Goal 61
- Goal 62

Also corrected the archive registration workflow so files under
`history/ad_hoc_reviews/` are archived as external reports instead of ordinary
project snapshots.

## Result

- `history/revisions/` now contains structured archive rounds for the accepted
  published goals through Goal 62.
- `history/history.db` now reflects those rounds.
- `history/revision_dashboard.md` and `history/revision_dashboard.html` now
  match the published project state again.

Current summary after the repair:

- revision rounds: `57`
- missing structured archive goals among the published completed goal set: none

## Explicit Non-Claim

Goal 58 is not included in the structured archive because it was exploratory
local work that was never accepted and never published as a completed goal.
