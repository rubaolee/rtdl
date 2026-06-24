# Goal831 External Consensus Review Request

Date: 2026-04-23

Please independently review Goal831 in:

`/Users/rl2025/rtdl_python_only`

## Required Verdict

Write one of:

- `ACCEPT`
- `BLOCK`

If `BLOCK`, list exact blocking files and fixes.

## Review Question

Does Goal831 correctly prepare the deferred segment/polygon native OptiX gate
for a future single-session RTX cloud run without promoting it to an active
public RTX speedup claim?

## Files To Read

Report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal831_segment_polygon_native_artifact_contract_2026-04-23.md`

Code:

- `/Users/rl2025/rtdl_python_only/scripts/goal807_segment_polygon_optix_mode_gate.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal762_rtx_cloud_artifact_report.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal824_pre_cloud_rtx_readiness_gate.py`

Tests:

- `/Users/rl2025/rtdl_python_only/tests/goal831_segment_polygon_native_artifact_contract_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal807_segment_polygon_optix_mode_gate_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal762_rtx_cloud_artifact_report_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal761_rtx_cloud_run_all_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal824_pre_cloud_rtx_readiness_gate_test.py`

Context docs:

- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md`
- `/Users/rl2025/rtdl_python_only/docs/rtx_cloud_single_session_runbook.md`

Latest readiness artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json`

## Evidence Commands Already Run

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal831_segment_polygon_native_artifact_contract_test tests.goal807_segment_polygon_optix_mode_gate_test tests.goal762_rtx_cloud_artifact_report_test tests.goal761_rtx_cloud_run_all_test tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `19 tests OK`.

```text
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json
```

Result: `valid: true`.

## Boundaries To Check

- No cloud pod should be started.
- Segment/polygon must remain a deferred readiness gate, not an active manifest
  entry.
- The new Goal807 contract must be machine-readable.
- The Goal762 analyzer must understand segment/polygon native-gate artifacts.
- Missing/malformed claim contracts must still fail closed via Goal827 logic.
- No pair-row any-hit, road-hazard whole-app, default public app, or public RTX
  speedup claim should be made.
