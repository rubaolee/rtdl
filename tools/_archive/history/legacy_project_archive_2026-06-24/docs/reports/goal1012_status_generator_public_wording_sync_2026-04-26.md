# Goal1012 Status Generator Public Wording Sync

Date: 2026-04-26

## Problem

After Goal1011 added `rtdsl.rtx_public_wording_matrix()`, the hand-edited
public status docs were correct, but `scripts/goal947_v1_rtx_app_status_page.py`
was still stale. Re-running the generator could remove the Goal1009 reviewed
wording table and collapse `robot_collision_screening` back into the generic
`ready_for_rtx_claim_review` display.

## Change

Updated the Goal947 generator so generated payloads include:

- `source_of_truth.public_wording = rtdsl.rtx_public_wording_matrix()`
- `summary.reviewed_public_wording = 7`
- `summary.blocked_public_wording = 1`
- per-row `public_wording_status`, `public_wording`, `public_wording_evidence`,
  and `public_wording_boundary`
- the Goal1009 reviewed public RTX sub-path wording table in generated Markdown
- `robot_collision_screening` rendered as `blocked_for_public_speedup_wording`
  in public Markdown while preserving the source matrix status
  `ready_for_rtx_claim_review`

Regenerated:

- `docs/v1_0_rtx_app_status.md`
- `docs/reports/goal947_v1_rtx_app_status_2026-04-25.json`
- `docs/reports/goal947_v1_rtx_app_status_page_2026-04-25.json`

## Tests

Updated `tests/goal947_v1_rtx_app_status_page_test.py`.

The test now verifies:

- generated payloads expose the public wording source of truth;
- generated Markdown contains the Goal1009 section;
- generated Markdown preserves `blocked_for_public_speedup_wording`;
- both checked-in Goal947 JSON artifacts include the public wording layer;
- robot is `public_wording_blocked` in both checked-in JSON artifacts.

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal1011_rtx_public_wording_matrix_test -v
```

Result: 15 tests OK.

## Boundary

This goal does not add new performance evidence and does not authorize any new
public speedup claim. It only prevents regenerated public status artifacts from
dropping the Goal1011 public-wording distinction.
