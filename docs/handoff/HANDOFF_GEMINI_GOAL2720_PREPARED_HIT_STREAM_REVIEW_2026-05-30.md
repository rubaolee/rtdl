# Handoff: Gemini Review for Goal2720 Prepared Hit-Stream Steady-State Evidence

Please perform an independent read-only review of Goal2720 and Goal2722.

## Context

Goal2720 added and measured a prepared steady-state RayDB-style v2.5 backend:

`paper_rt_optix_device_hit_stream_triton_prepared`

Goal2722 then extended that evidence to larger row counts on the same RTX A5000 pod.

The goal is not to claim true zero-copy, public whole-app speedup, or RayDB paper reproduction. The goal is narrower: verify that prepared app-owned setup reuse makes the v2.5 native OptiX device hit-stream + typed payload gather + Triton continuation path materially faster than the unprepared v2.5 path on the recorded pod smoke and large-scale cases, while preserving the app-agnostic native-engine boundary and the no-overclaim metadata.

## Files to Inspect

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py`
- `docs/reports/goal2720_raydb_prepared_device_hit_stream_steady_state_2026-05-30.md`
- `docs/reports/goal2720_pod_artifacts/goal2720_raydb_prepared_device_hit_stream_smoke_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2722_raydb_prepared_device_hit_stream_large_scale_pod_evidence_2026-05-30.md`
- `docs/reports/goal2722_pod_artifacts/goal2722_raydb_prepared_device_hit_stream_large_pod_69_30_85_171_2026-05-30.json`
- `tests/goal2720_raydb_prepared_device_hit_stream_steady_state_test.py`
- `tests/goal2720_raydb_prepared_device_hit_stream_pod_evidence_test.py`
- `tests/goal2722_raydb_prepared_device_hit_stream_large_scale_pod_evidence_test.py`

Helpful prior evidence:

- `docs/reports/goal2715_raydb_native_device_hit_stream_pointer_pod_evidence_2026-05-30.md`
- `docs/reports/goal2719_native_hit_stream_materialization_proof_metadata_cleanup_2026-05-30.md`

## Review Questions

1. Does the prepared backend reuse app-owned setup (`prepare_typed_payload_columns` / OptiX static scene) without introducing app-specific native engine logic?
2. Do the pod artifacts support the reported speedups versus the unprepared v2.5 backend for the smoke and large-scale cases?
3. Do the metadata and report preserve the claim boundary, especially `true_zero_copy_authorized = false`, no broad speedup claim, and no RayDB reproduction claim?
4. Are there remaining risks or missing tests before using this as v2.5 internal evidence?

## Required Output

Write the review to:

`docs/reviews/goal2721_gemini_review_goal2720_prepared_hit_stream_steady_state_2026-05-30.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please state explicitly that this is an independent Gemini review distinct from Codex.
