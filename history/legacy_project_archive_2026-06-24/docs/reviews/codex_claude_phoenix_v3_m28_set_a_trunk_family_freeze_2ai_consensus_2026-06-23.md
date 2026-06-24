# Codex + Claude 2-AI Consensus: Phoenix V3 M28 Set-A Runtime-Trunk Family Freeze

Date: 2026-06-23
Status: `approve_with_amendments_applied`

## Packet

Freeze document:

`docs/rebuild/v3/phoenix_v3_m28_set_a_trunk_family_freeze_aggregate_tree_fused_vector_sum_2026-06-23.md`

Call for review:

`docs/reviews/call_for_review_phoenix_v3_m28_set_a_trunk_family_freeze_2026-06-23.md`

Claude review:

`docs/reviews/claude_phoenix_v3_m28_set_a_trunk_family_freeze_review_2026-06-23.raw.md`

M29 draft runbook:

`docs/rebuild/v3/phoenix_v3_m29_barnes_hut_v2_14_current_focused_pod_runbook_draft_2026-06-23.md`

Gemini attempt:

`docs/reviews/gemini_phoenix_v3_m28_set_a_trunk_family_freeze_review_2026-06-23.stderr.txt`

The Gemini attempt does not count toward consensus because the CLI failed with
`IneligibleTierError`. Claude is the valid external reviewer for this M28
consensus.

## Consensus Decision

Codex and Claude agree to freeze Barnes-Hut pressure / aggregate-tree fused
weighted-vector sum as the first Phoenix V3 Set-A runtime-trunk family.

The accepted family is:

`generic aggregate-tree fused weighted-vector sum 2D, explicit Numba CUDA partner, routed through prepared_execution_session_runner`

This is accepted as a first Set-A family freeze, not as release evidence and not
as a public speedup claim.

## Why Accepted

RTDBSCAN and RayJoin remain candidate Set-A families, but current evidence does
not show a material productized-runner win there. Barnes-Hut aggregate-tree fused
weighted-vector sum has the cleanest focused evidence:

- runner/control geomean: `0.999328x`;
- every runner/control row is above `0.998x`;
- output equivalence passes at all three serious body counts;
- runner metadata shows the productized prepared-execution runner is used;
- internal residency metadata passes on every runner sample;
- hot-path frontier/contribution host materialization is absent;
- historical prepared-OptiX-frontier displacement is large, but remains a no-go
  reference rather than the primary claim.

## Amendments Applied

Claude returned `approve_with_amendments` with no blocking findings. Codex
applied all four required amendments:

1. `runtime_sourced_material_gain: true` in the evidence `summary.json` is now
   explicitly described as historical OptiX/frontier displacement, not current
   runner/control material gain.
2. `validation_skipped: true` on the 45 evidence rows is now explained as
   skipped per-row CPU/oracle validation for serious performance rows, with
   correctness for this freeze carried by summary-level runner/control
   equivalence.
3. "Generic" is now scoped to API design, not multi-app coverage.
4. The `git_commit: null` remote provenance caveat is now restated in the M28
   packet and carried into the M29 runbook.

## M29 Authorization

M29 may proceed only as a focused v2.14/current Barnes-Hut classification and
focused runner/control check.

Allowed:

- inspect v2.14/current surfaces on the same POD;
- classify whether v2.14 lacks the current trunk surface, has an equivalent
  fused surface, has only CPU fused/typed-stream pieces, or has only
  node-coverage/frontier evidence;
- run the narrowly scoped Barnes-Hut rows described in the M29 runbook;
- record exact provenance, commands, medians, metadata gates, and boundaries.

Not allowed:

- all-app timing;
- release wording;
- public speedup wording;
- broad V3-over-V2 wording;
- RT-core speedup wording for the Numba CUDA fused route;
- true-zero-copy wording;
- V4 or embedding work.

## Verification

Local focused tests passed after the M28 amendments:

`py -3 -m unittest tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test tests.v3_phoenix_prepared_execution_session_runner_test`

Result: `43 tests`, `OK`.

Scoped whitespace check passed:

`git diff --check -- <M28/M29/review files>`

## Goal-Level Decision Audit

Decision: close M28 as approved-with-amendments-applied and proceed to M29
focused classification, not all-app.

1. Was I foolish?
   No. The decision uses the strongest current Set-A candidate and external
   review before spending more POD time.

2. If yes, what actions made the decision foolish?
   The foolish path would have been to treat the historical `12.73x` OptiX
   frontier displacement as a public V3-over-V2 speedup, or to ignore Claude's
   four amendments. Both are now blocked.

3. Was there another path?
   Yes. RTDBSCAN or RayJoin could be retried first, but their current evidence
   lacks material gain. All-app could also be run, but that remains forbidden
   until two accepted Set-A families exist.

4. Can I now try a different path that truly solves the problem?
   Yes. Run M29 as a focused v2.14/current classification, then pick and probe
   the second Set-A family before any all-app work.

## Non-Authorization

This consensus authorizes no Phoenix V3 release, no all-app run, no public
speedup claim, no broad V3-over-V2 claim, no RT-core speedup claim, no
true-zero-copy claim, no automatic partner selection, no V4 work, and no
embedding work.
