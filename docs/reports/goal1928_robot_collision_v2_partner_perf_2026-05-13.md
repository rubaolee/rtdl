# Goal1928 - Robot Collision v2 Partner Perf Harness

Status: harness-ready-pod-needed

Date: 2026-05-13

## Purpose

Goal1928 turns the Goal1927 robot collision partner adapter into a pod-ready
same-contract performance harness for the `robot_collision_screening` app row.

The runner is:

`scripts/goal1928_robot_collision_v2_partner_perf.py`

## Comparison

The harness compares:

- v1.8 prepared OptiX pose flags through
  `scripts/goal760_optix_robot_pose_flags_phase_profiler.py`;
- v2 prepared OptiX partner columns through
  `robot_collision_pose_flags_optix_prepared_partner_device_columns`;
- Torch and CuPy partner paths;
- exact `pose_collision_flags` parity plus scalar `colliding_pose_count` parity
  after reducing partner-owned pose flags.

The RTDL native engine remains app-agnostic. It writes generic ray any-hit flags;
the robot-specific pose reduction is performed in Torch/CuPy.

Exact flag-vector parity is checked outside the timing window so correctness
does not weaken to count-only agreement.

## Pod Command

```bash
PYTHONPATH=src:. python3 scripts/goal1928_robot_collision_v2_partner_perf.py \
  --pose-count 4096 \
  --obstacle-count 256 \
  --partners cupy,torch \
  --repeat 5 \
  --output docs/reports/goal1928_robot_collision_v2_partner_perf_pod.json
```

The command prints `[goal1928]` progress lines for long pod runs.

## Boundaries

This goal does not authorize v2.0 release.

It does not claim broad RT-core speedup or whole-app speedup. It prepares one
app row for the final all-app v1.8 versus v2.0 matrix.

The result should be interpreted with the same care as earlier robot evidence:
small rows can be dispatch/setup dominated, while larger packed-array rows are
the useful performance surface.
