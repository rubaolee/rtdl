# Call For Review: Phoenix V3 M32 Continuation-Core Audit Surface

Date: 2026-06-23
Status: `request_m32_external_review_not_release`

This review asks whether M32 is a correct Phoenix V3 Step-4 engineering gate.
It does not ask for release authorization, all-app POD authorization, public
speedup wording, broad V3-over-V2 wording, or V4 work.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
```

## Patch Scope

Code:

- `src/rtdsl/prepared_execution.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`

Report:

- `docs/reports/phoenix_v3_m32_continuation_core_audit_surface_2026-06-23.md`

## Change Summary

M32 adds:

- `PREPARED_EXECUTION_CONTINUATION_AUDIT_VERSION`;
- `audit_prepared_execution_continuation_metadata(metadata)`.

The helper builds on M31. It requires Step-3 readiness plus:

- `primitive_family`;
- `runtime_trunk_family`;
- `continuation_contract`;
- `row_contract`;
- `focused_material_gain_required_before_all_app=true`;
- `full_all_app_rerun_authorized_by_this_packet=false`;
- `app_specific_native_engine_logic_allowed=false`;
- `automatic_partner_selection_authorized=false`.

It returns `accept_step4_continuation_core_ready` only when all fields pass, or
`incomplete_step4_continuation_audit` with `missing_step4_fields`.
The returned audit payload also echoes Set-A probe / Set-B control
classification for review.

Tests assert the Step-4 audit for:

- point-location topology stream;
- fixed-radius threshold reached count;
- fixed-radius ranked summary;
- fixed-radius graph component signature;
- aggregate-tree fused weighted vector sum;
- ray-triangle weighted summary device-output stream;
- segment-intersection topology stream.

Tests also assert negative gates for runner-shaped helpers that lack the
required residency/continuation facts:

- fixed-radius self-query device-column helper: blocked Set-A seed;
- AABB native query-handle range rows: blocked Set-B control;
- AABB native query-handle counts: blocked Set-B control;
- OptiX AABB prepared-query-set counts: blocked Set-B control.

Those helpers may report `runtime_executed=true`, but their M31/M32 audits must
remain `incomplete_step3_audit` / `incomplete_step4_continuation_audit` until
real Step-3 and Step-4 evidence exists.

M33 records the complete local promotion/control ledger for all 11 current
prepared-session helpers.

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

## Reviewer Questions

1. Is M32 aligned with Claude's Step 4 requirement that continuation work move
   into runner-callable core nodes instead of remaining route prose?
2. Is requiring M31 Step-3 readiness before Step-4 continuation readiness the
   right dependency?
3. Are the required fields strict enough to distinguish core continuation
   nodes from app-mode route code?
4. Does this helper preserve all non-authorization boundaries?
5. Should the next engineering step use M31/M32 to reject or promote remaining
   prepared-session families before any all-app POD rerun?
6. Does this patch authorize any release, public speedup, broad V3-over-V2,
   all-app POD, true-zero-copy, automatic partner-selection, or V4 work?

## Requested Verdict Labels

Choose exactly one:

- `accept_m32_continuation_core_audit_surface`
- `accept_with_amendments`
- `blocked_needs_code_changes`
- `reject_m32_wrong_direction`

Include blocking findings, required amendments if any, explicit answers to the
six questions, and an explicit non-authorization block.
