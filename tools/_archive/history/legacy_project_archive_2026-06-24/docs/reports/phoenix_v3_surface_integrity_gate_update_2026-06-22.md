# Phoenix V3 Surface Integrity Gate Update

Date: 2026-06-22
Status: `non-release engineering progress`

## Summary

Phoenix V3 remains `blocked_not_release`, but the current 13-row / 9-capability
release surface now has a machine-checkable integrity manifest in:

`docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`

The manifest records, for every current surface row:

- row id;
- generic capability family;
- source kind;
- evidence paths;
- review paths;
- consensus paths;
- path-existence booleans;
- blocked `release_authorized`, `public_speedup_claim_authorized`, and
  `broad_v3_faster_than_v2_claim_authorized` flags.

This prevents a future worker from treating stale, app-specific, missing-review,
or overclaiming material as part of the current V3 surface.

## Current Evidence

Surface breadth gate:

```text
status: surface_breadth_passed_not_release
surface row integrity rows: 13
surface row paths all exist: true
surface row unsupported-claim flags blocked: true
surface rows are generic capability rows: true
```

Release readiness gate:

```text
status: blocked_not_release
failed_checks: []
blocking_reasons:
  - release_authorization_false
  - updated_thirteen_row_release_readiness_consensus_required
```

Latest full local validation:

```text
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_serious_paired_conclusion_sync_20260622.json
106 modules / 509 tests OK
```

## What Changed

- `scripts/v3_phoenix_release_surface_breadth_gate.py` now emits and checks the
  13-row integrity manifest.
- `tests/v3_phoenix_release_surface_breadth_gate_test.py` asserts the manifest
  covers exactly the current surface, all paths exist, all unsupported-claim
  flags remain blocked, and all rows map to planned generic capabilities.
- `scripts/v3_phoenix_release_readiness_gate.py`, its test, the current handoff,
  the readiness packet, and the 13-row aggregate review packet now reference the
  post-surface-integrity full matrix artifact.

## What This Does Not Authorize

This update does not authorize:

- a Phoenix V3 release;
- broad V3-over-V2.x speedup wording;
- public whole-app acceleration wording;
- true-zero-copy, C ABI, embedding, or V4 wording;
- package-install or broad hardware-portability wording.

The remaining release blocker is still a real external aggregate
release-readiness verdict for the current 13-row packet, handled through the
bounded external review protocol.

## Goal-Level Decision Audit

Decision: strengthen the local Phoenix V3 release-surface gate before any new
external-review attempt.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? The foolish action would
   have been to keep relying on prose that says "13 rows" without a
   row-by-row machine-checkable evidence/review/claim-boundary manifest.
3. Was there another path? Yes. I could have retried Claude immediately, but
   that would not improve the local truth surface and could repeat the old
   external-tool fixation.
4. Can I now try a different path that actually solves the problem? Yes. The
   local gate now proves the current surface shape; the next external review,
   when attempted, can review a cleaner and less ambiguous packet.

