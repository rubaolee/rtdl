# Call For Review: Goal4937 RayJoin Public Sample Materializer Wiring

Please review Goal4937.

## Files

- Completion report: `history/internal_docs/goal4937_rayjoin_public_sample_materializer_wiring_2026-07-03.md`
- POD artifacts:
  - `history/internal_docs/goal4937_pod_artifacts/first_run/summary.json`
  - `history/internal_docs/goal4937_pod_artifacts/first_run/section57_overlay.json`
  - `history/internal_docs/goal4937_pod_artifacts/first_run/section57_overlay_numba_materializer.json`
  - `history/internal_docs/goal4937_pod_artifacts/rerun1/summary.json`
  - `history/internal_docs/goal4937_pod_artifacts/rerun1/section57_overlay.json`
  - `history/internal_docs/goal4937_pod_artifacts/rerun1/section57_overlay_numba_materializer.json`

## Requested Verdict

Choose one:

- `approve_goal4937_byte_equal_but_not_faster_stop`
- `redo_goal4937_due_to_missing_evidence`
- `reject_goal4937_interpretation`

## Review Questions

1. Does the evidence prove the materializer-wired route remained byte-for-byte correct on the RayJoin public sample?
2. Does the evidence prove the materializer-wired route missed the writer performance gate?
3. Is the interpretation correct that this failed because the materializer was inserted after the app chain-loop work, so it added a generic assembly pass instead of replacing structure assembly?
4. Is it correct that no RayJoin speedup claim is authorized from Goal4937?
5. Is it correct to revert the experimental app code and retain only the report/artifacts?
6. Should the next Layer 3 attempt move the generic boundary earlier, so generic code owns grouping/descriptor/item structure directly instead of materializing after RayJoin-specific chain loops?

## Boundaries

- Do not authorize a public speedup claim.
- Do not authorize keeping a slower RayJoin app path as the default.
- Do not authorize RayJoin-specific output semantics in RTDL core.
- Do not authorize further micro-patching unless a new design removes the app chain-loop phase.
