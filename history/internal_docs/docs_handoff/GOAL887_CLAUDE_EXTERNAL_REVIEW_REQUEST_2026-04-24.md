# Goal887 Claude External Review Request

Please review Goal887 and return `ACCEPT` or `BLOCK`.

Files to inspect:

- `scripts/goal887_prepared_decision_phase_profiler.py`
- `tests/goal887_prepared_decision_phase_profiler_test.py`
- `scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
- `docs/reports/goal887_prepared_decision_phase_profiler_2026-04-24.md`
- `docs/reports/goal887_pre_cloud_readiness_after_profiler_manifest_2026-04-24.json`

Review questions:

1. Does Goal887 correctly replace raw app commands for Hausdorff, ANN,
   facility, and Barnes-Hut deferred entries with a phase-profiler JSON
   artifact contract?
2. Does the profiler preserve claim boundaries for each sub-path?
3. Are dry-run and manifest tests sufficient for local readiness before a real
   RTX run?
4. Does the pre-cloud gate remain valid without starting cloud?

Local verification:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal887_prepared_decision_phase_profiler_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `17 tests OK`.

