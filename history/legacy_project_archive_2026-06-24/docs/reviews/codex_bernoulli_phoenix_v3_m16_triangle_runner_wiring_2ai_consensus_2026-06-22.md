# Codex + Bernoulli Consensus: Phoenix V3 M16 Triangle Runner Wiring

Date: 2026-06-22

Verdict: `accept_m16_prepare_m17_focused_pod_protocol_no_run`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
m16_closes_local_runner_wiring: true
triangle_counts_as_third_strict_set_a_material_probe_now: false
```

## Reviewed Packet

- M16 JSON:
  `docs/rebuild/v3/phoenix_v3_m16_triangle_runner_wiring_2026-06-22.json`
- M16 report:
  `docs/reports/phoenix_v3_m16_triangle_runner_wiring_2026-06-22.md`
- M16 call for review:
  `docs/reviews/call_for_review_phoenix_v3_m16_triangle_runner_wiring_2026-06-22.md`
- Implementation:
  `src/rtdsl/prepared_execution.py`
  `src/rtdsl/__init__.py`
- Tests:
  `tests/v3_phoenix_prepared_execution_session_runner_test.py`
  `tests/v3_phoenix_m16_triangle_runner_wiring_test.py`

## Bernoulli Verdict

Bernoulli returned:

```text
accept_m16_prepare_m17_focused_pod_protocol_no_run
```

Bernoulli's explicit authorization answers:

```text
release authorization: no
public speedup authorization: no
broad V3-over-V2 authorization: no
focused POD authorization now: no
all-app POD authorization now: no
M16 closes local runner wiring: yes
Triangle counts as the third strict Set-A material probe now: no
```

Bernoulli reported no blocking findings. The helper is generic-shaped,
OptiX-scoped, explicit-partner gated, rejects app-shaped output contracts, and
only sets `runtime_trunk_executes_end_to_end` when the local contract metadata
matches the current Phoenix productized runner requirements.

## Codex Position

I agree with the verdict.

M16 closes the local implementation gap required by M15: Triangle now has a
current Phoenix helper for the generic
`ray_triangle_weighted_summary_device_output_stream` route through
`prepared_execution_session_runner`.

M16 is still not performance evidence. The old Triangle row still does not
count as the third strict Set-A material probe because it was not produced by
this current productized runner path. A focused POD protocol must be written
and reviewed before spending POD.

## Verification Recorded

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 33 tests
OK

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_m15_third_strict_set_a_probe_audit_test tests.v3_release_wording_gate_test
Ran 8 tests
OK

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_m16_triangle_runner_wiring_test tests.v3_phoenix_m15_third_strict_set_a_probe_audit_test tests.v3_release_wording_gate_test
Ran 46 tests
OK

After this consensus record was added, the same command was rerun with the new
consensus-record test included:

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test tests.v3_phoenix_m16_triangle_runner_wiring_test tests.v3_phoenix_m15_third_strict_set_a_probe_audit_test tests.v3_release_wording_gate_test
Ran 47 tests
OK

py -3 scripts\v3_release_wording_gate.py --pretty
pass
```

## Next Step

M17 should prepare a focused Triangle POD protocol and review packet. M17 should
not run POD unless its own 2-AI review explicitly authorizes one focused run.

The protocol should compare the old Triangle route against the runner-backed
generic device-output stream route on the 80,000-clique row, keep Embree as a
control, and report hot-query and runner-inclusive wall metrics separately.

## Goal-Level Decision Audit

Decision: accept M16 as local wiring complete, but keep POD, release, and speed
claims blocked until a separate M17 protocol is reviewed.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be counting local wiring or old Triangle evidence
   as current performance proof.
3. Was there another path?
   Yes: authorize focused POD immediately from M16. That would skip the
   protocol review gate.
4. Can I now try a different path?
   Yes. Move to M17 protocol-only work, then seek 2-AI authorization before any
   POD run.
