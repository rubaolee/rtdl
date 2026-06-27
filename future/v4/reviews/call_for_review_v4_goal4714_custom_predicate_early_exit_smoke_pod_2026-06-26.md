# Call For Review: V4 Goal4714 Custom Predicate Early-Exit Smoke POD Result

Date: 2026-06-26

Requested verdict labels:

- `accept_goal4714_smoke_continue_goal4715_timing_gate`
- `accept_with_required_amendments`
- `reject_smoke_repair_before_timing`

## Files To Review

- Completion report:
  `future/v4/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.md`
- Evidence JSON:
  `future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.json`
- Evidence Markdown:
  `future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.md`
- POD stdout log:
  `future/v4/evidence/v4_goal4714_custom_predicate_early_exit_smoke_pod_2026-06-26.stdout.log`
- Classifier:
  `src/rtdsl/v4_goal4714_custom_predicate_early_exit_smoke_result.py`
- Runner:
  `scripts/v4_goal4714_custom_predicate_early_exit_smoke_pod.py`
- Tests:
  `tests/v4_goal4714_custom_predicate_early_exit_smoke_result_test.py`

## Review Questions

1. Does the smoke prove correctness for the tested regimes?
2. Does the invocation evidence prove early termination in primary rows?
   - k8: `4096` V4 invocations vs `32768` fallback invocations.
   - k32: `4096` V4 invocations vs `131072` fallback invocations.
3. Are controls behaving correctly?
   - reject-all: no early termination, correctness true.
   - no-hit: zero invocations, correctness true.
4. Is it correct that Goal4714 authorizes only Goal4715 timing, not release or
   performance wording?
5. Are there any app-specific semantics hidden in the route?

## Non-Authorization

This review request does not authorize:

- performance claims;
- formal high-performance V4 wording;
- V4 release;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support;
- all-app benchmarking.

