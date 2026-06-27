# Phoenix V3 M32 Continuation-Core Audit Surface

Date: 2026-06-23

Status: `continuation_core_audit_surface_added_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
performance_claim_authorized: false
```

## Change

M32 adds a second audit layer on top of M31:

- `PREPARED_EXECUTION_CONTINUATION_AUDIT_VERSION`
- `audit_prepared_execution_continuation_metadata(metadata)`

M31 answers: did the productized runner execute with accepted phase accounting,
internal residency, and no hot-path host materialization?

M32 answers: is the same result also a core continuation node, rather than only
route prose?

The M32 audit requires:

- M31 `step3_residency_default_ready`;
- `primitive_family`;
- `runtime_trunk_family`;
- `continuation_contract`;
- `row_contract`;
- `focused_material_gain_required_before_all_app=true`;
- `full_all_app_rerun_authorized_by_this_packet=false`;
- `app_specific_native_engine_logic_allowed=false`;
- `automatic_partner_selection_authorized=false`.

If any field is missing, the helper returns
`incomplete_step4_continuation_audit` and a concrete
`missing_step4_fields` list.
The returned audit payload also echoes Set-A probe / Set-B control
classification for review.

## Current Coverage

Route-level tests now assert `accept_step4_continuation_core_ready` for these
generic families:

- point-location topology stream;
- fixed-radius threshold reached count;
- fixed-radius ranked summary;
- fixed-radius graph component signature;
- aggregate-tree fused weighted vector sum;
- ray-triangle weighted summary device-output stream;
- segment-intersection topology stream.

M32 also adds negative gates. Helpers that merely run through the
prepared-session runner, but do not report Step-3 residency facts and Step-4
continuation facts, must remain blocked by audit:

- fixed-radius self-query device-column helper: blocked Set-A seed;
- AABB native query-handle range rows: blocked Set-B control;
- AABB native query-handle counts: blocked Set-B control;
- OptiX AABB prepared-query-set counts: blocked Set-B control.

These controls preserve the distinction between `runtime_executed=true` and
`accept_step3_ready` / `accept_step4_continuation_core_ready`.

This is a contract gate, not a performance run.

M33 records the follow-on promotion ledger for all current prepared-session
helpers:

- `docs/reports/phoenix_v3_m33_prepared_session_step4_promotion_ledger_2026-06-23.md`

## Validation

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 34 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test
Ran 4 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rtnn_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_evidence_test \
  tests.v3_phoenix_triangle_runner_m18_pod_ab_test \
  tests.v3_phoenix_m18_triangle_runner_harness_packet_test \
  tests.v3_phoenix_m16_triangle_runner_wiring_test \
  tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test \
  tests.v3_phoenix_step1_rtdbscan_trunk_probe_report_test \
  tests.v3_phoenix_rayjoin_point_location_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_release_wording_gate_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test
Ran 88 tests
OK
```

Windows Python emitted the known local warning:

```text
Could not find platform independent libraries <prefix>
```

The warning did not prevent tests from passing.

## Boundaries

M32 does not authorize:

- V3 release;
- public speedup wording;
- broad V3-over-V2 wording;
- all-app POD spend;
- true zero-copy wording;
- V4 / C ABI / embedding / external-buffer wording;
- automatic partner selection.

## Goal-Level Decision Audit

Decision: add a shared Step-4 continuation-core audit helper instead of
declaring continuation work complete from route-specific metadata.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be to treat `continuation_contract` strings as
   sufficient proof. M32 requires Step-3 readiness, core family identity,
   closed claim boundaries, and an explicit missing-field list.

3. Was there another path?

   Yes: keep optimizing one route at a time. That would repeat the leaf-first
   error and would not give V3 a reusable runtime contract.

4. Can I now try a different path that actually solves the problem?

   Yes. Use M31/M32 as shared gates before further focused POD work, then
   promote or reject remaining families based on missing fields rather than
   prose.
