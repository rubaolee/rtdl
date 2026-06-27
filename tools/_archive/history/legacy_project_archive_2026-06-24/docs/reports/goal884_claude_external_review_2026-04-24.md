# Goal884 Claude External Review

Date: 2026-04-24
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## Review Questions

### 1. Strict gate blocked only by missing `librtdl_optix`, not a correctness failure?

Yes. Both `goal884_segment_polygon_gate_local_strict_2026-04-24.json` and the non-strict JSON record `"error_type": "FileNotFoundError"` and `"error": "librtdl_optix not found"` for both `optix_host_indexed` and `optix_native`. The CPU Python reference ran successfully with `"status": "ok"` and produced a valid row digest. There is no correctness failure anywhere in the artifact set.

### 2. Claim boundary preserved — no promotion or speedup claim before a real RTX Linux artifact?

Yes. The boundary is stated at three independent layers:

- The narrative report: "not a segment/polygon promotion claim and not a speedup claim"
- Both gate JSONs: `"boundary": "...does not authorize a public NVIDIA RT-core speedup claim by itself."`
- The pre-cloud readiness JSON: `"boundary": "Local readiness only; does not start cloud and does not authorize speedup claims."`

The report also explicitly requires a real RTX Linux host with `librtdl_optix` built before promotion can proceed.

### 3. Tests correctly guard artifacts without overstating readiness?

Yes. `goal884_segment_polygon_precloud_gate_report_test.py` covers:

- `test_report_preserves_local_only_boundary`: asserts "local pre-cloud readiness artifact", "not a segment/polygon promotion claim", "not a speedup claim", and "Do not restart the pod per app" — all present in the report.
- `test_local_gate_artifacts_record_expected_optix_unavailability`: confirms `strict.status == "fail"`, `non_strict.status == "non_strict_recorded_gaps"`, and that OptiX failures are `FileNotFoundError` for `librtdl_optix` — not a passing claim.
- `test_pre_cloud_gate_remains_valid`: confirms `valid: true` locally while asserting "does not start cloud" in the boundary field.

No test passes a condition that would overstate cloud or promotion readiness.

### 4. Batched pod start appropriate rather than per-app restart?

Yes. Consolidating active Goal759/Goal761 entries plus the segment/polygon native gate into one pod run is the correct cost-efficiency posture at this stage. The policy is internally consistent: local readiness gates pass first, then one pod run collects all artifacts, then it shuts down. The test enforces "Do not restart the pod per app" as a text contract in the report.

## Summary

All four review questions pass. The package is internally consistent, claim boundaries are sound and multi-layered, tests guard without overstating, and the cloud-cost policy is appropriate. No blocking issues found.
