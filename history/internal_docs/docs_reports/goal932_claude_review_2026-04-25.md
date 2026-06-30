**ACCEPT — no blockers.**

---

## Summary

### What was changed (and verified)

| Item | Verification |
|---|---|
| `expected_tiled_candidate_threshold(copies, radius)` added to `rtdl_ann_candidate_app.py:201–223` | Runs oracle on 1 copy, tiles IDs — O(copies × base) not O(copies² × base²) |
| Profiler `_profile_ann` dry-run and validation use the tiled oracle (`goal887…profiler.py:178–194`) | No longer calls quadratic `candidate_threshold_oracle` at production copies |
| `matches_oracle: None` when `skip_validation=True` (profiler lines 152–153, 292–293) | Replaces the previous implicit `true`, which was fabricated |
| Hausdorff/ANN/Barnes-Hut deferred manifest commands have no `--skip-validation` (manifest script + JSON already in sync) | Confirmed in both `.py` and `.json` |
| `facility_knn_assignment` retains `--skip-validation` | Intentional; Goal920-reviewed policy; test `test_manifest_uses_phase_profiler_for_new_prepared_decision_entries` asserts this asymmetry explicitly |

### Test coverage

The test suite (`goal887_prepared_decision_phase_profiler_test.py`) directly enforces the invariant: `--skip-validation` must be absent for Hausdorff/ANN/Barnes-Hut and present for facility. `test_ann_dry_run_uses_tiled_threshold_oracle` at `copies=5000` confirms `query_count=15000`, `covered_query_count=15000` — tiled oracle correct.

---

## Is removing `--skip-validation` from Hausdorff/ANN/Barnes-Hut safe and honest?

**Yes on both counts.**

**Safe:** The profiler phases validation in a separate `validation_sec` bucket (lines 282–284, reported via `_stats(validation_samples)`). Removing `--skip-validation` does not pollute `optix_query_sec` — the phase separation required by the `baseline_review_contract` is preserved. The ANN oracle is now O(N) via tiling; Hausdorff already used `expected_tiled_hausdorff`; Barnes-Hut oracle runs once per iteration against the actual generated bodies/nodes (not a quadratic cross-copy expansion).

**Honest:** With `--skip-validation` the field previously emitted `matches_oracle: null` (now) vs. previously `true` by fabrication (pre-Goal932). Removing the flag causes the cloud run to record the actual `matches_oracle: true/false` from comparing OptiX output to the CPU oracle — which is the evidence the activation gates require. The report correctly bounds scope: these apps remain deferred, not promoted; production-scale RTX artifacts with honest validation plus analyzer/intake review are still mandatory before any readiness change.
