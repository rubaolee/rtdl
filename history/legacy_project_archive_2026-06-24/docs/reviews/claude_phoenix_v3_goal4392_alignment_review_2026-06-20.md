# Claude Phoenix V3 Goal4392 Alignment Review

Reviewer: Claude Code, independent compact no-tools review distinct from Codex.

Date: 2026-06-20.

Reviewed packet:

```text
docs/reviews/call_for_review_phoenix_v3_goal4392_alignment_2026-06-20.md
```

## Review

VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS

- The M1-M7 compliance-table-first approach correctly re-subordinates benchmark
  work to Goal4392's generic-capability requirements, and the P0 route mapping
  (grouped reduction, component union, ranked summary, topology streams,
  frontier/vector accumulation, prepared chunks) is a legitimate way to make
  benchmark rows serve as evidence for generic mechanisms rather than ends in
  themselves. However, the plan must state explicitly that no row may exist
  that lacks a named generic capability it instantiates, with rows failing that
  test removed rather than retained as "supplementary."
- The 1.012x geomean speedup makes any public claim beyond "runs correctly,
  performance parity-ish" unauthorized; the amendment should pin this
  explicitly as a release-blocking gate, not just "claims stay blocked until
  M7," since vague gating language has previously allowed claims to leak before
  M7 closes.
- M150+ embedding/C ABI/SDK/zero-copy exclusions should be enforced via a
  concrete artifact, for example a denylist checked at doc/release-build time,
  not just stated intent. Otherwise "OUT" is aspirational rather than
  controlled, and prior cycles show aspirational exclusions do not hold.
