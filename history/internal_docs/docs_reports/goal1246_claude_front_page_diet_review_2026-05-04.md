# Goal1246 Claude Review: Front-Page Diet

Date: 2026-05-04

Reviewer: Claude CLI (`claude --print --dangerously-skip-permissions ...`)

Scope:
- `README.md`
- `docs/README.md`
- `docs/application_catalog.md`
- `docs/release_facing_examples.md`
- `scripts/goal1020_public_docs_rtx_boundary_audit.py`
- `scripts/goal1179_public_docs_goal1177_boundary_audit.py`
- `scripts/goal1180_current_release_readiness_window_audit.py`
- `scripts/goal1185_goal1184_public_status_sync_audit.py`
- affected public-doc guard tests

## Initial Review

Claude initially returned `VERDICT: REJECT` because it believed
`tests/goal506_public_entry_v08_alignment_test.py` would fail on the phrase
`without claiming new backend or language internals`.

Codex verified that this was a false positive:

- `PYTHONPATH=src:. python3 -m unittest tests.goal506_public_entry_v08_alignment_test`
  - Result: `Ran 3 tests`, `OK`.
- A direct whitespace-normalized content check confirmed that
  `docs/README.md` contains:
  `The v0.8 app-building tutorial records future language pressure without claiming new backend or language internals.`

## Captured Claude Re-Review Verdict

VERDICT: ACCEPT

Reasons:
- My prior REJECT was based on the false belief that
  `"without claiming new backend or language internals"` was absent from
  `docs/README.md`. The string is present at lines 140-141, and the
  whitespace-normalized form matches the `assertIn` on `compact`. All three
  tests in `goal506_public_entry_v08_alignment_test.py` pass.
- The patch coherently slims the root `README.md` to a concise entry point and
  relocates detailed content to `docs/README.md` and other files in `docs/`.
  No guardrail content is lost: it is preserved in the docs subtree.
- All updated test files (`goal506`, `goal510`, `goal532`, `goal645`,
  `goal700`, `goal751`, `goal1179`) now point to the correct new file
  locations, and the required strings exist in those files. The `goal510`
  assertions (`"Goal509 Robot/Barnes-Hut Linux Performance Report"`,
  `"superseded by Goal748"`, `"candidate-generation timing separately from"`)
  are all present in `docs/release_facing_examples.md`. The `goal700`
  assertion (`outlier_detection / prepared_fixed_radius_density_summary`) is
  present in `docs/v1_0_rtx_app_status.md`.
- The audit scripts (`goal1179`, `goal1180`) correctly drop the `README.md`
  requirement block to match the thinned root README.
- The `goal1179` test assertion update (`assertNotIn("README.md", by_path)`)
  is consistent with the script no longer auditing `README.md`.

Required fixes:
- None.

## Final-Diff Re-Review Attempt

After the patch expanded to include additional old public-doc gates
(`Goal1020`, `Goal1185`, `Goal507`, `Goal524`, and v0.8/v0.9.5 link tests),
Codex attempted a final Claude review over the completed working-tree diff:

```bash
claude --print --dangerously-skip-permissions "Review Goal1246 final front-page diet ..."
```

The process produced no output for more than one minute and had closed stdin,
so it was terminated with `pkill -f "Review Goal1246 final front-page diet"`.
No final Claude verdict was produced. The earlier captured Claude review above
remains the external-AI review for the front-page diet goal; final acceptance is
therefore based on that saved ACCEPT plus the expanded local verification in
the consensus report.

## Gemini Attempt

Gemini CLI was attempted first with the same review packet. It failed after 10
retries with `No capacity available for model gemini-3-flash-preview on the
server`. No Gemini verdict was produced.
