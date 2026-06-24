# Phoenix V3 Short User Path Guard Update

Date: 2026-06-22
Status: `non-release user-surface cleanup complete`

## Summary

Phoenix V3 remains `blocked_not_release`. This update closes a user-surface gap:
the current documentation now gives a short, safe learner path into the Phoenix
V3 rebuild without sending a user through old V3/V4 material or the full
evidence archive first.

The path is intentionally narrow. It teaches the current V3 loop and its claim
boundaries; it does not promote a release, a broad V3-over-V2.x speedup claim,
whole-app acceleration, package-install readiness, true zero-copy, C ABI,
embedding, or V4 wording.

## What Changed

- `docs/public_documentation_map.md` now has a user/learner front door:
  `V3 Rebuild Tutorial Path`.
- `docs/public_documentation_map.md` now answers:
  `How do I learn the current V3 rebuild quickly?`
- `tutorials/current/README.md` now has a `Shortest Safe Path` before the full
  lesson list:
  first run, hello world, backend choice, one benchmark row, and claim
  boundaries.
- `tests/v3_rebuild_tutorial_surface_test.py` checks that the tutorial README
  keeps the short path before the full lessons.
- `tests/v3_public_docs_rebuild_surface_test.py` checks that the public map
  exposes the learner path before the deeper V3 rebuild control material.

## Verification

Focused surface tests:

```text
py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test
27 tests OK
```

Full V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild --json-out docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_serious_paired_conclusion_sync_20260622.json
106 modules / 509 tests OK
```

Wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --json-out docs/rebuild/v3/phoenix_v3_release_wording_gate_2026-06-21.json --pretty
status: passed
violations: []
```

Release readiness gate:

```text
py -3 scripts/v3_phoenix_release_readiness_gate.py --json-out docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json --pretty
status: blocked_not_release
failed_checks: []
blocking_reasons:
  - release_authorization_false
  - updated_thirteen_row_release_readiness_consensus_required
```

Aggregate readiness gate:

```text
py -3 scripts/v3_phoenix_release_readiness_gate.py --json-out docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json --pretty
status: blocked_not_release
failed_checks: []
blocking_reasons:
  - release_authorization_false
  - updated_thirteen_row_release_readiness_consensus_required
```

## What This Does Not Authorize

This update does not authorize:

- a Phoenix V3 release;
- broad V3-over-V2.x speedup wording;
- public whole-app acceleration wording;
- public Spatial speedup or RTDL-beats-RayJoin claims;
- true-zero-copy, C ABI, embedding, or V4 wording;
- general package-install claims;
- multi-GPU or broad hardware-portability claims.

## Goal-Level Decision Audit

Decision: improve the current V3 user learning path without treating that as
release authorization.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? The foolish action would
   have been to keep only internal evidence reports while leaving a new user to
   search through stale V3/V4 history.
3. Was there another path? Yes. I could have written another large explanatory
   document, but that would add one more thing to read instead of shortening
   the path.
4. Can I now try a different path that actually solves the problem? Yes. The
   current path gives users a compact, guarded route into V3 while the release
   gate still blocks unsupported public claims.

