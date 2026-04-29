# Goal1111 Robot Embree Timing-Only Chunk Mode

Date: 2026-04-29

## Purpose

Goal1110 showed that the current Robot Embree baseline runner is impractical because every 200k-pose chunk performs full CPU-oracle validation before Embree timing. Goal1111 adds a timing-only mode to the robot baseline artifact writer so correctness validation can be separated from large-scale timing collection.

## Code Change

Files changed:

- `scripts/goal839_baseline_artifact_schema.py`
- `scripts/goal839_robot_pose_count_baseline.py`
- `tests/goal839_local_baseline_collectors_test.py`

Behavior:

- Existing validated artifacts are unchanged: `correctness_parity: true` still yields `status: ok`.
- Embree timing-only chunks can now use `--skip-validation`.
- Timing-only artifacts use:
  - `status: timing_only`
  - `correctness_parity: null`
  - `phase_seconds.oracle_validation_separate: 0.0`
  - `validation.skipped: true`
  - `authorizes_public_speedup_claim: false`
- The CLI treats both `status: ok` and `status: timing_only` as successful exits so shell runners using `set -e` can collect timing-only chunks.

## Boundary

Timing-only chunks are not correctness evidence by themselves. They must be paired with separate validation chunks and a revised intake before comparison or public wording review.

## Verification

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal839_local_baseline_collectors_test -v
```

Initial result:

```text
Ran 8 tests in 0.279s
OK
```

Second-AI review found one blocker: the timing-only CLI wrote the right artifact but exited nonzero because `main()` only returned success for `status: ok`. The fix changes the CLI to return success for `status in {"ok", "timing_only"}` and adds a regression test for `--skip-validation`.

Compile check:

```text
python3 -m py_compile scripts/goal839_baseline_artifact_schema.py scripts/goal839_robot_pose_count_baseline.py tests/goal839_local_baseline_collectors_test.py
```

Result: OK

## Next Step

Run one real Linux 200k-pose timing-only chunk. If it completes quickly, update Goal1085/Goal1086 to formalize separate validation and timing chunk sets.
