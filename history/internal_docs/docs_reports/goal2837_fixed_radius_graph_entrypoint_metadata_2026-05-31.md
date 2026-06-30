# Goal2837: Fixed-Radius Graph Entrypoint Metadata

Date: 2026-05-31

Status: implemented locally, pending external review at initial write

## Purpose

Goal2835 made primitive-payload planner decisions attachable to continuation entrypoints. Goal2837 applies that contract to the real same-stream graph API introduced by Goal2829:

`PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D.replay_same_stream_device_partials_summary_cupy()`

The goal is simple: when this API launches the native CUDA graph and reduces graph-owned partial rows with the bounded same-stream CuPy consumer, its returned metadata should also say why that continuation was accepted.

## Implementation

Updated `src/rtdsl/optix_runtime.py`:

- imports `describe_primitive_payload_partner_continuation_entrypoint`;
- builds the existing fixed-radius graph partial descriptor once;
- records `primitive_payload_continuation_entrypoint`;
- records the nested `primitive_payload_continuation_plan`;
- surfaces `primitive_payload_planner_fallback_required` and `primitive_payload_planner_fallback_reasons`.

The attached plan uses:

- operation: `hit_stream_grouped_ray_id_primitive_i64`;
- partner request: `cupy`;
- resolved partner: `cupy_conformance`;
- plan status: `accepted_preview`;
- runtime action: `execute_preview_with_explicit_descriptor_plan`;
- execution status: `completed_same_stream_consumer`.

## Boundary

This does not change native execution, CuPy reduction code, stream synchronization behavior, block sizing, or final host materialization. It is metadata plumbing over the already-proven bounded same-stream consumer.

This does not authorize:

- broad true-zero-copy claims;
- public performance claims;
- arbitrary partner continuation claims;
- RT traversal replacement;
- v2.5 release readiness.

## Validation

New test:

- `tests.goal2837_fixed_radius_graph_entrypoint_metadata_test`

Focused checks:

- source wiring exists in `optix_runtime.py`;
- pod artifact records `accepted_preview`, resolved `cupy_conformance`, zero fallback, and no host scalar read before the consumer;
- report/review/consensus preserve claim boundaries.

## Codex Verdict

`accept-with-boundary`

Goal2837 is a real-entrypoint traceability improvement. It makes the same-stream graph API self-describing for v2.5 planner/execution audits, but it remains a bounded preview path.
