# Goal1014 Public Wording Pipeline Source Sync

Date: 2026-04-26

## Problem

The Goal978 -> Goal1006 -> Goal1008 -> Goal1009 public-wording pipeline is
historical and staged:

- Goal978 identifies preliminary speedup candidates.
- Goal1006 applies the 100 ms and margin gate.
- Goal1008 ingests larger-repeat artifacts.
- Goal1009 packages wording candidates and blocked rows.

After Goal1011 introduced `rtdsl.rtx_public_wording_matrix()`, these earlier
pipeline artifacts could still be misread as the current source of truth unless
they carried the final public wording status explicitly.

The most important case is `robot_collision_screening`: Goal978 can still say
it was a preliminary candidate, but the current release-facing status is
`public_wording_blocked`.

## Change

Updated generators:

- `scripts/goal978_rtx_speedup_claim_candidate_audit.py`
- `scripts/goal1006_public_rtx_claim_wording_gate.py`
- `scripts/goal1008_large_repeat_artifact_intake.py`
- `scripts/goal1009_public_rtx_wording_review_packet.py`

Regenerated artifacts:

- `docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.json`
- `docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.md`
- `docs/reports/goal1006_public_rtx_claim_wording_gate_2026-04-26.json`
- `docs/reports/goal1006_public_rtx_claim_wording_gate_2026-04-26.md`
- `docs/reports/goal1008_large_repeat_artifact_intake_2026-04-26.json`
- `docs/reports/goal1008_large_repeat_artifact_intake_2026-04-26.md`
- `docs/reports/goal1009_public_rtx_wording_review_packet_2026-04-26.json`
- `docs/reports/goal1009_public_rtx_wording_review_packet_2026-04-26.md`

## New Invariants

- Every pipeline artifact declares
  `current_public_wording_source = rtdsl.rtx_public_wording_matrix()`.
- Rows carry `current_public_wording_status` and
  `current_public_wording_boundary`.
- `robot_collision_screening` remains visible as a historical preliminary
  candidate in Goal978, but its current public wording status is explicitly
  `public_wording_blocked`.
- Goal1009 still excludes robot from candidate wording and lists it only under
  blocked rows.

## Tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal978_rtx_speedup_claim_candidate_audit_test \
  tests.goal1006_public_rtx_claim_wording_gate_test \
  tests.goal1008_large_repeat_artifact_intake_test \
  tests.goal1009_public_rtx_wording_review_packet_test \
  tests.goal1011_rtx_public_wording_matrix_test -v
```

Result: 18 tests OK.

## Boundary

This goal does not authorize any new public speedup wording. It only attaches
the current public-wording source of truth to older staged pipeline artifacts so
they cannot be mistaken for final release-facing wording.
