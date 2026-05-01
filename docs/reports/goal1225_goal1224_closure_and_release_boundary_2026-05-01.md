# Goal1225 Goal1224 Closure And Release Boundary

Date: 2026-05-01

## Purpose

This note records the closure state after Goal1224 resolved the final three
previously not-public-reviewed RTX public-wording rows on the current branch.
It is a post-release branch documentation note and does not move the `v0.9.8`
tag.

## Current Branch Outcome

| App | Final public-wording state | Evidence interpretation |
| --- | --- | --- |
| `hausdorff_distance` | `public_wording_reviewed` | Valid same-contract evidence shows OptiX `0.122389` s versus Embree `1.680214` s, ratio `13.73x`; only the prepared Hausdorff threshold-decision traversal sub-path is claimable. |
| `graph_analytics` | `public_wording_blocked` | Valid same-contract evidence shows OptiX `2.000505` s versus Embree `1.000280` s, ratio `0.50x`; no positive public RTX speedup wording is authorized. |
| `polygon_pair_overlap_area_rows` | `public_wording_blocked` | Valid same-contract evidence shows OptiX `3.452362` s versus Embree `2.896597` s, ratio `0.84x`; no positive public RTX speedup wording is authorized. |

## Source Files Updated By Goal1224

- `src/rtdsl/app_support_matrix.py`
- `scripts/goal1224_resolve_remaining_public_wording_rows.py`
- `scripts/goal947_v1_rtx_app_status_page.py`
- `docs/v1_0_rtx_app_status.md`
- `docs/reports/goal947_v1_rtx_app_status_page_2026-04-25.json`
- `docs/reports/goal1223_v0_9_8_rtx_app_speedup_summary_2026-05-01.md`
- `tests/goal1224_resolve_remaining_public_wording_rows_test.py`
- `tests/goal1011_rtx_public_wording_matrix_test.py`
- `tests/goal947_v1_rtx_app_status_page_test.py`

## Review And Consensus

Goal1224 has 2-AI consensus:

- Codex implemented and locally reviewed the change.
- Gemini reviewed the Goal1224 artifacts and returned `ACCEPT` with no required
  fixes.

Review trail:

- `docs/handoff/GOAL1224_CLAUDE_REMAINING_PUBLIC_WORDING_ROWS_REVIEW_REQUEST_2026-05-01.md`
- `docs/reports/goal1224_gemini_remaining_public_wording_rows_review_2026-05-01.md`
- `docs/reports/goal1224_two_ai_consensus_2026-05-01.md`

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1224_resolve_remaining_public_wording_rows_test \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal947_v1_rtx_app_status_page_test -v
```

Result: `18 tests`, `OK`.

## Git Boundary

- Goal1224 implementation commit: `6105699 Resolve remaining RTX public wording rows`
- Branch pushed: `origin/codex/rtx-cloud-run-2026-04-22`
- Release tag boundary: `v0.9.8` remains on `204b393 Release v0.9.8`

This means the current branch contains post-release public-wording resolution
work, while the published `v0.9.8` tag remains unchanged.
