# Codex + Bernoulli Consensus: Phoenix V3 M17 Triangle Focused POD Protocol

Date: 2026-06-22

Verdict: `accept_m17_authorize_m18_runner_harness_no_pod`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
m17_protocol_sufficient_for_m18_harness_only: true
runner_harness_is_pre_run_blocker: true
triangle_counts_as_third_strict_set_a_material_probe_now: false
```

## Reviewed Packet

- M17 JSON:
  `docs/rebuild/v3/phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.json`
- M17 report:
  `docs/reports/phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.md`
- M17 call for review:
  `docs/reviews/call_for_review_phoenix_v3_m17_triangle_focused_pod_protocol_2026-06-22.md`
- Source M16 consensus:
  `docs/reviews/codex_bernoulli_phoenix_v3_m16_triangle_runner_wiring_2ai_consensus_2026-06-22.md`

## Bernoulli Verdict

Bernoulli returned:

```text
accept_m17_authorize_m18_runner_harness_no_pod
```

Bernoulli's explicit authorization answers:

```text
release authorization: no
public speedup authorization: no
broad V3-over-V2 authorization: no
focused POD authorization now: no
all-app POD authorization now: no
M17 protocol is sufficient: yes, for M18 harness work only
runner harness is a pre-run blocker: yes
Triangle counts as the third strict Set-A material probe now: no
```

Bernoulli reported no blocking protocol fixes. The row, controls, success bars,
no-regression guard, metadata requirements, and failure classifications are
strict enough. The next step is local M18 harness implementation and tests, not
POD.

## Codex Position

I agree with the verdict. M17 correctly prevents the old 80,000-clique Triangle
row from being reused as current Phoenix runner evidence. The current Triangle
app route does not yet expose the M16 productized runner path as a serious POD
harness, so M18 must build that harness locally first.

## Verification Recorded

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.v3_phoenix_m17_triangle_focused_pod_protocol_test
Ran 5 tests
OK

py -3 scripts\v3_release_wording_gate.py --pretty
status: pass
violations: []

M17 overclaim scan
no matches
```

## Next Step

M18 should implement and locally test the Triangle runner harness. It may not
run POD. A later M18/M19 review must explicitly authorize any focused POD run.

## Goal-Level Decision Audit

Decision: accept M17 as protocol sufficient for M18 harness work only; keep POD,
release, and speed claims blocked.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be using protocol approval as permission to run POD.
3. Was there another path?
   Yes: authorize one focused run immediately. Bernoulli rejected that because
   the runner harness remains a pre-run blocker.
4. Can I now try a different path?
   Yes. Implement the M18 local harness and tests without spending POD.
