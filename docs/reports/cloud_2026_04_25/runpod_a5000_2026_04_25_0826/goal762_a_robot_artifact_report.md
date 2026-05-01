# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/Users/rl2025/rtdl_python_only/docs/reports/goal761_group_a_robot_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `7f569829fbad00f9bfa58e758b0fc4ee0324b410`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| robot_collision_screening | prepared_pose_flags | ok | ok | 0.000894 | 0.000362 |  | 0.000000 | not continuous collision detection, full robot kinematics, or mesh-engine replacement |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| robot_collision_screening | prepared_pose_flags | ok | prepared scalar colliding-pose count for the same poses, edges, obstacles, and iteration policy | scalar pose-count collision screening only; not full robot planning, kinematics, CCD, or witness-row output |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
