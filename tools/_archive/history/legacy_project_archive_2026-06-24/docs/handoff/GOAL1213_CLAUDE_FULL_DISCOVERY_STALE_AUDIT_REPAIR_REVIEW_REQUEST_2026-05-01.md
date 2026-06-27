# Goal1213 Claude Review Request: Full Discovery Stale-Audit Repair

Please review the bounded repair report:

- `docs/reports/goal1213_full_discovery_stale_audit_repair_2026-05-01.md`

Context:

- A local full unittest discovery run executed:
  `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v`
- It ran `2366` tests with `196` skips, `14` failures, and `8` errors.
- The failing set was concentrated in stale current-state audits after Goal1208
  promoted the narrow road-hazard public wording row and moved the current
  public wording count from `10` to `11`.
- The repair updates affected audit scripts/tests only; it does not change
  runtime kernels or public wording claims.
- The targeted formerly-failing module set now passes `42` tests.

Review questions:

1. Are these failures correctly classified as stale audit/current-state
   expectation drift rather than runtime or implementation regressions?
2. Are the updated counts and buckets consistent with the post-Goal1208 state:
   `11` reviewed public wording rows, `5` unresolved public-wording-evidence
   apps, and road hazard removed from unresolved/pre-pod buckets?
3. Does the report correctly avoid claiming that full discovery now passes
   until the full suite is rerun?
4. Are there required fixes before Codex records two-AI consensus for
   Goal1213?

Please write `ACCEPT` or `BLOCK` with reasons.
