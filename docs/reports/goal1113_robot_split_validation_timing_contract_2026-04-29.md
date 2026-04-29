# Goal1113 Robot Split Validation/Timing Contract

Date: 2026-04-29

## Purpose

Goal1110 showed the old Robot Embree baseline contract was too slow because every production chunk repeated full CPU-oracle validation. Goal1111 and Goal1112 proved timing-only chunks are feasible. Goal1113 formalizes the split contract.

## Changes

Files changed:

- `scripts/goal1085_robot_chunked_embree_baseline_packet.py`
- `scripts/goal1085_robot_chunked_embree_baseline_runner.sh`
- `scripts/goal1086_robot_chunked_embree_baseline_intake.py`
- `tests/goal1085_robot_chunked_embree_baseline_packet_test.py`
- `tests/goal1086_robot_chunked_embree_baseline_intake_test.py`

Runner behavior:

- Default mode remains validated chunks: `chunk_<index>.json`.
- `RTDL_GOAL1085_TIMING_ONLY=1` writes timing chunks: `timing_chunk_<index>.json`.
- Timing-only mode passes `--skip-validation` to `goal839_robot_pose_count_baseline.py`.
- Existing resume controls still apply: `RTDL_GOAL1085_START_CHUNK`, `RTDL_GOAL1085_END_CHUNK`, `RTDL_GOAL1085_SKIP_EXISTING`.

Intake behavior:

- Legacy mode remains accepted: all 180 `chunk_<index>.json` artifacts with `correctness_parity: true`.
- Split mode is accepted when at least one validation chunk is present and all 180 `timing_chunk_<index>.json` artifacts are present, scale-correct, and marked `status: timing_only`.
- Timing phase sums use timing chunks when present.
- No public speedup claim is authorized in either mode.

## Verification

Command:

```text
PYTHONPATH=src:. python3 scripts/goal1085_robot_chunked_embree_baseline_packet.py
PYTHONPATH=src:. python3 scripts/goal1086_robot_chunked_embree_baseline_intake.py
PYTHONPATH=src:. python3 -m unittest tests.goal1085_robot_chunked_embree_baseline_packet_test tests.goal1086_robot_chunked_embree_baseline_intake_test tests.goal839_local_baseline_collectors_test -v
```

Result:

```text
Ran 16 tests in 0.701s
OK
```

## Next Step

Run the split contract on Linux:

1. Generate or keep at least one validation chunk.
2. Run all 180 timing chunks with `RTDL_GOAL1085_TIMING_ONLY=1`.
3. Run Goal1086 intake.
4. Seek 2+ AI review before using the Robot baseline in any comparison.

## Boundary

This goal updates runner/intake mechanics only. It does not authorize public RTX speedup claims, release wording, or front-page wording.
