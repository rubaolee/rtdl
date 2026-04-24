# Goal888 External Review Request

Please review Goal887 + Goal888 as a combined local-readiness package and
return `ACCEPT` or `BLOCK`.

Files to inspect:

- `scripts/goal887_prepared_decision_phase_profiler.py`
- `scripts/goal888_road_hazard_native_optix_gate.py`
- `scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `scripts/goal824_pre_cloud_rtx_readiness_gate.py`
- `src/rtdsl/app_support_matrix.py`
- `docs/rtx_cloud_single_session_runbook.md`
- `docs/reports/goal886_rtx_cloud_start_packet_2026-04-24.md`
- `docs/reports/goal887_prepared_decision_phase_profiler_2026-04-24.md`
- `docs/reports/goal888_road_hazard_and_deferred_readiness_refresh_2026-04-24.md`
- `tests/goal887_prepared_decision_phase_profiler_test.py`
- `tests/goal888_road_hazard_native_optix_gate_test.py`

Review questions:

1. Do the four prepared-decision apps now have a real phase-profiler JSON
   artifact contract instead of raw app CLI commands?
2. Does road hazard now have a concrete deferred native OptiX gate?
3. Is it technically correct to mark road hazard, segment hit-count, polygon
   overlap, and polygon Jaccard as `needs_real_rtx_artifact` rather than still
   needing local interface/native gate packaging?
4. Does the updated deferred batch cover all 11 current deferred targets without
   overstating any as public speedup claims?

Local verification:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal888_road_hazard_native_optix_gate_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal887_prepared_decision_phase_profiler_test
```

Result: `33 tests OK`.

