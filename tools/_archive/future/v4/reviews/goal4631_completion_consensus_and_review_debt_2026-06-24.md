# V4 Goal4631 Completion Consensus And Review Debt

Date: 2026-06-24

Status: `goal4631_complete_tier3_deferred_not_supported`

## Verdict

Goal4631 is complete.

Decision:

- Tier-3 remains spike-only/deferred.
- Tier-3 is not V4.0 public support.
- V4.0 release decision cannot depend on Tier-3.
- Raw OptiX callbacks and arbitrary callback support are not authorized.

Primary decision document:

- `future/v4/v4_goal4631_tier3_spike_execution_decision_2026-06-24.md`

Code and tests:

- `src/rtdsl/v4_tier3_spike_decision.py`
- `tests/v4_goal4631_tier3_spike_decision_test.py`

Focused verification:

```text
py -m unittest tests.v4_tier3_callback_spike_protocol_test tests.v4_tier3_numba_ptx_probe_test tests.v4_tier3_optix_module_link_probe_test tests.v4_goal4631_tier3_spike_decision_test tests.v4_goal4630_pushdown_recognizer_test
Ran 24 tests
OK
```

Cross-gate verification:

```text
py -m unittest tests.v4_goal4629_weighted_sum_candidate_decision_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_goal4631_tier3_spike_decision_test tests.v4_tier3_callback_spike_protocol_test
Ran 25 tests
OK
```

## Consensus Seats

### Seat 1: Codex Implementation And Self-Audit

Codex implemented the Tier-3 spike decision helper and tests.

Self-audit:

1. Am I being foolish?
   - No. The evidence reaches a concrete blocked stage and does not justify support.

2. What would make this foolish?
   - Treating one Numba PTX generation as Tier-3 support.
   - Ignoring the `optixModuleCreate` failure.
   - Pretending correctness/overhead stages ran.

3. Is there another possible path?
   - Yes. Continue Tier-3 as V4.x spike work with a real wrapper/direct-callable ABI experiment.

4. Can we start a different path that truly solves the problem?
   - Yes. Proceed to Goal4632 with Tier-3 explicitly outside the release dependency path.

### Seat 2: Internal Reviewer

Reviewer:

- Maxwell
- agent id: `019efccb-fe04-7ad1-8cf2-beecbcb6f323`

Verdict:

- `accept_goal4631_defer_tier3_not_supported`

Summary:

- Stage 1 is correctly treated as narrow evidence, not a protocol pass.
- Stage 2 is correctly interpreted as blocked at `optix_module_create`.
- Stage 3 and Stage 4 are correctly blocked until link/launch exists.
- V4.0 is explicitly prevented from depending on Tier-3.
- Non-authorizations are preserved.
- Maxwell independently ran the 24-test Tier-3/recognizer suite and it passed.

## External Review Debt

### Claude

File:

- `future/v4/reviews/claude_v4_goal4631_tier3_spike_execution_decision_review_blocked_2026-06-24.md`

Debt:

- `claude_goal4631_review_session_limit_debt`

Reason:

- Claude CLI returned session limit.

### Antigravity

File:

- `future/v4/reviews/antigravity_v4_goal4631_tier3_spike_execution_decision_review_blocked_2026-06-24.md`

Debt:

- `antigravity_goal4631_review_empty_output_debt`

Reason:

- Antigravity CLI exited with code 0 and empty stdout/stderr.

## Evidence Used

Stage 1:

- `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json`
- one scalar device callback generated PTX;
- protocol did not pass because the attempt/variant matrix was not met.

Stage 2:

- `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json`
- direct `optixModuleCreate` on bare helper PTX failed;
- blocker: `No functions with semantic types found`.

## Non-Authorization

Goal4631 does not authorize:

- V4 release.
- V4 release-candidate status.
- measured-catalog promotion.
- broad V4 speedup claims.
- whole-application speedup claims.
- public true-zero-copy wording.
- Tier-3 callback support.
- raw OptiX callback support.
- CuPy performance claims.
- C ABI / embedding / non-Python-host work.
- app-specific native kernels.

## Next Goal

Proceed to Goal4632:

- assemble the V4 release decision packet over gates G1-G7;
- decide whether V4 is release-ready, performance-preview, development-state, or not authorized;
- preserve exact public wording boundaries.

