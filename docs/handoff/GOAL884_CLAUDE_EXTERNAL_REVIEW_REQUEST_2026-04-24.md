# Goal884 Claude External Review Request

Please review the bounded Goal884 segment/polygon native OptiX local pre-cloud
gate package and return `ACCEPT` or `BLOCK`.

Scope to inspect:

- `docs/reports/goal884_segment_polygon_native_gate_local_precloud_2026-04-24.md`
- `docs/reports/goal884_segment_polygon_gate_local_non_strict_2026-04-24.json`
- `docs/reports/goal884_segment_polygon_gate_local_strict_2026-04-24.json`
- `docs/reports/goal884_pre_cloud_readiness_after_goal879_883_2026-04-24.json`
- `tests/goal884_segment_polygon_precloud_gate_report_test.py`

Review questions:

1. Does the report correctly state that local strict segment/polygon OptiX
   promotion is blocked only by missing `librtdl_optix` on macOS, not by a
   discovered correctness failure?
2. Does it preserve the claim boundary: no promotion claim and no speedup
   claim before a real RTX Linux artifact exists?
3. Do the tests correctly guard the local artifacts and the pre-cloud readiness
   JSON without overstating readiness?
4. Is it appropriate to keep the next pod start batched rather than restarting
   cloud per app?

Local verification already run:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal884_segment_polygon_precloud_gate_report_test \
  tests.goal807_segment_polygon_optix_mode_gate_test \
  tests.goal808_segment_polygon_app_native_mode_propagation_test
```

Result: `11 tests OK`.

```bash
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal884_pre_cloud_readiness_after_goal879_883_2026-04-24.json
```

Result: `valid: true`.

