# Goal1034 Claude Review

Date: 2026-04-26
Reviewer: Claude (claude-sonnet-4-6)
Artifacts reviewed:
- `docs/reports/goal1034_scipy_enabled_local_smoke_2026-04-26.md`
- `docs/reports/goal1034_local_baseline_smoke_with_scipy_2026-04-26.md`
- `docs/reports/goal1034_local_baseline_smoke_with_scipy_2026-04-26.json`

## Verdict

**ACCEPT**

## Checklist

### 1. Scope boundary is honestly stated

Pass. The narrative report (`goal1034_scipy_enabled_local_smoke`) carries an explicit **Boundary** section:

> "This is a smoke-scale run with `--copies` rewritten to `50`. It checks command health and dependency readiness only. It is not same-scale baseline evidence and does not authorize speedup claims."

The machine-readable JSON artifact carries the same boundary verbatim in its top-level `"boundary"` field (line 2), making the limitation queryable programmatically. The smoke runner report header also opens with:

> "Smoke mode intentionally scales --copies down and only checks local command health. It is not same-scale baseline evidence and does not authorize speedup claims."

The limitation is stated three independent times across the two documents and the JSON — no ambiguity.

### 2. SciPy-enabled commands passed for all four ready apps

Pass. JSON `returncode` and `status` fields per app:

| App | SciPy returncode | SciPy status | summary_mode |
|---|---|---|---|
| `outlier_detection` | `0` | `ok` | `scipy_ckdtree_threshold_count` |
| `dbscan_clustering` | `0` | `ok` | `scipy_ckdtree_threshold_count` |
| `service_coverage_gaps` | `0` | `ok` | (no summary_mode field — app-specific schema) |
| `event_hotspot_screening` | `0` | `ok` | (no summary_mode field — app-specific schema) |

For `outlier_detection` and `dbscan_clustering`, `matches_oracle: true` is confirmed in the JSON summary, meaning the SciPy path produced numerically correct results against the oracle. For `service_coverage_gaps`, the `covered_household_count` is consistent with cpu/embree runs (150 of 200 households). For `event_hotspot_screening`, no result-count field is emitted by the app at smoke scale, but the process exited cleanly with returncode 0.

Overall row status: all four are `"status": "ok"`. Top-level JSON status is `"status": "ok"`, `"failed_entry_count": 0`, `"optional_gap_entry_count": 0`.

### 3. No speedup claims

Pass. The report verdict is `smoke_pass_no_speedup_claim`. No text in any of the three artifacts asserts that SciPy is faster, slower, or that any timing result supports a performance conclusion. The elapsed times are recorded in the JSON (e.g., `outlier_detection` scipy is 6.79 s vs cpu 0.21 s at 50 copies) but the report makes no interpretation of these numbers, correctly treating them as incidental smoke-scale observations only.

### 4. Additional observations (non-blocking)

- `event_hotspot_screening` scipy summary does not emit a correctness metric (no `matches_oracle`, no output count). This is an existing app-specific behavior at smoke scale, not introduced by this goal. The exit-code-0 gate used by the smoke runner is the appropriate check for this app in this mode.
- SciPy elapsed time for `outlier_detection` (6.79 s) is roughly 54× slower than embree (0.13 s) at smoke scale. This is expected startup/import overhead at tiny input size and is correctly left uninterpreted.
- The `.venv-rtdl-scipy` venv approach isolates the SciPy install from the system Python, which is the right approach. No concern there.

## Summary

The three artifacts are internally consistent, clearly scoped, and make no claims beyond what was measured. All four SciPy backend commands exited cleanly. The goal delivers what it promises: dependency-readiness and command-health evidence at smoke scale, with the boundary stated explicitly in both human- and machine-readable form.
