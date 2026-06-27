# Codex Consensus: Phoenix V3 Repeated Prepared-Session Runner M3.3

Date: 2026-06-22
Status: `2ai_consensus_complete_local_contract_not_release`

## External Review

```text
review: docs/reviews/claude_phoenix_v3_repeated_prepared_session_runner_m3_3_review_2026-06-22.md
verdict: approve_with_required_edits_not_release
```

Claude's required edits:

1. Update `PREPARED_EXECUTION_SESSION_RUNNER_VERSION` to reflect M3.3 schema
   changes.
2. Add a test rejecting `measured_repeat_count=0`.

Both required edits have been applied.

## Codex Verdict

```text
approve_local_contract_not_release_after_required_edits
```

M3.3 is valid Phoenix V3 local engineering progress because it adds a generic
productized repeated prepared-session runner:

```text
run_repeated_prepared_execution_session(...)
```

The API executes warmup plus N measured prepared operations inside one runner
call after one cache lookup / prepare phase, and emits one report payload. This
directly targets the measured M3.1/M3.2 failure mode where productized runner
overhead recovered only to parity.

## Applied Evidence

Code/report files:

```text
src/rtdsl/prepared_execution.py
src/rtdsl/__init__.py
tests/v3_phoenix_prepared_execution_session_runner_test.py
docs/reports/phoenix_v3_repeated_prepared_session_runner_m3_3_2026-06-22.md
```

Validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test

Ran 18 tests
OK
```

Package-surface check:

```text
import rtdsl as rt
rt.PREPARED_EXECUTION_SESSION_RUNNER_VERSION
=> rtdl.v3.phoenix.prepared_execution_session_runner.m3_3

hasattr(rt, "run_repeated_prepared_execution_session") => True
hasattr(rt, "PreparedExecutionSessionTask") => True
```

## Explicit Non-Authorization

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
all_app_pod_rerun_authorized: false
second_material_set_a_probe_obtained: false
```

## Next Work

The next Phoenix V3 engineering step is to wire this repeated runner into a real
Set-A route and measure focused same-pod A/B against the relevant incumbent
route. This consensus does not authorize a full all-app pod rerun.

## Goal-Level Decision Audit

Decision: accept M3.3 as closed local contract progress after Claude required
edits, while keeping release and all-app pod work blocked.

1. Was I foolish?
   No. The acceptance is bounded to local contract evidence and external review
   requirements were applied.
2. If yes, what actions made the decision foolish?
   It would be foolish to count this as pod evidence, a second Set-A material
   win, or V3 release progress beyond the local runtime mechanism.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. The alternative would be to skip review or call the API enough; the
   better path is review, required edits, tests, and then real route wiring.
4. Can I now try a different path that truly solves the problem?
   Yes. Use the repeated runner in a real Set-A probe and require focused
   same-pod evidence before any broader benchmark spend.
