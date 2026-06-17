# External Review Request: Goal4536 V3 Completion Packet

Date: 2026-06-17

Please review the V3.0 current benchmark-app completion packet and its
supporting gates. The intended conclusion is narrow:

- V3 current benchmark-app implementation queue is complete.
- Runtime, claim/evidence, and current design-blocker queues are empty.
- Barnes-Hut and Triangle Counting remain future design targets, not current
  V3 implementation blockers.
- No release, public speedup, broad RT-core, paper-reproduction, automatic
  partner-selection, or app-specific native-engine claim is authorized.

## Primary Evidence

- `docs/reports/goal4534_v3_0_m136_v3_current_app_completion_gate_2026-06-17.md`
- `docs/reports/goal4535_v3_0_m137_v3_completion_readiness_audit_2026-06-17.md`
- `docs/reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md`
- `docs/learn/benchmark_evidence_index.md`
- `src/rtdsl/v3_0_benchmark_implementation_queue.py`

## Key State

The queue should validate as:

- Runtime queue: empty
- Claim/evidence queue: empty
- Design blocker queue: empty
- Future design target queue: `barnes_hut`, `triangle_counting`
- Closed current targets: 8 apps
- All ten benchmark apps accounted for

## Review Questions

1. Does Goal4536 correctly summarize all ten benchmark apps without hiding the
   two future design targets?
2. Does the reclassification of Barnes-Hut and Triangle Counting from current
   blockers to future design targets read as honest and technically bounded?
3. Do Goal4534/Goal4535/Goal4536 keep public performance, broad RT-core,
   paper-reproduction, automatic partner-selection, and app-specific native
   engine claims blocked?
4. Are any current docs still likely to mislead a reader into thinking V3.0 has
   a public speedup claim, full paper reproduction claim, or completed RT-native
   Barnes-Hut/Triangle design?
5. Is there any release-readiness gap that should be fixed before presenting
   the V3 current-app completion state to the project owner?

## Validation Already Run

Local:

- `PYTHONPATH=src:. python scripts/goal4536_m138_v3_internal_completion_packet.py`
- `PYTHONPATH=src:. python -m unittest tests.goal4535_v3_0_m137_v3_completion_readiness_audit_test tests.goal4536_v3_0_m138_v3_internal_completion_packet_test tests.goal4534_v3_0_m136_v3_current_app_completion_gate_test tests.goal4524_v3_0_m128_benchmark_implementation_queue_test`
- `PYTHONPATH=src:. python -m unittest discover -s tests`

Pod:

- `PYTHONPATH=src:. python scripts/goal4536_m138_v3_internal_completion_packet.py`
- `PYTHONPATH=src:. python -m unittest tests.goal4536_v3_0_m138_v3_internal_completion_packet_test tests.goal4535_v3_0_m137_v3_completion_readiness_audit_test tests.goal4534_v3_0_m136_v3_current_app_completion_gate_test tests.goal4524_v3_0_m128_benchmark_implementation_queue_test`
- `PYTHONPATH=src:. python -m unittest discover -s tests`

## Expected Verdict Format

Please answer with one of:

- `approve`
- `approve_with_caveats`
- `request_changes`

If requesting changes, list each blocking issue with file/report references and
the smallest required fix.
