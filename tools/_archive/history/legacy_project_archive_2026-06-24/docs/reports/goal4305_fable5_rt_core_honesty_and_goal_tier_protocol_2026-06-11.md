# Goal4305: RT-Core Honesty Matrix and Goal Tier Protocol

Date: 2026-06-11

## Purpose

Goal4305 continues the Claude Fable5 review intake after Goal4301/4303. It
addresses two non-pod, high-leverage findings:

- F5/P6: the project must not let "ten benchmark apps" sound like ten broad
  RT-core wins.
- F4/P12: low-risk hygiene/doc/refactor goals should not carry the same process
  ceremony as runtime, claim, roadmap, or release goals.

## Changes

Added learner-facing evidence interpretation:

- `docs/learn/rt_core_evidence_matrix.md`
- linked from:
  - `docs/learn/benchmark_evidence_index.md`
  - `docs/learn/README.md`
  - `docs/README.md`

Added process guidance:

- `docs/audit/process/goal_tier_protocol.md`
- linked from:
  - `docs/audit/README.md`
  - `docs/audit/process/README.md`

Added guard tests:

- `tests/goal4305_fable5_evidence_and_process_docs_test.py`

## Design Boundary

The RT-core evidence matrix classifies rows as strong RT evidence, mixed RT
evidence, partner-led evidence, or coverage/pressure-test evidence. It does not
authorize any new public speedup wording. It makes the conservative boundary
more visible:

`the ten-app packet is not ten broad RT-core speedup claims`

The goal tier protocol reduces ceremony only for low-risk work. It explicitly
keeps release, roadmap, architecture, zero-copy, automatic partner selection,
and public performance claims in the highest-review tier.

## Validation

Focused Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4305_fable5_evidence_and_process_docs_test tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4303_current_security_redaction_guard_test tests.goal4299_numba_topk_partner_reference_test tests.goal4298_v2_11_embree_cpu_partner_reference_packet_test

Ran 19 tests in 2.822s
OK (skipped=3)
```

## Remaining Fable5 Work

Still open after Goal4305:

- P2: split/shared partner-column runtime layer.
- P4: kernel DSL bridge pilot.
- P5: timing-floor enforcement in the ten-app scale runner.
- P7: learner setup friction reduction.
- P8: RTNN Embree front door.
- P9: historical report/archive curation.
- P11: declared whole-app mid-scale measurement on the strongest RT app.
