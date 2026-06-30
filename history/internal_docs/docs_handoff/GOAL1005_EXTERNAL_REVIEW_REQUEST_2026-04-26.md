# Goal1005 External Review Request

Please independently review Goal1005, which replaces the stale Goal978/Goal969-derived speedup-candidate audit with one based directly on the final Goal1004 RTX A5000 v2 artifact bundle.

## Files

- Script: `scripts/goal1005_post_a5000_speedup_candidate_audit.py`
- Tests: `tests/goal1005_post_a5000_speedup_candidate_audit_test.py`
- JSON report: `docs/reports/goal1005_post_a5000_speedup_candidate_audit_2026-04-26.json`
- Markdown report: `docs/reports/goal1005_post_a5000_speedup_candidate_audit_2026-04-26.md`
- Source final merged summary: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_final_merged_summary_2026-04-26.json`
- Source final bundle: `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_artifacts_with_report_2026-04-26-v2.tgz`

## Review Questions

1. Does Goal1005 actually read the final A5000 v2 artifacts, rather than stale Goal969 group reports?
2. Are phase extractions reasonable for the app families: robot, fixed-radius, DB compact summaries, spatial summaries, prepared-decision paths, segment/polygon, graph, and polygon native-assisted paths?
3. Are the recommendations conservative?
   - `candidate_for_separate_2ai_public_claim_review` means candidate only, not authorized claim.
   - `internal_only_margin_or_scale` means no public claim.
   - `reject_current_public_speedup_claim` means do not claim speedup under current evidence.
4. Does the report preserve the no-public-speedup boundary?

## Expected Output

Write `ACCEPT` or `BLOCK` with concrete findings. If writing to repo is available, save to `docs/reports/goal1005_<reviewer>_external_review_2026-04-26.md`.
