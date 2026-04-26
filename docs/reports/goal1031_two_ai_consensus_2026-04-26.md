# Goal1031 Two-AI Consensus

Date: 2026-04-26

Scope: Local baseline smoke runner for the four `baseline_ready` Goal1030 entries.

Primary artifacts:

- `scripts/goal1031_local_baseline_smoke_runner.py`
- `tests/goal1031_local_baseline_smoke_runner_test.py`
- `docs/reports/goal1031_local_baseline_smoke_2026-04-26.md`
- `docs/reports/goal1031_local_baseline_smoke_2026-04-26.json`

Reviews:

- `docs/reports/goal1031_claude_review_2026-04-26.md`
- `docs/reports/goal1031_gemini_review_2026-04-26.md`

## Consensus Verdict

Status: `ACCEPT_WITH_OPTIONAL_DEPENDENCY_GAPS`.

Goal1031 is accepted as a smoke-scale local command-health check. It is not same-scale baseline evidence and does not authorize speedup claims.

## Shared Findings

Both reviewers agree that the runner:

- Clearly distinguishes smoke mode from full same-scale baseline work.
- Scales `--copies` down to `50` in smoke mode.
- Preserves explicit no-speedup-claim boundaries in JSON and Markdown.
- Separates optional SciPy dependency gaps from real command failures.
- Captures enough JSON summaries to verify command health without making backend speed comparisons.

## Smoke Run Result

The final smoke run status is `ok_with_optional_dependency_gaps`:

- `outlier_detection`: CPU, Embree, and SciPy commands passed.
- `dbscan_clustering`: CPU, Embree, and SciPy commands passed.
- `service_coverage_gaps`: CPU and Embree passed; SciPy is unavailable locally.
- `event_hotspot_screening`: CPU and Embree passed; SciPy is unavailable locally.

## Applied Follow-Ups

After Claude review, Codex applied two cleanup fixes:

- Subprocess execution now preserves the inherited environment with `os.environ` while overriding `PYTHONPATH`.
- Tests now directly validate `build_report(..., include_partial=False)` and `include_partial=True` selection behavior without executing commands.

The remaining non-blocking issue is that default output paths are date-stamped for this run and should be explicitly overridden for future runs to avoid overwriting archived evidence.

## Codex Decision

Close Goal1031. Next work should either install SciPy locally or mark SciPy baselines as Linux/optional-environment tasks, then begin same-scale baseline extraction for the highest-value `baseline_ready` app paths.
