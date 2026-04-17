# Goal 477 External Review

Date: 2026-04-16
Reviewer: Claude (external AI review)
Verdict: **ACCEPT**

## What Was Reviewed

- Goal 477 goal definition: `docs/goal_477_v0_7_broad_unittest_discovery_repair.md`
- Goal 477 repair report: `docs/reports/goal477_v0_7_broad_unittest_discovery_repair_2026-04-16.md`
- Five narrow test edits in `tests/`:
  - `goal199_fixed_radius_neighbors_cpu_oracle_test.py`
  - `goal205_knn_rows_cpu_oracle_test.py`
  - `goal166_orbiting_star_ball_demo_test.py`
  - `goal168_hidden_star_stable_ball_demo_test.py`
  - `goal178_smooth_camera_orbit_demo_test.py`

## Findings

**PYTHONPATH fix (goal199, goal205):** Both CLI subprocess tests now build an explicit `env` dict that prepends `src` to `PYTHONPATH` before passing it to `subprocess.run` (goal199:61-62, goal205:63-64). The fix is correct and minimal — it does not alter any assertion logic or change what the test verifies. The existing `cwd=REPO_ROOT` ensures the repo root is the working directory; the PYTHONPATH addition ensures `rtdsl` is importable from `src/` regardless of how the test runner was invoked.

**SkipTest on PermissionError (goal166, goal168, goal178):** Each multi-process visual-demo test wraps only the `ProcessPoolExecutor`-dependent render call in a `try/except PermissionError` that raises `unittest.SkipTest` (goal166:370-371, goal168:165-172, goal178:144-145). The guard is narrow: single-process unit tests in the same files are unaffected. The skip message is descriptive. This is the correct portable pattern for sandbox-restricted multiprocessing; it does not hide real failures on hosts where multiprocessing is available.

**Broad discovery result:** `python3 -m unittest discover -s tests -p '*test*.py'` went from `FAILED (errors=5, skipped=105)` to `OK (skipped=108)` at 1151 tests. The three additional skips correspond exactly to the three SkipTest guards added, which is consistent.

**Boundary compliance:** The report clearly states Goal 477 does not stage, commit, tag, push, merge, or release. No release authorization is claimed.

**Acceptance criteria met:** All six criteria from `docs/goal_477_v0_7_broad_unittest_discovery_repair.md` are satisfied: broad discovery was run, all five failures triaged, narrow fixes applied, final count recorded, no VCS operations performed, and this external review is preserved.

## Conclusion

All five edits are minimal, correct, and honest. The broad discovery result is clean. No concerns.
