# Goal1296 v1.5 Prepared Scene Session Evidence Plan

Date: 2026-05-05

## Purpose

Use the still-running RTX pod to validate Goal1295 against real OptiX. The
Goal1294 pod evidence showed that any-hit/count queries are fast and scene
preparation dominates. Goal1295 added a reusable prepared scene API; Goal1296
collects evidence that one prepared scene can serve multiple ray batches.

## Command

```bash
PYTHONPATH=src:. python3 scripts/goal1296_v1_5_prepared_scene_session_evidence.py \
  --copies 256 \
  --query-repeats 100 \
  --output docs/reports/goal1296_v1_5_prepared_scene_session_pod_results/session_evidence.json
```

## Expected Artifact

`session_evidence.json` should record:

- one source commit;
- fixture and batch counts;
- two query batches against one prepared scene;
- CPU expected count per batch;
- `all_batches_match_cpu: true`;
- `scene_prepare_paid_once: true`;
- `scene_prepare_sec_this_batch: 0.0` for each batch;
- no public wording authorization.

## Boundary

Internal v1.5 evidence only. No public speedup wording, whole-app claim, public
release claim, or Vulkan/HIPRT/Apple RT implementation before v2.1.

## Local Verification

Passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1296_v1_5_prepared_scene_session_evidence_test \
  tests.goal1295_v1_5_generic_prepared_scene_session_test
```

Result: 7 tests OK.

```bash
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal1296_v1_5_prepared_scene_session_evidence.py \
  tests/goal1296_v1_5_prepared_scene_session_evidence_test.py
```

Result: OK.

Broader v1.5/v1.4 focused regression passed 127 tests OK.
