# Claude Review: Phoenix V3 Repeated Prepared-Session Runner M3.3

Date: 2026-06-22
Reviewer: Claude
Packet: `docs/reviews/call_for_review_phoenix_v3_repeated_prepared_session_runner_m3_3_2026-06-22.md`

## Verdict

```text
approve_with_required_edits_not_release
```

Explicit claim boundary declarations:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_rerun_authorized: false
```

## Review Summary

Claude approved the M3.3 direction as a generic Phoenix V3 runtime fix, not an
app-specific benchmark patch. The new repeated runner correctly consolidates
one cache lookup / prepare phase, warmup, N measured prepared executions, and
one report payload into one productized runner call.

Claude also confirmed the claim boundaries remain strict: release, public
speedup, broad V3-over-V2, true-zero-copy, automatic partner selection, and
app-specific native engine logic remain false.

## Required Edits

1. Update `PREPARED_EXECUTION_SESSION_RUNNER_VERSION` to reflect the M3.3 schema
   extension. The old value
   `rtdl.v3.phoenix.prepared_execution_session_runner.m1` is stale now that the
   metadata includes repeated-run fields.
2. Add a test that rejects `measured_repeat_count=0`.

## Non-Blocking Observations

- The helper dispatch between `run_prepared_execution_session` and
  `run_repeated_prepared_execution_session` is logically redundant because both
  reach the same internal executor, but it is not incorrect.
- Metadata fields such as `single_cache_lookup_for_measured_repeats` are
  structural assertions rather than measured counters; acceptable for local
  contract level because tests verify the behavior.
- `validate_each_repeat=True` validates all repeat outputs while returning only
  the final output unless `retain_repeat_outputs=True`; this is acceptable but
  should be kept in mind for future caller docs.

## Required Next Step

Apply the two required edits, rerun focused tests, and record Codex consensus.
