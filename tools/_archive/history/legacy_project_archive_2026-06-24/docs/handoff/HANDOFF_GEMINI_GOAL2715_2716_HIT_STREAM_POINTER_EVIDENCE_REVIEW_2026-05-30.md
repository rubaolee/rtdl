# Handoff: Gemini Review for Goal2715/Goal2716 Hit-Stream Pointer Evidence

Please perform an independent read-only review of the latest RTDL v2.5 RayDB native device hit-stream handoff evidence.

## Context

The earlier v2.5 reviews argued that Goal2685 was only a contract/host-bridge milestone until native OptiX device hit-stream columns were exercised on real CUDA hardware and the Torch/Triton carrier path proved whether it preserved pointers or silently copied.

Recent work:

- Goal2714 added runtime `torch_carrier_execution` metadata.
- Goal2715 ran a full RTX A5000 pod grid proving native device hit-stream columns, host-row bridge bypass, same-pointer carrier evidence, correctness, and nonzero RT traversal timing.
- Goal2716 cleaned an evidence-field contradiction: the planning adapter still says `adapter_execution_proven_on_hardware = false`, but executed CUDA carrier metadata now says `adapter_execution_proven_on_hardware = true` only when same-pointer CUDA evidence is observed.

## Files To Review

- `docs/reports/goal2715_raydb_native_device_hit_stream_pointer_pod_evidence_2026-05-30.md`
- `docs/reports/goal2715_pod_artifacts/goal2715_raydb_native_device_hit_stream_pointer_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2716_pod_artifacts/goal2716_hit_stream_carrier_execution_flag_smoke_pod_69_30_85_171_2026-05-30.json`
- `src/rtdsl/hit_stream_handoff.py`
- `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py`
- `tests/goal2715_raydb_native_device_hit_stream_pointer_pod_evidence_test.py`
- `tests/goal2708_hit_stream_cuda_array_torch_carrier_adapter_test.py`

## Review Questions

1. Does the evidence support the narrow claim that the RayDB native OptiX device-column path bypasses host hit-row construction?
2. Does the evidence support the narrow claim that the CUDA-array-interface/DLPack Torch carrier preserved the same device pointer during execution?
3. Are the claim boundaries still honest, especially `true_zero_copy_authorized = false`, `no_public_speedup_claim = true`, and no broad speedup wording?
4. Are the performance results interpreted correctly as mixed wall-clock results, not broad speedup?
5. Are there metadata inconsistencies, missing tests, or artifact weaknesses that should block using Goal2715/2716 as internal v2.5 evidence?

## Required Output

Write your review to:

`docs/reviews/goal2717_gemini_review_goal2715_2716_hit_stream_pointer_evidence_2026-05-30.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is a review task only. Do not edit source code. If you recommend changes, list them as findings.
