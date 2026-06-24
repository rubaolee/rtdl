# External Review: Phoenix V3 M72 Barnes-Hut POD Intake

Date: 2026-06-24

Reviewer: Claude Code CLI

Packet: `phoenix_v3_m72_barnes_hut_blocker_bound_pod_20260624_091320`

Verdict: `accept_m72_goal_complete_as_trunk_productization_parity_not_release`

## Q1: Is the M72 POD artifact valid and properly ingested?

Yes.

The packet completed with `failed_checks: []`. The claimed gate checks are
verified in the JSON, including:

- `runner_used_all_samples`;
- `runner_runtime_trunk_executes_all_samples`;
- `runner_internal_device_residency_all_samples`;
- `runner_scorecard_blocker_bound_all_samples`;
- `runner_scorecard_blocker_id_all_samples`;
- `runner_win_source_partner_continuation_all_samples`;
- `control_not_scorecard_bound`;
- `all_claim_flags_false`.

All runner samples carry `step3_audit_status: accept_step3_ready` and
`missing_step3_fields: []`. Checksums pass for all body counts. The two failed
launch attempts left no performance artifact and are correctly excluded.

## Q2: Is the interpretation honest: current-control parity, not a new speedup?

Yes, without qualification.

The primary current-control read is:

```text
runner_vs_existing_fused_control_geomean = 0.9997602284020717x
```

The per-size speedups are approximately `0.9994x`, `0.9995x`, and `1.0004x`.
These are parity, not a new speedup. The packet keeps all release and public
claim flags false.

## Q3: Is closing M72 as trunk productization/parity acceptable?

Yes.

The closure label
`runtime_trunk_productization_parity_for_barnes_hut_not_current_control_speedup`
is precise. It records that the runtime trunk can carry a productized,
scorecard-bound, Step-3-ready Barnes-Hut aggregate-tree route while preserving
the current fused partner's hot-path speed.

## Q4: Should M74 target a different Set-A blocker?

Yes, strongly.

The existing fused Numba CUDA control is already fast. The runner wraps it
through the runtime trunk without beating it. Further Barnes-Hut polishing in
the current route design is unlikely to produce a material current-control win.
M74 should target a Set-A blocker where the runtime trunk can plausibly improve
over, not merely match, the current control.

## Q5: Are amendments required before M72 goal completion?

No.

The prior amendments are closed:

- A1 behavioral dispatch test:
  `test_prepared_execution_mode_dispatches_to_runtime_runner_payload`;
- A2 incumbent route declaration:
  `summary.incumbent_route_declaration`.

No new amendments are required.

## Specific Finding: 12.7559x vs 0.999760x

The `12.75587197083642x` value is only the historical no-go OptiX displacement.
It is not the primary claim.

The `0.9997602284020717x` value is the sole primary current-control performance
read. It compares the M72 runner to the existing fused Numba CUDA control in the
same POD session with matching parameters.

The packet treats this distinction correctly.

## Non-Authorization

This review does not authorize:

- V3 release;
- all-app benchmarking;
- public speedup wording;
- broad V3-over-V2 claims;
- treating `0.999760x` or `12.7559x` as a V3 release performance claim;
- V4 work;
- embedding;
- external zero-copy claims.
