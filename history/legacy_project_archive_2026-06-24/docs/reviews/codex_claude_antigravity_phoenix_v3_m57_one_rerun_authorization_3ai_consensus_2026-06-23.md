# Codex + Claude + Antigravity Consensus: Phoenix V3 M57 One-Rerun Authorization

Date: 2026-06-23

Consensus status:

```text
m57_one_source_signature_gated_librts_rerun_authorized_no_release_no_claims
```

## Scope

This consensus authorizes exactly one future source-signature-gated LibRTS M47
rerun after the M56 metadata diagnosis and M57 fail-closed hardening.

Authorized script:

```text
scripts/v3_phoenix_m47_librts_stability_protocol.py
```

Authorized token:

```text
M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED
```

The run has not been executed by this consensus file. This file only records
authorization.

## Inputs

- `docs/reviews/call_for_review_phoenix_v3_m57_source_signature_gated_librts_rerun_authorization_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m57_source_signature_gated_librts_rerun_authorization_recorded_review_2026-06-23.md`
- `docs/reviews/antigravity_phoenix_v3_m57_authorization_after_fail_closed_fix_review_2026-06-23.md`
- `docs/reports/phoenix_v3_m56_goal_completion_audit_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m56_goal_completion_3ai_consensus_2026-06-23.md`

## Verdicts

Codex:

```text
authorize_m57_one_source_signature_gated_librts_rerun_after_fail_closed_fix
```

Claude:

```text
authorize_m57_one_source_signature_gated_librts_rerun_after_fail_closed_fix
```

Antigravity:

```text
authorize_m57_one_source_signature_gated_librts_rerun_after_fail_closed_fix
```

## Required Preconditions

The executor must satisfy all conditions below:

1. Run target-machine dry-run first with `--run-preflight`, without
   `--execute`.
2. Use real current and V2.14 roots.
3. Use explicit Linux/POD Python paths.
4. Confirm dry-run `failed_checks=[]`.
5. Confirm dry-run preflight row `current_librts_set_b_source_signature`
   exists, has `returncode=0`, and its stdout contains `"failed": []`.
6. If the source-signature preflight fails or is missing, stop immediately,
   copy back failed dry-run evidence, and do not run measured samples.
7. Only after conditions 1-5 pass, execute exactly one run with:

```text
--execute --authorization-token M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED
```

8. Use unchanged M47 scenario set: `optix_cold_single_shot` and
   `embree_32768_stress`.
9. Use exactly 8 paired samples per scenario.
10. Copy back full evidence: `summary.json`, `README.md`, all measured
    stdout/stderr files, all preflight files, and driver logs.
11. Do not close watch rows from raw output. Copied evidence requires a later
    review packet.

## Fail-Closed Hardening

M57 fixed the issue Claude found in the first review:

- `scripts/v3_phoenix_m47_librts_stability_protocol.py` now aborts before
  `execute_schedule()` if `execute_preflight()` returns any error.
- `scripts/v3_phoenix_m47_librts_stability_protocol.py` now supports
  `--run-preflight`, which executes preflight rows during dry-run without
  executing measured samples.
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py` includes
  `test_execute_aborts_before_samples_when_preflight_fails`.

## Residual Risks

- A metadata-fixed run may still be performance-red.
- Static source-signature checks do not prove runtime metadata emission.
- The old M54 token is consumed; M57 authorizes only the token listed above.
- No second M57 run is authorized.

## Non-Authorization

This consensus does not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure
- no scenario changes
- no sample-count changes
- no second M57 run

## Goal-Level Decision Audit

Decision: authorize exactly one future M57 source-signature-gated LibRTS rerun,
but do not execute it in this authorization document.

1. Was I foolish? No, because the code-level preflight gap was fixed before
   final authorization.
2. If yes, what actions made the decision foolish? The foolish path would have
   been accepting a purely procedural dry-run gate while `--execute` still ran
   samples after preflight errors.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Fix the harness to fail closed before external authorization is final.
4. Can I now try a different path that actually solves the problem? Yes. Use
   this consensus to run exactly one gated POD rerun, copy back evidence, and
   send the result through a later review packet before any interpretation.
