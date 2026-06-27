# Goal 523: v0.8 Linux Public Command Validation

Date: 2026-04-17

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goal522 refreshed the local macOS audit after the v0.8 scope expanded to six
apps. Goal523 validates the same public tutorial/example command surface on the
canonical Linux host with all RTDL runtime backends available in a fresh synced
checkout.

## Host

- host alias: `lestat-lx1`
- hostname: `lx1`
- checkout: `/home/lestat/work/rtdl_goal523_v08_linux`
- GPU: NVIDIA GeForce GTX 1070
- Python: `3.12.3`

Backend probe after building missing checkout-local libraries:

```text
embree_version (4, 3, 0)
optix_version (9, 0, 0)
vulkan_version (0, 1, 0)
```

Build commands used in the fresh synced checkout:

```text
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
```

## Command Harness

Command:

```text
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py \
  --machine linux-goal523-v08-six-app-scope \
  --output docs/reports/goal523_linux_public_command_check_2026-04-17.json
```

Copied artifact:

- `docs/reports/goal523_linux_public_command_check_2026-04-17.json`

Summary:

```json
{
  "passed": 88,
  "failed": 0,
  "skipped": 0,
  "total": 88
}
```

Backend status in the artifact:

```json
{
  "cpu_python_reference": true,
  "oracle": true,
  "cpu": true,
  "embree": true,
  "optix": true,
  "vulkan": true
}
```

## v0.8 Six-App Coverage

The public command harness includes the v0.8 app-building examples:

- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_ann_candidate_app.py`
- `examples/rtdl_outlier_detection_app.py`
- `examples/rtdl_dbscan_clustering_app.py`
- `examples/rtdl_robot_collision_screening_app.py`
- `examples/rtdl_barnes_hut_force_app.py`

For the three new Stage-1 proximity apps, the harness checks public commands on:

- `cpu_python_reference`
- `cpu`
- `embree`
- `optix`
- `vulkan`

Known app-specific gap:

- `examples/rtdl_robot_collision_screening_app.py` is intentionally not exposed
  through Vulkan in the public harness because earlier Goal509 evidence found a
  per-edge hit-count parity issue for that app.

## Honesty Boundary

This is public command validation, not a performance claim.

It proves that the public tutorial/example command surface runs on Linux with
all RTDL backends available in this checkout. It does not claim that the new
ANN, outlier, or DBSCAN apps are faster than mature non-RT libraries.

Performance comparison for the new Stage-1 proximity apps remains a separate
future gate.

## Verdict

Linux public command status: **ACCEPT**.

No Linux public-command blocker is known from this validation.

## AI Consensus

- Claude review: `docs/reports/goal523_claude_review_2026-04-17.md`, verdict
  `ACCEPT`.
- Gemini Flash review:
  `docs/reports/goal523_gemini_review_2026-04-17.md`, verdict `ACCEPT`.
- Codex review: accepted after explicitly restating the known robot Vulkan gap
  in this report.
