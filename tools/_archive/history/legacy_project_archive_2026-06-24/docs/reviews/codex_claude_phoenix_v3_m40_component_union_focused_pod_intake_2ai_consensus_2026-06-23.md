# Codex + Claude 2-AI Consensus: Phoenix V3 M40 Component-Union Focused POD Intake

Date: 2026-06-23

Consensus verdict: `accept_with_caveats_fixed_locally_continue_step2`

## Inputs

M40 intake:

- `docs/reports/phoenix_v3_m40_component_union_focused_pod_intake_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_component_union_m39_focused_pod_ab_20260623_142706/run.log`

External review:

- Raw Claude review:
  `docs/reviews/claude_phoenix_v3_m40_component_union_focused_pod_intake_review_2026-06-23.raw.md`
- Recorded Claude review:
  `docs/reviews/claude_phoenix_v3_m40_component_union_focused_pod_intake_recorded_review_2026-06-23.md`

Local fix validation:

- Focused:
  `PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_m39_component_union_harness_test tests.v3_release_wording_gate_test`
  ran 9 tests OK.
- Full V3 rebuild:
  `PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild`
  ran 119 modules / 620 tests in 72.675s OK.
  stdout:
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m40_harness_caveat_fixes_20260623_143417.stdout.txt`
  stderr:
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m40_harness_caveat_fixes_20260623_143417.stderr.txt`

## Shared Conclusion

Codex and Claude agree:

- M40 is a real, RT-hardware-gated, interpretable focused POD run.
- M40 satisfies the bar for one positive Step-1 Set-A probe with caveats.
- The result is not invalidated by the stale status label, because `dry_run=false`,
  exit code `0`, variant JSONs, and timing metadata make the run state clear.
- The result is not release evidence and not all-app evidence.
- Step 2 may proceed only after the local harness caveats are fixed and verified.

The required caveats have been fixed locally:

- real-run status is now distinct from dry-run `not_pod_run`
- `runner_vs_legacy_hot_speedup` is now machine-readable

## Evidence Interpretation

M40 preliminary performance facts:

- runner vs Embree hot: `1.221027x`
- runner vs Embree inclusive wall: `2.421405x`
- runner vs legacy inclusive wall: `1.254316x`
- runner vs legacy hot: about `0.994x`, which is parity/slightly slower

The accepted interpretation is narrow:

- This is one positive Step-1 probe for fixed-radius graph component-union on
  one clustered geometry and one seed.
- The runner's legacy win in this run is inclusive wall, apparently from lower
  prepare/integration cost, not a faster hot path than the existing legacy
  OptiX route.
- Step 2 must track hot and wall metrics separately.
- Step 2 should prefer a non-degenerate geometry where possible.

## Next Authorized Work

Proceed to Step 2 local work:

1. Select a second Set-A family from the frozen Set-A list.
2. Attach it to the same productized prepared-execution runner discipline.
3. Expose full output contract and phase accounting.
4. Add machine-readable hot and wall comparisons.
5. Run local gates first.
6. Seek external review before any additional focused POD spend.

No new POD spend is authorized by this consensus. It authorizes Step-2 local
implementation and review preparation only.

## Goal-Level Decision Audit

1. Was I foolish? No, accepting M40 as narrow Step-1 evidence is supported by
   the POD artifacts and Claude's review.
2. If yes, what actions made the decision foolish? The only foolish risk would
   be converting M40 into release/all-app/public speedup claims; this consensus
   explicitly blocks that.
3. Was there another path that avoided getting stuck on the wrong idea? Yes:
   fix the harness caveats and require full matrix validation before moving to
   Step 2.
4. Can I now try a different path that actually solves the problem? Yes: move
   from one component-union probe to a second Set-A family under the same
   runner, which tests whether Phoenix V3 is becoming a general runtime trunk
   rather than another route-specific optimization.

## Non-Authorization Block

This consensus does not authorize release, all-app POD spend, public speedup
wording, V4/embedding/C-ABI work, external zero-copy claims, or broad
V3-over-V2 claims.
