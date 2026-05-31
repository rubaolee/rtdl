# Goal2839: RTNN Same-Stream Runner Mode

Date: 2026-05-31

Status: implemented locally and pod-probed; pending external review at initial write

## Purpose

Goal2837 made the low-level prepared graph API self-describing. Goal2839 moves that capability into an app-facing benchmark runner mode so a user does not need to call runtime internals directly.

The new explicit result mode is:

```text
ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32
```

It lives in `scripts/goal2348_rtnn_v2_2_external_runner.py` and selects:

- prepared OptiX fixed-radius 3-D search structure;
- prepared query columns;
- heterogeneous batched ranked-summary aggregate requests;
- static CUDA graph replay;
- the bounded same-stream CuPy consumer for graph-owned native partial rows;
- app-facing `same_stream_entrypoint_metadata`.

## Implementation

Updated runner behavior:

- adds the new result mode to the CLI;
- prepares graph handles for both direct graph replay and same-stream graph consumer modes;
- calls `replay_same_stream_device_partials_summary_cupy()` for the new mode;
- stores `same_stream_entrypoint_metadata` in the returned JSON payload;
- marks `contract.same_stream_partner_consumer` and `claim_boundary.same_stream_partner_consumer`;
- preserves the existing direct CUDA graph replay mode.

The metadata records:

- plan status: `accepted_preview`;
- resolved partner: `cupy_conformance`;
- fallback required: `false`;
- stream ordering: `same_cuda_stream`;
- host scalar read before consumer: `false`.

## Pod Probe

Pod used:

```text
ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Artifact files:

- `docs/reports/goal2839_rtnn_same_stream_runner_pod/goal2839_summary.json`
- `docs/reports/goal2839_rtnn_same_stream_runner_pod/goal2839_same_stream_runner.json`

Probe shape:

- 8192 deterministic uniform 3-D points;
- radius `0.08`;
- base `k_max=8`;
- 3 heterogeneous aggregate requests;
- 2 repeats;
- result mode `ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32`.

Summary:

```text
ok: true
row_count: 8192
first_entrypoint_plan_status: accepted_preview
first_entrypoint_resolved_partner: cupy_conformance
first_entrypoint_fallback_required: false
host_scalar_read_before_consumer: false
same_stream_partner_consumer: true
public_speedup_claim_authorized: false
```

## Boundary

This is an app-facing result mode and metadata traceability improvement.

It is not a public speedup claim. It does not claim that RTDL beats RTNN, CuPy, or any paper implementation. It does not claim broad true zero-copy, arbitrary partner continuation, or v2.5 release readiness.

## Codex Verdict

`accept-with-boundary`

Goal2839 makes the v2.5 same-stream primitive-payload continuation usable from a real benchmark runner while keeping the claim boundary narrow and inspectable.
