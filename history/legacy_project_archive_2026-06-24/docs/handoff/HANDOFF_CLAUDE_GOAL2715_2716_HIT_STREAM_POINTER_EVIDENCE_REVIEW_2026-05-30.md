# Handoff: Claude Review for Goal2715/Goal2716 Hit-Stream Pointer Evidence

Please perform a fresh independent read-only review of the RTDL v2.5 RayDB native device hit-stream handoff evidence.

## Files To Review

- `docs/reports/goal2715_raydb_native_device_hit_stream_pointer_pod_evidence_2026-05-30.md`
- `docs/reports/goal2715_pod_artifacts/goal2715_raydb_native_device_hit_stream_pointer_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2716_pod_artifacts/goal2716_hit_stream_carrier_execution_flag_smoke_pod_69_30_85_171_2026-05-30.json`
- `src/rtdsl/hit_stream_handoff.py`
- `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py`
- `tests/goal2715_raydb_native_device_hit_stream_pointer_pod_evidence_test.py`
- `tests/goal2708_hit_stream_cuda_array_torch_carrier_adapter_test.py`

## Questions

1. Does the evidence prove the narrow internal claim that native OptiX device hit-stream columns bypass host hit-row construction for the RayDB path?
2. Does the evidence prove the narrow internal claim that the executed Torch carrier preserved same device pointers for primitive ids, group ids, and values?
3. Are the boundaries still honest: no public true-zero-copy claim, no broad speedup claim, and mixed performance interpreted as mixed?
4. Is the `adapter_execution_proven_on_hardware` split correct: false in the planning adapter, true only in executed CUDA carrier metadata when same-pointer evidence is observed?
5. What must be fixed before this contract can be generalized to other v2.5 benchmark apps?

## Required Output

Write your review to:

`docs/reviews/goal2718_claude_review_goal2715_2716_hit_stream_pointer_evidence_2026-05-30.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is a review task only. Do not edit source code.
