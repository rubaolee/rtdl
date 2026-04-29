# Goal1089 Robot Chunk Pose-ID Offset Update

Date: 2026-04-29

## Status

Implemented.

## Change

The robot chunked Embree baseline now supports distinct pose-id ranges per
chunk:

- `examples/rtdl_robot_collision_screening_app.make_scaled_case(...)` accepts
  `pose_id_start`, defaulting to `1`.
- `scripts/goal839_robot_pose_count_baseline.py` accepts `--pose-id-start` and
  records it in `benchmark_scale`.
- `scripts/goal1085_robot_chunked_embree_baseline_runner.sh` passes
  `--pose-id-start $(( chunk_index * 200000 + 1 ))`.
- `scripts/goal1086_robot_chunked_embree_baseline_intake.py` validates that
  each chunk's `pose_id_start` matches its chunk index.

## Reason

Before this update, the chunked 36M-pose baseline plan represented total work
but repeated the first 200k-pose fixture in every chunk. That was usable only as
a weak same-total-work engineering baseline. With pose-id offsets, the chunked
baseline represents the actual intended pose-id range across 36M poses while
remaining resumable and memory bounded.

## Boundary

Goal1089 improves the robot baseline contract only. It does not run the heavy
baseline, does not authorize release, does not change public wording, and does
not authorize public RTX speedup claims.
