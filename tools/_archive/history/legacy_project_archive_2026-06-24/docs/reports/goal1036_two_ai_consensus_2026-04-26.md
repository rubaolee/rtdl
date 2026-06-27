# Goal1036 Two-AI Consensus

Date: 2026-04-26

## Scope

Goal1036 fixes the `outlier_detection` `density_count` oracle path so it no longer performs brute-force neighbor expansion after computing scalar density counts.

Reviewed artifacts:

- `examples/rtdl_outlier_detection_app.py`
- `tests/goal1036_outlier_density_count_oracle_test.py`
- `docs/reports/goal1036_outlier_density_count_oracle_fix_2026-04-26.md`
- `docs/reports/goal1036_outlier_density_count_after_oracle_fix_2026-04-26.md`
- `docs/reports/goal1036_all_ready_apps_20000_after_outlier_fix_2026-04-26.md`
- `docs/reports/goal1036_claude_review_2026-04-26.md`
- `docs/reports/goal1036_gemini_review_2026-04-26.md`

## Independent Review Verdicts

| Reviewer | Verdict | Notes |
|---|---|---|
| Claude | `ACCEPT` | Verified `density_count` uses the closed-form tiled oracle, full mode still calls brute force, 20000-copy CPU/Embree/SciPy rows pass, and no public claim is authorized. |
| Gemini | `ACCEPT` | Accepted the bounded fix and claim boundary. |

## Codex Consensus

Status: `accepted_correctness_and_local_baseline_fix`.

The fix is accepted because:

- `density_count` now uses `expected_tiled_density_rows()` for oracle checking, avoiding accidental O(N^2) work.
- `full` output mode remains unchanged and still uses `brute_force_outlier_rows()`.
- Regression tests cover both behaviors.
- Local post-fix ramp artifacts show `outlier_detection` and the four baseline-ready apps pass at `copies=20000`.

## Boundary

This consensus closes only the outlier density-count oracle fix and local baseline execution evidence. It does not authorize public speedup claims, release authorization, or NVIDIA RT-core claims.
