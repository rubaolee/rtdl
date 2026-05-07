# Goal1455 External Review Request

## Request

Review the v1.5.2 prepared host-output `COLLECT_K_BOUNDED` evidence and gate
boundary. Decide whether it is acceptable to mark
`embree_optix_same_contract_parity` as satisfied while keeping
`prepared_buffer_reuse_proven=False` and leaving `external_ai_review` as the
only missing gate item until this review is accepted.

## Files To Review

- Gate implementation:
  `src/rtdsl/v1_5_2_collect_buffers.py`
- Gate tests:
  `tests/goal1445_v1_5_2_prepared_buffer_reuse_gate_test.py`
  `tests/goal1449_v1_5_2_prepared_host_output_overflow_gate_test.py`
  `tests/goal1452_v1_5_2_prepared_host_output_parity_gate_test.py`
- Local/pod evidence reports:
  `docs/reports/goal1452_v1_5_2_prepared_host_output_parity_gate_2026-05-07.md`
  `docs/reports/goal1450_rtx2000ada_pod_required_final_2026-05-07.md`
  `docs/reports/goal1453_rtx2000ada_latest_main_validation_2026-05-07.md`
  `docs/reports/goal1454_rtx2000ada_generic_optix_smoke_2026-05-07.md`
- Required parity payload:
  `docs/reports/goal1453_rtx2000ada_latest_main_required_2026-05-07/goal1450_prepared_host_output_parity_pod_required_2026-05-07.md`
- Latest-main RTX collect slice:
  `docs/reports/goal1453_rtx2000ada_validation_2026-05-07/goal1453_collect_slice.log`

## Evidence Summary

- Windows optional Embree prepared host-output parity passed.
- Linux optional Embree prepared host-output parity passed.
- Linux GTX 1070 OptiX compatibility parity passed, but was explicitly not
  treated as RT-core evidence.
- RTX 2000 Ada pod required Embree+OptiX parity passed:
  Embree `pass=4, fail=0, skipped=0`; OptiX `pass=4, fail=0, skipped=0`.
- Latest-main RTX collect/prepared-host-output slice passed:
  `Ran 92 tests ... OK`.
- Generic raw ray/triangle OptiX smoke passed on RTX after correcting
  `RTDL_OPTIX_LIB` to the pod path. That smoke is orthogonal compatibility
  evidence only.

## Current Boundary

The gate now records:

- `embree_optix_same_contract_parity` in satisfied evidence.
- `external_ai_review` as the only missing evidence.
- `prepared_buffer_reuse_proven=False`.
- `true_zero_copy_authorized=False`.
- `public_speedup_wording_authorized=False`.
- `whole_app_speedup_claim_authorized=False`.
- `stable_public_primitive_authorized=False`.
- `release_action_authorized=False`.

## Review Questions

1. Is the evidence sufficient to mark same-contract Embree/OptiX prepared
   host-output parity as satisfied for this narrow gate?
2. Does the gate still correctly block prepared-buffer reuse, true zero-copy,
   speedup, whole-app, stable primitive, and release claims?
3. Are there any blocker issues that must be fixed before `external_ai_review`
   can be moved from missing to satisfied?

Please answer with `ACCEPT`, `ACCEPT_WITH_NOTES`, or `REJECT`, and give precise
blockers if rejecting.
