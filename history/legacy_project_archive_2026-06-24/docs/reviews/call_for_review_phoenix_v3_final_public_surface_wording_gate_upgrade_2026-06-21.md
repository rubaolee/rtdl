# Call For Review: Phoenix V3 Final Public-Surface Wording Gate Upgrade

Date: 2026-06-21

Reviewer requested: Claude via local Claude Code.

## Scope

Review the focused Phoenix V3 wording-gate upgrade that converts the prior
first-pass wording scanner into a machine-readable final public-surface
claim-boundary gate, while keeping release authorization false.

Files to review:

- `scripts/v3_release_wording_gate.py`
- `scripts/v3_phoenix_release_readiness_gate.py`
- `tests/v3_release_wording_gate_test.py`
- `tests/v3_phoenix_release_readiness_gate_test.py`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_release_wording_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json`

## Intended Change

The wording gate now reports:

```text
gate_level: final_public_surface_claim_boundary_gate
final_public_surface_gate: true
missing_expected_m7_row_ids: []
release_authorized: false
public_speedup_claim_authorized: false
```

It adds checks for:

- all eleven exact M7 row ids present in the scanned public/evidence surface;
- unsupported `true` claim flags for release, broad speedup, package install,
  multi-GPU portability, secondary RT performance confirmation, or unscoped
  public speedup;
- existing overclaim and post-M150 leakage patterns.

The Phoenix release-readiness gate now requires:

```text
wording_gate_final_public_surface: true
wording_gate_level_is_final_public_surface: true
wording_gate_has_all_expected_m7_row_ids: true
```

Release remains blocked:

```text
status: blocked_not_release
release_authorized: false
blocking_reasons:
- release_authorization_false
- eleven_row_surface_still_too_narrow_for_major_release
- aggregate_release_readiness_consensus_blocks_release
```

## Validation Already Run

Targeted:

```text
py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test
Ran 23 tests OK
```

Full V3 rebuild:

```text
py -3 scripts\run_test_matrix.py --group v3_rebuild
91 modules / 438 tests OK
```

## Review Questions

1. Does this change truly close the old "first-pass wording scanner only"
   ambiguity as a final public-surface claim-boundary gate?
2. Does it preserve the key boundary that this gate does not authorize release?
3. Are the new regex checks too broad or too weak?
4. Does the release-readiness gate correctly consume the stronger wording gate?
5. Are there any P0/P1 fixes required before Codex records consensus?

## Required Verdict Format

Please return one of:

- `approve`
- `approve-with-amendments`
- `block`

Then list P0/P1 findings and a concise final recommendation.

