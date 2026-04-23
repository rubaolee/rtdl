# Goal841 Linux Robot Baseline Collection Request

Repo: `/Users/rl2025/rtdl_python_only`
Branch: `codex/rtx-cloud-run-2026-04-22`
Date: `2026-04-23`

## Purpose

Collect the two remaining active robot RT baseline artifacts on Linux, not on macOS.

Reason:

- The active robot baseline pair still requires exact large-scale traversal at:
  - `pose_count=200000`
  - `obstacle_count=1024`
  - `iterations=10`
- macOS local collection is technically correct but too expensive for an efficient unattended batch.
- Linux is the right batch host for these remaining active robot artifacts.

## Required Artifacts

1. `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_cpu_oracle_pose_count_2026-04-23.json`
2. `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_embree_anyhit_pose_count_or_equivalent_compact_summary_2026-04-23.json`

## Exact Commands

1. CPU oracle:

```bash
cd /Users/rl2025/rtdl_python_only
python3 scripts/goal839_robot_pose_count_baseline.py \
  --backend cpu \
  --pose-count 200000 \
  --obstacle-count 1024 \
  --iterations 10 \
  --output-json docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_cpu_oracle_pose_count_2026-04-23.json
```

2. Embree compact-summary path:

```bash
cd /Users/rl2025/rtdl_python_only
python3 scripts/goal839_robot_pose_count_baseline.py \
  --backend embree \
  --pose-count 200000 \
  --obstacle-count 1024 \
  --iterations 10 \
  --output-json docs/reports/goal835_baseline_robot_collision_screening_prepared_pose_flags_embree_anyhit_pose_count_or_equivalent_compact_summary_2026-04-23.json
```

## Validation After Collection

Run:

```bash
cd /Users/rl2025/rtdl_python_only
python3 scripts/goal836_rtx_baseline_readiness_gate.py \
  --output-json docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.json \
  --output-md docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.generated.md
```

Expected change:

- `valid_artifact_count` should increase by `2`
- `missing_artifact_count` should decrease by `2`
- No invalid artifacts should appear

## Evidence Files

- Robot-only plan JSON:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal841_robot_only_local_baseline_run_plan_2026-04-23.json`
- Robot-only plan markdown:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal841_robot_only_local_baseline_run_plan_2026-04-23.md`
- Current local progress report:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal840_local_baseline_collection_progress_2026-04-23.md`

## Boundary

- This request is only for the two active robot baseline artifacts.
- Do not collect deferred-app baselines in this batch.
- Do not make any RTX speedup claim from this collection step.
