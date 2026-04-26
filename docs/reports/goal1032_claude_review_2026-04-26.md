# Goal1032 Claude Review

Date: 2026-04-26

Reviewer: Claude (claude-sonnet-4-6)

## Verdict

**ACCEPT**

## Scope

This review covers:

- `docs/reports/goal1032_baseline_manifest_correction_2026-04-26.md`
- `scripts/goal1030_local_baseline_manifest.py`
- `tests/goal1030_local_baseline_manifest_test.py`
- `docs/reports/goal1031_local_baseline_smoke_2026-04-26.md`
- `docs/reports/goal1031_two_ai_consensus_2026-04-26.md`

## Classification Correctness

**Moving `outlier_detection` and `dbscan_clustering` from `baseline_ready` to `baseline_partial` is correct.**

The root cause is clearly identified and the reasoning is sound. SciPy is not installed locally. The `--backend scipy` compact scalar modes (`--output-mode density_count` for outlier_detection, `--output-mode core_count` for dbscan_clustering) passed not because SciPy executed, but because those modes activate analytic/oracle scalar shortcuts in the app that bypass the SciPy cKDTree codepath entirely. A command that succeeds via an oracle shortcut is not SciPy baseline evidence.

The correction is applied consistently:

- Both entries reclassified to `baseline_partial` in `ENTRIES` at lines 29–48 of the script.
- The SciPy commands are removed from their command lists; only CPU and Embree commands remain.
- The reason fields explicitly state: "compact scalar SciPy is not a real cKDTree baseline in this app mode and needs a dedicated extractor."
- The resulting count (2 `baseline_ready`, 15 `baseline_partial`) is internally consistent and matches the test assertions at lines 40–41 of the test file.

The two remaining `baseline_ready` entries (`service_coverage_gaps`, `event_hotspot_screening`) are correctly retained. Their SciPy commands exist as distinct CLI paths. The smoke runner correctly classifies their SciPy failures as `optional_dependency_unavailable` (not `failed`) because the dependency is absent at the OS level, not because the command path is wrong.

## No-Speedup-Claim Boundary

All artifacts are clean. No speedup claims are present.

- Manifest script boundary string (line 208–211): "does not execute benchmarks, does not authorize speedup claims, and does not replace same-semantics review."
- Smoke report header: "It is not same-scale baseline evidence and does not authorize speedup claims."
- Correction doc boundary section: "This correction does not authorize speedup claims."
- Two-AI consensus: "It is not same-scale baseline evidence and does not authorize speedup claims."
- Test `test_cli_writes_outputs` (line 71): asserts `"does not authorize speedup claims"` appears in the written Markdown, providing code-level enforcement that the boundary cannot be removed silently.

## Test Consistency

The test file is consistent with the corrected script:

- `test_manifest_covers_goal1029_apps` asserts `baseline_ready == 2` and `baseline_partial == 15`, matching the script's ENTRIES.
- All 17 apps in the expected set match the 17 ENTRIES in the script.
- Command structure checks (prefix `python3`, paths starting with `examples/` or `scripts/`) are still satisfied by the corrected entries.
- `test_cli_writes_outputs` exercises the CLI end-to-end and enforces the no-speedup-claim string.

## Smoke Run Consistency

The regenerated smoke report covers exactly the 2 `baseline_ready` entries. Both show:

- CPU: `ok`
- Embree: `ok`
- SciPy: `optional_dependency_unavailable`

This matches the expected state: SciPy CLI paths exist in the app but the library is absent on this machine. Status `ok_with_optional_dependency_gaps` is the correct summary.

## Minor Observations (Non-Blocking)

1. The `service_coverage_gaps` and `event_hotspot_screening` reason fields say "SciPy paths are exposed by the app CLI" without noting that SciPy is currently unavailable locally. This is accurate but could be misleading to a future reader who does not look at the smoke report. Suggest adding a parenthetical "(SciPy unavailable locally)" in a future pass.

2. The correction document lists the next-work items clearly (dedicated SciPy/cKDTree extractors, Linux SciPy environment). These are appropriate future-scope items and do not block this correction.

## Summary

The reclassification is technically correct, the documentation is precise, no speedup claims appear anywhere, and the tests enforce the key invariants. Goal1032 is accepted as a tightening correction to Goal1030.
