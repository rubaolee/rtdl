# Goal 528: v0.8 Post-Doc-Refresh Local Audit

Date: 2026-04-18

Status: accepted after Claude/Gemini/Codex consensus

## Purpose

Goals 525-527 updated public, example, capability-boundary, and history-facing
documentation after the earlier v0.8 local audit. Goal528 reruns local
release-readiness checks after those changes so the current `main` state does
not rely on stale Goal522 evidence alone.

## Inputs Since The Previous Audit

- Goal525: refreshed public docs after Goal524 Stage-1 proximity Linux
  performance characterization.
- Goal526: removed stale v0.8 app-count wording and listed all six current
  accepted v0.8 app examples.
- Goal527: refreshed `examples/README.md` and `docs/capability_boundaries.md`
  so the Stage-1 proximity apps and bounded ANN-candidate boundary are clear.

## Local Full Test Discovery

Command:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 232 tests in 60.097s
OK
```

## Public Command Harness

Command:

```text
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py \
  --machine macos-goal528-v08-post-doc-refresh \
  --output docs/reports/goal528_macos_public_command_check_2026-04-18.json
```

Artifact:

- `docs/reports/goal528_macos_public_command_check_2026-04-18.json`

Summary:

```json
{
  "passed": 62,
  "failed": 0,
  "skipped": 26,
  "total": 88
}
```

Backend status on this macOS host:

```json
{
  "cpu_python_reference": true,
  "oracle": true,
  "cpu": true,
  "embree": true,
  "optix": false,
  "vulkan": false
}
```

The OptiX/Vulkan skips are expected on this local macOS host. Linux backend
coverage remains anchored by Goal523 and Goal524.

## Documentation Stale-Phrase Scan

Command:

```text
rg -n "other two v0\\.8 apps|do not yet have Linux performance closure|Goal507 and Goal509 reports|pending external AI review|Status: pending external|TODO|TBD" \
  README.md docs/*.md docs/tutorials/*.md examples/README.md \
  history/COMPLETE_HISTORY.md history/revision_dashboard.md
```

Result:

```text
no matches
```

## History Map

Command:

```text
PYTHONPATH=src:. python3 scripts/goal495_complete_history_map.py
```

Result:

```json
{
  "valid": true,
  "counts": {
    "revision_rounds": 102,
    "archived_files": 1072,
    "docs_reports": 1551,
    "ad_hoc_reviews": 689,
    "handoffs": 404,
    "tracked_files": 5294
  }
}
```

## Diff Hygiene

Command:

```text
git diff --check
```

Result:

```text
pass
```

## Current Local Verdict

Goal528 local audit result: **ACCEPT PENDING EXTERNAL REVIEW**.

Known local boundaries:

- This is a macOS local audit, not a replacement for the Linux backend evidence
  in Goal523 and Goal524.
- The current v0.8 line remains accepted app-building work on `main`, not a new
  released support-matrix line.
- Stage-1 proximity performance remains a bounded RTDL-backend
  characterization, not an external-baseline speedup claim.

No local blocker is known from this audit.

## AI Consensus

- Claude review: `docs/reports/goal528_claude_review_2026-04-18.md`, verdict
  `ACCEPT`.
- Gemini Flash review: `docs/reports/goal528_gemini_review_2026-04-18.md`,
  verdict `ACCEPT`.
- Codex consensus: accepted. The audit is accurate, bounded to macOS local
  release-readiness evidence, and sufficient as a post-doc-refresh gate while
  preserving Linux backend reliance on Goals 523 and 524.
