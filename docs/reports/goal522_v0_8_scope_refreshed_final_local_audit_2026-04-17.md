# Goal 522: v0.8 Scope-Refreshed Final Local Audit

Date: 2026-04-17

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

The previous v0.8 final local audit predated Goal520 and Goal521. After the
accepted workload-scope gate, v0.8 now has six app-building examples:

- Hausdorff distance
- ANN candidate search
- outlier detection
- DBSCAN clustering
- robot collision screening
- Barnes-Hut force approximation

Goal522 refreshes the local release evidence so the final audit reflects the
current six-app scope, public docs, public command harness, and history state.

## Scope Inputs

- Goal519: `docs/reports/goal519_rt_workload_universe_from_2603_28771_2026-04-17.md`
- Goal520: `docs/reports/goal520_v0_8_stage1_proximity_apps_2026-04-17.md`
- Goal521: `docs/reports/goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md`
- ITRE model: `docs/rtdl/itre_app_model.md`
- v0.8 tutorial: `docs/tutorials/v0_8_app_building.md`
- release-facing examples: `docs/release_facing_examples.md`

## Local Test Evidence

Full local unittest discovery:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 61.959s
OK
```

Focused current-scope validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal520_dbscan_clustering_app_test \
  tests.goal521_v0_8_workload_scope_decision_matrix_test \
  tests.goal518_v0_8_final_local_release_audit_test -v
```

Result:

```text
Ran 10 tests in 0.350s
OK
```

Static checks:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_ann_candidate_app.py \
  examples/rtdl_outlier_detection_app.py \
  examples/rtdl_dbscan_clustering_app.py \
  tests/goal520_dbscan_clustering_app_test.py \
  tests/goal521_v0_8_workload_scope_decision_matrix_test.py

git diff --check
```

Both passed.

## Public Command Harness Evidence

Command:

```text
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py \
  --machine macos-goal522-v08-scope-refresh \
  --output docs/reports/goal522_macos_public_command_check_2026-04-17.json
```

Result:

```json
{
  "passed": 62,
  "failed": 0,
  "skipped": 26,
  "total": 88
}
```

Backend probe in that artifact:

```json
{
  "cpu_python_reference": true,
  "oracle": true,
  "cpu": true,
  "embree": true,
  "optix": false,
  "vulkan": false
}
```

This is a macOS-local public command check. OptiX and Vulkan are correctly
unavailable on this host and are skipped by the harness.

## Documentation Audit Readout

Public docs now name the six-app v0.8 scope and preserve the honesty boundary:

- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/release_facing_examples.md`
- `docs/rtdl/itre_app_model.md`
- `docs/rtdl_feature_guide.md`
- `docs/tutorials/v0_8_app_building.md`
- `examples/README.md`

The docs explicitly state:

- v0.8 uses existing RTDL kernels plus Python orchestration
- ANN is candidate-subset kNN reranking, not a full ANN index
- outlier detection is density-threshold labeling, not a full anomaly framework
- DBSCAN uses RTDL neighbor rows plus Python expansion, not a built-in clustering primitive
- robot Vulkan remains rejected for that app until hit-count parity is fixed
- Barnes-Hut remains bounded one-level candidate generation plus Python force logic

## Flow Audit Readout

Goal521 is the release-scope gate that prevents uncontrolled app expansion.
Every paper workload has a decision and reason:

- do now in v0.8
- already covered
- defer to later focused version
- out-of-scope until reframed

Goal520 and Goal521 both have Claude, Gemini, and Codex consensus artifacts.

## Verdict

Local status: **ACCEPT**.

No local code, doc, or flow blocker is known from this audit. The remaining
honesty boundary is that this is a local/macOS release audit. Linux backend
performance closure for the new Stage-1 proximity apps has not been claimed.

## AI Consensus

- Claude review: `docs/reports/goal522_claude_review_2026-04-17.md`, verdict
  `ACCEPT`.
- Gemini Flash review:
  `docs/reports/goal522_gemini_review_2026-04-17.md`, verdict `ACCEPT`.
- Codex review: accepted. The audit remains a local/macOS release audit and
  does not claim Linux backend performance closure for the new Stage-1
  proximity apps.
