# Goal832 External Consensus Review Request

Date: 2026-04-23

Please independently review Goal832 in:

`/Users/rl2025/rtdl_python_only`

## Required Verdict

Write one of:

- `ACCEPT`
- `BLOCK`

If `BLOCK`, list exact blocking files and fixes.

## Review Question

Does Goal832 correctly add comparable baseline-review contracts to the RTX
cloud benchmark manifest without starting cloud, promoting deferred apps, or
authorizing public RTX speedup claims?

## Files To Read

Report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal832_rtx_baseline_review_contract_2026-04-23.md`

Code:

- `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py`

Tests:

- `/Users/rl2025/rtdl_python_only/tests/goal759_rtx_cloud_benchmark_manifest_test.py`

Context:

- `/Users/rl2025/rtdl_python_only/docs/reports/nvidia_rt_core_work_in_progress_report_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md`
- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/rtx_cloud_single_session_runbook.md`

## Evidence Commands Already Run

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal759_rtx_cloud_benchmark_manifest_test
```

Result: `8 tests OK`.

```text
PYTHONPATH=src:. python3 scripts/goal759_rtx_cloud_benchmark_manifest.py --output-json /tmp/goal832_manifest_check.json
```

Result: manifest emitted `5` active entries and `3` deferred entries, each with
`baseline_review_contract`.

## Boundaries To Check

- No cloud pod should be started.
- Goal832 must not authorize public RTX speedup claims.
- Active entries must require comparable baselines before public claims.
- Deferred entries must remain deferred.
- Baseline contracts must prevent comparing scalar/prepared RTX sub-paths
  against whole-app, row-output, validation-included, or different-result-mode
  baselines.
