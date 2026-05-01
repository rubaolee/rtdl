# Goal1224 Claude Review Request: Remaining RTX Public Wording Rows

Date: 2026-05-01

Primary reviewer: Codex
Requested external reviewer: Claude

## Task

Review Goal1224, which resolves the three remaining RTX public-wording rows that were previously not public-reviewed:

- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `hausdorff_distance`

Return a formal `ACCEPT` or `BLOCK` verdict. If blocked, list exact required fixes.

## Evidence Source

Goal1224 uses the existing valid same-contract intake:

- `docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.json`
- `docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.md`

The resolver output is:

- `docs/reports/goal1224_resolve_remaining_public_wording_rows_2026-05-01.json`
- `docs/reports/goal1224_resolve_remaining_public_wording_rows_2026-05-01.md`

## Proposed Decisions

| App | Path | Embree phase sec | OptiX phase sec | Ratio | Proposed status |
| --- | --- | ---: | ---: | ---: | --- |
| `graph_analytics` | `graph_visibility_edges` | `1.000280` | `2.000505` | `0.50x` | `public_wording_blocked` |
| `polygon_pair_overlap_area_rows` | `native_assisted_lsi_pip_candidate_discovery` | `2.896597` | `3.452362` | `0.84x` | `public_wording_blocked` |
| `hausdorff_distance` | `directed_threshold_prepared` | `1.680214` | `0.122389` | `13.73x` | `public_wording_reviewed` |

The positive public ratio floor used by the resolver is `1.2x`.

## Files To Review

- `scripts/goal1224_resolve_remaining_public_wording_rows.py`
- `tests/goal1224_resolve_remaining_public_wording_rows_test.py`
- `src/rtdsl/app_support_matrix.py`
- `tests/goal1011_rtx_public_wording_matrix_test.py`
- `scripts/goal947_v1_rtx_app_status_page.py`
- `tests/goal947_v1_rtx_app_status_page_test.py`
- `docs/v1_0_rtx_app_status.md`
- `docs/reports/goal947_v1_rtx_app_status_page_2026-04-25.json`
- `docs/reports/goal1223_v0_9_8_rtx_app_speedup_summary_2026-05-01.md`

## Verification Already Run

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1224_resolve_remaining_public_wording_rows_test \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal947_v1_rtx_app_status_page_test -v
```

Result: `18 tests`, `OK`.

## Review Questions

1. Is it technically correct to promote only `hausdorff_distance` to `public_wording_reviewed` based on 13.73x same-contract OptiX-vs-Embree evidence?
2. Is it technically correct to mark `graph_analytics` and `polygon_pair_overlap_area_rows` as `public_wording_blocked` because valid same-contract evidence shows OptiX slower than Embree?
3. Are the public wording boundaries narrow enough to avoid whole-app, default-mode, Python postprocess, graph analytics system, exact polygon-area, and exact Hausdorff claims?
4. Are docs/tests/source-of-truth updates consistent enough for current branch closure without moving the `v0.9.8` release tag?
