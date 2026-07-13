# Call For Review - Goal5155 X-HD Production Mode And Route Profile

Please strictly review Goal5155.

## Files

- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py`
- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_matrix_pod.json`
- `Paper-reproduction-apps/x-hd-paper/data/manifest.json`
- `tests/goal5155_xhd_production_validation_and_route_profile_test.py`
- `history/internal_docs/goal5155_xhd_production_mode_and_route_profile_result_2026-07-08.md`

## Review Questions

1. Does `--validation-mode author-only` truly skip exact-reference validation
   while preserving author HDResult comparison?
2. Does the matrix preserve `exact_reference_sec_* = null` and
   `rtdl_matches_exact_reference = null` rather than treating skipped exact
   validation as a failure?
3. Are the new per-direction subphase timings actually recorded for seed,
   native frontier rows, nearest continuation, max-nearest reduction, and total
   direction time?
4. Is the interpretation correct that Goal5155 is a timing-boundary/profile
   improvement rather than an algorithmic speedup?
5. Does the production matrix avoid speedup/parity ratios and keep the phase
   mismatch visible?
6. Do the tests pin the production validation mode and profile fields strongly
   enough?
7. Does the manifest artifact entry state the boundary without overclaiming?

## Expected Verdict Shape

```text
verdict_label:
blocking_findings:
required_amendments:
non_blocking_notes:
```
