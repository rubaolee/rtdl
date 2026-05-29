# Critical Review Request: RTDL v2.4/v2.5 Partner Work

Status: request for independent external review.

Target commit:

```text
121431432d414ece1dd4e7b95f5e9faa6f80eab5
```

Repository:

```text
https://github.com/rubaolee/rtdl.git
```

## Review Purpose

Please critically review the RTDL v2.4/v2.5 work so far. The main question is
whether the current direction is architecturally sound and whether the
implementation evidence is strong enough to continue toward a Triton-first
partner path.

The intended design boundary is:

- RT traversal stays in RTDL native backends: Embree and OptiX.
- Triton handles generic continuation/reduction/compaction/finalization after
  RT traversal.
- App semantics stay outside the native engine and outside generic primitives.
- Torch may be used as the CUDA tensor carrier for Triton launch, but PyTorch
  is not the v2.5 partner. CuPy should not be the v2.5 partner.
- No public speedup or release wording is allowed unless the exact path has
  reviewed evidence.

Please assume this is a high-bar review. Look for hidden app-specific logic,
overclaimed performance, weak contracts, misleading docs, and missing tests.

## Primary Files To Review

Roadmap and boundary:

- `docs/partner_acceleration_boundaries.md`
- `docs/reports/goal2657_v2_4_v2_5_partner_roadmap_2026-05-27.md`
- `docs/reports/goal2657_v2_4_v2_5_partner_roadmap_3ai_consensus_2026-05-27.md`

v2.4 protocol foundation:

- `src/rtdsl/partner_protocol.py`
- `docs/reports/goal2658_v2_4_partner_protocol_foundation_2026-05-27.md`
- `docs/reports/goal2659_v2_4_benchmark_protocol_integration_2026-05-27.md`
- `docs/reports/goal2660_v2_4_phase_timing_metadata_2026-05-27.md`
- `docs/reports/goal2661_v2_4_completion_gate_2026-05-27.md`

v2.5 generic partner continuation:

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/numba_partner_continuation.py`
- `docs/reports/goal2662_v2_5_partner_continuation_contract_2026-05-27.md`
- `docs/reports/goal2662_v2_5_partner_continuation_3ai_consensus_2026-05-27.md`

Triton preview kernels and adapter front door:

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2676_v2_5_triton_partner_pivot_2026-05-27.md`
- `docs/reports/goal2677_v2_5_triton_segmented_minmax_preview_2026-05-27.md`
- `docs/reports/goal2678_v2_5_triton_compact_mask_preview_2026-05-27.md`
- `docs/reports/goal2679_v2_5_triton_grouped_argmin_preview_2026-05-27.md`
- `docs/reports/goal2680_v2_5_triton_bounded_collect_preview_2026-05-27.md`
- `docs/reports/goal2681_v2_5_triton_partner_adapter_front_door_2026-05-27.md`

GPU validation and first app integration:

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py`
- `scripts/goal2682_v2_5_triton_adapter_front_door_pod_runner.py`
- `scripts/goal2683_raydb_triton_front_door_pod_runner.py`
- `docs/reports/goal2683_v2_5_triton_partner_gpu_validation_2026-05-28.md`
- `docs/reports/artifacts/goal2683_goal2665_low_level_triton_l4.json`
- `docs/reports/artifacts/goal2683_goal2682_adapter_front_door_triton_l4.json`
- `docs/reports/artifacts/goal2683_raydb_triton_front_door_l4.json`

Relevant tests:

- `tests/goal2658_v2_4_partner_protocol_test.py`
- `tests/goal2659_v2_4_benchmark_protocol_integration_test.py`
- `tests/goal2661_v2_4_completion_gate_test.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `tests/goal2663_v2_5_triton_segmented_sum_test.py`
- `tests/goal2665_v2_5_triton_grouped_runner_test.py`
- `tests/goal2669_v2_5_raydb_continuation_plan_test.py`
- `tests/goal2676_v2_5_triton_partner_pivot_test.py`
- `tests/goal2677_v2_5_triton_segmented_minmax_preview_test.py`
- `tests/goal2678_v2_5_triton_compact_mask_preview_test.py`
- `tests/goal2679_v2_5_triton_grouped_argmin_preview_test.py`
- `tests/goal2680_v2_5_triton_bounded_collect_preview_test.py`
- `tests/goal2681_v2_5_triton_partner_adapter_front_door_test.py`
- `tests/goal2682_v2_5_triton_adapter_front_door_runner_test.py`
- `tests/goal2683_v2_5_triton_partner_gpu_validation_test.py`

## Specific Questions

1. Architecture boundary:
   Does the current v2.4/v2.5 design preserve the rule that RT traversal is
   owned by RTDL/Embree/OptiX, generic continuation is owned by Triton, and app
   logic stays outside the engine?

2. App-specific leakage:
   Is there any RayDB, DBSCAN, triangle-counting, Barnes-Hut, collision, or
   other benchmark-specific logic hidden inside generic runtime, primitive, or
   native-engine surfaces?

3. Primitive quality:
   Are the v2.5 continuation operations truly generic primitives, or are any of
   them just app-specific helpers with generic names?

4. Partner boundary:
   Is the claim "Triton is the partner; Torch is only a tensor carrier"
   implemented honestly? Are there places where PyTorch is effectively doing
   partner work that should be attributed as such?

5. Performance honesty:
   Goal2683 shows Triton correctness on GPU but also shows the preview Triton
   kernels are slower than Torch CUDA baselines. Are the reports and docs
   sufficiently clear that this is not a promoted performance path?

6. RayDB integration:
   RayDB is now wired through public `partner="triton"` front doors for
   post-RT grouped continuation. Is this integration meaningful, or is it too
   detached from the full RT path because the current native RayDB path still
   reduces inside the RTDL native primitive?

7. Next-goal correctness:
   The proposed next goal is a generic RT hit-stream handoff so OptiX/Embree can
   emit app-free hit rows/columns for Triton continuation. Is this the right
   next step? What contract should it use?

8. Contract completeness:
   Are typed buffers, prepared sessions, segmented row streams, and phase timing
   metadata sufficiently specified for v2.5 work, or are there missing lifecycle
   and ownership rules?

9. Failure semantics:
   Are overflow, missing groups, empty groups, row ordering, dtype, and capacity
   semantics specified tightly enough for cross-backend parity?

10. Test coverage:
   Which tests are missing before claiming v2.5 partner readiness? Please be
   specific about local tests vs pod/GPU tests.

11. Documentation consistency:
   Are any docs outdated or misleading relative to the current state at commit
   `121431432d414ece1dd4e7b95f5e9faa6f80eab5`?

12. Release/public-claim gate:
   What must still happen before any public statement like "RTDL supports a
   Triton partner path" or "Triton partner improves usability without losing
   performance" can be made?

## Known Current Limitations

Please verify whether these are accurately described and whether any should be
treated as blockers:

- Goal2683 validates correctness of Triton continuation and public adapter
  APIs on GPU, but does not promote performance.
- The current Triton kernels are slower than Torch CUDA baselines on the tested
  L4 continuation-only workloads.
- RayDB has app-level Triton front-door continuation wiring, but the full
  RT+Triton total path is not complete because the native RT path currently
  reduces inside the RTDL primitive instead of exposing a generic hit stream.
- Numba is secondary and unavailable on the Goal2683 pod.
- Some benchmark apps are only classified as
  `dispatcher_ready_app_wiring_required`; not all have public Triton adapter
  front-door app wiring.
- Current artifacts are internal evidence, not public release evidence.

## Requested Output Format

Please produce a critical review with:

1. Final verdict: `accept`, `accept_with_fixes`, or `reject`.
2. Blocking issues, if any.
3. Non-blocking issues.
4. Required fixes before continuing to the next goal.
5. Assessment of whether Goal2684, the generic RT hit-stream handoff, is the
   correct next engineering target.
6. Any exact files/tests/docs that must be changed.

Do not be polite at the expense of technical accuracy. If a claim is weak,
overstated, or unsupported, call it out directly.
