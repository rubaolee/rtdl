# Codex + Claude 2-AI Consensus: Phoenix V3 M29 Barnes-Hut Surface Classification

Date: 2026-06-23

Status: `approve_with_amendments_applied`

## Inputs

- M29 report:
  `docs/reports/phoenix_v3_m29_barnes_hut_v2_14_current_surface_classification_2026-06-23.md`
- M29 evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_m29_barnes_hut_surface_Cv7ppr/`
- M29 classifier:
  `scripts/v3_phoenix_m29_barnes_hut_surface_classification.py`
- Claude review:
  `docs/reviews/claude_phoenix_v3_m29_barnes_hut_surface_classification_review_2026-06-23.raw.md`
- M28 consensus:
  `docs/reviews/codex_claude_phoenix_v3_m28_set_a_trunk_family_freeze_2ai_consensus_2026-06-23.md`

## Consensus

Codex and Claude agree that M29 supports the classification:

`v2_14_has_cpu_fused_or_typed_stream_only`

The classification means v2.14 has Barnes-Hut CPU fused force-summary and
typed-stream pieces, but does not have the current Numba CUDA fused route and
does not have the Phoenix V3 prepared-execution session runner route for the
M28 aggregate-tree fused weighted-vector sum family.

Therefore M29 confirms a V3 surface/capability addition for this family, not a
same-contract v2.14 speedup claim.

## Claude Review Result

Claude verdict: `approve_with_amendments`

Blocking findings: none.

Required amendment:

- M28 amendment 3 must be carried forward explicitly: "generic" in the M28
  freeze means API-design scope only, not multi-app coverage.

Applied amendment:

- Added `generic_scope_note` to
  `docs/rebuild/v3/evidence/phoenix_v3_m29_barnes_hut_surface_Cv7ppr/summary.json`.
- Added matching prose to the M29 report's Carry-Forward Boundaries section.

After amendment, M29 carries all four M28 amendments forward:

- `runtime_sourced_material_gain: true` is scoped to historical
  OptiX/frontier displacement only, not current runner/control parity.
- `validation_skipped: true` is explained as large-row per-row CPU/oracle
  validation skipped, with runner/control contribution count and checksum X/Y
  gates carrying correctness for the freeze.
- "generic" means API-design scope only, not multi-app coverage.
- `git_commit: null` is preserved as a current remote execution tree caveat.

## Decision

M29 is closed as `classified_not_release`.

No additional timing rows are authorized for M29. Timing v2.14 node-coverage or
CPU fused rows against the current Numba CUDA runner would mix contracts and
create a false same-contract V3-over-v2.14 speedup claim.

M30 may proceed only as a focused second Set-A family probe/freeze. It must not
be an all-app run and must not broaden M29 into a release or public performance
claim.

## Goal-Level Decision Audit

Decision: close M29 after classification plus amendment, and move to focused M30.

1. Was I foolish?
   No. The evidence and Claude review agree that no equivalent v2.14 current
   runner surface exists to time against.

2. If yes, what actions made the decision foolish?
   The foolish action would be to manufacture a speedup by timing different
   contracts, such as v2.14 CPU fused or node-coverage rows against the current
   CUDA prepared runner.

3. Was there another path?
   Yes. Re-run current runner/control timing or force a v2.14/current timing
   row anyway. The first is redundant for M29, and the second would undermine
   the release discipline.

4. Can I now try a different path that truly solves the problem?
   Yes. M30 should seek the second true Set-A runtime-trunk family using
   focused POD evidence, with RTNN or RTDBSCAN as candidates and all-app still
   forbidden until two true Set-A families are accepted.

## Verification

- `Get-Content -Raw docs\rebuild\v3\evidence\phoenix_v3_m29_barnes_hut_surface_Cv7ppr\summary.json | ConvertFrom-Json`
- `git diff --check -- docs/rebuild/v3/evidence/phoenix_v3_m29_barnes_hut_surface_Cv7ppr/summary.json docs/reports/phoenix_v3_m29_barnes_hut_v2_14_current_surface_classification_2026-06-23.md docs/reviews/claude_phoenix_v3_m29_barnes_hut_surface_classification_review_2026-06-23.raw.md`

Both checks passed.

Earlier M29 validation remains part of the packet:

- `py -3 -m py_compile scripts\v3_phoenix_m29_barnes_hut_surface_classification.py`
- `git diff --check -- scripts/v3_phoenix_m29_barnes_hut_surface_classification.py`
- `py -3 -m unittest tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test tests.v3_phoenix_prepared_execution_session_runner_test`

Result: `43 tests`, `OK`.

## Non-Authorization

This consensus authorizes no Phoenix V3 release, no all-app run, no public
speedup claim, no broad V3-over-V2 claim, no RT-core speedup claim, no
true-zero-copy claim, no automatic partner-selection claim, no embedding work,
and no V4 work.
